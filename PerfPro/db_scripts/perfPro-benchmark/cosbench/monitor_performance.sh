#!/bin/bash
INFLUXDB=`cat /etc/telegraf/telegraf.conf | grep -A 3 outputs.influxdb | grep urls | cut -d "=" -f2 | tr -d '"[]' | tr -d ' '`
URL="$INFLUXDB/write?db=testdb"
host=`hostname`
OBJECT_SIZE=$1
BENCHMARK=$3
line=$(tail -n 1 $2) 
update_value_1=
update_value_2=
update_value_3=


ops1=$(echo "$line" | cut -f 6 -d ',' | cut -d ":" -f2 | tr -d '"' | tr -d " "  )
ops2=$(echo "$line" | cut -f 20 -d ',' | cut -d ":" -f2 | tr -d '"' | tr -d " "  )

if [[ "$ops1" = "read" ]] || [[ "$ops1" = "write" ]] 
then
        IOPS=$(echo "$line" | cut -f 9 -d ',' | cut -d ":" -f2 )
        Th_value=$(echo "$line" | cut -f 9 -d ',' | cut -d ":" -f2 )
        Th=`expr "$Th_value * $OBJECT_SIZE" | bc -l`
        value=`printf "%.2f" $(echo $Th | bc -l)`
        Latency=$(echo "$line" | cut -f 12 -d ',' | cut -d ":" -f2 )
        Lat=`printf "%.2f" $(echo $Th | bc -l)`
        size=$OBJECT_SIZE\Mb
        ops1=${ops1^}
        update_value_1="Latency,host=`hostname`,operation=$ops1,Obj_size=$size,Benchmark_Type=$BENCHMARK,region=us-west value=$Lat"
        update_value_2="Throughput,host=`hostname`,operation=$ops1,Obj_size=$size,Benchmark_Type=$BENCHMARK,region=us-west value=$value"
        update_value_3="IOPS,host=`hostname`,operation=$ops1,Obj_size=$size,Benchmark_Type=$BENCHMARK,region=us-west value=$IOPS"
        curl -i -XPOST "$URL" --data-binary "$update_value_1"  > /dev/null 2>&1;
        curl -i -XPOST "$URL" --data-binary "$update_value_2"  > /dev/null 2>&1;
        curl -i -XPOST "$URL" --data-binary "$update_value_3"  > /dev/null 2>&1;
        echo "$ops1 Data captured for latency, throughput and IOPS..."
fi

if [[ "$ops2" = "read" ]] || [[ "$ops2" = "write" ]]
then
        IOPS=$(echo "$line" | cut -f 23 -d ',' | cut -d ":" -f2 )
        Th_value=$(echo "$line" | cut -f 23 -d ',' | cut -d ":" -f2 )
        Th=`expr "$Th_value * $OBJECT_SIZE" | bc -l`
        value=`printf "%.2f" $(echo $Th | bc -l)`
        Latency=$(echo "$line" | cut -f 26 -d ',' | cut -d ":" -f2 )
        Lat=`printf "%.2f" $(echo $Latency | bc -l)`
        size=$OBJECT_SIZE\Mb
        ops2=${ops2^}
        update_value_1="Latency,host=`hostname`,operation=$ops2,Obj_size=$size,Benchmark_Type=$BENCHMARK,region=us-west value=$Lat"
        update_value_2="Throughput,host=`hostname`,operation=$ops2,Obj_size=$size,Benchmark_Type=$BENCHMARK,region=us-west value=$value"
        update_value_3="IOPS,host=`hostname`,operation=$ops2,Obj_size=$size,Benchmark_Type=$BENCHMARK,region=us-west value=$IOPS"
        curl -i -XPOST "$URL" --data-binary "$update_value_1"  > /dev/null 2>&1;
        curl -i -XPOST "$URL" --data-binary "$update_value_2"  > /dev/null 2>&1;
        curl -i -XPOST "$URL" --data-binary "$update_value_3"  > /dev/null 2>&1;
        echo "$ops2 Data captured for latency, throughput and IOPS..."

fi     
