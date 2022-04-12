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
DISKS=$(cat /tmp/cortx_disks_map | grep 'IO:' | sed 's/IO://')
MD_DISKS=$(cat /tmp/cortx_disks_map | grep 'MD:' | sed 's/MD://')


function main()
{
    for d in $DISKS; do
        dm=$(realpath "$d" | xargs basename)
        disks_dm="$disks_dm $dm"
        echo "IO $d $dm"
    done

    for d in $MD_DISKS; do
        dm=$(realpath "$d" | xargs basename)
        disks_dm="$disks_dm $dm"
        echo "MD $d $dm"
    done
}


main "$@"
exit $?
