#!/usr/bin/env bash
#
# Copyright (c) 2020 Seagate Technology LLC and/or its Affiliates
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# For any questions about this software or licensing,
# please email opensource@seagate.com or cortx-questions@seagate.com.
#

set -e

# LR CODE
# CLUSTER_CONFIG_FILE="/var/lib/hare/cluster.yaml"
# ASSIGNED_IPS=$(ifconfig | grep inet | awk '{print $2}')
# SCRIPT_PATH="$(readlink -f $0)"
# SCRIPT_DIR="${SCRIPT_PATH%/*}"
# RESULT="$(python3 $SCRIPT_DIR/../../stat/extract_disks.py $CLUSTER_CONFIG_FILE $ASSIGNED_IPS)"
# NODE=`echo $RESULT | cut -d' ' -f 1`
# CURRENT_NODE="srvnode-${NODE}"
# DISKS=`echo "$RESULT" | grep 'IO:' | sed 's/IO://'`
# MD_DISKS=`echo "$RESULT" | grep 'MD:' | sed 's/MD://'`

# LC CODE
DISKS=`cat /tmp/cortx_disks_map | grep 'IO:' | sed 's/IO://'`
MD_DISKS=`cat /tmp/cortx_disks_map | grep 'MD:' | sed 's/MD://'`


function main()
{ 
    for d in $DISKS; do
        dm=`realpath $d | xargs basename`
        disks_dm="$disks_dm $dm"
        echo "IO $d $dm"
    done

    for d in $MD_DISKS; do
        dm=`realpath $d | xargs basename`
        disks_dm="$disks_dm $dm"
        echo "MD $d $dm"
    done
}


main $@
exit $?
