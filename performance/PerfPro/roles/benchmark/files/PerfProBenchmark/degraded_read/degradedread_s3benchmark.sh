#! /usr/bin/bash
TOOL_NAME='s3bench'
ACCESS_KEY=`cat /root/.aws/credentials | grep -A 3 default | grep aws_access_key_id | cut -d " " -f3`
SECRET_KEY=`cat /root/.aws/credentials | grep -A 3 default | grep secret_access_key | cut -d " " -f3`
BINPATH=/root/PerfProBenchmark/s3bench
CURRENTPATH=`pwd`
BENCHMARKLOG=$CURRENTPATH/dr_s3b.log
#ENDPOINTS=https://s3.seagate.com         
BUCKETNAME="seagate-dr"
TIMESTAMP=`date +'%Y-%m-%d_%H:%M:%S'`
CLIENTS=""     
NUMSAMPLES=""     
IO_SIZE=""
FLAGS=""
CLUSTER_STATE=""
MAIN="/root/PerfProBenchmark/main.yml"
CONFIG="/root/PerfProBenchmark/config.yml"
LOG_COLLECT="/root/PerfProBenchmark/collect_logs.py"
BUILD=`python3 /root/PerfProBenchmark/read_build.py $CONFIG 2>&1`
ENDPOINTS=`python3 /root/PerfProBenchmark/get_param.py $CONFIG`
RESULT_DIR=/root/PerfProBenchmark/perfpro_build$BUILD/results/degraded_read/

validate_args() {

        if [[ -z $CLIENTS ]] || [[ -z $NUMSAMPLES ]] || [[ -z $IO_SIZE ]] || [[ -f $FLAGS ]] || [[ -c $CLUSTER_STATE ]]; then
                show_usage
        fi

}

show_usage() {
        echo -e "\n \t  Usage : ./run_s3benchmark.sh -nc NO_OF_CLIENTS -ns NO_OF_SAMPLES -s \"iosize\" -f FLAGS  -cs CLUSTER_STATE \n"
        echo -e "\t -nc\t:\t number of clients \n"
        echo -e "\t -ns\t:\t number of samples\n"
        echo -e "\t -s\t:\t size of the objects in bytes\n" 
        echo -e "\t -f\t:\t flags for s3bench_perfpro\n" 
        echo -e "\t -cs\t:\t cluster state\n"     
        echo -e "\tExample\t:\t ./run_s3benchmark.sh -nc 128,256,512 -ns 1024,2048,4096 -s 4Kb,16Kb,1Mb,4Mb,128Mb -f '-skipCleanup' -cs 'normal_read' \n"
        exit 1
}


s3benchmark() {
for NO_OF_SAMPLES in ${NUMSAMPLES//,/ }     
do
    for NUMCLIENTS in ${CLIENTS//,/ }
    do 
        for SIZE_OF_OBJECTS in  ${IO_SIZE//,/ }    
        do
            bucket=$BUCKETNAME-${SIZE_OF_OBJECTS,,}
            aws s3 mb s3://$bucket > /dev/null 2>&1
            value=$(echo "$SIZE_OF_OBJECTS" | sed -e 's/Kb//g' | sed -e 's/Mb//g' )
            units=$(echo ${SIZE_OF_OBJECTS:(-2)})
            case "$units" in
                 Mb)   let 'value *= 1024 * 1024'  ;;
                 Kb)   let 'value *= 1024' ;;
                 b|'')   let 'value += 0'    ;;
                 *)
                     value=
                     echo "Unsupported units '$units'" >&2
                 ;;
            esac

            echo "S3Benchmark is running for object size : $SIZE_OF_OBJECTS, Clients: $NUMCLIENTS"

            echo 'y' | rm report.s3bench > /dev/null 2>&1
            rm -rf s3bench-*.log
            
            TOOL_DIR=$BENCHMARKLOG/$TOOL_NAME/numclients_$NUMCLIENTS/buckets_1/$SIZE_OF_OBJECTS
            mkdir -p $TOOL_DIR 
            if [ $SIZE_OF_OBJECTS = "1Kb" ]; then         
                  echo "$BINPATH/s3bench_perfpro -accessKey=$ACCESS_KEY  -accessSecret=$SECRET_KEY -bucket=$bucket -endpoint=$ENDPOINTS -numClients=$NUMCLIENTS -numSamples=$NO_OF_SAMPLES -objectNamePrefix=loadgen -objectSize=$SIZE_OF_OBJECTS -headObj -putObjTag -getObjTag $FLAGS -o $TOOL_DIR/report.s3bench -label object_$SIZE_OF_OBJECTS\_numsamples_$NO_OF_SAMPLES\_buckets_1\_sessions_$NUMCLIENTS" 

                  $BINPATH/s3bench_perfpro -accessKey=$ACCESS_KEY  -accessSecret=$SECRET_KEY -bucket=$bucket -endpoint=$ENDPOINTS -numClients=$NUMCLIENTS -numSamples=$NO_OF_SAMPLES -objectNamePrefix=loadgen -objectSize=$SIZE_OF_OBJECTS -headObj -putObjTag -getObjTag $FLAGS -o $TOOL_DIR/report.s3bench -label object_$SIZE_OF_OBJECTS\_numsamples_$NO_OF_SAMPLES\_buckets_1\_sessions_$NUMCLIENTS 
                  mv s3bench-object_$SIZE_OF_OBJECTS\_numsamples_$NO_OF_SAMPLES\_buckets_1\_sessions_$NUMCLIENTS.log $TOOL_DIR/s3bench_$CLUSTER_STATE\_object_$SIZE_OF_OBJECTS\_numsamples_$NO_OF_SAMPLES\_buckets_1\_sessions_$NUMCLIENTS\.log

            else
               echo "$BINPATH/s3bench_perfpro -accessKey=$ACCESS_KEY  -accessSecret=$SECRET_KEY -bucket=$bucket -endpoint=$ENDPOINTS -numClients=$NUMCLIENTS -numSamples=$NO_OF_SAMPLES -objectNamePrefix=loadgen -objectSize=$SIZE_OF_OBJECTS $FLAGS -o $TOOL_DIR/report.s3bench -label object_$SIZE_OF_OBJECTS\_numsamples_$NO_OF_SAMPLES\_buckets_1\_sessions_$NUMCLIENTS"

                    $BINPATH/s3bench_perfpro -accessKey=$ACCESS_KEY  -accessSecret=$SECRET_KEY -bucket=$bucket -endpoint=$ENDPOINTS -numClients=$NUMCLIENTS -numSamples=$NO_OF_SAMPLES -objectNamePrefix=loadgen -objectSize=$SIZE_OF_OBJECTS $FLAGS -o $TOOL_DIR/report.s3bench -label object_$SIZE_OF_OBJECTS\_numsamples_$NO_OF_SAMPLES\_buckets_1\_sessions_$NUMCLIENTS
                  mv s3bench-object_$SIZE_OF_OBJECTS\_numsamples_$NO_OF_SAMPLES\_buckets_1\_sessions_$NUMCLIENTS.log $TOOL_DIR/s3bench_$CLUSTER_STATE\_object_$SIZE_OF_OBJECTS\_numsamples_$NO_OF_SAMPLES\_buckets_1\_sessions_$NUMCLIENTS\.log

            fi
            aws s3 rb s3://$bucket > /dev/null 2>&1
            echo "S3Benchmark is completed for object size : $SIZE_OF_OBJECTS"
        done
        echo "S3Benchmark is completed for number of clients : $NUMCLIENTS"
    done
    echo "S3Benchmark is completed for number of Samples : $NO_OF_SAMPLES"
done
echo 'Successfully completed'

}


while [ ! -z $1 ]; do
        
        case $1 in
        -nc)     shift
                CLIENTS="$1"
        ;;

        -ns)    shift
                NUMSAMPLES="$1"
        ;;

        -s)    shift
                IO_SIZE="$1"       
        ;;

        -f)    shift
                FLAGS="$1"
        ;;

        -cs)    shift
                CLUSTER_STATE="$1"
        ;;
        
        *)     
                show_usage
                break
        esac
        shift
done

validate_args

if [ ! -d $BENCHMARKLOG ]; then
     mkdir $BENCHMARKLOG
     s3benchmark
     sleep 20
     mkdir -p $RESULT_DIR/ 
     cp -r $BENCHMARKLOG/$TOOL_NAME $RESULT_DIR/

else
     rm -rf $BENCHMARKLOG
     mkdir $BENCHMARKLOG
     s3benchmark
     sleep 20
     mkdir -p $RESULT_DIR/
     cp -r $BENCHMARKLOG/$TOOL_NAME $RESULT_DIR/     
fi
