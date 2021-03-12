#! /usr/bin/bash
ACCESS_KEY=`cat /root/.aws/credentials | grep -A 3 default | grep aws_access_key_id | cut -d " " -f3`
SECRET_KEY=`cat /root/.aws/credentials | grep -A 3 default | grep secret_access_key | cut -d " " -f3`
BINPATH=/root/go/bin
CURRENTPATH=`pwd`
BENCHMARKLOG=$CURRENTPATH/benchmark.log
IO_SIZE=""
ENDPOINTS=https://s3.seagate.com         
BUCKETNAME="seagate"
skipCleanup="no"
CLIENTS=""     
NUMSAMPLES=""     
TIMESTAMP=`date +'%Y-%m-%d_%H:%M:%S'`
SAMPLE=""
PID=


validate_args() {

        if [ -z $CLIENTS ] || [ -z $NUMSAMPLES ] || [ -z $IO_SIZE ] || [ -z $SAMPLE ] ; then
                show_usage
        fi

}

show_usage() {
        echo -e "\n \t  Usage : ./run_s3benchmark.sh -nc NO_OF_CLIENTS -ns NO_OF_SAMPLES -s \"iosize\"  [ -b bucketname ] -sm SAMPLE [ -cl skipCleanup ]\n"
        echo -e "\t -nc\t:\t number of clients \n"
        echo -e "\t -ns\t:\t number of samples\n"
        echo -e "\t -s\t:\t size of the objects in bytes\n"
        echo -e "\t -b\t:\tname of the bucket [optional] default is 'seagate1'\n"
        echo -e "\t -sm\t:\t sampling time in seconds\n"
        echo -e "\t -cl\t:\t Type yes/no skipCleanup [optional]\n"
        echo -e "\tExample\t:\t ./run_s3benchmark.sh -nc 128,256,512 -ns 1024,2048,4096 -s 4Kb,16Kb,1Mb,4Mb,128Mb -sm 5 -cl yes \n"
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

           mkdir $MKDIR
           if [ "$skipCleanup" = "no" ];
           then         
                echo "$BINPATH/s3bench -accessKey=$ACCESS_KEY  -accessSecret=$SECRET_KEY -bucket=$bucket -endpoint $ENDPOINTS -numClients $NUMCLIENTS -numSamples $NO_OF_SAMPLES -objectSize $value -verbose > $MKDIR/s3bench_Numclients_$NUMCLIENTS\_NS_$NO_OF_SAMPLES\_size_$SIZE_OF_OBJECTS.log" 


                $BINPATH/s3bench -accessKey=$ACCESS_KEY  -accessSecret=$SECRET_KEY -bucket=$bucket -endpoint $ENDPOINTS -numClients $NUMCLIENTS -numSamples $NO_OF_SAMPLES -objectSize $value -verbose > $MKDIR/s3bench_Numclients_$NUMCLIENTS\_NS_$NO_OF_SAMPLES\_size_$SIZE_OF_OBJECTS.log &
                PID=$!
           else 
                echo "$BINPATH/s3bench -accessKey=$ACCESS_KEY  -accessSecret=$SECRET_KEY -bucket=$bucket -endpoint $ENDPOINTS -numClients $NUMCLIENTS -numSamples $NO_OF_SAMPLES -objectSize $value -verbose -skipCleanup > $MKDIR/s3bench_Numclients_$NUMCLIENTS\_NS_$NO_OF_SAMPLES\_size_$SIZE_OF_OBJECTS.log"


                $BINPATH/s3bench -accessKey=$ACCESS_KEY  -accessSecret=$SECRET_KEY -bucket=$bucket -endpoint $ENDPOINTS -numClients $NUMCLIENTS -numSamples $NO_OF_SAMPLES -objectSize $value -verbose -skipCleanup > $MKDIR/s3bench_Numclients_$NUMCLIENTS\_NS_$NO_OF_SAMPLES\_size_$SIZE_OF_OBJECTS.log &
                PID=$!
           fi
           system_monitoring
#           aws s3 rb s3://$bucket --force  
           echo "S3Benchmark is completed for object size : $SIZE_OF_OBJECTS"
        done
        echo "S3Benchmark is completed for number of clients : $NUMCLIENTS"
    done
    echo "S3Benchmark is completed for number of Samples : $NO_OF_SAMPLES"
done
echo 'Successfully completed'

}

system_monitoring() {
 
      systemctl start telegraf
      while [ true ]
      do
         if kill -0 $PID > /dev/null 2>&1;
         then
             ./monitor_performance.sh $SIZE_OF_OBJECTS $MKDIR/s3bench_Numclients_$NUMCLIENTS\_NS_$NO_OF_SAMPLES\_size_$SIZE_OF_OBJECTS\.log s3bench_basic
             sleep $SAMPLE
         else
             break
         fi
      done
      systemctl stop telegraf
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

        -b)     shift
                BUCKETNAME="$1"
        ;;
        -sm)    shift
                SAMPLE="$1"
        ;;
        -cl)    shift
                skipCleanup="$1"
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
./installS3bench.sh
#
if [ ! -d $BENCHMARKLOG ]; then
      mkdir $BENCHMARKLOG
      s3benchmark
else
      mv $BENCHMARKLOG $CURRENTPATH/benchmark.bak_$TIMESTAMP
      mkdir $BENCHMARKLOG
      s3benchmark
fi

