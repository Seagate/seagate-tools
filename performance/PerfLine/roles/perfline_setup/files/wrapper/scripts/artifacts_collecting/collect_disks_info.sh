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


CLUSTER_CONFIG_FILE="/var/lib/hare/cluster.yaml"
ASSIGNED_IPS=$(ifconfig | grep inet | awk '{print $2}')
SCRIPT_PATH="$(readlink -f $0)"
SCRIPT_DIR="${SCRIPT_PATH%/*}"
RESULT=$(python3 $SCRIPT_DIR/../../stat/extract_disks.py $CLUSTER_CONFIG_FILE $ASSIGNED_IPS)
NODE=`echo $RESULT | cut -d' ' -f 1`
CURRENT_NODE="srvnode-${NODE}"
DISKS=`echo $RESULT | cut -d' ' -f 2-`


function main()
{ 
    md=`mount | grep -e mero -e m0tr -e motr | awk '{print $1}'`
    md_base=`echo $md | awk -F/ '{print $NF}'`
    md_base=${md_base::-1}

    for d in $DISKS; do
        dm=`realpath $d | xargs basename`
        disks_dm="$disks_dm $dm"
        echo "IO $d $dm"
    done

    dm=`multipath -ll | grep $md_base | awk '{print $3}'`
    disks_dm="$disks_dm $dm"
    echo "MD $md $dm"
}


main $@
exit $?
