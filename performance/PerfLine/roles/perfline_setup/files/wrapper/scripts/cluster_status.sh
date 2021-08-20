#!/bin/bash

function is_cluster_online() {
    local all_services=$(ssh $1 'hctl status | grep "\s*\[.*\]"')
    local srvc_states=$(echo "$all_services" | grep -E 's3server|ioservice|confd|hax' | awk '{print $1}')
    for state in $srvc_states; do
        if [[ "$state" != "[started]" ]]; then
            return 1
        fi
    done
    return 0
}
