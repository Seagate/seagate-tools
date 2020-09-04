#! /usr/bin/bash
#
# Script to select and launch benchamrk
#
ECHO='echo AutoPerf >'
source ./launch_benchmark.conf
#
# Select options
#
$ECHO " "
$ECHO "Script to select Benchmark"
$ECHO "=========================="
$ECHO "Select Benchmark"
read -p "AutoPerf > [ $benchmarks ] : " benchmark
if [ "$benchmark" = "s3bench_basic" ]
then
   $ECHO "Select type yes or no for skipClean up"
   read -p "AutoPerf > [ $skipcleanup ] : " skip
fi

if [ "$benchmark" = "cosbench" ]
then
   $ECHO "Select operation"
   read -p "AutoPerf > [ $operations ] : " value
fi
if [ "$benchmark" = "fio" ]
then
   $ECHO "Select Template"
   read -p "AutoPerf > [ $templates ] : " value
fi

$ECHO "Select Configuration"
read -p "AutoPerf > [ $configurations ] : " configuration
$ECHO "Select S3 Client"
read -p "AutoPerf > [ $clients ] : " client
$ECHO "Select Primary Server"
read -p "AutoPerf > [ $primaryserver ] : " primary
$ECHO "Select Secondary Server"
read -p "AutoPerf > [ $secondaryserver ] : " secondary
$ECHO "Select Server auth key"
read -p "AutoPerf > Key : " key
$ECHO "Select Sampling"
read -p "AutoPerf > [ sec $sampling ] : " sample
$ECHO " "
$ECHO "============================"
$ECHO "Benchmark: " $benchmark 
if [ "$benchmark" = "s3bench_basic" ]
then
    $ECHO "skipCleanup: " $skip
fi

$ECHO "Config   : " $configuration
if [ "$benchmark" = "cosbench" ]
then
    $ECHO "Operation: " $value
fi
if [ "$benchmark" = "fio" ]
then
    $ECHO "Template: " $value
fi

$ECHO "Client   : " $client 
$ECHO "Primary  : " $primary
$ECHO "Secondary: " $secondary
$ECHO "Sampling : " $sample
$ECHO "============================"
#
#  setting up customize variables
if [ $configuration == "custom" ]
then
    ./customVariables.sh $benchmark
fi

#
$ECHO " "
read -p "AutoPerf > Correct [Y/N] : " opt
$ECHO " "
#
# launch benchmark
#

if [ $opt == "Y" ]
then
#    yes | cp hosts.bak hosts >/dev/null 2>&1
#    sed -i "/^\[clientserver\]/a serverclient ansible_host=$client" hosts    
#    sed -i "/^\[s3server\]/a serverprimary ansible_host=$primary" hosts
#    sed -i "/^\[s3server\]/a serversecondary ansible_host=$secondary" hosts
#    sed -i "/^\[allserver\]/a serverclient ansible_host=$client" hosts
#    sed -i "/^\[allserver\]/a serverprimary ansible_host=$primary" hosts
#    sed -i "/^\[allserver\]/a serversecondary ansible_host=$secondary" hosts
#
#    yes | mv hosts /etc/ansible/ >/dev/null 2>&1
#    ./automatePasswordless.sh root $client $key >/dev/null 2>&1
#    ./automatePasswordless.sh root $primary $key >/dev/null 2>&1
#    ./automatePasswordless.sh root $secondary $key >/dev/null 2>&1
#    ./s3workloads.sh $benchmark $configuration $client $server $sample $value
    startTime=`date -u +"%Y-%m-%dT%H:%M:%SZ"`
    ansible-playbook main.yml --extra-vars "BENCHMARK=$benchmark CONFIGURATION=$configuration  SAMPLE=$sample OPERATION=$value SKIPCLEANUP=$skip CLIENT=$client PRIMARY=$primary SECONDARY=$secondary KEY=$key" -v
    endTime=`date -u +"%Y-%m-%dT%H:%M:%SZ"`
    ./generateCSVReport.sh $startTime $endTime $benchmark $configuration $client $primary $secondary
else
  exit
fi
