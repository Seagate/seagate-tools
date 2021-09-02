#!/usr/bin/env bash

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
