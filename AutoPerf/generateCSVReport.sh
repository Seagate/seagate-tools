#! /bin/bash

# ./generateCSVReport.sh startTime endTime BENCHMARK SIZE host1 host2 host3
DATE=`date +'%F_%T'`

echo "Generating CSV report for $3"
if [ ! -d report ];
then
     mkdir report
fi
influx -host 'cftic2.pun.seagate.com' -port 8086 -precision rfc3339 -database 'performance_db' -execute "SELECT * FROM IOPS where time >= '$1' and time <= '$2' or host='$5' or host='$6' or host='$7'" -format csv > report/report_$3\_Configuration_$4\_$DATE\.csv

influx -host 'cftic2.pun.seagate.com' -port 8086 -precision rfc3339 -database 'performance_db' -execute "SELECT * FROM Throughput where time >= '$1' and time <= '$2' or host='$5' or host='$6' or host='$7'" -format csv >> report/report_$3\_Configuration_$4\_$DATE\.csv

influx -host 'cftic2.pun.seagate.com' -port 8086 -precision rfc3339 -database 'performance_db' -execute "SELECT * FROM Latency where time >= '$1' and time <= '$2' or host='$5' or host='$6' or host='$7'" -format csv >> report/report_$3\_Configuration_$4\_$DATE\.csv

influx -host 'cftic2.pun.seagate.com' -port 8086 -precision rfc3339 -database 'performance_db' -execute "SELECT usage_user,usage_system,usage_iowait FROM cpu where time >= '$1' and time <= '$2' or host='$5' or host='$6' or host='$7'" -format csv >> report/report_$3\_Configuration_$4\_$DATE\.csv

influx -host 'cftic2.pun.seagate.com' -port 8086 -precision rfc3339 -database 'performance_db' -execute "SELECT load1,load5,load15 FROM system where time >= '$1' and time <= '$2' or host='$5' or host='$6' or host='$7'" -format csv >> report/report_$3\_Configuration_$4\_$DATE\.csv

influx -host 'cftic2.pun.seagate.com' -port 8086 -precision rfc3339 -database 'performance_db' -execute "SELECT read_bytes,write_bytes FROM diskio where time >= '$1' and time <= '$2' or host='$5' or host='$6' or host='$7'" -format csv >> report/report_$3\_Configuration_$4\_$DATE\.csv

influx -host 'cftic2.pun.seagate.com' -port 8086 -precision rfc3339 -database 'performance_db' -execute "SELECT used,total FROM mem where time >= '$1' and time <= '$2' or host='$5' or host='$6' or host='$7'" -format csv >> report/report_$3\_Configuration_$4\_$DATE\.csv

influx -host 'cftic2.pun.seagate.com' -port 8086 -precision rfc3339 -database 'performance_db' -execute "SELECT bytes_recv,bytes_sent FROM net where time >= '$1' and time <= '$2' or host='$5' or host='$6' or host='$7'" -format csv >> report/report_$3\_Configuration_$4\_$DATE\.csv
