#! /bin/bash
BENCHMARK_PATH=/root/go/bin
CURRENTPATH=`pwd`
ACCESS_KEY=`cat /root/.aws/credentials | grep -A 3 default | grep aws_access_key_id | cut -d " " -f3`		
SECRET_KEY=`cat /root/.aws/credentials | grep -A 3 default | grep secret_access_key | cut -d " " -f3` 	
BENCHMARKLOG=$CURRENTPATH/benchmark.log
NO_OF_BUCKET=""  				
TEST_DURATION=600   				
BUCKET_PREFIX=Seagate  		
MAX_ATTEMPT=1				
NO_OF_THREADS=""			
NO_OF_OBJECTS=""			
REGION=US				
ENDPOINTS=https://s3.seagate.com		
COUNT=0
SIZE_OF_OBJECTS=""
JSON_FILENAME=				
OUTPUT_FILE=
TIMESTAMP=`date +'%Y-%m-%d_%H:%M:%S'`
IFS=”,”




validate_args() {

        if [[ -z $NO_OF_BUCKET ]] ||  [[ -z $SIZE_OF_OBJECTS ]] || [[ -z $NO_OF_OBJECTS ]] || [[ -z $NO_OF_THREADS ]] ;
        then
                show_usage
        fi

}

show_usage() {
        echo -e "\n \t  Usage : ./run_benchmark.sh -b \"NO_OF_BUCKET\"  -o \"NO_OF_OBJECTS\"  -s \"SIZE_OF_OBJECT\" -t \"NO_OF_THREADS\" [ -d TEST_DURATION ] \n"
        echo -e "\t -b\t:\t number of buckets \n"
        echo -e "\t -o\t:\t number of objects [optional] default is '4096'\n"
        echo -e "\t -s\t:\t size of the objects K|M\n"
        echo -e "\t -t\t:\t number of the Threads\n"
        echo -e "\t -d\t:\t TEST_DURATION [optional] default is '600'\n"
        echo -e "\tExample\t:\t ./run_benchmark.sh -b \"8,16,32,64\" -o \"1024,2048\" -s \"1Mb,4Mb,16Mb,32Mb\" -t \"32,48,64,96,128\" -d 600 \n"
        exit 1
}

hotsause_benchmark()
{
    while [ $MAX_ATTEMPT -gt $COUNT ]
    do
               
        MKDIR=runid_$TIMESTAMP
        mkdir -p $BENCHMARKLOG/$MKDIR
        SAMPLES=($NO_OF_OBJECTS)
        THREAD=($NO_OF_THREADS)
        OBJ_SIZE=($SIZE_OF_OBJECTS)
        for index in ${!THREAD[@]};
        do
           for nc in ${!SAMPLES[@]};
           do
               for size in ${!OBJ_SIZE[@]}
               do
                 echo "Thread: ${THREAD[$index]} \t SAMPLE: ${SAMPLES[$nc]} \t OBJECT_SIZE: ${OBJ_SIZE[$size]}"        
                 JSON_FILENAME=Clients_${THREAD[$index]}\_Objects_${SAMPLES[$nc]}\_Bucket_$NO_OF_BUCKET\_object_size_${OBJ_SIZE[$size]}\.json
                 obj_size=$(echo "${OBJ_SIZE[$size]}" | tr -d 'b')
                 echo "$BENCHMARK_PATH/hsbench -a $ACCESS_KEY -s $SECRET_KEY -u $ENDPOINTS -z $obj_size -d $TEST_DURATION -t ${THREAD[$index]} -b $NO_OF_BUCKET -n ${SAMPLES[$nc]} -r $REGION -j $JSON_FILENAME"

                 $BENCHMARK_PATH/hsbench -a $ACCESS_KEY -s $SECRET_KEY -u $ENDPOINTS -z $obj_size -d $TEST_DURATION -t ${THREAD[$index]} -b $NO_OF_BUCKET -n ${SAMPLES[$nc]} -r $REGION -j $JSON_FILENAME

               done 
           done
        done
        mv $CURRENTPATH/*.json $CURRENTPATH/benchmark.log/$MKDIR/
        COUNT=$(($COUNT + 1))
        sleep 30
#        python3 $CURRENTPATH/hsbenchReport.py $BENCHMARKLOG/$MKDIR/    
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

        *)
                show_usage
                break
        esac
        shift
done

validate_args

if [ ! -d $BENCHMARKLOG ]; then
      if ! `pip3 list | grep pandas` > /dev/null 2>&1; then
          pip3 install pandas
      fi
      mkdir $BENCHMARKLOG
      hotsause_benchmark 2>&1 | tee benchmark.log/output.log 
      unset IFS
else
      mv $BENCHMARKLOG $CURRENTPATH/benchmark.bak_$TIMESTAMP
      mkdir $BENCHMARKLOG
      hotsause_benchmark 2>&1 | tee benchmark.log/output.log 
      unset IFS
fi
