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

SCRIPT_NAME=`echo $0 | awk -F "/" '{print $NF}'`
SCRIPT_PATH="$(readlink -f $0)"
SCRIPT_DIR="${SCRIPT_PATH%/*}"


function create_tmp_container()
{
    ssh $PRIMARY_NODE "docker run --rm -d --name $TMP_CONTAINER_NAME $BASE_IMAGE sleep infinity" || return 1
}

function update_files()
{
    local tmp_dir="/tmp/perfline_tmp_files"

    ssh $PRIMARY_NODE "if [[ -d \"$tmp_dir\" ]]; then rm -rf \"$tmp_dir\"; fi"
    ssh $PRIMARY_NODE "mkdir $tmp_dir"

    if [[ -n "$MOTR_PARAMS" ]]; then
        update_motr_config $tmp_dir || return 1
    fi

    ssh $PRIMARY_NODE "rm -rf \"$tmp_dir\""
}

function update_motr_config()
{
    local tmp_dir="$1"

    ssh $PRIMARY_NODE "docker cp $TMP_CONTAINER_NAME:/etc/sysconfig/motr $tmp_dir/motr" || return 1
    ssh $PRIMARY_NODE "docker cp $TMP_CONTAINER_NAME:/opt/seagate/cortx/motr/conf/motr.conf $tmp_dir/motr.conf" || return 1

    local params=""

    for motr_param in $MOTR_PARAMS; do
        params="$params --param $motr_param"

        # remove param from motr.conf file
        local param_name=$(echo $motr_param | awk -F '=' '{print $1}')
        ssh $PRIMARY_NODE "sed -i '/$param_name/d' $tmp_dir/motr.conf"
    done

    # update /etc/sysconfig/motr values
    ssh $PRIMARY_NODE "$SCRIPT_DIR/../conf_customization/customize_motr_conf.py \
      -s $tmp_dir/motr -d $tmp_dir/motr $params" || return 1

    ssh $PRIMARY_NODE "docker cp $tmp_dir/motr $TMP_CONTAINER_NAME:/etc/sysconfig/motr"
    ssh $PRIMARY_NODE "docker cp $tmp_dir/motr.conf $TMP_CONTAINER_NAME:/opt/seagate/cortx/motr/conf/motr.conf"
}

function commit_image()
{
    local cont_id=$(ssh $PRIMARY_NODE docker ps | grep $TMP_CONTAINER_NAME | awk '{print $1}')
    ssh $PRIMARY_NODE "docker commit $cont_id $NEW_IMAGE" || return 1
}

function stop_tmp_container()
{
    ssh $PRIMARY_NODE "docker stop $TMP_CONTAINER_NAME" || return 1
}

function save_image()
{
    ssh $PRIMARY_NODE "docker save --output $NEW_IMAGE_TAR $NEW_IMAGE" || return 1
}

function copy_to_nodes()
{
    pdsh -S -w $OTHER_NODES "scp $PRIMARY_NODE:$NEW_IMAGE_TAR $NEW_IMAGE_TAR" || return 1
}

function load_image_on_nodes()
{
    pdsh -S -w $OTHER_NODES "docker load --input $NEW_IMAGE_TAR" || return 1
}

function remove_image_tar()
{
    pdsh -S -w $NODES "rm -f $NEW_IMAGE_TAR" || return 1
}

function parse_params()
{
    while [[ $# -gt 0 ]]; do
        case $1 in
            -n|--nodes)
                NODES="$2"
                shift
                ;;
            --base-image)
                BASE_IMAGE="$2"
                shift
                ;;
            --image)
                NEW_IMAGE="$2"
                shift
                ;;
            --tmp-container)
                TMP_CONTAINER_NAME="$2"
                shift
                ;;
            --motr-param)
                MOTR_PARAMS="$MOTR_PARAMS $2"
                shift
                ;;
            *)
                echo "unsupported parameter $1"
                exit 1
                ;;
        esac

        shift
    done
}

function check_params()
{
    if [ -z "$NODES" ] || [ -z "$BASE_IMAGE" ] || [ -z "$NEW_IMAGE" ] || [ -z "$TMP_CONTAINER_NAME" ]; then
        echo "missed required parameters"
        exit 1
    fi
}

function main()
{
    parse_params $@
    check_params
    local primary_other=$(echo $NODES | sed 's/,/ /')
    local PRIMARY_NODE=$(echo $primary_other | awk '{print $1}')
    local OTHER_NODES=$(echo $primary_other | awk '{print $2}')

    NEW_IMAGE_TAR="/root/cortx-all_perfline_tmp.tar"

    create_tmp_container && \
    update_files && \
    commit_image && \
    stop_tmp_container && \
    save_image && \
    copy_to_nodes && \
    load_image_on_nodes && \
    remove_image_tar || {
        # error handler
        cleanup
        return 1
    }
}

function cleanup()
{
    ssh $PRIMARY_NODE "docker ps | grep $TMP_CONTAINER_NAME" && stop_tmp_container
    remove_image_tar
}

main $@
exit $?
