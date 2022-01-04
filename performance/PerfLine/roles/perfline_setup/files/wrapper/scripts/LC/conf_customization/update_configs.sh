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
set -x

SCRIPT_NAME=`echo $0 | awk -F "/" '{print $NF}'`
SCRIPT_PATH="$(readlink -f $0)"
SCRIPT_DIR="${SCRIPT_PATH%/*}"

source "$SCRIPT_DIR/../../../../perfline.conf"

SOLUTION_CONFIG="$CORTX_K8S_REPO/k8_cortx_cloud/solution.yaml"
SOLUTION_CONFIG_BACKUP="$CORTX_K8S_REPO/k8_cortx_cloud/.perfline__solution.yaml__backup"

function parse_args()
{
    echo "params: $@"

    while [[ $# -gt 0 ]]; do
        case $1 in
            --hare-custom-cdf)
                HARE_CONF_CUSTOM_CDF="$2"
                shift
                ;;
            --hare-sns-data-units)
                HARE_CONF_SNS_DATA_UNITS="$2"
                shift
                ;;
            --hare-sns-parity-units)
                HARE_CONF_SNS_PARITY_UNITS="$2"
                shift
                ;;
            --hare-sns-spare-units)
                HARE_CONF_SNS_SPARE_UNITS="$2"
                shift
                ;;
            --hare-dix-data-units)
                HARE_CONF_DIX_DATA_UNITS="$2"
                shift
                ;;
            --hare-dix-parity-units)
                HARE_CONF_DIX_PARITY_UNITS="$2"
                shift
                ;;
            --hare-dix-spare-units)
                HARE_CONF_DIX_SPARE_UNITS="$2"
                shift
                ;;
            *)
                echo -e "Invalid option: $1\nUse --help option"
                exit 1
                ;;
        esac
        shift
    done
}

function save_original_solution_config()
{
    cp $SOLUTION_CONFIG $SOLUTION_CONFIG_BACKUP
}

function customize_solution_config()
{
    update_solution_file
}

function restore_original_solution_config()
{
    yes | mv $SOLUTION_CONFIG_BACKUP $SOLUTION_CONFIG
}

function update_solution_file() {
    output=`python3  <<END
import yaml
import sys
solution_file = "$SOLUTION_CONFIG"
SNS = "$HARE_CONF_SNS_DATA_UNITS+$HARE_CONF_SNS_PARITY_UNITS+$HARE_CONF_SNS_SPARE_UNITS"
DIX = "$HARE_CONF_DIX_DATA_UNITS+$HARE_CONF_DIX_PARITY_UNITS+$HARE_CONF_DIX_SPARE_UNITS"
with open(solution_file, 'r') as f:
    data = yaml.safe_load(f)
data['solution']['common']['storage_sets']['durability']['sns'] = SNS
data['solution']['common']['storage_sets']['durability']['dix'] = DIX

with open(solution_file, 'w') as yaml_file:
    yaml_file.write( yaml.dump(data, sort_keys = False))

print("Successfully updated solution.yaml")
END`

echo $output

}

function main()
{
    parse_args "$@"
    save_original_solution_config
    customize_solution_config
    restore_original_solution_config
}

main "$@"
exit $?
