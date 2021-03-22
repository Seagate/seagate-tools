#!/bin/bash
source /root/cortx-benchmark/influxdbDetails.conf
INFLUXDB=`cat /etc/telegraf/telegraf.conf | grep -A 3 outputs.influxdb | grep urls | cut -d "=" -f2 | tr -d '"[]' | tr -d ' '`
URL="$INFLUXDB/write?db=$benchmarkdb"
host=`hostname`
OBJECT_SIZE=$1
BENCHMARK=$3
line=$(tail -n 1 $2)
CSV_FILE=$(echo "$2" | sed -e 's/output.log/output.csv/g')
OpsType=
update_value_1=
update_value_2=
update_value_3=

if [[ "$line" != *"Running"*  ]]
then
    if [[ "$line" = *"PUT"* ]]  || [[ "$line" = *"GET"* ]]
    then
        ops=$(echo "$line" | cut -f 10 -d ' ' | tr -d ',' | tr -d ' ')
        Th=$(echo "$line" | cut -f 14 -d ' ' | tr -d ',' | tr -d ' ')
        IOPS=$(echo "$line" | cut -f 16 -d ' ' | tr -d ',' | tr -d ' ')
        Lat=$(echo "$line" | cut -f 22 -d ' ' | tr -d ',' | tr -d ' ')
        size=$OBJECT_SIZE\b
        if [ ! -f "$CSV_FILE" ]
        then
            echo "Date Time,Hostname,Operation,IO_size,Benchmark_Type,Throughput,IOPS,Latency" > $CSV_FILE
        fi
        
        if [[ "$ops" = "PUT" ]]
        then
            OpsType="Write"
            update_value_1="Latency,host=`hostname`,operation=$OpsType,Obj_size=$size,Benchmark_Type=$BENCHMARK,region=us-west value=$Lat"
            update_value_2="Throughput,host=`hostname`,operation=$OpsType,Obj_size=$size,Benchmark_Type=$BENCHMARK,region=us-west value=$Th"
            update_value_3="IOPS,host=`hostname`,operation=$OpsType,Obj_size=$size,Benchmark_Type=$BENCHMARK,region=us-west value=$IOPS"
            echo -e "`date +'%F %T'`,`hostname`,$OpsType,$size,$BENCHMARK,$Th,$IOPS,$Lat" >> $CSV_FILE

        else
            OpsType="Read"
            update_value_1="Latency,host=`hostname`,operation=$OpsType,Obj_size=$size,Benchmark_Type=$BENCHMARK,region=us-west value=$Lat"
            update_value_2="Throughput,host=`hostname`,operation=$OpsType,Obj_size=$size,Benchmark_Type=$BENCHMARK,region=us-west value=$Th"
            update_value_3="IOPS,host=`hostname`,operation=$OpsType,Obj_size=$size,Benchmark_Type=$BENCHMARK,region=us-west value=$IOPS"
            echo -e "`date +'%F %T'`,`hostname`,$OpsType,$size,$BENCHMARK,$Th,$IOPS,$Lat" >> $CSV_FILE

        fi 
        curl -i -XPOST "$URL" --data-binary "$update_value_1"  > /dev/null 2>&1;
        curl -i -XPOST "$URL" --data-binary "$update_value_2"  > /dev/null 2>&1;
        curl -i -XPOST "$URL" --data-binary "$update_value_3"  > /dev/null 2>&1;
        echo "$OpsType Data captured for Latency throughput and IOPS..."
    fi
fi
