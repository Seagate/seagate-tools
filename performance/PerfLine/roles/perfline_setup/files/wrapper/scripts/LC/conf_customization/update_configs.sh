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

# SCRIPT_NAME=$(echo "$0" | awk -F "/" '{print $NF}')
SCRIPT_PATH="$(readlink -f "$0")"
SCRIPT_DIR="${SCRIPT_PATH%/*}"

source "$SCRIPT_DIR/../../../../perfline.conf"

SOLUTION_CONFIG="$CORTX_K8S_REPO/k8_cortx_cloud/solution.yaml"
SOLUTION_CONFIG_BACKUP="$CORTX_K8S_REPO/k8_cortx_cloud/.perfline__solution.yaml__backup"

function parse_args()
{
    echo "params: $@"

    while [[ $# -gt 0 ]]; do
        case $1 in
            --solution-custom-conf)
                SOLUTION_CUSTOM_CONF="$2"
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
            --task-id)
                TASK_ID="$2"
                shift
                ;;
            --motr-param)
                MOTR_PARAMS="$MOTR_PARAMS --motr-param $2"
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
    cp -f "$SOLUTION_CONFIG" "$SOLUTION_CONFIG_BACKUP"
}

function customize_solution_config()
{
    copy_custom_solution_file

    if [[ -n "$MOTR_PARAMS" ]]; then
        local base_docker_image=$(cat "$SOLUTION_CONFIG" | grep cortxdata: | awk '{print $2}')
        local base_docker_image_name=$(echo "$base_docker_image" | awk -F ':' '{print $1}')
        local base_docker_image_tag=$(echo "$base_docker_image" | awk -F ':' '{print $2}')
        local new_docker_image="$base_docker_image_name:perfline_$TASK_ID"

        "$SCRIPT_DIR"/../update_docker_image.sh \
            --base-image "$base_docker_image" \
            --image "$new_docker_image" \
            --tmp-container tmp_perfline_"$TASK_ID" \
            --nodes "$NODES" "$MOTR_PARAMS"

        sed -i "s|$base_docker_image|$new_docker_image|" "$SOLUTION_CONFIG"
    fi

    check_solution_config
}

function copy_custom_solution_file() {
    if [[ -n "$SOLUTION_CUSTOM_CONF" ]]; then
        cp -f "$SOLUTION_CUSTOM_CONF" "$SOLUTION_CONFIG"
    fi
}

function check_solution_config(){
    local sns_params=""
    local dix_params=""

    if [[ -n "$HARE_CONF_SNS_DATA_UNITS" ]] && [[ -n "$HARE_CONF_SNS_PARITY_UNITS" ]] &&
       [[ -n "$HARE_CONF_SNS_SPARE_UNITS" ]]; then
        sns_params="--sns $HARE_CONF_SNS_DATA_UNITS+$HARE_CONF_SNS_PARITY_UNITS+$HARE_CONF_SNS_SPARE_UNITS"
    fi

    if [[ -n "$HARE_CONF_DIX_DATA_UNITS" ]] && [[ -n "$HARE_CONF_DIX_PARITY_UNITS" ]] &&
       [[ -n "$HARE_CONF_DIX_SPARE_UNITS" ]]; then
        dix_params="--dix $HARE_CONF_DIX_DATA_UNITS+$HARE_CONF_DIX_PARITY_UNITS+$HARE_CONF_DIX_SPARE_UNITS"
    fi

    if [[ -n "$sns_params" ]] || [[ -n "$dix_params" ]]; then
       update_solution_file "$sns_params" "$dix_params"
    fi

}

function update_solution_file() {
    echo "parameters: $@"
    while [[ $# -gt 0 ]]; do
    case $1 in
        --sns)
            SNS="$2"
            shift
            ;;
        --dix)
            DIX="$2"
            shift
            ;;
        --help)
                echo -e "Usage: bash update_solution_file --sns 1+0+0 --dix 1+0+0 \n"
                exit 0
                ;;
        *)
            echo -e "Invalid option: $1\nUse --help option"
            exit 1
             ;;
    esac
    shift
    done
    output=$(python3  <<END
import yaml
import sys
solution_file = "$SOLUTION_CONFIG"
with open(solution_file, 'r') as f:
    data = yaml.safe_load(f)
if "$SNS" != "":
    data['solution']['common']['storage_sets']['durability']['sns'] = "$SNS"

if "$DIX" != "":
    data['solution']['common']['storage_sets']['durability']['dix'] = "$DIX"

with open(solution_file, 'w') as yaml_file:
    yaml_file.write( yaml.dump(data, sort_keys = False))

print("Successfully updated solution.yaml")
END
)

echo "$output"

}

function main()
{
    parse_args $@
    save_original_solution_config
    customize_solution_config
}

main $@
exit $?
