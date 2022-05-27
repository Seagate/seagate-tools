#!/usr/bin/env bash
#
#
# Copyright (c) 2022 Seagate Technology LLC and/or its Affiliates
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
#
# For any questions about this software or licensing,
# please email opensource@seagate.com or cortx-questions@seagate.com.
#
# -*- coding: utf-8 -*-

source "$SCRIPT_DIR/$CLUSTER_TYPE/${S3_APP}_artifacts.sh"

K8S_SCRIPTS_DIR="$CORTX_K8S_REPO/k8_cortx_cloud"

HAX_CONTAINER="cortx-hax"
LOCAL_PODS_FS='/mnt/fs-local-volume/local-path-provisioner'
DATA_POD_FS_TEMPLATE="cortx-data-fs"
SERVER_POD_FS_TEMPLATE="cortx-server-fs"
LOCAL_MOUNT_POINT='/mnt/fs-local-volume/etc/gluster'
CONTAINER_MOUNT_POINT='/share'
DOCKER_CONTAINER_NAME="perfline_cortx"
MOTR_ARTIFACTS_DIR="m0d"
S3_ARTIFACTS_DIR="s3server"
CORTX_DATA_POD_PREFIX="cortx-data"
CORTX_SERVER_POD_PREFIX="cortx-server"

M0D_INIT_PID=1
S3_INIT_PID=10001
M0CRATE_INIT_PID=20001


function run_cmd_in_container()
{
    local pod="$1"
    local container="$2"
    shift
    shift

    ssh "$PRIMARY_NODE" "kubectl exec $pod -c $container -- $@"
}

function is_cluster_online()
{
    local all_services=$(run_cmd_in_container "$PRIMARY_POD" $HAX_CONTAINER hctl status | grep "\s*\[.*\]")
    local srvc_states=$(echo "$all_services" | grep -E 'rgw|s3server|ioservice|confd|hax' | awk '{print $1}')
    for state in $srvc_states; do
        if [[ "$state" != "[started]" ]]; then
            return 1
        fi
    done
    return 0
}

function stop_cluster() {
    echo "Stop LC cluster"

    # wait for m0d to complete all operations
    sleep 120

    ssh "$PRIMARY_NODE" "cd $K8S_SCRIPTS_DIR && ./shutdown-cortx-cloud.sh"
}

function cleanup_logs() {
    echo "Remove m0trace/addb/log files from LC cluster"
    $EX_SRV 'rm -rf /mnt/fs-local-volume/etc/gluster/var/log/cortx/*' || true
}

function detect_primary_pod()
{
    PRIMARY_POD=$(ssh "$PRIMARY_NODE" "kubectl get pod -o wide" \
         | grep $CORTX_DATA_POD_PREFIX \
         | grep "$PRIMARY_NODE" \
         | awk '{print $1}')

    if [[ -z "$PRIMARY_POD" ]]; then
        echo "detection of POD failed"
        exit 1
    fi
}

function cleanup_k8s() {
    $EX_SRV 'rm -rf /etc/3rd-party/openldap'
    $EX_SRV 'rm -rf /var/data/3rd-party/*'
    $EX_SRV 'rm -rf /mnt/fs-local-volume/local-path-provisioner/*'
    $EX_SRV 'rm -rf /mnt/fs-local-volume/etc/gluster/var/log/cortx/*'
}

function restart_cluster() {
    echo "Restart LC cluster (PODs)"

    if [[ -n "$MKFS" ]]; then
        ssh "$PRIMARY_NODE" "cd $K8S_SCRIPTS_DIR && ./destroy-cortx-cloud.sh"
        cleanup_k8s
#        $EX_SRV "cd "$K8S_SCRIPTS_DIR" && ./prereq-deploy-cortx-cloud.sh $DISK"
        ssh "$PRIMARY_NODE" "cd $K8S_SCRIPTS_DIR && ./deploy-cortx-cloud.sh"
    else
        ssh "$PRIMARY_NODE" "cd $K8S_SCRIPTS_DIR && ./start-cortx-cloud.sh"
    fi

    detect_primary_pod
    wait_for_cluster_start

    ssh "$PRIMARY_NODE" "kubectl get pod"
    sleep 20
}

function wait_for_cluster_start() {
    echo "wait for cluster start"

    while ! is_cluster_online "$PRIMARY_NODE"
    do
        sleep 5
    done

    # $EX_SRV $SCRIPT_DIR/wait_s3_listeners.sh $S3SERVER
    # sleep 300
}

function save_m0crate_artifacts()
{
    start_docker_container

    local m0crate_dir="$LOCAL_MOUNT_POINT/var/log/cortx/m0crate"
    local m0crate_dir_docker="$CONTAINER_MOUNT_POINT/var/log/cortx/m0crate"

    # check if directory exists
    if ssh "$PRIMARY_NODE" "[ ! -d $m0crate_dir ]"; then
        echo "directory $m0crate_dir doesn't exist"
        return 0
    fi

    local pid=$M0CRATE_INIT_PID

    for iteration in $(ssh "$PRIMARY_NODE" "ls $m0crate_dir"); do
        mkdir "$iteration"
        pushd "$iteration"

        local machine_ids=$(ssh "$PRIMARY_NODE" "ls $m0crate_dir/$iteration")

        for machine_id in $machine_ids; do

            local fid_dirs=$(ssh "$PRIMARY_NODE" "ls $m0crate_dir/$iteration/$machine_id")

            for fid_dir in $fid_dirs; do
                mkdir "$fid_dir"
                pushd "$fid_dir"

                scp "$PRIMARY_NODE":/$m0crate_dir/"$iteration"/"$machine_id"/"$fid_dir"/*.log ./ || true
                scp "$PRIMARY_NODE":/$m0crate_dir/"$iteration"/"$machine_id"/"$fid_dir"/*.yaml ./ || true

                if [[ -n $ADDB_DUMPS ]]; then
                    local addb_dirs=$(ssh "$PRIMARY_NODE" "ls $m0crate_dir/$iteration/$machine_id/$fid_dir | grep addb_ || true")

                    for addb_dir in $addb_dirs; do
                        local addb_stob="$m0crate_dir_docker/$iteration/$machine_id/$fid_dir/$addb_dir/o/100000000000000:2"
                        ssh "$PRIMARY_NODE" "docker exec $DOCKER_CONTAINER_NAME m0addb2dump -f -- \"$addb_stob\"" > dumpc_${pid}.txt
                        ((pid=pid+1))
                    done
                fi

                if [[ -n $M0TRACE_FILES ]]; then
                    local m0traces=$(ssh "$PRIMARY_NODE" "ls $m0crate_dir/$iteration/$machine_id/$fid_dir | grep m0trace. || true")

                    for m0trace in $m0traces; do
                        local m0trace_path="$m0crate_dir_docker/$iteration/$machine_id/$fid_dir/$m0trace"
                        ssh "$PRIMARY_NODE" "docker exec $DOCKER_CONTAINER_NAME m0trace --no-pager -i $m0trace_path" > "$m0trace".txt
                    done
                fi

                popd # $fid_dir
            done
        done
        popd # $iteration
    done

    stop_docker_container

    # create m0play.db if dumpc* files exist
    if ls */*/dumpc* &> /dev/null; then
        "$TOOLS_DIR"/addb2db_multiprocess.sh --dumps ./*/*/dumpc*
        mv m0play.db m0play.m0crate.db
    fi
}

function save_motr_configs() {
    local config_dir="configs"

    local pod
    local containers
    local mapping
    local service
    local trace_dir
    local addb_dir

    mkdir -p $config_dir
    pushd $config_dir

    for srv in $(echo $NODES | tr ',' ' '); do
 	    pod=$(ssh "$PRIMARY_NODE" "kubectl get pod -o wide" | grep "$srv" | grep $CORTX_DATA_POD_PREFIX | awk '{print $1}')
	    containers=$(ssh "$PRIMARY_NODE" "kubectl get pods $pod -o jsonpath='{.spec.containers[*].name}'" | tr ' ' '\n' | grep cortx-motr-io)
        mkdir -p "$srv"
	    pushd "$srv"

	    for cont in $containers ; do
	        mkdir -p "$cont"
	        pushd "$cont"

	        # Copy motr config
	        ssh "$PRIMARY_NODE" "kubectl exec $pod -c $cont -- cat /etc/sysconfig/motr" > motr
	        ssh "$PRIMARY_NODE" "kubectl exec $pod -c $cont -- cat /etc/cortx/cluster.conf" > cluster.conf

	        # Gather metadata
	        service=$(ssh "$PRIMARY_NODE" "kubectl exec $pod -c $cont -- ps auxww" | grep m0d | tr ' ' '\n' | grep -A1 -- "-f" | tail -n1 | tr -d '<' | tr -d '>')

	        trace_dir=$(cat motr | grep MOTR_M0D_TRACE | grep -v "#")
	        addb_dir=$(cat motr | grep MOTR_M0D_ADDB | grep -v "#")

	        mapping="${srv} ${pod} ${cont} ${service} ${trace_dir} ${addb_dir}\n${mapping}"
	        popd		# $cont
	    done
	    popd			# $srv
    done

    popd			# $config_dir

    printf "$mapping" > ioservice_map
}




function save_cluster_status() {
    run_cmd_in_container "$PRIMARY_POD" $HAX_CONTAINER hctl status > hctl-status.stop

    mkdir -p $MOTR_ARTIFACTS_DIR
    pushd $MOTR_ARTIFACTS_DIR
    save_motr_configs
    popd 			# $MOTR_ARTIFACTS_DIR

    save_s3app_configs
}

function prepare_cluster() {
    # update /etc/hosts
    local i=0
    ssh "$PRIMARY_NODE" 'sed -i "/seagate/d" /etc/hosts'
    for node in ${NODES//,/ };
    do
        local ip=$(ssh "$PRIMARY_NODE" "kubectl get pods -o custom-columns=NAME:.metadata.name,NODE:.spec.nodeName,IP:.status.podIP | grep $node | grep $CORTX_SERVER_POD_PREFIX" | awk '{print $3}')
        ((i=i+1))
        if [ -z "$ip" ]; then
           echo "s3 ip detection failed"
           exit 1
        fi
        ssh "$PRIMARY_NODE" "echo $ip s3node$i s3.seagate.com sts.seagate.com iam.seagate.com >> /etc/hosts"
    done

    create_s3_account
}

function collect_stat_data()
{
    run_cmd_in_container "$PRIMARY_POD" $HAX_CONTAINER cat /etc/cortx/cluster.conf > cluster.conf

    for srv in $(echo "$NODES" | tr ',' ' '); do
        local cluster_conf="/tmp/cluster.conf"
        local disks_map="/tmp/cortx_disks_map"
        local hostname_short=$(echo "$srv" | awk -F '.' '{print $1}')
        scp cluster.conf $srv:$cluster_conf
        ssh "$srv" "$SCRIPT_DIR/LC/get_disks_map.py $cluster_conf $hostname_short > $disks_map"
    done
}

function save_motr_traces() {
    local pod
    local cont
    local serv
    local trace
    local addb
    local lines_n
    local rel_path
    local files
    local dirs
    local uid
    local name

    set +e

    lines_n=$(cat ../ioservice_map | wc -l)
    for i in $(seq 1 "$lines_n") ; do
	read h pod cont serv trace addb <<< $(awk "NR==$i" ../ioservice_map)

	eval "$trace/m0d-$serv"
	dirs=$(ssh "$PRIMARY_NODE" "docker exec $DOCKER_CONTAINER_NAME find /share/var/log/motr -name \"*$serv*\" -exec realpath {} \;" | grep trace)
	for d in $dirs ; do
	    files=$(ssh "$PRIMARY_NODE" "docker exec $DOCKER_CONTAINER_NAME ls -1 $d" | grep m0trace | grep -v txt)
	    for file in $files; do
		ssh "$PRIMARY_NODE" "nohup docker exec $DOCKER_CONTAINER_NAME m0trace -i $d/$file -o $d/$file.txt &" &
	    done
	done
    done

    # Wait until all async m0traces finish
    wait

    # Copy traces to results folder
    for i in $(seq 1 "$lines_n") ; do
	read h pod cont serv trace addb <<< $(awk "NR==$i" ../ioservice_map)

	eval "$trace/m0d-$serv"
	name="m0d-$serv"

	mkdir -p "$name"
	pushd "$name"
	dirs=$( ssh "$PRIMARY_NODE" "docker exec $DOCKER_CONTAINER_NAME find /share/var/log/motr -name \"*$serv*\" -exec realpath {} \;" | grep trace)
	for d in $dirs ; do
	    uid=$(echo "$d" | awk -F'/' '{print $(NF-2)}')

	    mkdir -p "$uid"
	    pushd "$uid"
	    # Assuming `/share` at the beginning of the string
	    rel_path="${d:6}"
	    scp -r "$PRIMARY_NODE":$LOCAL_MOUNT_POINT/"$rel_path"/* ./
	    popd		# $uid
	done
	popd			# $name
    done

    set -e
}

function save_motr_addb() {
    local pod
    local cont
    local serv
    local trace
    local addb
    local lines_n
    local rel_path
    local pid
    local addb_stob
    local uid

    set +e

    > addb_mapping
    pid=$M0D_INIT_PID
    lines_n=$(cat ../ioservice_map | wc -l)
    for i in $(seq 1 "$lines_n") ; do
	read h pod cont serv trace addb <<< $(awk "NR==$i" ../ioservice_map)

	eval "$addb/m0d-$serv"
	dirs=$(ssh "$PRIMARY_NODE" "docker exec $DOCKER_CONTAINER_NAME find /share/var/log/motr -name \"*$serv*\" -exec realpath {} \;" | grep addb)

	for d in $dirs ; do
	    uid=$(echo "$d" | awk -F'/' '{print $(NF-2)}')

	    stobs=$(ssh "$PRIMARY_NODE" "docker exec $DOCKER_CONTAINER_NAME ls -1 $d" | grep "addb-stob")
	    for st in $stobs; do
		addb_stob="$d/$st/o/100000000000000:2"
		echo "$h" "$pod" "$cont" "$serv" "$addb_stob" "$uid" $pid >> addb_mapping
                ssh "$PRIMARY_NODE" "docker exec $DOCKER_CONTAINER_NAME /bin/bash -c \"m0addb2dump -f -- $addb_stob\"" > dumps_${pid}.txt &
		((pid=pid+1))
	    done
	done
    done

    wait
    set -e
}

function generate_motr_m0play() {
    if ls dumps* &> /dev/null; then
        "$TOOLS_DIR"/addb2db_multiprocess.sh --dumps ./dumps*
	mv m0play.db m0play.m0d.db
    fi
}

function check_existing_docker() {
    docker ps | grep "$DOCKER_CONTAINER_NAME"
    status=$?
    if [ $status -eq 0 ]; then
        docker rm -f "$DOCKER_CONTAINER_NAME"
    fi
}
function start_docker_container() {
    local image

    set +e
    check_existing_docker
    image=$(ssh "$PRIMARY_NODE" "cat $K8S_SCRIPTS_DIR/solution.yaml" | grep "cortxdata:" | awk '{print $2}')
    ssh "$PRIMARY_NODE" "docker run --rm -dit --name $DOCKER_CONTAINER_NAME --mount type=bind,source=$LOCAL_MOUNT_POINT,target=/share $image sleep infinity"
    set -e
}

function stop_docker_container() {
    set +e
    ssh "$PRIMARY_NODE" "docker stop $DOCKER_CONTAINER_NAME"
    set -e
}

function save_motr_artifacts() {
    local ios_m0trace_dir="m0trace_ios"
    local dumps_dir="dumps"

    start_docker_container

    mkdir -p $ios_m0trace_dir
    pushd $ios_m0trace_dir
    if [[ -n $M0TRACE_FILES ]]; then
	save_motr_traces
    fi
    popd # $ios_motrace_dir

    mkdir -p $dumps_dir
    pushd $dumps_dir
    if [[ -n $ADDB_DUMPS ]]; then
        save_motr_addb
        fiter_addb_dumps "m0d"
        generate_motr_m0play
    fi
    popd # $dumps_dir

    stop_docker_container
}

function copy_pods_artifacts() {
    local var_dir="var"

    mkdir -p $var_dir
    pushd $var_dir

    for srv in $(echo "$NODES" | tr ',' ' '); do
        data_pod_fs_dir=$(ssh "$srv" ls -t $LOCAL_PODS_FS | grep $DATA_POD_FS_TEMPLATE | head -1)
        server_pod_fs_dir=$(ssh "$srv" ls -t $LOCAL_PODS_FS | grep $SERVER_POD_FS_TEMPLATE | head -1)

        if [[ -z "$data_pod_fs_dir" ]]; then
            echo "detection of data POD filesystem was failed"
            exit 1
        fi

        if [[ -z "$server_pod_fs_dir" ]]; then
            echo "detection of server POD filesystem was failed"
            exit 1
        fi

        set +e
        rsync -avr --exclude "db" --exclude "db-log" "$srv":$LOCAL_PODS_FS/"$data_pod_fs_dir"/* ./
        rsync -avr --exclude "db" --exclude "db-log" "$srv":$LOCAL_PODS_FS/"$server_pod_fs_dir"/* ./
        set -e
    done

    popd			# $var_dir

    LOCAL_MOUNT_POINT=$(pwd)
}

function collect_artifacts() {
    local m0d="$MOTR_ARTIFACTS_DIR"
    local s3srv="$S3_ARTIFACTS_DIR"
    local stats="stats"
    local pods="pods"

    echo "Collect artifacts"

    mkdir -p $pods
    pushd $pods
    copy_pods_artifacts
    popd

    mkdir -p $stats
    pushd $stats
    save_stats
    popd

    mkdir -p $m0d
    pushd $m0d
    save_motr_artifacts
    popd			# $m0d

    save_s3app_artifacts

    if [[ -n "$RUN_M0CRATE" ]]; then
         mkdir -p "$M0CRATE_ARTIFACTS_DIR"
         pushd "$M0CRATE_ARTIFACTS_DIR"
         save_m0crate_artifacts
         popd
    fi

    save_perf_results

    if [[ -n $ADDB_DUMPS ]]; then
        local m0playdb_parts="$m0d/dumps/m0play*"

        # TODO: improve that
        if [[ "$S3_APP" == "s3rsv" ]]; then
            m0playdb_parts="$m0playdb_parts $s3srv/dumps/m0play*"
        fi

        if [[ -n "$RUN_M0CRATE" ]]; then
            if ls "$M0CRATE_ARTIFACTS_DIR"/m0play* &> /dev/null; then
                m0playdb_parts="$m0playdb_parts $M0CRATE_ARTIFACTS_DIR/m0play*"
            else
                echo "m0play not found"
            fi
        fi

        "$SCRIPT_DIR"/merge_m0playdb "$m0playdb_parts"
        rm -f "$m0playdb_parts"
        #$SCRIPT_DIR/../../chronometry_v2/fix_reqid_collisions.py --fix-db --db ./m0play.db
    fi

    if [[ -n $ADDB_ANALYZE ]] && [[ -f "m0play.db" ]]; then
        local m0play_path="$(pwd)/m0play.db"
        local stats_addb="$stats/addb"
        mkdir -p $stats_addb
        pushd $stats_addb
        "$SCRIPT_DIR"/process_addb_data.sh --db "$m0play_path"
        popd
    fi

    if [[ "$STAT_COLLECTION" == *"GLANCES"* ]]; then
        pushd $stats
        local srv_nodes=$(echo "$NODES" | tr ',' ' ')
        "$SCRIPT_DIR"/artifacts_collecting/process_glances_data.sh "$srv_nodes"
        popd
    fi

    # # generate structured form of stats
    # $SCRIPT_DIR/../stat/gen_run_metadata.py -a $(pwd) -o run_metadata.json
}

function m0crate_workload()
{
    local iteration=$1
    shift

    local m0crate_params=$@
    START_TIME=$(date +%s000000000)

    local pids=""

    for srv in $(echo "$NODES" | tr ',' ' '); do
        local hostname_short=$(echo "$srv" | awk -F '.' '{print $1}')
        ssh "$PRIMARY_NODE" "$SCRIPT_DIR/$CLUSTER_TYPE/run_m0crate $iteration $hostname_short $m0crate_params" &
        pids="$pids $!"
    done

    wait "$pids"

    # STATUS=$?

    STATUS=0 #TODO: fix it

    STOP_TIME=$(date +%s000000000)
    sleep 20
}

function parse_addb_duration_in_sec()
{
    local duration=$(echo "$@" | grep -o -E '[0-9]+')
    local time_unit=$(echo "$@" | tr -d ' ' | sed 's/[0-9]*//g')
    case $time_unit in
        'sec'|'s'|'second')
            ADDB_DURATION_IN_SEC=$duration
            ;;
        'min'|'m'|'minute')
            ADDB_DURATION_IN_SEC=$((duration * 60))
            ;;
        'hr'|'h'|'hour')
            ADDB_DURATION_IN_SEC=$((duration * 3600))
            ;;
        'all'|'')
            ADDB_DURATION_IN_SEC="all"
            ;;
        *)
            echo -e "Invalid time unit"
            exit 1
            ;;
    esac

}

function fiter_addb_dumps()
{
    dump_file_type=$1
    parse_addb_duration_in_sec "$ADDB_DURATION"

    if [ $ADDB_DURATION_IN_SEC != 'all' ]; then
        for dump_file in $(find . -name "dump*txt" -exec realpath {} \; | grep "$dump_file_type"); do
            local end_time=$(cat "$dump_file" | sort -n | tail -1 | awk '{print $2}' | cut -d "." -f1)
            local reformat_endtime=$(echo "$end_time" | sed 's/-/ /3')
            local end_time_in_s=$(date -d "$reformat_endtime" +%s)

            local tmp_time=$((end_time_in_s - ADDB_DURATION_IN_SEC))
            local start_time=$(date -d @$tmp_time '+%Y-%m-%d-%H:%M:%S')
            python3 - "$dump_file" "$start_time" "$end_time" << EOF
import sys
with open(sys.argv[1],'r') as f:
    for line in f:
        d = line.strip().split(" ")[1]
        if d >= sys.argv[2] and d <= sys.argv[3]:
           with open('tmp_dump', 'a') as the_file:
                the_file.write(line)
EOF
            mv -f tmp_dump "$dump_file"
        done
    fi
}
