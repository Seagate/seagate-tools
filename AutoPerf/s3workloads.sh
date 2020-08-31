#! /usr/bin/bash
#
# Variable declarations
#

# BUCKET variable used by only hs bench
BUCKETS=""
CLIENTS=""
NUMSAMPLES=""
IOSIZE=""
# DURATION variable defined for cosbench and fio
DURATION=""
CONFIGURATION=$2
CLIENT=$3
SERVER=$4
SAMPLE=$5
OPERATION=$6
TEMPLATE=$6
# NUMJOBS variable defined for fio benchmark
NUMJOBS=""
START=
END=

check_telegraf()
{
    ssh root@$CLIENT "if [ ! `rpm -qa | grep git-1.8.3` > /dev/null 2>&1 ]; then yum install git bc -y; else echo -e \"\n \t git already installed \"; fi"
    ssh root@$CLIENT "if [ ! -d \"cortx-benchmark\" ]; then git clone https://github.com/Seagate/cortx-benchmark.git; else cd cortx-benchmark; echo -e \"\n \t `git pull` \"; fi"
    ssh root@$CLIENT "sh /root/cortx-benchmark/check_telegraf.sh"
    ssh root@$SERVER "salt '*' cmd.run 'if [ `rpm -qa | grep git-1.8.3` > /dev/null 2>&1 ]; then echo \"  git already installed  \"; else yum install git bc -y; fi'"

    ssh root@$SERVER "salt '*' cmd.run 'if  [ ! -d \"cortx-benchmark\" ]; then yum install bc -y; git clone https://github.com/Seagate/cortx-benchmark.git; else cd cortx-benchmark; echo -e \" `git pull` \"; fi'"
    ssh root@$SERVER "salt '*' cmd.run 'sh /root/cortx-benchmark/check_telegraf.sh'"
}

configuration_type()
{
       while [ ! -z $CONFIGURATION ];
       do
          case $CONFIGURATION in
          short)
               BUCKETS=4
               CLIENTS=32
               NUMJOBS=16
               NUMSAMPLES=2048,4096
               IOSIZE=1Mb,4Mb,8Mb
               DURATION=300
               break
          ;;
          long)
               BUCKETS=8
               CLIENTS=64
               NUMJOBS=32
               NUMSAMPLES=2048,4096
               IOSIZE=32Mb,64Mb
               DURATION=600
               break
          ;;
          small)
               BUCKETS=16
               CLIENTS=128,256
               NUMJOBS=16
               NUMSAMPLES=4096
               IOSIZE=4Mb,16Mb,32Mb
               DURATION=300
               break
          ;;
          large)
               BUCKETS=32
               CLIENTS=128,256
               NUMJOBS=16
               NUMSAMPLES=4096
               IOSIZE=64Mb,128Mb,256Mb
               DURATION=600
               break
          ;;
          *)
               echo "wrong configuration choice!"
               exit
          esac
       done
}
#
#
# calling function to set parameters value based on user choice
#
configuration_type
check_telegraf
#
# Running selected benchmark to monitor system and s3 performance
#
START=`date -u +"%Y-%m-%dT%H:%M:%SZ"`
while [ ! -z $1 ];
do
   case $1 in
   s3bench_basic)
         ssh root@$SERVER "salt '*' cmd.run 'echo System monitoring starting;systemctl start telegraf'" &
         sleep 60
         ssh root@$CLIENT "yes | cp /root/go/bin/s3bench.old /root/go/bin/s3bench;cd /root/cortx-benchmark/s3bench_basic; ./run_s3benchmark.sh -nc $CLIENTS -ns $NUMSAMPLES -s $IOSIZE -sm $SAMPLE"         
         ssh root@$SERVER "salt '*' cmd.run 'echo System monitoring stopping;systemctl stop telegraf'"
         break
   ;;

   hsbench)
         ssh root@$SERVER "salt '*' cmd.run 'echo System monitoring starting;systemctl start telegraf'" &
         sleep 60
         ssh root@$CLIENT "cd /root/cortx-benchmark/hsbench; ./run_benchmark.sh -b $BUCKETS -o $NUMSAMPLES -s $IOSIZE -t $CLIENTS -d $DURATION -sm $SAMPLE"
         ssh root@$SERVER "salt '*' cmd.run 'echo System monitoring stopping;systemctl stop telegraf'"
         break
   ;;

   cosbench)
         ssh root@$SERVER "salt '*' cmd.run 'echo System monitoring starting;systemctl start telegraf'" &
         sleep 60
         ssh root@$CLIENT "cd /root/cortx-benchmark/cosbench; ./s3cosbench_benchmark.sh -nc $CLIENTS -ns $NUMSAMPLES -s $IOSIZE  -b $BUCKETS -w $OPERATION -t $DURATION -sm $SAMPLE"
         ssh root@$SERVER "salt '*' cmd.run 'echo System monitoring stopping;systemctl stop telegraf'"
         break
   ;;

   fio)
         ssh root@$SERVER "salt '*' cmd.run 'echo System monitoring starting;systemctl start telegraf'" &
         sleep 60
         ssh root@$CLIENT "cd ~/cortx-benchmark/fio; ./run_fio.sh $SERVER $DURATION $IOSIZE $NUMJOBS $SAMPLE $TEMPLATE"
         ssh root@$SERVER "salt '*' cmd.run 'echo System monitoring stopping;systemctl stop telegraf'"
         break
   ;;
   *)
         echo -e "`date -u | awk '{print $2 " " $3 " " $4}'` \t wrong benchmark choice!"
         exit
   esac
done

END=`date -u +"%Y-%m-%dT%H:%M:%SZ"`
sh `pwd`/generateCSVReport.sh $START $END $1 $IOSIZE
