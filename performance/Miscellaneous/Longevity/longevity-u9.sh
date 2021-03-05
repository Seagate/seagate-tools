#!/bin/bash
for objectSize in 128Mb; do
samples=2300
clients=12
aws_access_key_id=`cat /root/.aws/credentials | grep -A 3 default | grep aws_access_key_id | cut -d " " -f3`
aws_secret_access_key=`cat /root/.aws/credentials | grep -A 3 default | grep secret_access_key | cut -d " " -f3`

cwd=`date +%F`
mkdir -p /root/s3bench_log/write-only/$cwd

for x in {1..100}; do
now=`date +%F-%T`
/root/go/bin/s3bench_skip -accessKey=$aws_access_key_id -accessSecret=$aws_secret_access_key -bucket=u29-bucket$x  -endpoint=https://s3.seagate.com -numClients=$clients -numSamples=$samples -objectNamePrefix=loadgen -objectSize=$objectSize -skipCleanup -skipRead -verbose > /root/s3bench_log/write-only/$cwd/s3bench_log_$objectSize\_$now-$x.log 

done

done
