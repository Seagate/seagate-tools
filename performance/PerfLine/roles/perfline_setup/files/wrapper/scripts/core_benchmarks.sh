#!/bin/bash

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
    for ((i = 0; i < $((${#CUSTOM_BENCHMARKS[*]})); i++)); do
        echo "workload $i"
        local cmd=${CUSTOM_BENCHMARKS[((i))]}
        eval $cmd | tee custom-corebenchmark-${i}.log
	STATUS=${PIPESTATUS[0]}
    done
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
   $EX_SRV "$SCRIPT_DIR/run_fiobenchmark.sh -t $DURATION -bs $BLOCKSIZE -nj $NUMJOBS -tm $TEMPATE"
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
    ssh $PRIMARY_NODE "$SCRIPT_DIR/lnet_workload.sh $NODES $LNET_OPS" | tee $LNET_WORKLOG
    STATUS=${PIPESTATUS[0]}
    STOP_TIME=`date +%s000000000`
    popd
}

function iperf_workload()
{
    mkdir -p $CORE_BENCHMARK
    pushd $CORE_BENCHMARK
    START_TIME=`date +%s000000000`
    iperf -s | tee $(hostname)_iperf.log &
    for node in ${NODES//,/ }
    do
        ssh $node "iperf -c $PUBLIC_DATA_INTERFACE $IPERF_PARAMS" > $node\_iperf_workload.log
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
    
    # Start custom benchmarks
    if [[ -n "$CUSTOM_BENCHMARKS" ]]; then
        custom_benchmark
    fi

    # lnet workload
    if [[ -n $LNET ]]; then
        run_lnet_workloads
    fi
    
    # fio workload
    if [[ -n $FIO ]]; then
        fio_workloads
    fi
    
    if [[ -n $RUN_IPERF ]]; then
        iperf_workload
    fi

    # Stop workload time execution measuring
    stop_measuring_benchmark_time
 
    exit $STATUS
}

echo "parameters: $@"

while [[ $# -gt 0 ]]; do
    case $1 in
        -w|--workload_config)
            CUSTOM_BENCHMARKS+=("$2")
            shift
            ;;

        -p|--result-path)
            RESULTS_DIR=$2
            shift
            ;;
        --fio)                 
            FIO="1"
            ;;
        -t)
            DURATION=$2
            shift
            ;;
        -bs)
            BLOCKSIZE=$2
            shift
            ;;
        -nj)
            NUMJOBS=$2
            shift
            ;;
        -tm)
            TEMPATE=$2
            shift
            ;;
        --lnet)
            LNET="1"
            ;;
        -ops)
            LNET_OPS=$2
            shift
            ;;       
        --iperf)
            RUN_IPERF="1"
            ;;
        --iperf-params)
            IPERF_PARAMS="$2"
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
