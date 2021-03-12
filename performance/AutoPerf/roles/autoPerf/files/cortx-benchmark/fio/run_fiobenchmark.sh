#!/bin/bash
set -e
#
# Variables deaclaration
#

TIME_INTERVAL=""
BLOCK_SIZE=""
NUMOFJOBS=""
CURRENTPATH=`pwd`
TIMESTAMP=`date +'%Y-%m-%d_%H:%M:%S'`
SAMPLE=""
TEMPLATE=""
HOSTNAME=`hostname`

validate_args() {

        if [[ -z $TIME_INTERVAL ]] || [[ -z $NUMOFJOBS ]] || [[ -z $BLOCK_SIZE ]] || [[ -z $TEMPLATE ]] || [[ -z $SAMPLE ]]; then
                show_usage
        fi

}

show_usage() {
        echo -e "\n \t  Usage : ./run_fiobenchmark.sh -t TIME_INTERVAL -bs BLOCK_SIZE -nj NUMOFJOBS -sm SAMPLE -tm TEMPLATE  \n"
        echo -e "\t -t\t:\t Run time (Duration) \n"
        echo -e "\t -bs\t:\t Blocksize\n"
        echo -e "\t -nj\t:\t Number of jobs\n"
        echo -e "\t -sm\t:\t Sampling time \n"
        echo -e "\t -tm\t:\t Template for fio like seq_read_fio, seq_write_fio, randmix_80-20_fio, randmix_20-80_fio and rand_fio \n"
        echo -e "\tExample\t:\t ./run_fiobenchmark.sh -t 300 -bs 1Mb,4Mb,16Mb -nj 16,32,64 -sm 5 -tm seq_read_fio  \n"
        exit 1
}

fio_benchmark() {
       salt-call pillar.get cluster:`cat /etc/salt/minion_id`:storage:data_devices --output=newline_values_only | cut -d "-" -f4 > DISKLIST       
       for bs in ${BLOCK_SIZE//,/ }
       do
           for numjob in ${NUMOFJOBS//,/ }
           do     
                   IOSIZE=$(echo "$bs" | sed -e 's/Mb/M/g') 
                   template_file=$CURRENTPATH/fio-template/$TEMPLATE
                   workload_file=$CURRENTPATH/benchmark.log/$TEMPLATE\_bs_$IOSIZE\_numjobs_$numjob\_hostname_$HOSTNAME
                   cp $template_file $workload_file
                   sed -i "/\[global\]/a bs=$IOSIZE" $workload_file
                   sed -i "/time_based/a runtime=$TIME_INTERVAL" $workload_file
                   sed -i "/runtime/a numjobs=$numjob" $workload_file
                   while IFS=  read -r disk
                   do
                       echo -e "\n[$disk]" >> $workload_file
                       echo -e "filename = /dev/disk/by-id/dm-name-$disk \n" >> $workload_file 
                   done < "DISKLIST"
                   FIOLOG=benchmark.log/$TEMPLATE\_bs_$IOSIZE\_numjobs_$numjob\.log
                   fio --status-interval=$SAMPLE $workload_file > $FIOLOG & 
                   echo "Fio scripts is running on $HOSTNAME ..."
                   PID=$!
                   sleep 30
                   system_monitoring $bs $FIOLOG fio
           done
       done

}

system_monitoring()
{
      while [ true ]
      do
         if kill -0 $PID > /dev/null 2>&1;
         then
             ./monitor_performance.sh $1 $2 $3 
             sleep $SAMPLE
         else
             break
         fi
      done
}



while [ ! -z $1 ]; do

        case $1 in
        -t)     shift
                TIME_INTERVAL="$1"
        ;;

        -bs)    shift
                BLOCK_SIZE="$1"
        ;;

        -nj)    shift
                NUMOFJOBS="$1"
        ;;

        -sm)    shift
                SAMPLE="$1"
        ;;

        -tm)    shift
                TEMPLATE="$1"
        ;;

        *)
                show_usage
                break
        esac
        shift
done

validate_args

if [ ! -d benchmark.log ]; then
      mkdir $CURRENTPATH/benchmark.log
      if [ ! `rpm -qa | grep telegraf` > /dev/null 2>&1 ]; then
          sh /root/BENCHMARK/setup_telegraf.sh
      fi
      if [ ! `rpm -qa | grep fio` > /dev/null 2>&1 ]; then
          yum install fio -y
      fi
      fio_benchmark
else
      mv benchmark.log $CURRENTPATH/benchmark.bak_$TIMESTAMP
      mkdir $CURRENTPATH/benchmark.log
      fio_benchmark
fi

