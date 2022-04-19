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

SCRIPT_PATH="$(readlink -f $0)"
SCRIPT_DIR="${SCRIPT_PATH%/*}"
GLANCES_DIR="$SCRIPT_DIR/../../stat/glances"


DISKS_MAPPING_FILE="../disks.mapping"
NETWORK_IFACES_FILE="../network/network_interfaces_info"
CPU_INFO_FILE="../hw/cpu_info"
CSV_DATA_FILE="glances.csv"

YAML_TEMPLATE_FILE="$GLANCES_DIR/glances_stats_schema.template.yaml"


function process_data_for_node()
{
    local hostname="$1"

    pushd $hostname/glances

    local cpu_nr=$(cat $CPU_INFO_FILE | grep '^CPU(s):' | sed "s/'//g" | awk '{print $2}')
    local data_vols=$(cat $DISKS_MAPPING_FILE | grep IO | awk '{print $3}')
    local md_vols=$(cat $DISKS_MAPPING_FILE | grep MD | awk '{print $3}')
    local net_ifaces=$(cat $NETWORK_IFACES_FILE | grep '^[0-9]:' | awk -F ': ' '{print $2}' | sed 's/@.*$//')

    $GLANCES_DIR/gen_glances_stats_schema.py -y $YAML_TEMPLATE_FILE \
            -d "$data_vols" -m "$md_vols" -n "$net_ifaces" -c "$cpu_nr"
    $GLANCES_DIR/plot_glances_stats.py -y "glances_stats_schema.yaml" -c "$CSV_DATA_FILE"

    popd
}


function main()
{
    local hostnames="$@"

    for hostname in $hostnames; do
        process_data_for_node $hostname
    done
}


main $@
exit $?
