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

source "$SCRIPT_DIR/../../../perfline.conf"

EX_SRV="pdsh -S -w $NODES"

HARE_CONF_LOCATION="/var/lib/hare"
HARE_CONFIG="$HARE_CONF_LOCATION/cluster.yaml"
HARE_CONFIG_BACKUP="$HARE_CONF_LOCATION/.perfline__cluster.yaml__backup"


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

function check_backup_files()
{
    $EX_SRV "[[ ! -e $HARE_CONFIG_BACKUP ]]"
}

function save_original_configs()
{
    save_original_hare_config
}

function save_original_hare_config()
{
    $EX_SRV cp $HARE_CONFIG $HARE_CONFIG_BACKUP
}

function customize_configs()
{
    customize_hare_config
}

function customize_hare_config()
{
    if [[ -n "$HARE_CONF_CUSTOM_CDF" ]]; then
        $EX_SRV "scp root@$(hostname):$HARE_CONF_CUSTOM_CDF $HARE_CONFIG"
    fi

    # generate params string
    local params=""

    if [[ -n "$HARE_CONF_SNS_DATA_UNITS" ]]; then
        params="$params --sns-data-units $HARE_CONF_SNS_DATA_UNITS"
    fi

    if [[ -n "$HARE_CONF_SNS_PARITY_UNITS" ]]; then
        params="$params --sns-parity-units $HARE_CONF_SNS_PARITY_UNITS"
    fi

    if [[ -n "$HARE_CONF_SNS_SPARE_UNITS" ]]; then
        params="$params --sns-spare-units $HARE_CONF_SNS_SPARE_UNITS"
    fi

    if [[ -n "$HARE_CONF_DIX_DATA_UNITS" ]]; then
        params="$params --dix-data-units $HARE_CONF_DIX_DATA_UNITS"
    fi

    if [[ -n "$HARE_CONF_DIX_PARITY_UNITS" ]]; then
        params="$params --dix-parity-units $HARE_CONF_DIX_PARITY_UNITS"
    fi

    if [[ -n "$HARE_CONF_DIX_SPARE_UNITS" ]]; then
        params="$params --dix-spare-units $HARE_CONF_DIX_SPARE_UNITS"
    fi

    if [[ -n "$params" ]]; then
        $EX_SRV "$SCRIPT_DIR/customize_hare_conf.py \
          -s $HARE_CONFIG -d $HARE_CONFIG $params"
    fi
}


function main()
{
    parse_args $@
    check_backup_files
    save_original_configs
    customize_configs
}

main $@
exit $?
