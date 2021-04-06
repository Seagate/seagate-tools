#!/bin/bash

set -x

CLUSTER_CONFIG_FILE="/var/lib/hare/cluster.yaml"
ASSIGNED_IPS=$(ifconfig | grep inet | awk '{print $2}')
SCRIPT_PATH="$(readlink -f $0)"
SCRIPT_DIR="${SCRIPT_PATH%/*}"
RESULT=$(python3 $SCRIPT_DIR/extract_disks.py $CLUSTER_CONFIG_FILE $ASSIGNED_IPS)
DISKS=`echo $RESULT | cut -d' ' -f 2-`

function removing_dir()
{
     rm -rf /var/perfline/iostat.$(hostname -s) || true
     rm -rf /var/perfline/dstat.$(hostname -s) || true
     rm -rf /var/perfline/blktrace.$(hostname -s) || true
     rm -rf /var/perfline/glances.$(hostname -s) || true
}

function creating_dir()
{
     mkdir -p /var/perfline/iostat.$(hostname -s)
     mkdir -p /var/perfline/dstat.$(hostname -s)
     mkdir -p /var/perfline/blktrace.$(hostname -s)
     mkdir -p /var/perfline/glances.$(hostname -s)
}

echo "stat collection: $1"
removing_dir    
creating_dir
if [[ "$1" == *"IOSTAT"* ]]
then
     iostat -yxmt 1 > /var/perfline/iostat.$(hostname -s)/iostat.log & 
     echo "iostat collection started"
fi
sleep 5

if [[ "$1" == *"DSTAT"* ]]
then
    dstat --full --output /var/perfline/dstat.$(hostname -s)/dstat.csv > /dev/null &
    echo "dstat collection started"
fi
sleep 5

if [[ "$1" == *"GLANCES"* ]]
then
    glances --stdout now,core,cpu,percpu,diskio,fs,load,system,mem,memswap,\
network,processcount,raid,sensors,uptime --export csv --export-csv-file \
/var/perfline/glances.$(hostname -s)/glances.csv > /dev/null 2>&1 &
    echo "Glances collection started"
fi
sleep 5

if [[ "$1" == *"BLKTRACE"* ]]
then
    echo "blktrace collection starting"
    blktrace $DISKS -D /var/perfline/blktrace.$(hostname -s) 
fi

