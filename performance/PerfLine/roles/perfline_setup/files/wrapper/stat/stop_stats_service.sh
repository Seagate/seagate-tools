#!/bin/bash

set -x

DISKS=$(salt-call pillar.get cluster:`cat /etc/salt/minion_id`:storage:data_devices --output=newline_values_only)
CURRENT_NODE=$(cat /etc/salt/minion_id)

function iostat_service_stop()
{
     iostat_pid=$(pidof iostat)
     kill $iostat_pid

     while kill -0 "$iostat_pid"; do
         sleep 1
     done
#     disks=$(salt-call pillar.get cluster:`cat /etc/salt/minion_id`:storage:data_devices --output=newline_values_only)
     
     md=`mount | grep -e mero -e m0tr -e motr | awk '{print $1}'`
     md_base=`echo $md | awk -F/ '{print $NF}'`
     md_base=${md_base::-1}

     pushd /var/perfline/iostat.$(hostname -s)

     disks_dm=
     > disks.mapping
     for d in $DISKS; do
         dm=`realpath $d | xargs basename`
         disks_dm="$disks_dm $dm"
         echo "IO $d $dm" >> disks.mapping
     done

     dm=`multipath -ll | grep $md_base | awk '{print $3}'`
     disks_dm="$disks_dm $dm"
     echo "MD $md $dm" >> disks.mapping

     iostat-cli --fig-size 20,20 --data iostat.log \
           --disks $disks_dm \
           --fig-output iostat.aggregated.png plot

     for plot in io_rqm iops io_transfer "%util" avgrq-sz avgqu-sz await svctm; do
     iostat-cli --fig-size 20,20 --data iostat.log \
           --disks $disks_dm \
           --fig-output iostat.$plot.png plot --subplots $plot
     done

#     current_node=$(cat /etc/salt/minion_id)
     > nodes.mapping
     echo "$CURRENT_NODE $(hostname)" >> nodes.mapping

     popd

 
}

function dstat_service_stop ()
{
     pids=`ps ax | grep dstat | grep -v grep | grep -v dstat_stop | grep -v dstat_start | awk '{print $1}'`
     for pid in $pids ; do
        kill $pid

        while kill -0 "$pid"; do
             sleep 1
        done
     done

}

function blktrace_service_stop()
{
     blk_pid=$(pidof blktrace)
     kill -SIGINT $blk_pid
     
     while kill -0 "$blk_pid"; do
         sleep 1
     done
     
     pushd /var/perfline/blktrace.$(hostname -s)
     for d in $(ls -1 | grep dm | awk -F. '{print $1}' | sort | uniq); do
         echo $d
         blkparse -i "$d.blktrace.*" -d $d.dump -O
         iowatcher -t $d.dump -o $d.aggregated.svg
         for graph in io tput latency queue_depth iops; do
             iowatcher -t $d.dump -o $d.$graph.svg -O $graph
         done
     done
     
     dumps=$(ls -1 | grep "dm.*dump" | awk '{print "-t "$1}' | tr '\n' ' ')
     iowatcher $dumps -o node.$(hostname -s).aggregated.svg
     for graph in io tput latency queue_depth iops; do
         iowatcher $dumps -o node.$(hostname -s).$graph.svg -O $graph
     done
 
}

iostat_service_stop
dstat_service_stop
blktrace_service_stop

