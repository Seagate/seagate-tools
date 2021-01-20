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
