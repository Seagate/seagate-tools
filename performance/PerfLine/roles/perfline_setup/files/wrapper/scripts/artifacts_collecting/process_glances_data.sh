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

SCRIPT_PATH="$(readlink -f $0)"
SCRIPT_DIR="${SCRIPT_PATH%/*}"
GLANCES_DIR="$SCRIPT_DIR/../../stat/glances"


DISKS_MAPPING_FILE="../disks.mapping"
NETWORK_IFACES_FILE="../network/network_interfaces_info"
CSV_DATA_FILE="glances.csv"

YAML_TEMPLATE_FILE="$GLANCES_DIR/glances_stats_schema.template.yaml"


function process_data_for_node()
{
    local hostname="$1"
    
    pushd $hostname/glances

    local cpu_nr=$(lscpu | grep '^CPU(s):' | awk '{print $2}')
    local data_vols=$(cat $DISKS_MAPPING_FILE | grep IO | awk '{print $3}')
    local md_vols=$(cat $DISKS_MAPPING_FILE | grep MD | awk '{print $3}')
    local net_ifaces=$(cat $NETWORK_IFACES_FILE | grep '^[0-9]:' | awk -F ': ' '{print $2}')
    
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
