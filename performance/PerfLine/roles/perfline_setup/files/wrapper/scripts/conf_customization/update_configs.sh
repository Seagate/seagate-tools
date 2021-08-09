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

MOTR_CONFIG="/etc/sysconfig/motr"
MOTR_CONFIG_BACKUP="/etc/sysconfig/.perfline__motr__backup"

HAPROXY_CONFIG="/etc/haproxy/haproxy.cfg"
HAPROXY_CONFIG_BACKUP="/etc/haproxy/.perfline__haproxy.cfg__backup"

S3_CONFIG="/opt/seagate/cortx/s3/conf/s3config.yaml"
S3_CONFIG_BACKUP="/opt/seagate/cortx/s3/conf/.perfline__s3config.yaml__backup"

LNET_CONFIG="/etc/modprobe.d/lnet.conf"
LNET_CONFIG_BACKUP="/etc/modprobe.d/.perfline__lnet.conf__backup"

IB_CONFIG="/etc/modprobe.d/ko2iblnd.conf"
IB_CONFIG_BACKUP="/etc/modprobe.d/.perfline__ko2iblnd.conf__backup"

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
            --motr-custom-conf)
                MOTR_CUSTOM_CONF="$2"
                shift
                ;;
            --motr-param)
                MOTR_PARAMS="$MOTR_PARAMS $2"
                shift
                ;;
            --s3-custom-conf)
                S3_CUSTOM_CONF="$2"
                shift
                ;;
            --s3-instance-nr)
                S3_INSTANCE_NR="$2"
                shift
                ;;
            --s3-srv-param|--s3-auth-param|--s3-motr-param|--s3-thirdparty-param)
                S3_PARAMS="$S3_PARAMS $1 \"$2\""
                shift
                ;;
	    --lnet-custom-conf)
		LNET_CUSTOM_CONF="$2"
		shift
		;;
	    --ib-custom-conf)
		IB_CUSTOM_CONF="$2"
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
    $EX_SRV "[[ ! -e $MOTR_CONFIG_BACKUP ]]"
    $EX_SRV "[[ ! -e $HAPROXY_CONFIG_BACKUP ]]"
    $EX_SRV "[[ ! -e $S3_CONFIG_BACKUP ]]"
    $EX_SRV "[[ ! -e $LNET_CONFIG_BACKUP ]]"
    $EX_SRV "[[ ! -e $IB_CONFIG_BACKUP ]]"
}

function save_original_configs()
{
    save_original_hare_config
    save_original_motr_config
    save_original_haproxy_config
    save_original_s3_config
    save_original_lnet_config
    save_original_ib_config
}

function save_original_hare_config()
{
    $EX_SRV cp $HARE_CONFIG $HARE_CONFIG_BACKUP
}

function save_original_motr_config()
{
    $EX_SRV cp $MOTR_CONFIG $MOTR_CONFIG_BACKUP
}

function save_original_haproxy_config()
{
    $EX_SRV cp $HAPROXY_CONFIG $HAPROXY_CONFIG_BACKUP
}

function save_original_s3_config()
{
    $EX_SRV cp $S3_CONFIG $S3_CONFIG_BACKUP
}

function save_original_lnet_config()
{
    $EX_SRV cp $LNET_CONFIG $LNET_CONFIG_BACKUP
}

function save_original_ib_config()
{
    $EX_SRV cp $IB_CONFIG $IB_CONFIG_BACKUP
}

function customize_configs()
{
    customize_hare_config
    customize_motr_config
    customize_haproxy_config
    customize_s3_config
    customize_lnet_config
    customize_ib_config
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

    if [[ -n "$S3_INSTANCE_NR" ]]; then
        params="$params --s3-instance-nr $S3_INSTANCE_NR"
    fi

    if [[ -n "$params" ]]; then
        $EX_SRV "$SCRIPT_DIR/customize_hare_conf.py \
          -s $HARE_CONFIG -d $HARE_CONFIG $params"
    fi
}

function customize_motr_config()
{
    if [[ -n "$MOTR_CUSTOM_CONF" ]]; then
        $EX_SRV "scp root@$(hostname):$MOTR_CUSTOM_CONF $MOTR_CONFIG"
    fi

    if [[ -n "$MOTR_PARAMS" ]]; then
        local params=""

        for motr_param in $MOTR_PARAMS; do
            params="$params --param $motr_param"
        done

        $EX_SRV "$SCRIPT_DIR/customize_motr_conf.py \
          -s $MOTR_CONFIG -d $MOTR_CONFIG $params"
    fi
}

function customize_haproxy_config()
{
    if [[ -n "$S3_INSTANCE_NR" ]]; then
        $EX_SRV "$SCRIPT_DIR/customize_haproxy_conf.py -s $HAPROXY_CONFIG \
            -d $HAPROXY_CONFIG --s3-instance-nr $S3_INSTANCE_NR"
    fi
}

function customize_s3_config()
{
    if [[ -n "$S3_CUSTOM_CONF" ]]; then
        $EX_SRV "scp root@$(hostname):$S3_CUSTOM_CONF $S3_CONFIG"
    fi

    if [[ -n "$S3_PARAMS" ]]; then
        $EX_SRV "$SCRIPT_DIR/customize_s3_conf.py -s $S3_CONFIG \
            -d $S3_CONFIG $S3_PARAMS"
    fi
}

function customize_lnet_config()
{
    if [[ -n "$LNET_CUSTOM_CONF" ]]; then
        $EX_SRV "scp root@$(hostname):$LNET_CUSTOM_CONF $LNET_CONFIG"
    fi
}

function customize_ib_config()
{
    if [[ -n "$IB_CUSTOM_CONF" ]]; then
        $EX_SRV "scp root@$(hostname):$IB_CUSTOM_CONF $IB_CONFIG"
    fi
}

function apply_configs()
{
    set +e
    $EX_SRV "systemctl stop lnet"
    $EX_SRV "systemctl start lnet"
    $EX_SRV "systemctl restart haproxy"
    set -e
}

function main()
{
    parse_args "$@"
    check_backup_files
    save_original_configs
    customize_configs
    apply_configs
}

main "$@"
exit $?
