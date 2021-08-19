#! /usr/bin/bash
ACCESS_KEY=`cat /root/.aws/credentials | grep -A 3 default | grep aws_access_key_id | cut -d " " -f3`
SECRET_KEY=`cat /root/.aws/credentials | grep -A 3 default | grep secret_access_key | cut -d " " -f3`
BINPATH=/root/PerfProBenchmark/s3bench
CURRENTPATH=/root/PerfProBenchmark
BENCHMARKLOG=$CURRENTPATH/prefill/
ENDPOINTS=https://s3.seagate.com         
BUCKETNAME="prefill"
TIMESTAMP=`date +'%Y-%m-%d_%H:%M:%S'`
CLIENTS=""     
NUMSAMPLES=""     
IO_SIZE=""


validate_args() {

        if [[ -z $CLIENTS ]] || [[ -z $NUMSAMPLES ]] || [[ -z $IO_SIZE ]] ; then
                show_usage
        fi

}

show_usage() {
        echo -e "\n \t  Usage : ./run_s3benchmark.sh -nc NO_OF_CLIENTS -ns NO_OF_SAMPLES -s \"iosize\"   \n"
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

            TIMESTAMP=`date +'%d-%m-%Y_%H:%M:%S'`
            MKDIR=$BENCHMARKLOG/$TIMESTAMP\_object_$SIZE_OF_OBJECTS\_numclient_$NO_OF_SAMPLES

            mkdir -p $MKDIR

           echo "$BINPATH/s3bench_perfpro -accessKey=$ACCESS_KEY  -accessSecret=$SECRET_KEY -bucket=$bucket -endpoint=$ENDPOINTS -numClients=$NUMCLIENTS -numSamples=$NO_OF_SAMPLES -objectNamePrefix=loadgen -objectSize=$SIZE_OF_OBJECTS -skipRead -skipCleanup > $MKDIR/s3bench_Numclients_$NUMCLIENTS\_NS_$NO_OF_SAMPLES\_size_$SIZE_OF_OBJECTS\.log"

           $BINPATH/s3bench_perfpro -accessKey=$ACCESS_KEY  -accessSecret=$SECRET_KEY -bucket=$bucket -endpoint=$ENDPOINTS -numClients=$NUMCLIENTS -numSamples=$NO_OF_SAMPLES -objectNamePrefix=loadgen -objectSize=$SIZE_OF_OBJECTS -skipCleanup -skipRead > $MKDIR/s3bench_Numclients_$NUMCLIENTS\_NS_$NO_OF_SAMPLES\_size_$SIZE_OF_OBJECTS\.log

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
        
        *)     
                show_usage
                break
        esac
        shift
done

validate_args
#
# It will configure s3benchmark tools if it's not available
#
#./installS3bench.sh
#

s3benchmark
