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
source "$SCRIPT_DIR/../../../perfline.conf"

# TODO: move it to some constants.sh file
CUSTOM_DOCKER_IMAGE_TAG_PREFIX="perfline_"


function parse_params()
{
    while [[ $# -gt 0 ]]; do
        case $1 in
            --task-id)
                TASK_ID="$2"
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

function remove_custom_docker_image()
{
    local docker_image_tag="${CUSTOM_DOCKER_IMAGE_TAG_PREFIX}${TASK_ID}"
    pdsh -R ssh -S -w $NODES $SCRIPT_DIR/remove_tmp_docker_image.sh $docker_image_tag
}

function main()
{
    parse_params $@
    remove_custom_docker_image
}

main $@
exit $?
