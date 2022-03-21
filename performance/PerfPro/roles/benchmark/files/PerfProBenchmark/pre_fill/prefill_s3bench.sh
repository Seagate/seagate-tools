#! /usr/bin/bash
TOOL_NAME='s3bench'
ACCESS_KEY=`cat /root/.aws/credentials | grep -A 3 default | grep aws_access_key_id | cut -d " " -f3`
SECRET_KEY=`cat /root/.aws/credentials | grep -A 3 default | grep secret_access_key | cut -d " " -f3`
BINPATH=/root/PerfProBenchmark/s3bench
CURRENTPATH=/root/PerfProBenchmark
BENCHMARKLOG=$CURRENTPATH/prefill/
BUCKETNAME="prefill"
CLIENTS=""
NUMSAMPLES=""
NUMBUCKET=""
IO_SIZE=""
CONFIG="/root/PerfProBenchmark/config.yml"
BUILD=`python3 /root/PerfProBenchmark/read_build.py $CONFIG 2>&1`
RESULT_DIR=/root/PerfProBenchmark/perfpro_build$BUILD/results/prefill
REGION=us-east-1

validate_args() {

        if [[ -z $ENDPOINTS ]] || [[ -z $CLIENTS ]] || [[ -z $NUMSAMPLES ]] || [[ -z $IO_SIZE ]] || [[ -z $NUMBUCKET ]] ; then
                show_usage
        fi

}

show_usage() {
        echo -e "\n \t  Usage : ./run_s3benchmark.sh -ep END_POINTS -nc NO_OF_CLIENTS -ns NO_OF_SAMPLES -s \"iosize\"   \n"
        echo -e "\t -ep\t:\t endpoints \n"
        echo -e "\t -nc\t:\t number of clients \n"
        echo -e "\t -ns\t:\t number of samples\n"
        echo -e "\t -s\t:\t size of the objects in bytes\n"       
        echo -e "\tExample\t:\t ./run_s3benchmark.sh -nc 128,256,512 -ns 1024,2048,4096 -s 4Kb,16Kb,1Mb,4Mb,128Mb  \n"
        exit 1
}


s3benchmark() {
for NO_OF_SAMPLES in ${NUMSAMPLES//,/ }     
do
    for NUMCLIENTS in ${CLIENTS//,/ }
    do 
        for SIZE_OF_OBJECTS in  ${IO_SIZE//,/ }    
        do
            bucket=$BUCKETNAME-$RANDOM
            aws s3 mb s3://$bucket
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

            echo "$BINPATH/s3bench_perfpro -region $REGION  -accessKey=$ACCESS_KEY  -accessSecret=$SECRET_KEY -bucket=$bucket -endpoint=$ENDPOINTS -numClients=$NUMCLIENTS -numSamples=$NO_OF_SAMPLES -objectNamePrefix=prefill -objectSize=$SIZE_OF_OBJECTS"

	    "$BINPATH"/s3bench_perfpro -region="$REGION"  -accessKey="$ACCESS_KEY"  -accessSecret="$SECRET_KEY" -bucket="$bucket" -endpoint="$ENDPOINTS" -numClients="$NUMCLIENTS" -numSamples="$NO_OF_SAMPLES" -objectNamePrefix=prefill -objectSize="$SIZE_OF_OBJECTS" -skipCleanup -skipRead -o "$TOOL_DIR"/report.s3bench -label object_"$SIZE_OF_OBJECTS"\_numsamples_"$NO_OF_SAMPLES"\_bucket_"$NUMBUCKET"\_sessions_"$NUMCLIENTS"

            mv s3bench-object_$SIZE_OF_OBJECTS\_numsamples_$NO_OF_SAMPLES\_bucket_$NUMBUCKET\_sessions_$NUMCLIENTS\.log $TOOL_DIR/s3bench_object_$SIZE_OF_OBJECTS\_numsamples_$NO_OF_SAMPLES\_buckets_$NUMBUCKET\_sessions_$NUMCLIENTS\.log

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
        -ep)     shift
                ENDPOINTS="$1"
        ;;

        -nc)     shift
                CLIENTS="$1"
        ;;

        -ns)    shift
                NUMSAMPLES="$1"
        ;;

        -s)    shift
                IO_SIZE="$1"       
        ;;

        -nb)    shift
                NUMBUCKET="$1"
        ;;

        
        *)     
                show_usage
                break
        esac
        shift
done

validate_args

if [ ! -d $BENCHMARKLOG ]; then
     mkdir -p $BENCHMARKLOG
     s3benchmark
     sleep 20
     mkdir -p $RESULT_DIR/
     cp -r $BENCHMARKLOG/$TOOL_NAME $RESULT_DIR/

else
#     rm -rf $BENCHMARKLOG
     mkdir -p $BENCHMARKLOG
     s3benchmark
     sleep 20
     mkdir -p $RESULT_DIR/
     cp -r $BENCHMARKLOG/$TOOL_NAME $RESULT_DIR/

fi

