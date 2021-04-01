#!/bin/bash

set -e
set -x

SCRIPT_NAME=`echo $0 | awk -F "/" '{print $NF}'`
SCRIPT_PATH="$(readlink -f $0)"
SCRIPT_DIR="${SCRIPT_PATH%/*}"

TOOLS_DIR="$SCRIPT_DIR/../../chronometry"
PERFLINE_DIR="$SCRIPT_DIR/../"
STAT_DIR="$SCRIPT_DIR/../stat"
BUILD_DEPLOY_DIR="/root/perfline/build_deploy"
STAT_COLLECTION=""
# NODES="ssc-vm-c-1042.colo.seagate.com,ssc-vm-c-1043.colo.seagate.com"
# EX_SRV="pdsh -S -w $NODES"
# HA_TYPE="hare"
MKFS=

PERF_RESULTS_FILE='perf_results'
CLIENT_ARTIFACTS_DIR='client'
M0CRATE_ARTIFACTS_DIR='m0crate'
S3BENCH_LOGFILE='workload_s3bench.log'

function validate() {
    local leave=
    if [[ -z "$RESULTS_DIR" ]]; then
	echo "Result dir parameter is not passed"
	leave="1"
    fi

    if [[ -z "$WORKLOADS" ]]; then
	echo "Application workload is not specified"
	leave="1"
    fi

    if [[ -z "$NODES" ]]; then
	echo "Nodes are not specified"
	leave="1"
    fi

    case $HA_TYPE in
	"hare") echo "HA type: HARE" ;;
	"pcs") echo "HA type: Pacemaker" ;;
	*) 
	    echo "Unknown HA type: $HA_TYPE"
	    leave="1"
	    ;;
    esac

    if [[ -n $leave ]]; then
	exit 1
    fi
}

function build_deploy() {
    pushd $BUILD_DEPLOY_DIR
    ansible-playbook -i hosts run_build_deploy.yml --extra-vars "motr_repo_path=$MOTR_REPO \
hare_repo_path=$HARE_REPO s3server_repo_path=$S3SERVER_REPO hare_commit_id=$HARE_COMMIT_ID \
motr_commit_id=$MOTR_COMMIT_ID s3server_commit_id=$S3SERVER_COMMIT_ID" -v
    popd
}

function stop_hare() {
    ssh $PRIMARY_NODE 'hctl shutdown || true'    
}

function stop_pcs() {
    ssh $PRIMARY_NODE 'pcs resource disable motr-ios-c{1,2}'
    ssh $PRIMARY_NODE 'pcs resource disable s3server-c{1,2}-{1,2,3,4,5,6,7,8,9,10,11}'
    sleep 30
}

function stop_cluster() {
    echo "Stop cluster"

    case $HA_TYPE in
	"hare") stop_hare ;;
	"pcs") stop_pcs ;;
    esac
}

function cleanup_hare() {
    echo "Remove /var/log/seagate/motr/*"
    pdsh -S -w $NODES 'rm -rf /var/log/seagate/motr/*' || true

    echo "Remove /var/motr/*"
    pdsh -S -w $NODES 'rm -rf /var/motr/*' || true
}

function cleanup_pcs() {
    echo "Remove /var/motr/s3server*"
    pdsh -S -w $NODES 'rm -rf /var/motr/s3server*' || true
    pdsh -S -w $NODES 'rm -rf /var/log/seagate/motr/*' || true
    pdsh -S -w $NODES 'rm -rf /var/log/seagate/s3/s3server-*' || true
    

    local ioservice_list=$(ssh $PRIMARY_NODE "hctl status \
        | grep ioservice | sed 's/\[.*\]//' | awk '{print $2}'")

    echo "Remove ioservice(s)"
    for ios_fid in $ioservice_list; do
        local ios_dir="/var/motr/m0d-$ios_fid"
        local srv_node_cmd="ssh $PRIMARY_NODE 'if [ -e $ios_dir ]; then rm -rf $ios_dir; fi'"
        $EX_SRV $srv_node_cmd
    done
}

function cleanup_cluster() {
    case $HA_TYPE in
	"hare") cleanup_hare ;;
	"pcs") cleanup_pcs ;;
    esac
}

function restart_hare() {
    if [[ -n "$MKFS" ]]; then
        ssh $PRIMARY_NODE 'hctl bootstrap --mkfs /var/lib/hare/cluster.yaml'
    else
        ssh $PRIMARY_NODE 'hctl bootstrap /var/lib/hare/cluster.yaml'
    fi
}

function restart_pcs() {
    if [[ -n "$MKFS" ]]; then
        ssh $PRIMARY_NODE "ssh srvnode-1 'systemctl start motr-mkfs@0x7200000000000001:0xc'"
        ssh $PRIMARY_NODE "ssh srvnode-2 'systemctl start motr-mkfs@0x7200000000000001:0x55'"
    fi


    ssh $PRIMARY_NODE 'pcs resource enable motr-ios-c{1,2}'
#    sleep 30
    ssh $PRIMARY_NODE 'pcs resource enable s3server-c{1,2}-{1,2,3,4,5,6,7,8,9,10,11}'
#    sleep 120
    wait_for_cluster_start
}

function restart_cluster() {
    echo "Restart cluster"
    
    case $HA_TYPE in
	"hare") restart_hare ;;
	"pcs") restart_pcs ;;
    esac
}

function wait_for_cluster_start() {

    echo "wait for cluster start"

    while ! is_cluster_online
    do
#        if _check_is_cluster_failed; then
#            _err "cluster is failed"
#            exit 1
#        fi
#
        sleep 5
    done

    $EX_SRV $SCRIPT_DIR/wait_s3_listeners.sh 11

}

function is_cluster_online() {
    local all_services=$(ssh $PRIMARY_NODE 'hctl status | grep "\s*\[.*\]"')

    local srvc_states=$(echo "$all_services" | grep -E 's3server|ioservice|confd|hax' | awk '{print $1}')
    
    for state in $srvc_states; do
        if [[ "$state" != "[started]" ]]; then
            return 1
        fi
    done

    return 0
}

function run_workloads()
{
    mkdir -p $CLIENT_ARTIFACTS_DIR
    pushd $CLIENT_ARTIFACTS_DIR

    START_TIME=`date +%s000000000`
    for ((i = 0; i < $((${#WORKLOADS[*]})); i++)); do
        echo "workload $i"
        local cmd=${WORKLOADS[((i))]}
        #eval $cmd | tee workload-$i.log        
        #echo $cmd
        eval $cmd | tee workload-$i.log
	STATUS=${PIPESTATUS[0]}
    done

    STOP_TIME=`date +%s000000000`
    sleep 30
    popd			# $CLIENT_ARTIFACTS_DIR
}

function s3bench_workloads()
{
    mkdir -p $CLIENT_ARTIFACTS_DIR
    pushd $CLIENT_ARTIFACTS_DIR
    START_TIME=`date +%s000000000`
    $SCRIPT_DIR/s3bench_run.sh -b $BUCKETNAME -n $SAMPLE -c $CLIENT -o $IOSIZE | tee $S3BENCH_LOGFILE
    STATUS=${PIPESTATUS[0]}
    STOP_TIME=`date +%s000000000`
    sleep 120
    popd
}

function m0crate_workload()
{
    START_TIME=`date +%s000000000`

    local m0crate_work_dir="/tmp/m0crate_tmp" #TODO: make it random

    $EX_SRV "if [[ -d "$m0crate_work_dir" ]]; then rm -rf $m0crate_work_dir; fi;"

    $EX_SRV "mkdir -p $m0crate_work_dir \
             && cd $m0crate_work_dir \
             && $SCRIPT_DIR/run_m0crate $M0CRATE_PARAMS &> m0crate.%h.log"

    STATUS=$?

    STOP_TIME=`date +%s000000000`
    sleep 120
}

function create_results_dir() {
    echo "Create results folder"
    mkdir -p $RESULTS_DIR
    pushd $RESULTS_DIR
}

function save_motr_artifacts() {
    local ios_m0trace_dir="m0trace_ios"
    local configs_dir="configs"
    local dumps_dir="dumps"

    # local variables for Hare cluster
    local ioservice_list=$(cat $RESULTS_DIR/hctl-status.stop \
        | grep ioservice | sed 's/\[.*\]//' | awk '{print $2}')

    local ios_l=""
    for zzz in $ioservice_list; do
        ios_l="$ios_l $zzz"
    done

    mkdir -p $configs_dir
    pushd $configs_dir
    scp -r $PRIMARY_NODE:/etc/sysconfig/motr ./
    scp -r $PRIMARY_NODE:/var/lib/hare/cluster.yaml ./
    popd

    mkdir -p $ios_m0trace_dir
    pushd $ios_m0trace_dir
    if [[ -n $M0TRACE_FILES ]]; then
        $EX_SRV $SCRIPT_DIR/save_m0traces $(hostname) $(pwd) "motr" "\"$ios_l\""
    fi
    popd # $ios_motrace_dir

    mkdir -p $dumps_dir
    pushd $dumps_dir
    if [[ -n $ADDB_STOBS ]] && [[ -n $ADDB_DUMPS ]]; then
        if [[ -z "$M0PLAY_DB" ]]; then
            local no_m0play_option="--no-m0play-db"
        fi
        $EX_SRV $SCRIPT_DIR/process_addb $no_m0play_option --host $(hostname) --dir $(pwd) --app "motr" --io-services "\"$ios_l\"" --start $START_TIME --stop $STOP_TIME
    fi
    popd # $dumps_dir
}


function save_s3srv_artifacts() {
    local auth_dir="auth"
    local haproxy_dir="haproxy"
    local log_dir="log"
    local cfg_dir="cfg"
    local crash_dir="crash"

    for srv in $(echo $NODES | tr ',' ' '); do
        mkdir -p $srv
        pushd $srv

        # Fetch list of folders per server
        dirs=`ssh $srv -T "ls /var/log/seagate/motr/ | grep s3server | xargs -n1 basename"`
        echo $dirs
        mkdir $dirs

        for s3d in s3server*; do
            # Copy logs
            scp -r $srv:/var/log/seagate/s3/$s3d ./$s3d/$log_dir
        done

        mkdir -p $auth_dir
        scp -r $srv:/var/log/seagate/auth/* $auth_dir || true
        mv $auth_dir/server/app.log $auth_dir/server/app.$srv.log || true

        mkdir -p $haproxy_dir
        mkdir -p $haproxy_dir/$log_dir
        scp -r $srv:/var/log/haproxy* $haproxy_dir/$log_dir || true

        mkdir -p $haproxy_dir/$cfg_dir
        scp -r $srv:/etc/haproxy/* $haproxy_dir/$cfg_dir

        scp -r $srv:/opt/seagate/cortx/s3/conf/s3config.yaml ./
        scp -r $srv:/opt/seagate/cortx/s3/s3startsystem.sh ./
        scp -r $srv:/etc/hosts ./

        popd
    done

    if [[ -n $M0TRACE_FILES ]]; then
        $EX_SRV $SCRIPT_DIR/save_m0traces $(hostname) $(pwd) "s3server"
    fi

    if [[ -n $ADDB_STOBS ]]; then
        if [[ -z "$M0PLAY_DB" ]]; then
            local no_m0play_option="--no-m0play-db"
        fi
        $EX_SRV $SCRIPT_DIR/process_addb $no_m0play_option --host $(hostname) --dir $(pwd) --app "s3server" --start $START_TIME --stop $STOP_TIME
    fi
}

function save_m0crate_artifacts()
{
    local m0crate_workdir="/tmp/m0crate_tmp"

    $EX_SRV "scp -r $m0crate_workdir/m0crate.*.log $(hostname):$(pwd)"
    $EX_SRV "scp -r $m0crate_workdir/test_io.*.yaml $(hostname):$(pwd)"
    $EX_SRV "scp -r $m0crate_workdir/m0trace.* $(hostname):$(pwd)"

    if [[ -n $ADDB_STOBS ]]; then
        $EX_SRV $SCRIPT_DIR/process_addb --host $(hostname) --dir $(pwd) \
            --app "m0crate" --m0crate-workdir $m0crate_workdir \
            --start $START_TIME --stop $STOP_TIME
    fi

   $EX_SRV "rm -rf $m0crate_workdir"
}

function save_stats() {
    for srv in $(echo $NODES | tr ',' ' '); do
        mkdir -p $srv
        pushd $srv
	scp -r $srv:/var/perfline/iostat* iostat || true
	scp -r $srv:/var/perfline/blktrace* blktrace || true
	scp -r $srv:/var/perfline/dstat* dstat || true
        scp -r $srv:/var/perfline/glances* glances || true
	scp -r $srv:/var/perfline/hw* hw || true
	scp -r $srv:/var/perfline/network* network || true
	scp -r $srv:/var/perfline/5u84* 5u84 || true
	popd
    done
}

function save_perf_results() {
    local s3bench_log="$CLIENT_ARTIFACTS_DIR/$S3BENCH_LOGFILE"

    if [[ -f "$s3bench_log" ]]; then
        echo "Benchmark: s3bench" >> $PERF_RESULTS_FILE
        $SCRIPT_DIR/../stat/report_generator/s3bench_log_parser.py $s3bench_log >> $PERF_RESULTS_FILE
        echo "" >> $PERF_RESULTS_FILE
    fi

    if [[ -n "$RUN_M0CRATE" ]]; then
        for m0crate_log in $M0CRATE_ARTIFACTS_DIR/m0crate.*.log; do
            local hostname=$(echo $m0crate_log | awk -F "/" '{print $NF}' \
                           | sed 's/m0crate.//' | sed 's/.log//')
            echo "Benchmark: m0crate" >> $PERF_RESULTS_FILE
            echo "Host: $hostname" >> $PERF_RESULTS_FILE
            $SCRIPT_DIR/../stat/report_generator/m0crate_log_parser.py \
                    $m0crate_log >> $PERF_RESULTS_FILE
            echo "" >> $PERF_RESULTS_FILE
        done
    fi
}

function collect_artifacts() {
    local m0d="m0d"
    local s3srv="s3server"

    local stats="stats"

    echo "Collect artifacts"

    mkdir -p $stats
    pushd $stats
    save_stats
    popd

    mkdir -p $m0d
    pushd $m0d
    save_motr_artifacts
    popd			# $m0d

    mkdir -p $s3srv
    pushd $s3srv
    save_s3srv_artifacts
    popd			# $s3server

    if [[ -n "$RUN_M0CRATE" ]]; then
        mkdir -p $M0CRATE_ARTIFACTS_DIR
        pushd $M0CRATE_ARTIFACTS_DIR
        save_m0crate_artifacts
        popd
    fi

    save_perf_results    
    
    if [[ -n $ADDB_STOBS ]] && [[ -n $ADDB_DUMPS ]] && [[ -n $M0PLAY_DB ]]; then

        local m0playdb_parts="$m0d/dumps/m0play* $s3srv/*/m0play*"

        if [[ -n "$RUN_M0CRATE" ]]; then
            if ls $M0CRATE_ARTIFACTS_DIR/m0play* &> /dev/null; then
                m0playdb_parts="$m0playdb_parts $M0CRATE_ARTIFACTS_DIR/m0play*"
            else
                echo "m0play not found"
            fi
        fi

        $SCRIPT_DIR/merge_m0playdb $m0playdb_parts
        rm -f $m0playdb_parts
    fi
}

function close_results_dir() {
    echo "Close results dir"
    popd
}

function start_stat_utils()
{
    echo "Start stat utils"
    $EX_SRV "$STAT_DIR/start_stats_service.sh $STAT_COLLECTION" &
    sleep 30
}

function stop_stat_utils()
{
    echo "Stop stat utils"
    $EX_SRV "$STAT_DIR/stop_stats_service.sh $STAT_COLLECTION" 

    echo "Gather static info"
    $EX_SRV "$STAT_DIR/collect_static_info.sh"

    # wait
}

function start_measuring_workload_time()
{
    WORKLOAD_TIME_START_SEC=$(date +'%s')
}

function stop_measuring_workload_time()
{
    WORKLOAD_TIME_STOP_SEC=$(date +'%s')

    local stats="stats"
    mkdir -p $stats
    pushd $stats
    # Save workload time
    echo "workload_start_time: $WORKLOAD_TIME_START_SEC" > common_stats.yaml
    echo "workload_stop_time: $WORKLOAD_TIME_STOP_SEC" >> common_stats.yaml
    popd
}

function start_measuring_test_time()
{
    TEST_TIME_START_SEC=$(date +'%s')
}

function stop_measuring_test_time()
{
    TEST_TIME_STOP_SEC=$(date +'%s')
    
    local stats="stats"
    mkdir -p $stats
    pushd $stats
    # Save test time
	echo "test_start_time: $TEST_TIME_START_SEC" >> common_stats.yaml
    echo "test_stop_time: $TEST_TIME_STOP_SEC" >> common_stats.yaml
    popd
}

function generate_report()
{
    python3 $STAT_DIR/report_generator/gen_report.py . $STAT_DIR/report_generator
}

function main() {

    start_measuring_test_time
    
    if [[ -n $BUILD_DEPLOY ]]; then
        build_deploy       
    fi

    if [[ -n $MKFS ]]; then
	# Stop cluster 
	stop_cluster
	cleanup_cluster
	
	# Restart cluster -- do mkfs, whatever...
#	restart_cluster
    fi

    restart_cluster

    # Create artifacts folder
    create_results_dir

    # @artem -- place code below
    # Start stat utilities
    echo "Start stat utilities"
    start_stat_utils

    # Start workload time execution measuring
    start_measuring_workload_time
    
    # Start workload
    run_workloads
    
    # Start s3bench workload
    if [[ -n $S3BENCH ]]; then
        s3bench_workloads
    fi

    if [[ -n "$RUN_M0CRATE" ]]; then
        m0crate_workload
    fi

    # Stop workload time execution measuring
    stop_measuring_workload_time

    # @artem -- place code below
    # Stop stat utilities
    echo "Stop stat utilities"
    stop_stat_utils


    ssh $PRIMARY_NODE 'hctl status' > hctl-status.stop
    # if [[ -n $MKFS ]]; then
    # 	# Stop cluster
    # 	stop_cluster
    # fi
    stop_cluster

    # Collect ADDBs/m0traces/m0play.db
    collect_artifacts

    # Generate plots, hists, etc
    echo "Generate plots, hists, etc"

    # if [[ -n $MKFS ]]; then
    # 	cleanup_cluster
    # 	restart_cluster
    # fi

    stop_measuring_test_time
    
   generate_report

    # Close results dir
    close_results_dir

    exit $STATUS
}

echo "parameters: $@"

while [[ $# -gt 0 ]]; do
    case $1 in
        -w|--workload_config)
            WORKLOADS+=("$2")
            shift
            ;;
        -p|--result-path)
            RESULTS_DIR=$2
            shift
            ;;
        --deploybuild)
            BUILD_DEPLOY="1"
            ;;
        -motr_repo)
            MOTR_REPO=$2
            shift
            ;;
        -hare_repo)
            HARE_REPO=$2
            shift
            ;;
	-s3server_repo)
            S3SERVER_REPO=$2
            shift
            ;;
	-motr_commit_id)
            MOTR_COMMIT_ID=$2
            shift
            ;;
	-hare_commit_id)
            HARE_COMMIT_ID=$2
            shift
            ;;
	-s3server_commit_id)
	    S3SERVER_COMMIT_ID=$2
	    shift
	    ;;
        -bucket)
            BUCKETNAME=$2
            shift
            ;;
        -clients)
            CLIENT=$2
            shift
            ;;
        -sample)
            SAMPLE=$2
            shift
            ;;
        -size)
            IOSIZE=$2
            shift
            ;;
        --nodes)
            NODES=$2
            EX_SRV="pdsh -S -w $NODES"
            PRIMARY_NODE=$(echo "$NODES" | cut -d "," -f1)
            shift
            ;;
        --ha_type)
            HA_TYPE=$2
            shift
            ;;
        --fio)                 
            FIO="1"
            ;;
        --s3bench)
            S3BENCH="1"
            ;;
        --iostat)
            STAT_COLLECTION="$STAT_COLLECTION-IOSTAT"
            ;;
        --dstat)
            STAT_COLLECTION="$STAT_COLLECTION-DSTAT"
            ;;
        --blktrace)
            STAT_COLLECTION="$STAT_COLLECTION-BLKTRACE"
            ;;
        --glances)
            STAT_COLLECTION="$STAT_COLLECTION-GLANCES"
            ;;
        --m0trace-files)
            M0TRACE_FILES="1"
            ;;
        --m0trace-dumps)
            M0TRACE_DUMPS="1"
            ;;
        --addb-stobs)
            ADDB_STOBS="1"
            ;;
        -d|--addb-dumps)
            ADDB_DUMPS="1"
            ;;
        --m0play-db)
            M0PLAY_DB="1"
            ;;
        --motr-trace)
            MOTR_TRACE="1"
            ;;
        --m0crate)
            RUN_M0CRATE="1"
            ;;
        --m0crate-params)
            M0CRATE_PARAMS="$2"
            shift
            ;;
	--mkfs)
	    MKFS="1"
	    ;;
        *)
            echo -e "Invalid option: $1\nUse --help option"
            exit 1
            ;;
    esac
    shift
done

validate

# int main()
main
