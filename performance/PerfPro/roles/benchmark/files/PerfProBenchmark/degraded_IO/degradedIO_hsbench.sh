#! /bin/bash
TOOL_NAME='hsbench'
BENCHMARK_PATH=/root/go/bin
CURRENTPATH=`pwd`
ACCESS_KEY=`cat /root/.aws/credentials | grep -A 3 default | grep aws_access_key_id | cut -d " " -f3`		
SECRET_KEY=`cat /root/.aws/credentials | grep -A 3 default | grep secret_access_key | cut -d " " -f3` 	
BENCHMARKLOG=$CURRENTPATH/dr_hsb.log
NO_OF_BUCKET=""
TEST_DURATION=-1
BUCKET_PREFIX=Seagate  		
MAX_ATTEMPT=1				
NO_OF_THREADS=""			
NO_OF_OBJECTS=""			
REGION=us-east-1
#ENDPOINTS=https://s3.seagate.com		
COUNT=0
SIZE_OF_OBJECTS=""
JSON_FILENAME=				
OUTPUT_FILE=
FLAGS=""
CLUSTER_STATE=""
TIMESTAMP=`date +'%Y-%m-%d_%H:%M:%S'`
MAIN="/root/PerfProBenchmark/main.yml"
CONFIG="/root/PerfProBenchmark/config.yml"
BUILD=`python3 /root/PerfProBenchmark/read_build.py $CONFIG 2>&1`
ENDPOINTS=`python3 /root/PerfProBenchmark/get_param.py $CONFIG`
RESULT_DIR=/root/PerfProBenchmark/perfpro_build$BUILD/results/degraded_IO
validate_args() {

        if [[ -z $NO_OF_BUCKET ]] ||  [[ -z $SIZE_OF_OBJECTS ]] || [[ -z $NO_OF_OBJECTS ]] || [[ -z $NO_OF_THREADS ]] || [[ -f $FLAGS ]] || [[ -c $CLUSTER_STATE ]];
        then
                show_usage
        fi

}

show_usage() {
        echo -e "\n \t  Usage : ./run_benchmark.sh -b \"NO_OF_BUCKET\"  -o \"NO_OF_OBJECTS\"  -s \"SIZE_OF_OBJECT\" -t \"NO_OF_THREADS\" [ -d TEST_DURATION ] -f FLAGS -cs CLUSTER_STATE \n"
        echo -e "\t -b\t:\t number of buckets \n"
        echo -e "\t -o\t:\t number of objects [optional] default is '4096'\n"
        echo -e "\t -s\t:\t size of the objects K|M\n"
        echo -e "\t -t\t:\t number of the Threads\n"
        echo -e "\t -d\t:\t TEST_DURATION [optional] default is '600'\n"
        echo -e "\t -f\t:\t FLAGS for HSbench \n"
        echo -e "\t -f\t:\t CLUSTER_STATE \n"
        echo -e "\tExample\t:\t ./run_benchmark.sh -b \"8,16,32,64\" -o \"1024,2048\" -s \"1Mb,4Mb,16Mb,32Mb\" -t \"32,48,64,96,128\" -d 600 -f cxip -cs normal_read \n"
        exit 1
}

hotsause_benchmark()
{
    while [ $MAX_ATTEMPT -gt $COUNT ]
    do
               
      SAMPLES=($NO_OF_OBJECTS)
      THREAD=($NO_OF_THREADS)
      OBJ_SIZE=($SIZE_OF_OBJECTS)
      for bucket in ${NO_OF_BUCKET//,/ }
      do
        for client in ${THREAD//,/ }
        do
           for sample in ${SAMPLES//,/ }
           do
               for size in ${OBJ_SIZE//,/ }
               do
                 echo -e "Thread: $client \t SAMPLE: $sample \t OBJECT_SIZE: $size \t BUCKET: $bucket"        
                 JSON_FILENAME=$TOOL_NAME\_$CLUSTER_STATE\_object_$size\_numsamples_$sample\_buckets_$bucket\_sessions_$client\.json
                 obj_size=$(echo "$size" | tr -d 'b')
                 NUMSAMPLE=$((sample / client))
                 TOOL_DIR=$BENCHMARKLOG/$TOOL_NAME/numclients_$client/buckets_$bucket/$size
                 echo "$BENCHMARK_PATH/hsbench -a $ACCESS_KEY -s $SECRET_KEY -u $ENDPOINTS -z $obj_size -d $TEST_DURATION -t $client -b $bucket -n $sample -r $REGION -bp hsbench-dr-${obj_size,,} -m $FLAGS -j $JSON_FILENAME"

                 $BENCHMARK_PATH/hsbench -a $ACCESS_KEY -s $SECRET_KEY -u $ENDPOINTS -z $obj_size -d $TEST_DURATION -t $client -b $bucket -n $sample -r $REGION -bp hsbench-dr-${obj_size,,} -m $FLAGS -j $JSON_FILENAME

                 mkdir -p $TOOL_DIR
                 mv $CURRENTPATH/*.json $TOOL_DIR/
                 sleep 30
               done 
           done
        done
      done
      COUNT=$(($COUNT + 1))
    done
} 

while [ ! -z $1 ]; do

        case $1 in
        -b)    shift
                NO_OF_BUCKET="$1"
        ;;

        -o)    shift
                NO_OF_OBJECTS="$1"
        ;;

        -s)    shift
                SIZE_OF_OBJECTS="$1"
        ;;

        -t)    shift
                NO_OF_THREADS="$1"
        ;;

	-d)     shift
                TEST_DURATION="$1"
        ;;

        -f)     shift
                FLAGS="$1"
        ;;

        -cs)     shift
                CLUSTER_STATE="$1"
        ;;

        *)
                show_usage
                break
        esac
        shift
done

validate_args
#
# It will configure hsbenchmark tools if it's not available
#
./installHSbench.sh
#
if [ ! -d $BENCHMARKLOG ]; then
    mkdir $BENCHMARKLOG
    hotsause_benchmark 2>&1 | tee $BENCHMARKLOG/output.log
    sleep 20 
#    python3 hsbench_DBupdate.py $BENCHMARKLOG $MAIN $CONFIG 
    mkdir -p $RESULT_DIR/
    cp -r $BENCHMARKLOG/$TOOL_NAME $RESULT_DIR/    
    cp $BENCHMARKLOG/output.log $RESULT_DIR/$TOOL_NAME/    
      
else
    rm -rf $BENCHMARKLOG
    mkdir $BENCHMARKLOG
    hotsause_benchmark 2>&1 | tee $BENCHMARKLOG/output.log
    sleep 20 
#    python3 hsbench_DBupdate.py $BENCHMARKLOG $MAIN $CONFIG
    mkdir -p $RESULT_DIR/
    cp -r $BENCHMARKLOG/$TOOL_NAME $RESULT_DIR/    
    cp  $BENCHMARKLOG/output.log $RESULT_DIR/$TOOL_NAME/    

fi
