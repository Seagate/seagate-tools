#!/usr/bin/env bash
#
#
# Copyright (c) 2022 Seagate Technology LLC and/or its Affiliates
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
#
# For any questions about this software or licensing,
# please email opensource@seagate.com or cortx-questions@seagate.com.
#
# -*- coding: utf-8 -*-

set -x

# # LR CODE
# CLUSTER_CONFIG_FILE="/var/lib/hare/cluster.yaml"
# ASSIGNED_IPS=$(ifconfig | grep inet | awk '{print $2}')
# SCRIPT_PATH="$(readlink -f $0)"
# SCRIPT_DIR="${SCRIPT_PATH%/*}"
# RESULT=$(python3 $SCRIPT_DIR/extract_disks.py $CLUSTER_CONFIG_FILE $ASSIGNED_IPS)
# NODE=`echo $RESULT | cut -d' ' -f 1`
# CURRENT_NODE="srvnode-${NODE}"
# DISKS=`echo "$RESULT" | grep 'IO:' | sed 's/IO://'`
# MD_DISKS=`echo "$RESULT" | grep 'MD:' | sed 's/MD://'`


# LC CODE
DISKS_MAP="/tmp/cortx_disks_map"
DISKS=$(cat "$DISKS_MAP" | grep 'IO:' | sed 's/IO://')
MD_DISKS=$(cat "$DISKS_MAP" | grep 'MD:' | sed 's/MD://')


function iostat_service_stop()
{
    iostat_pid=$(pidof iostat)
    kill "$iostat_pid"

    while kill -0 "$iostat_pid"; do
        sleep 1
    done

    pushd /var/perfline/iostat."$(hostname -s)"
    disks_dm=""
    for d in $DISKS; do
        dm=$(realpath "$d" | xargs basename)
        disks_dm="$disks_dm $dm"
        echo "IO $d $dm" >> disks.mapping
    done

    for d in $MD_DISKS; do
        dm=$(realpath "$d" | xargs basename)
        disks_dm="$disks_dm $dm"
        echo "MD $d $dm" >> disks.mapping
    done

    iostat-cli --fig-size 20,20 --data iostat.log \
               --disks ${disks_dm} \
               --fig-output iostat.aggregated.png plot

    # Below code has been commented intensionally, Since it's generating the same graph by above command.
    # To generate sepearte graph for "io_rqm iops io_transfer "%util" avgrq-sz avgqu-sz await svctm"

    # for plot in io_rqm iops io_transfer "%util" avgrq-sz avgqu-sz await svctm; do
    #    iostat-cli --fig-size 20,20 --data iostat.log \
    #               --disks $disks_dm \
    #               --fig-output iostat.$plot.png plot --subplots $plot
    # done

    > nodes.mapping
    echo "$CURRENT_NODE $(hostname)" >> nodes.mapping
    popd
}

function dstat_service_stop ()
{
     pids=$(ps ax | grep dstat | grep -v grep | grep -v worker | grep -v dstat_stop | grep -v dstat_start | awk '{print $1}')
     for pid in "$pids" ; do
        kill "$pid"

        while kill -0 "$pid"; do
             sleep 1
        done
     done

}

function blktrace_service_stop()
{
     blk_pid=$(pidof blktrace)
     kill -SIGINT "$blk_pid"

     while kill -0 "$blk_pid"; do
         sleep 1
     done

     pushd /var/perfline/blktrace."$(hostname -s)"
     for d in $(ls -1 | grep blktrace | awk -F. '{print $1}' | sort | uniq); do
         echo "$d"
         blkparse -i "$d.blktrace.*" -d "$d".dump -O
         iowatcher -t "$d".dump -o "$d".aggregated.svg
         for graph in io tput latency queue_depth iops; do
             iowatcher -t "$d".dump -o "$d"."${graph}".svg -O "${graph}"
         done
     done

     dumps=$(ls -1 | grep "dump" | awk '{print "-t "$1}' | tr '\n' ' ' | sed 's/ *$//g')
     iowatcher ${dumps} -o node."$(hostname -s)".aggregated.svg
     for graph in io tput latency queue_depth iops; do
         iowatcher ${dumps} -o node."$(hostname -s)"."${graph}".svg -O "${graph}"
     done
     pop

}

function glances_service_stop()
{
     pids=$(ps ax | grep glances | grep -v worker | grep -v grep | awk '{print $1}')
     for pid in "$pids" ; do
        kill -9 "$pid"

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
