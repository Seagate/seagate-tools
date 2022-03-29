#!/bin/bash
# for getting small object performance
for objectSize in 4Kb 100Kb 1Mb 5Mb; do
samples=5000
clients=100

aws_access_key_id=`cat /root/.aws/credentials | grep -A 3 default | grep aws_access_key_id | cut -d " " -f3`
aws_secret_access_key=`cat /root/.aws/credentials | grep -A 3 default | grep secret_access_key | cut -d " " -f3`

cwd=`date +%F`
mkdir -p /root/s3bench_log/"$cwd"

now=`date +%F-%T`

/root/go/bin/s3bench_meta -accessKey="$aws_access_key_id" -accessSecret="$aws_secret_access_key" -bucket=s3benchbucket  -endpoint=https://s3.seagate.com -numClients="$clients" -numSamples="$samples" -objectNamePrefix=loadgen -objectSize="$objectSize"  -verbose > /root/s3bench_log/"$cwd"/s3bench_log_"$objectSize"\_"$now".log;
sleep 10
done

#for getting large object performance
for objectSize in 36Mb 64Mb 128Mb 256Mb; do
samples=2000
clients=100

now=`date +%F-%T`

/root/go/bin/s3bench_meta -accessKey=$aws_access_key_id -accessSecret=$aws_secret_access_key -bucket=s3benchbucket  -endpoint=https://s3.seagate.com -numClients=$clients -numSamples=$samples -objectNamePrefix=loadgen -objectSize=$objectSize  -verbose > /root/s3bench_log/$cwd/s3bench_log_$objectSize\_$now.log;
sleep 10
done

#for getting metadata performance

clients=50
samples=2000
objectsize=1Kb
sampleReads=12

now=`date +%F-%T`

/root/go/bin/s3bench_meta -accessKey="$aws_access_key_id" -accessSecret="$aws_secret_access_key" -bucket=metabucket -endpoint=https://s3.seagate.com -numClients="$clients" -numSamples="$samples" -objectNamePrefix=loadgen -objectSize="$objectsize"  -headObj -putObjTag -getObjTag -verbose -sampleReads="$sampleReads" > /root/s3bench_log/"$cwd"/s3bench_log_"$objectsize"\_"$now".log

