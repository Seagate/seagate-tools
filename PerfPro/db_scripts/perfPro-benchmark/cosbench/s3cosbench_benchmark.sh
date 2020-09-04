#!/usr/bin/bash

#
#  variables Declaration
#
no_of_buckets=""
no_of_objects=""
object_size_in_mb=""
no_of_workers=""
workload_type=""
run_time_in_seconds=""
SAMPLE=""
CURRENT_PATH=`pwd`
LOG=$CURRENT_PATH/benchmark.log
HOSTNAME=`hostname`
TIMESTAMP=`date +'%Y-%m-%d_%H:%M:%S'`
size=

validate_args() {

        if [[ -z $no_of_buckets ]] || [[ -z $no_of_objects ]] || [[ -z $object_size_in_mb ]] || [[ -z $no_of_workers ]] || [[ -z $workload_type ]]  || [[ -z $run_time_in_seconds ]] || [[ -z $SAMPLE ]]
        then
                show_usage
        fi

}

show_usage() {
        echo -e "\n \t  Usage : ./s3cosbench_benchmark.sh -nc no_of_workers -ns no_of_objects -s \"object_size_in_mb\"  -b no_of_buckets -w workload_type -t run_time_in_seconds -sm SAMPLE \n"
        echo -e "\t -nc\t:\t number of clients/workers \n"
        echo -e "\t -ns\t:\t number of samples/objects \n"
        echo -e "\t -s\t:\t size of the objects in Mb \n"
        echo -e "\t -b\t:\t number of the buckets \n"
        echo -e "\t -w\t:\t workload type like read,write,mixed,all \n"
        echo -e "\t -t\t:\t run time in seconds \n"
        echo -e "\t -sm\t:\t sampling time in seconds \n"
        echo -e "\tExample\t:\t ./s3cosbench_benchmark.sh -nc \"8,16,32\" -ns \"1024,2048,4096 \" -s \"1Mb,4Mb,16Mb\"  -b \"8,16,32\" -w read -t 600 -sm 5 \n"
        exit 1
}

config_s3workloads() {
        
      for clients in ${no_of_workers//,/ };
      do
          for sample in ${no_of_objects//,/ }
          do
               for io_size in ${object_size_in_mb//,/ }
               do
                    workload_file=$LOG/workloads_workers_$clients\_sample_$sample\_size_$io_size\.log
                    size=$(echo "$io_size" | tr -d 'Mb')
                    echo "no_of_workers=$clients" > $workload_file
                    echo "no_of_objects=$sample" >> $workload_file
                    echo "object_size_in_mb=$size" >> $workload_file
                    echo "no_of_buckets=${no_of_buckets[$index]}" >> $workload_file
                    echo "workload_type=$workload_type" >> $workload_file
                    echo "run_time_in_seconds=$run_time_in_seconds" >> $workload_file
                    sh configure.sh
                    sh run-test.sh --s3setup s3setup.properties --controller $HOSTNAME --workload $workload_file
                    echo "System monitoring started"
                    system_monitoring $io_size $workload_file
                    echo "System monitoring stopped"
               done
          done
      done
}

system_monitoring()
{
      systemctl start telegraf
      sleep 60
      while [ true ]
      do 
         if tail -n 1 ~/cos/log/system.log | grep "throughput" > /dev/null 2>&1;
         then
             line=`tail -n 1 ~/cos/log/system.log | grep "throughput"`
             if [[ "$line" = *"op1.dispose.delete.dispose"* ]]
             then
                break
             else
                ./monitor_performance.sh $1 ~/cos/log/system.log cosbench $2
                sleep $SAMPLE
             fi
         
         elif tail -n 1 ~/cos/log/system.log | grep "dispose" > /dev/null 2>&1;
         then
             break
         fi
         
      done
      systemctl stop telegraf
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
                object_size_in_mb="$1"
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
        -sm)    shift
                SAMPLE="$1"
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
if [ ! -d $LOG ]; then
      mkdir $LOG
      config_s3workloads
      
else
      mv $LOG $CURRENT_PATH/benchmark.bak_$TIMESTAMP
      mkdir $LOG
      config_s3workloads
      
fi
