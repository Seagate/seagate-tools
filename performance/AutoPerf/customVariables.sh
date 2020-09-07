#! /bin/bash

ECHO='echo AutoPerf >'
file="roles/autoPerf/vars/custom.yml"
while [ ! -z $1 ];
do
   case $1 in
   s3bench_basic)
          $ECHO "Enter number of clients separated by ',' (Ex: 32,64,128)"
          read -p "AutoPerf > " CLIENTS
          $ECHO "Enter number of samples separated by ',' (Ex: 1024,2048,4096)"
          read -p "AutoPerf > " NUMSAMPLES
          $ECHO "Enter number of object size separated by ',' (Ex: 4Mb,16Mb,32Mb)"
          read -p "AutoPerf > " IOSIZE
          sed -i 's/CLIENTS:.*/CLIENTS: '$CLIENTS'/' $file
          sed -i 's/NUMSAMPLES:.*/NUMSAMPLES: '$NUMSAMPLES'/' $file
          sed -i 's/IOSIZE:.*/IOSIZE: '$IOSIZE'/' $file
          break
   ;;

   hsbench)
          $ECHO "Enter number of clients separated by ',' (Ex: 32,64,128)"
          read -p "AutoPerf > " CLIENTS
          $ECHO "Enter number of samples separated by ',' (Ex: 1024,2048,4096)"
          read -p "AutoPerf > " NUMSAMPLES
          $ECHO "Enter number of object size separated by ',' (Ex: 4Mb,16Mb,32Mb)"
          read -p "AutoPerf > " IOSIZE
          $ECHO "Enter number of Bucket (Ex: 10)"
          read -p "AutoPerf > " BUCKETS
          $ECHO "Enter duration in seconds (Ex: 600)"
          read -p "AutoPerf > " DURATION
          sed -i 's/BUCKETS:.*/BUCKETS: '$BUCKETS'/' $file
          sed -i 's/DURATION:.*/DURATION: '$DURATION'/' $file
          sed -i 's/CLIENTS:.*/CLIENTS: '$CLIENTS'/' $file
          sed -i 's/NUMSAMPLES:.*/NUMSAMPLES: '$NUMSAMPLES'/' $file
          sed -i 's/IOSIZE:.*/IOSIZE: '$IOSIZE'/' $file
          break
   ;;

   cosbench)
          $ECHO "Enter number of clients separated by ',' (Ex: 32,64,128)"
          read -p "AutoPerf > " CLIENTS
          $ECHO "Enter number of samples separated by ',' (Ex: 1024,2048,4096)"
          read -p "AutoPerf > " NUMSAMPLES
          $ECHO "Enter number of object size separated by ',' (Ex: 4Mb,16Mb,32Mb)"
          read -p "AutoPerf > " IOSIZE
          $ECHO "Enter number of Bucket (Ex: 10)"
          read -p "AutoPerf > " BUCKETS
          $ECHO "Enter duration in seconds (Ex: 600)"
          read -p "AutoPerf > " DURATION
          sed -i 's/BUCKETS:.*/BUCKETS: '$BUCKETS'/' $file
          sed -i 's/DURATION:.*/DURATION: '$DURATION'/' $file
          sed -i 's/CLIENTS:.*/CLIENTS: '$CLIENTS'/' $file
          sed -i 's/NUMSAMPLES:.*/NUMSAMPLES: '$NUMSAMPLES'/' $file
          sed -i 's/IOSIZE:.*/IOSIZE: '$IOSIZE'/' $file

          break
   ;;

   fio)
          $ECHO "Enter number of object size separated by ',' (Ex: 4Mb,16Mb,32Mb)"
          read -p "AutoPerf > " IOSIZE
          $ECHO "Enter duration in seconds (Ex: 600)"
          read -p "AutoPerf > " DURATION
          $ECHO "Enter number of jobs separated by ',' (Ex: 1024,2048,4096)"
          read -p "AutoPerf > " NUMJOBS 
          sed -i 's/DURATION:.*/DURATION: '$DURATION'/' $file
          sed -i 's/IOSIZE:.*/IOSIZE: '$IOSIZE'/' $file          
          sed -i 's/NUMJOBS:.*/NUMJOBS: '$NUMJOBS'/' $file
          break
   ;;
   *)
         echo -e "`date -u | awk '{print $2 " " $3 " " $4}'` \t wrong benchmark choice!"
         exit
   esac
done

