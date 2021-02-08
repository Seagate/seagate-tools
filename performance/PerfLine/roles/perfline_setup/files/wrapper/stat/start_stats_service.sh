#!/bin/bash

set -x

DISKS=$(salt-call pillar.get cluster:`cat /etc/salt/minion_id`:storage:data_devices --output=newline_values_only)

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



