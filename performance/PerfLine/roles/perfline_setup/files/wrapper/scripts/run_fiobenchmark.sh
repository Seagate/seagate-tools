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

set -e
set -x

#
# Variables deaclaration
#
CLUSTER_CONFIG_FILE="/var/lib/hare/cluster.yaml"
ASSIGNED_IPS=$(ifconfig | grep inet | awk '{print $2}')
SCRIPT_PATH="$(readlink -f $0)"
SCRIPT_DIR="${SCRIPT_PATH%/*}"
RESULT=$(python3 $SCRIPT_DIR/../stat/extract_disks.py $CLUSTER_CONFIG_FILE $ASSIGNED_IPS)
DISKS=$(echo $RESULT | cut -d' ' -f 2-)
PERFLINE_DIR="/var/perfline/"

DURATION=""
BLOCK_SIZE=""
NUMOFJOBS=""
TIMESTAMP=`date +'%Y-%m-%d_%H:%M:%S'`
SAMPLE=""
TEMPLATE=""

validate_args() {

        if [[ -z $DURATION ]] || [[ -z $NUMOFJOBS ]] || [[ -z $BLOCK_SIZE ]] || [[ -z $TEMPLATE ]] ; then
                show_usage
        fi

}

show_usage() {
        echo -e "\n \t  Usage : ./run_fiobenchmark.sh -t DURATION -bs BLOCK_SIZE -nj NUMOFJOBS -tm TEMPLATE  \n"
        echo -e "\t -t\t:\t Run time (Duration) \n"
        echo -e "\t -bs\t:\t Blocksize\n"
        echo -e "\t -nj\t:\t Number of jobs\n"
        echo -e "\t -tm\t:\t Template for fio like seq_read_fio, seq_write_fio, randmix_80-20_fio, randmix_20-80_fio and rand_fio \n"
        echo -e "\tExample\t:\t ./run_fiobenchmark.sh -t 300 -bs 1Mb,4Mb,16Mb -nj 16,32,64 -tm seq_read_fio  \n"
        exit 1
}

fio_benchmark() {
       rm -rf $PERFLINE_DIR/fio-workload_$(hostname)
       WORKLOAD_DIR=$PERFLINE_DIR/fio-workload_$(hostname)
       mkdir -p $WORKLOAD_DIR
       for bs in ${BLOCK_SIZE//,/ }
       do
           for numjob in ${NUMOFJOBS//,/ }
           do
                   IOSIZE=$(echo "$bs" | sed -e 's/Mb/M/g')
                   template_file=$SCRIPT_DIR/fio-template/$TEMPLATE
                   workload_file=$WORKLOAD_DIR/$TEMPLATE\_bs_$IOSIZE\_numjobs_$numjob\_$(hostname)
                   cp $template_file $workload_file
                   sed -i "/\[global\]/a bs=$IOSIZE" $workload_file
                   sed -i "/time_based/a runtime=$DURATION" $workload_file
                   sed -i "/runtime/a numjobs=$numjob" $workload_file
                   for i in $DISKS
                   do
                       disk=$(echo "$i" | cut -d '/' -f 4)
                       echo -e "\n[$disk]" >> $workload_file
                       echo -e "filename = /dev/disk/by-id/dm-name-$disk \n" >> $workload_file
                   done
                   FIOLOG=$WORKLOAD_DIR/$TEMPLATE\_bs_$IOSIZE\_numjobs_$numjob\.log
                   fio $workload_file > $FIOLOG
                   echo "Fio scripts is completed on $(hostname) ..."
           done
       done

}

while [ ! -z $1 ]; do

        case $1 in
        -t)     shift
                DURATION="$1"
        ;;

        -bs)    shift
                BLOCK_SIZE="$1"
        ;;

        -nj)    shift
                NUMOFJOBS="$1"
        ;;

        -tm)    shift
                TEMPLATE="$1"
        ;;

        *)
                show_usage
                break
        esac
        shift
done

validate_args
fio_benchmark

