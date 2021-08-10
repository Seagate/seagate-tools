#!/bin/bash

declare -A benchmark_type
declare -A benchmarks

set -e
set -x

SCRIPT_NAME=`echo $0 | awk -F "/" '{print $NF}'`
SCRIPT_PATH="$(readlink -f $0)"
SCRIPT_DIR="${SCRIPT_PATH%/*}"
PERFLINE_DIR="$SCRIPT_DIR/../.."
PUBLIC_DATA_INTERFACE=$(ip addr show | egrep 'data0|enp179s0|enp175s0f0|eth0' | grep -Po 'inet \K[\d.]+')
source "$SCRIPT_DIR/../../perfline.conf"

EX_SRV="pdsh -S -w $NODES"
PRIMARY_NODE=$(echo "$NODES" | cut -d "," -f1)
CUSTOM_COUNT=1
COUNT=0

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

function start_measuring_benchmark_time()
{
    WORKLOAD_TIME_START_SEC=$(date +'%s')
}

function stop_measuring_benchmark_time()
{
    WORKLOAD_TIME_STOP_SEC=$(date +'%s')
}

function pushd_to_results_dir() {
    echo "go to results folder"
    pushd $RESULTS_DIR
}

function custom_benchmark()
{
    mkdir -p $CORE_BENCHMARK
    pushd $CORE_BENCHMARK
    START_TIME=`date +%s000000000`
    eval $CUSTOM_BENCHMARKS | tee custom-benchmark-$CUSTOM_COUNT-$(date +"%F_%T.%3N").log
    ((CUSTOM_COUNT=CUSTOM_COUNT+1))
    STATUS=${PIPESTATUS[0]}
    STOP_TIME=`date +%s000000000`
    sleep 30
    popd			# $CORE_BENCHMARK
}

function fio_workloads()
{
   mkdir -p $CORE_BENCHMARK
   pushd $CORE_BENCHMARK
   START_TIME=`date +%s000000000`  
   echo "Fio workload triggered on $NODES" 
   $EX_SRV "$SCRIPT_DIR/run_fiobenchmark.sh $FIO_PARAMS"
   STATUS=${PIPESTATUS[0]}
   STOP_TIME=`date +%s000000000`
   sleep 120
   popd
}

function run_lnet_workloads()
{
    mkdir -p $CORE_BENCHMARK
    pushd $CORE_BENCHMARK
    START_TIME=`date +%s000000000`
    ssh $PRIMARY_NODE "$SCRIPT_DIR/lnet_workload.sh $NODES $LNET_OPS" | tee $LNET_WORKLOG-$(date +"%F_%T.%3N").log
    STATUS=${PIPESTATUS[0]}
    STOP_TIME=`date +%s000000000`
    popd
}

function iperf_workload()
{
    mkdir -p $CORE_BENCHMARK
    pushd $CORE_BENCHMARK
    START_TIME=`date +%s000000000`
    iperf -s | tee $(hostname)_iperf-$(date +"%F_%T.%3N").log &
    for node in ${NODES//,/ }
    do
        ssh $node "iperf -c $PUBLIC_DATA_INTERFACE $IPERF_PARAMS" > $node-iperf_workload-$(date +"%F_%T.%3N").log
    done
    pkill iperf
    STATUS=${PIPESTATUS[0]}
    STOP_TIME=`date +%s000000000`
    popd
}

function close_results_dir() {
    echo "Close results dir"
    popd
}

function main() {

    start_measuring_benchmark_time

    # go to artifacts folder
    pushd_to_results_dir
    
    for key in ${!benchmark_type[@]}; do
        case "${benchmark_type[${key}]}" in
             "custom")
                echo "Start custom benchmarkss"
                CUSTOM_BENCHMARKS=${benchmarks[${key}]}
                custom_benchmark
                ;;
             "lnet")
                echo "Start lnet workload"
                LNET_OPS=${benchmarks[${key}]}
                run_lnet_workloads
                ;;
             "fio")
                echo "Start fio workload"
                FIO_PARAMS=${benchmarks[${key}]}
                fio_workloads
                ;;
             "iperf")
                echo "Start iperf workload"
                IPERF_PARAMS=${benchmarks[${key}]}
                iperf_workload
                ;;
             *)
                echo "Default condition to be executed"
                ;;
        esac
    done

    # Stop workload time execution measuring
    stop_measuring_benchmark_time
 
    exit $STATUS
}

echo "parameters: $@"

while [[ $# -gt 0 ]]; do
    case $1 in
        -w|--workload_config)
            benchmark_type["$COUNT"]+="custom"
            benchmarks["$COUNT"]+="$2"
            ((COUNT=COUNT+1))
            shift
            ;;

        -p|--result-path)
            RESULTS_DIR=$2
            shift
            ;;
        --fio)                 
            FIO="1"
            ;;
        --fio-params)
            benchmark_type["$COUNT"]+="fio"
            benchmarks["$COUNT"]+="$2"
            ((COUNT=COUNT+1))
            shift
            ;;
        --lnet)
            LNET="1"
            ;;
        -ops)
            benchmark_type["$COUNT"]+="lnet"
            benchmarks["$COUNT"]+="$2"
            ((COUNT=COUNT+1))
            shift
            ;;       
        --iperf)
            RUN_IPERF="1"
            ;;
        --iperf-params)
            benchmark_type["$COUNT"]+="iperf"
            benchmarks["$COUNT"]+="$2"
            ((COUNT=COUNT+1))
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

# int main()
main