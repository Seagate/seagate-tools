#!/bin/bash
source /root/cortx-benchmark/influxdbDetails.conf
INFLUXDB=`cat /etc/telegraf/telegraf.conf | grep -A 3 outputs.influxdb | grep urls | cut -d "=" -f2 | tr -d '"[]' | tr -d ' '`
URL="$INFLUXDB/write?db=$benchmarkdb"
host=`hostname`
OBJECT_SIZE=$(echo "$1" | sed -e 's/M/Mb/g' )
BENCHMARK=$3


tail -n 40 $2 | grep -e 'read\|write' > DATA
while IFS= read -r line
do
    OPS=$(echo "$line" | awk '{print $1}'| tr -d ':' | tr -d ' ' )
    TH=$(echo "$line" | grep -e 'read\|write' | awk '{print $4}' | cut -d "(" -f2 | sed -e 's/[a-zA-Z/)]//g' )
    IOPS=$(echo "$line" | grep -e 'read\|write' | awk '{print $2}' | cut -d "=" -f2 | sed -e 's/,//g' )
    LAT=$(echo "$line" | grep -e 'read\|write' | awk '{print $4}' | cut -d ")" -f2 | cut -d "/" -f2 | sed -e 's/[a-z]//g')
    ops=${OPS^}
    update_value_1="Latency,host=`hostname`,operation=$ops,Obj_size=$OBJECT_SIZE,Benchmark_Type=$BENCHMARK,region=us-west value=$LAT"
    update_value_2="Throughput,host=`hostname`,operation=$ops,Obj_size=$OBJECT_SIZE,Benchmark_Type=$BENCHMARK,region=us-west value=$TH"
    update_value_3="IOPS,host=`hostname`,operation=$ops,Obj_size=$OBJECT_SIZE,Benchmark_Type=$BENCHMARK,region=us-west value=$IOPS"
    curl -i -XPOST "$URL" --data-binary "$update_value_1" > /dev/null 2>&1;
    curl -i -XPOST "$URL" --data-binary "$update_value_2" > /dev/null 2>&1;
    curl -i -XPOST "$URL" --data-binary "$update_value_3" > /dev/null 2>&1;
    echo "$ops Data captured for Latency, Throughput and IOPS from $HOSTNAME ..."
done < "DATA"

