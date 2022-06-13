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


# public interface

RGW_ARTIFACTS_DIR="rgw"

function create_s3_account()
{
    # Currently accesskey/secretkey are hardcoded in the cortx-k8s framework (v0.1.0)
    ssh "$PRIMARY_NODE" 'echo AccountId = 000, CanonicalId = 000, RootUserName = 000, AccessKeyId = sgiamadmin, SecretKey = ldapadmin > s3user.txt'

    # configure aws utility
    ssh "$PRIMARY_NODE" "$SCRIPT_DIR/../../s3account/lc_setup_aws.sh"
}

function save_s3app_configs()
{
    mkdir -p $RGW_ARTIFACTS_DIR
    pushd $RGW_ARTIFACTS_DIR
    save_rgw_configs
    popd
}

function save_s3app_artifacts()
{
    mkdir -p $RGW_ARTIFACTS_DIR
    pushd $RGW_ARTIFACTS_DIR
    save_rgw_artifacts
    popd
}

# implementation

function save_rgw_configs() {
    local config_dir="configs"

    local pod
    local containers
    local rgw_mapping
    local log_dir
    local trace_dir

    mkdir -p $config_dir
    pushd $config_dir

    for srv in $(echo "$NODES" | tr ',' ' '); do
        pod=$(ssh "$PRIMARY_NODE" "kubectl get pod -o wide" | grep "$srv" | grep "$CORTX_SERVER_POD_PREFIX" | awk '{print $1}')
        containers=$(ssh "$PRIMARY_NODE" "kubectl get pods $pod -o jsonpath='{.spec.containers[*].name}'" | tr ' ' '\n' | grep rgw)
        mkdir -p "$srv"
        pushd "$srv"

        for cont in $containers ; do
            mkdir -p "$cont"
            pushd "$cont"

            # Copy config
            local conf_file=$(ssh "$PRIMARY_NODE" "kubectl exec $pod -c $cont -- ps auxww" | grep radosgw | tr ' ' '\n' | grep -m 1 '\.conf$')

            if [[ -n "$conf_file" ]]; then
                local conf_filename=$(echo "$conf_file" | awk -F "/" '{print $NF}')
                ssh "$PRIMARY_NODE" "kubectl exec $pod -c $cont -- cat $conf_file" > "$conf_filename"

                local log_file=$(cat "$conf_filename" | grep 'log file' | sed 's/log file\s*=\s*//' | head -1)
                log_dir="${log_file%/*}"
                trace_dir="$log_dir/motr_trace_files"
                rgw_mapping="${srv} ${pod} ${cont} FID ${trace_dir} ADDB_DIR ${log_dir}\n${rgw_mapping}"
            fi

            popd		# $cont
        done

        popd			# $srv
    done

    popd			# $config_dir

    printf "$rgw_mapping" > rgw_map
}

function save_rgw_artifacts() {
    local log_dir="log"
    local m0trace_dir="m0trace"

    start_docker_container

    mkdir -p $log_dir
    pushd $log_dir
    save_rgw_logs
    popd

    if [[ -n $M0TRACE_FILES ]]; then
        mkdir -p $m0trace_dir
        pushd $m0trace_dir
        save_rgw_traces
        popd
    fi

    stop_docker_container
}

function save_rgw_logs() {
    local hostname
    local pod
    local cont
    local serv
    local trace
    local addb
    local lines_n
    local log_dir

    lines_n=$(cat ../rgw_map | wc -l)
    for i in $(seq 1 "$lines_n") ; do
        read hostname pod cont serv trace addb log <<< $(awk "NR==$i" ../rgw_map)
        mkdir -p "$hostname"
        pushd "$hostname"

        log_dir=$(echo "$log" | sed 's|/etc/cortx/||')
        log_dir="$LOCAL_MOUNT_POINT/var/$log_dir"

        if [[ -d "$log_dir" ]]; then
            cp "$log_dir"/*.log ./
        fi

        popd
    done
}

function save_rgw_traces()
{
    local hostname
    local pod
    local cont
    local serv
    local trace
    local addb
    local log
    local lines_n
    local files

    set +e
    lines_n=$(cat ../rgw_map | wc -l)
    for i in $(seq 1 "$lines_n") ; do
        read hostname pod cont serv trace addb log <<< $(awk "NR==$i" ../rgw_map)

        local trace_dir=$(echo "$trace" | sed 's|/etc/cortx/||')
        trace_dir="/share/var/$trace_dir"

        files=$( ssh "$PRIMARY_NODE" "docker exec $DOCKER_CONTAINER_NAME ls -1 $trace_dir" | grep m0trace | grep -v txt)
        for file in $files; do
            ssh "$PRIMARY_NODE" "docker exec $DOCKER_CONTAINER_NAME m0trace -i $trace_dir/$file -o $trace_dir/$file.txt"
        done
    done

    # Copy traces to results folder
    for i in $(seq 1 "$lines_n") ; do
        read hostname pod cont serv trace addb log <<< $(awk "NR==$i" ../rgw_map)
        mkdir -p "$hostname"
        pushd "$hostname"

        local trace_dir=$(echo "$trace" | sed 's|/etc/cortx/||')
        trace_dir="$LOCAL_MOUNT_POINT/var/$trace_dir"

        if [[ -d "$trace_dir" ]]; then
            cp "$trace_dir"/m0trace.*.txt ./
        fi

        popd
    done
    set -e
}
