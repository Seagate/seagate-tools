#!/bin/bash

set -x

CLUSTER_CONFIG_FILE="/var/lib/hare/cluster.yaml"
ASSIGNED_IPS=$(ifconfig | grep inet | awk '{print $2}')
SCRIPT_PATH="$(readlink -f $0)"
SCRIPT_DIR="${SCRIPT_PATH%/*}"
RESULT=$(python3 $SCRIPT_DIR/extract_disks.py $CLUSTER_CONFIG_FILE $ASSIGNED_IPS)
NODE=`echo $RESULT | cut -d' ' -f 1`
CURRENT_NODE="srvnode-${NODE}"
DISKS=`echo $RESULT | cut -d' ' -f 2-`
# CURRENT_NODE=$(cat /etc/salt/minion_id)

function iostat_service_stop()
{
     iostat_pid=$(pidof iostat)
     kill $iostat_pid

     while kill -0 "$iostat_pid"; do
         sleep 1
     done
     
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

function glances_service_stop()
{
     pids=`ps ax | grep glances |  grep -v grep | awk '{print $1}'`
     for pid in $pids ; do
        kill -9 $pid

     done

}

if [[ "$1" == *"IOSTAT"* ]]
then
    iostat_service_stop
fi
if [[ "$1" == *"DSTAT"* ]]
then
    dstat_service_stop
fi
if [[ "$1" == *"BLKTRACE"* ]]
then
    blktrace_service_stop
fi
if [[ "$1" == *"GLANCES"* ]]
then
    glances_service_stop
fi
