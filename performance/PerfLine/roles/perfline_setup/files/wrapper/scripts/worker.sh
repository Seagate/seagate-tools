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


declare -A workloads
declare -A workload_type
set -e
set -x

SCRIPT_NAME=`echo $0 | awk -F "/" '{print $NF}'`
SCRIPT_PATH="$(readlink -f $0)"
SCRIPT_DIR="${SCRIPT_PATH%/*}"

TOOLS_DIR="$SCRIPT_DIR/../../chronometry"
PERFLINE_DIR="$SCRIPT_DIR/../"
STAT_DIR="$SCRIPT_DIR/../stat"
# PUBLIC_DATA_INTERFACE=$(ip addr show | egrep 'data0|enp179s0|enp175s0f0|eth0|p1p1' | grep -Po 'inet \K[\d.]+')

source "$SCRIPT_DIR/../../perfline.conf"
source "$SCRIPT_DIR/$CLUSTER_TYPE/worker_polymorphic_funcs.sh"

STAT_COLLECTION=""
MKFS=""
EX_SRV="pdsh -R ssh -S -w $NODES"
PRIMARY_NODE=$(echo "$NODES" | cut -d "," -f1)
# S3SERVER=$(ssh $PRIMARY_NODE "cat /var/lib/hare/cluster.yaml | \
#             grep -o 's3: [[:digit:]]*'| head -1 | cut -d ':' -f2 | tr -d ' '")

COUNT=0
CUSTOM_COUNT=1

function validate() {
    local leave=
    if [[ -z "$RESULTS_DIR" ]]; then
	echo "Result dir parameter is not passed"
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

function custom_workloads()
{
    mkdir -p $CLIENT_ARTIFACTS_DIR
    pushd $CLIENT_ARTIFACTS_DIR

    START_TIME=`date +%s000000000`
    eval $CUSTOM_WORKLOADS | tee custom-workload-$CUSTOM_COUNT-$(date +"%F_%T.%3N").log
    ((CUSTOM_COUNT=CUSTOM_COUNT+1))
    STATUS=${PIPESTATUS[0]}

    STOP_TIME=`date +%s000000000`
    sleep 30

    popd			# $CLIENT_ARTIFACTS_DIR
}

function s3bench_workloads()
{
    local s3bench_params=$@
    mkdir -p $CLIENT_ARTIFACTS_DIR
    pushd $CLIENT_ARTIFACTS_DIR
    START_TIME=`date +%s000000000`
    $SCRIPT_DIR/s3bench_run.sh $s3bench_params | tee $S3BENCH_LOGFILE-$(date +"%F_%T.%3N").log
    STATUS=${PIPESTATUS[0]}
    STOP_TIME=`date +%s000000000`
    sleep 60
    popd
}

function pushd_to_results_dir() {
    echo "go to results folder"
    pushd $RESULTS_DIR
}

function save_stats() {
    for srv in $(echo $NODES | tr ',' ' '); do
        mkdir -p $srv
        pushd $srv
        scp -r $srv:/var/perfline/iostat* iostat || true
        scp -r $srv:/var/perfline/blktrace* blktrace || true
        scp -r $srv:/var/perfline/dstat* dstat || true

        if [[ "$STAT_COLLECTION" == *"GLANCES"* ]]; then
            mkdir glances
            scp $srv:/var/perfline/glances*/glances.csv glances
        fi

        scp -r $srv:/var/perfline/hw* hw || true
        scp -r $srv:/var/perfline/network* network || true
        scp -r $srv:/var/perfline/5u84* 5u84 || true
        scp -r $srv:/var/perfline/fio* fio || true

        ssh $srv "$SCRIPT_DIR/artifacts_collecting/collect_disks_info.sh" > disks.mapping
        popd
    done
}

function save_perf_results() {
    local s3bench_files=$(ls $CLIENT_ARTIFACTS_DIR | grep $S3BENCH_LOGFILE)
    for s3bench_file in $s3bench_files;
    do
       local s3bench_log="$CLIENT_ARTIFACTS_DIR/$s3bench_file"
       if [[ -f "$s3bench_log" ]]; then
           echo "Benchmark: $s3bench_file" >> $PERF_RESULTS_FILE
           $SCRIPT_DIR/../stat/report_generator/s3bench_log_parser.py $s3bench_log >> $PERF_RESULTS_FILE
           echo "" >> $PERF_RESULTS_FILE
       fi
    done

    if [[ -n "$RUN_M0CRATE" ]]; then

        # TODO: m0crate execution code for LR have to be changed
        # in order to support the same structure of m0crate artifacts.
        # Example: m0crate/0/m0crate-0x7200000000000001:0x29
        for iteration in $(ls "$M0CRATE_ARTIFACTS_DIR" | grep -E ^[0-9]+$); do
            for m0crate_log in $M0CRATE_ARTIFACTS_DIR/$iteration/m0crate-*/m0crate.*.log; do
                local fname=$(echo $m0crate_log | awk -F "/" '{print $NF}')
                local motr_port=$(echo $fname | awk -F '.' '{print $2}')
                local hostname=$(echo $fname | sed "s/m0crate.$motr_port.//" | sed "s/.log//")

                echo "Benchmark: m0crate" >> $PERF_RESULTS_FILE
                echo "Host: $hostname" >> $PERF_RESULTS_FILE
                echo "Motr port: $motr_port" >> $PERF_RESULTS_FILE
                $SCRIPT_DIR/../stat/report_generator/m0crate_log_parser.py \
                        $m0crate_log >> $PERF_RESULTS_FILE
                echo "" >> $PERF_RESULTS_FILE
            done
        done
    fi

    if `ls $CORE_BENCHMARK/*iperf-* > /dev/null`; then
        i=0
        iperf_logs=$(ls $CORE_BENCHMARK/*iperf-*)
        for iperf_log in $iperf_logs;
        do
            ((i=i+1))
            echo "Benchmark: iPerf-$i" >> $PERF_RESULTS_FILE
            $SCRIPT_DIR/../stat/report_generator/iperf_log_parser.py $iperf_log >> $PERF_RESULTS_FILE
            echo "" >> $PERF_RESULTS_FILE
        done
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
    WORKLOAD_TIME_START_SEC=`date +'%s'`
}

function stop_measuring_workload_time()
{
    WORKLOAD_TIME_STOP_SEC=`date +'%s'`
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

function do_result_backup()
{
    result_dir_path=$(dirname ${RESULTS_DIR})
    cur_result_dir=$(basename ${RESULTS_DIR})
    pushd $result_dir_path

    echo "Backing up results to NFS Location"
    if ! mount | grep "$BACKUP_MOUNT_POINT"
    then
        mkdir -p $BACKUP_MOUNT_POINT
        mount $BACKUP_NFS_LOCATION $BACKUP_MOUNT_POINT
    fi
    tar -czf /tmp/${cur_result_dir}.tar.gz $cur_result_dir
    cp /tmp/${cur_result_dir}.tar.gz ${BACKUP_MOUNT_POINT}/
    tar -xzf ${BACKUP_MOUNT_POINT}/${cur_result_dir}.tar.gz -C ${BACKUP_MOUNT_POINT}/
    rm -rf $cur_result_dir /tmp/${cur_result_dir}.tar.gz ${BACKUP_MOUNT_POINT}/${cur_result_dir}.tar.gz
    ln -s ${BACKUP_MOUNT_POINT}/${cur_result_dir} $cur_result_dir
    echo "Backup complete"
    popd
}

function perform_workloads()
{
    local m0crate_iteration=0

    length=${#workload_type[@]}
    for (( key=0; key<${length}; key++ )); do
        case "${workload_type[${key}]}" in
             "custom")
                echo "Start custom workloads"
                CUSTOM_WORKLOADS=${workloads[${key}]}
                custom_workloads
                ;;
             "s3bench")
                echo "Start s3bench workload"
                s3bench_workloads ${workloads[${key}]}
                ;;
             "m0crate")
                echo "Start m0crate workload (iteration $m0crate_iteration)"
                m0crate_workload $m0crate_iteration ${workloads[${key}]}
                ((m0crate_iteration=m0crate_iteration+1))
                ;;
            *)
                echo "Default condition to be executed"
                ;;
        esac
    done
}

function main() {

    start_measuring_test_time

    stop_cluster
    cleanup_logs

    # go to artifacts folder
    pushd_to_results_dir

    restart_cluster
    prepare_cluster
    collect_stat_data

    # Start stat utilities
    echo "Start stat utilities"
    start_stat_utils

    # Start workload time execution measuring
    start_measuring_workload_time

    perform_workloads

    # Stop workload time execution measuring
    stop_measuring_workload_time

    # Stop stat utilities
    echo "Stop stat utilities"
    stop_stat_utils

    save_cluster_status
    stop_cluster

    # Collect ADDBs/m0traces/m0play.db
    collect_artifacts

    # Generate plots, hists, etc
    echo "Generate plots, hists, etc"

    stop_measuring_test_time

    generate_report

    # Close results dir
    close_results_dir

    # Backup result dir
    if [[ -n $BACKUP_RESULT ]]; then
        do_result_backup
    fi

    exit $STATUS
}

echo "parameters: $@"

while [[ $# -gt 0 ]]; do
    case $1 in
        -w|--workload_config)
            workload_type["$COUNT"]+="custom"
            workloads["$COUNT"]+="$2"
            ((COUNT=COUNT+1))
            shift
            ;;
        -p|--result-path)
            RESULTS_DIR=$2
            shift
            ;;
        --s3bench)
            S3BENCH="1"
            ;;
        --s3bench-params)
            workload_type["$COUNT"]+="s3bench"
            workloads["$COUNT"]+="$2"
            ((COUNT=COUNT+1))
            shift
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
        -d|--addb-dumps)
            ADDB_DUMPS="1"
            ;;
	    --addb-analyze)
            ADDB_ANALYZE="1"
            ;;
        --motr-trace)
            MOTR_TRACE="1"
            ;;
        --m0crate)
            RUN_M0CRATE="1"
            ;;
        --m0crate-params)
            workload_type["$COUNT"]+="m0crate"
            workloads["$COUNT"]+="$2"
            ((COUNT=COUNT+1))
            shift
            ;;
        --mkfs)
            MKFS="1"
            ;;
        --backup-result)
            BACKUP_RESULT="1"
            ;;
        --addb-duration)
            ADDB_DURATION=$2
            shift
            ;;
        *)
            echo -e "Invalid option: $1\nUse --help option"
            exit 1
            ;;
    esac
    shift
done

validate
main

