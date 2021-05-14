#!/usr/bin/bash

#
#  variables Declaration
#
no_of_buckets=""
no_of_objects=""
object_size=""
no_of_workers=""
workload_type=""
run_time_in_seconds=""
CURRENT_PATH=`pwd`
LOG=$CURRENT_PATH/benchmark.log
HOSTNAME=`hostname`
TIMESTAMP=`date +'%Y-%m-%d_%H:%M:%S'`
size=
MAIN="/root/PerfProBenchmark/main.yml"
CONFIG="/root/PerfProBenchmark/config.yml"
LOG_COLLECT="/root/PerfProBenchmark/collect_logs.py"
ITERATION=$(yq -r .ITERATION $CONFIG)

validate_args() {

        if [ -z $no_of_buckets ] || [ -z $no_of_objects ] || [ -z $object_size ] || [ -z $no_of_workers ] || [ -z $workload_type ] || [ -z $run_time_in_seconds ]
        then
                show_usage
        fi

}

show_usage() {
        echo -e "\n \t  Usage : ./s3cosbench_benchmark.sh -nc no_of_workers -ns no_of_objects -s \"object_size\"  -b no_of_buckets -w workload_type -t run_time_in_seconds \n"
        echo -e "\t -nc\t:\t number of clients/workers \n"
        echo -e "\t -ns\t:\t number of samples/objects \n"
        echo -e "\t -s\t:\t size of the objects in Mb/Kb \n"
        echo -e "\t -b\t:\t number of the buckets \n"
        echo -e "\t -w\t:\t workload type like read,write,mixed,all \n"
        echo -e "\t -t\t:\t run time in seconds \n"
        echo -e "\tExample\t:\t ./s3cosbench_benchmark.sh -nc \"8,16,32\" -ns \"1024,2048,4096 \" -s \"4Kb,100Kb,1Mb,4Mb,16Mb\"  -b 1,10,50 -w mixed -t 600  \n"
        exit 1
}

config_s3workloads() {
  for bucket in ${no_of_buckets//,/ }
  do       
      for clients in ${no_of_workers//,/ };
      do
          for sample in ${no_of_objects//,/ }
          do
               for io_size in ${object_size//,/ }
               do
                    workload_file=$LOG/workloads_workers_$clients\_sample_$sample\_size_$io_size
                    size=$(echo "$io_size" | sed 's/[a-zA-Z]//g' )
                    obj_type=$(echo "$io_size" | sed 's/[0-9]*//g' | sed 's/b/B/g' )
                    echo "no_of_workers=$clients" > $workload_file
                    echo "no_of_objects=$sample" >> $workload_file
                    echo "type_of_object_MB_or_KB=$obj_type" >> $workload_file
                    echo "object_size=$size" >> $workload_file
                    echo "no_of_buckets=$bucket" >> $workload_file
                    echo "workload_type=$workload_type" >> $workload_file
                    echo "run_time_in_seconds=$run_time_in_seconds" >> $workload_file
                    sh configure.sh
                    sh run-test.sh --s3setup s3setup.properties --controller $HOSTNAME --workload $workload_file >> $LOG/workloads
                    check_completion `tail -n 3 $LOG/workloads | grep Accepted | cut -d ":" -f2 | tr -d ' '`
                    echo "Cosbench Triggered for worker: $clients sample: $sample obj_size:$io_size bucket:$bucket"
                    
               done
          done
      done
  done
}

check_completion() {
    while [ true ]
    do
         if [ -d /root/cos/archive/$1* ]
         then
             break
         fi
    done
      
}


while [ ! -z $1 ]; do

        case $1 in
        -nc)    shift
                no_of_workers="$1"
        ;;
        -ns)    shift
                no_of_objects="$1"
        ;;
        -s)     shift
                object_size="$1"
        ;;
        -b)     shift
                no_of_buckets="$1"
        ;;

        -w)     shift
                workload_type="$1"
        ;;

        -t)     shift
                run_time_in_seconds="$1"
        ;;

        *)
                show_usage
                break
        esac
        shift
done

validate_args
# It will configure Cosbenchmark it's not available
#
./installCosbench.sh `hostname`
#
for ((ITR=1;ITR<=ITERATION;ITR++))
do
    if [ ! -d $LOG ]; then
          mkdir $LOG
          config_s3workloads
          for i in `cat $LOG/workloads | grep Accepted | cut -d ":" -f2 | tr -d ' '`; 
          do 
              cp -r ~/cos/archive/$i* $LOG;
          done     
          python3 cosbench_DBupdate.py $LOG $MAIN $CONFIG $ITR
          python3 $LOG_COLLECT $CONFIG
    else
          mv $LOG $CURRENT_PATH/benchmark.bak_$TIMESTAMP
          mkdir $LOG
          config_s3workloads
          for i in `cat $LOG/workloads | grep Accepted | cut -d ":" -f2 | tr -d ' '`;
          do
              cp -r ~/cos/archive/$i* $LOG;
          done
          python3 cosbench_DBupdate.py $LOG $MAIN $CONFIG $ITR
          python3 $LOG_COLLECT $CONFIG

    fi
done
