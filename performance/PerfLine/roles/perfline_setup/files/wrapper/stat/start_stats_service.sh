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
}

function creating_dir()
{
     mkdir -p /var/perfline/iostat.$(hostname -s)
     mkdir -p /var/perfline/dstat.$(hostname -s)
     mkdir -p /var/perfline/blktrace.$(hostname -s)
}

function iostat-service-start()
{
     iostat -yxmt 1 > /var/perfline/iostat.$(hostname -s)/iostat.log &
}

function dstat-service-start()
{
     dstat --full --output /var/perfline/dstat.$(hostname -s)/dstat.csv > /dev/null &
}

function blktrace-service-start()
{    
     blktrace $DISKS -D /var/perfline/blktrace.$(hostname -s) 

}



removing_dir    
creating_dir
iostat-service-start   
dstat-service-start 
blktrace-service-start  



