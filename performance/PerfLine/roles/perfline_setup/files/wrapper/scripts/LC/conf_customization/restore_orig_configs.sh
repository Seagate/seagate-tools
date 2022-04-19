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

source "$SCRIPT_DIR/../../../../perfline.conf"

SOLUTION_CONFIG="$CORTX_K8S_REPO/k8_cortx_cloud/solution.yaml"
SOLUTION_CONFIG_BACKUP="$CORTX_K8S_REPO/k8_cortx_cloud/.perfline__solution.yaml__backup"

function restore_original_solution_config()
{
    if [[ -e $SOLUTION_CONFIG_BACKUP ]]; then
        mv -f $SOLUTION_CONFIG_BACKUP $SOLUTION_CONFIG
    fi
}

function main()
{
    restore_original_solution_config
}

main "$@"
exit $?
