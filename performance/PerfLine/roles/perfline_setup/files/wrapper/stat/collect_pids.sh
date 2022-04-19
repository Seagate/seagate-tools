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

function main()
{
    local nodes="$1"
    local out_file="$2"

    echo "" > $out_file

    for srv_node in $(echo $nodes | tr ',' ' '); do
        for app_name in m0d s3server hax; do
            local pids=$(ssh $srv_node "pgrep $app_name")

            for pid in $pids; do
                echo "$srv_node $app_name $pid" >> $out_file
            done

        done
    done

}

main $@
exit $?
