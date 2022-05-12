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
# DISKS=`echo "$RESULT" | grep 'IO:' | sed 's/IO://'`

# LC CODE
DISKS=`cat /tmp/cortx_disks_map | grep 'IO:' | sed 's/IO://'`

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
    csv_file="/var/perfline/glances.$(hostname -s)/glances.csv"
    glances --quiet --export csv --export-csv-file $csv_file &
    echo "Glances collection started"
fi
sleep 5

if [[ "$1" == *"BLKTRACE"* ]]
then
    echo "blktrace collection starting"
    blktrace $DISKS -D /var/perfline/blktrace.$(hostname -s)
fi

