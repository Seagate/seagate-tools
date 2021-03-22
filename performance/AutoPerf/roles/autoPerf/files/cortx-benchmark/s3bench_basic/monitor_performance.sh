#!/usr/bin/bash
source /root/cortx-benchmark/influxdbDetails.conf
INFLUXDB=`cat /etc/telegraf/telegraf.conf | grep -A 3 outputs.influxdb | grep urls | cut -d "=" -f2 | tr -d '"[]' | tr -d ' '`
URL="$INFLUXDB/write?db=$benchmarkdb"
host=`hostname`
OBJECT_SIZE=$1
BENCHMARK=$3
obj_size=$(echo "$OBJECT_SIZE" | sed -e 's/Mb//g' )
line=$(tail -n 1 $2)
CSV_FILE=$(echo "$2" | sed -e 's/Mb.log/Mb.csv/g' )
ops=$(echo "$line" | grep "completed in" | cut -d ' ' -f 1 | tr -d ' ')

if [ "$ops" = "Write" ] || [ "$ops" = "Read" ] 
then
    write_ops=$(echo "$line" | cut -f 2 -d '-')
    th_value=$(echo "$write_ops" | sed -e 's/MB\/s//g' | tr -d ' ' )
    if [ -n "$th_value" ]
    then
        IOPS=`expr "$th_value / $obj_size" | bc -l`
        latency=`expr "1000 / $IOPS" | bc -l`
        update_value_1="Latency,host=`hostname`,operation=$ops,Obj_size=$OBJECT_SIZE,Benchmark_Type=$BENCHMARK,region=us-west value=$latency"
        update_value_2="Throughput,host=`hostname`,operation=$ops,Obj_size=$OBJECT_SIZE,Benchmark_Type=$BENCHMARK,region=us-west value=$th_value"
        update_value_3="IOPS,host=`hostname`,operation=$ops,Obj_size=$OBJECT_SIZE,Benchmark_Type=$BENCHMARK,region=us-west value=$IOPS"
        if [ ! -f "$CSV_FILE" ]
        then
            
            echo "Date Time,Hostname,Operation,IO_size,Benchmark_Type,Throughput,IOPS,Latency" > $CSV_FILE
        fi
        echo -e "`date +'%F %T'`,`hostname`,$ops,$OBJECT_SIZE,$BENCHMARK,$th_value,$IOPS,$latency" >> $CSV_FILE        
        
        curl -i -XPOST "$URL" --data-binary "$update_value_1" > /dev/null 2>&1;
        curl -i -XPOST "$URL" --data-binary "$update_value_2" > /dev/null 2>&1;
        curl -i -XPOST "$URL" --data-binary "$update_value_3" > /dev/null 2>&1;
        echo "$ops Data captured for Latency, Throughput and IOPS..."

    fi
fi


