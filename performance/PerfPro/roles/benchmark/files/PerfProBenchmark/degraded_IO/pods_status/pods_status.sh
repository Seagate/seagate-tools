#!/bin/bash
#
# Seagate-tools: PerfPro
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

solution_yaml=${1:-'/root/PerfProBenchmark/degraded_read/pods_status/solution.yaml'}
pwd
ls

# Check if the file exists
if [ ! -f "$solution_yaml" ]
then
    echo "ERROR: $solution_yaml does not exist"
    exit 1
fi


function parseSolution()
{
    echo "$(/root/PerfProBenchmark/degraded_read/pods_status//parse_yaml.sh "$solution_yaml" "$1")"
}

namespace=$(parseSolution 'solution.namespace')
namespace=$(echo "$namespace" | cut -f2 -d'>')


# Check pods
num_nodes=3
count=0
while IFS= read -r line; do
    IFS=" " read -r -a status <<< "$line"
    IFS="/" read -r -a ready_status <<< "${status[1]}"
    if [[ "${status[0]}" != "" ]]; then
        if [[ ! "${status[2]}" != "Running" || "${ready_status[0]}" != "${ready_status[1]}" ]]; then
            count=$((count+1))
        fi
    fi
done <<< "$(kubectl get pods --namespace="$namespace" | grep 'cortx-data-')"

if [[ $num_nodes -eq $count ]]; then
    printf "PASSED\n"
else
    printf "FAILED\n"
fi


