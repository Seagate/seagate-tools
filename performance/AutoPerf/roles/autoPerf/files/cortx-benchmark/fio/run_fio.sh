#! /bin/bash
SERVER=$1
DURATION=$2
IOSIZE=$3
NUMJOBS=$4
SAMPLE=$5
TEMPLATE=$6


echo "System monitoring started"
systemctl restart telegraf
ssh root@$SERVER "cd ~/cortx-benchmark/fio; ./run_fiobenchmark.sh -t $DURATION -bs $IOSIZE -nj $NUMJOBS -sm $SAMPLE -tm $TEMPLATE" &
PID1=$!
ssh root@$SERVER "ssh srvnode-2 'cd ~/cortx-benchmark/fio; ./run_fiobenchmark.sh -t $DURATION -bs $IOSIZE -nj $NUMJOBS -sm $SAMPLE -tm $TEMPLATE'" &
PID2=$!
sleep 20
while [ true ]
do
    if  kill -0 $PID1 > /dev/null 2>&1 ;
    then
        continue
    else
        echo "Fio scripts is completed sucessfully"
        break
    fi
    if  kill -0 $PID2 > /dev/null 2>&1 ;
    then
        continue
    else
        echo "Fio scripts is completed sucessfully"
        break
    fi
done

echo "System monitoring stopped"
systemctl stop telegraf
