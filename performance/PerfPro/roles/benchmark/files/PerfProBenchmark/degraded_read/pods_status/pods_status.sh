#!/bin/bash

solution_yaml=${1:-'/root/PerfProBenchmark/degraded_read/pods_status/solution.yaml'}
pwd
ls

# Check if the file exists
if [ ! -f $solution_yaml ]
then
    echo "ERROR: $solution_yaml does not exist"
    exit 1
fi


function parseSolution()
{
    echo "$(/root/PerfProBenchmark/degraded_read/pods_status//parse_yaml.sh $solution_yaml $1)"
}

namespace=$(parseSolution 'solution.namespace')
namespace=$(echo $namespace | cut -f2 -d'>')


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
done <<< "$(kubectl get pods --namespace=$namespace | grep 'cortx-data-')"

if [[ $num_nodes -eq $count ]]; then
    printf "PASSED\n"
else
    printf "FAILED\n"
fi


