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
    if [[ "$#" -ne "1" ]]; then
        echo "expected number of s3 listeners wasn't specified"
        return 1
    fi

    local s3_instances_nr="$1"
    echo "waiting for s3server tcp listeners"

    while true; do
        local s3_ports=$(netstat -tlpn | grep s3server | grep -E '0.0.0.0:[0-9]+' | wc -l)
        if [[ "$s3_ports" -ge "$s3_instances_nr" ]]; then
            echo "found $s3_ports listeners"
            break
        fi
        sleep 5
    done
}

main $@
exit $?
