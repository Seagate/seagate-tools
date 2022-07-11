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

    local pods
    local pod
    local containers
    local rgw_mapping
    local log_dir
    local trace_dir
    local addb_dir

    mkdir -p $config_dir
    pushd $config_dir

    for srv in $(echo "$NODES" | tr ',' ' '); do
        mkdir -p "$srv"
        pushd "$srv"

        pods=$(ssh "$PRIMARY_NODE" "kubectl get pods -n $NAMESPACE -o wide" | grep "$srv" | grep "$CORTX_SERVER_POD_PREFIX" | awk '{print $1}')

        for pod in $pods; do

            containers=$(ssh "$PRIMARY_NODE" "kubectl get pods -n $NAMESPACE $pod -o jsonpath='{.spec.containers[*].name}'" | tr ' ' '\n' | grep rgw)

            for cont in $containers ; do
                mkdir -p "${pod}_${cont}"
                pushd "${pod}_${cont}"

                # Copy config
                local conf_file=$(ssh "$PRIMARY_NODE" "kubectl exec -n $NAMESPACE $pod -c $cont -- ps auxww" | grep radosgw | tr ' ' '\n' | grep -m 1 '\.conf$')

                if [[ -n "$conf_file" ]]; then
                    local conf_filename=$(echo "$conf_file" | awk -F "/" '{print $NF}')
                    ssh "$PRIMARY_NODE" "kubectl exec -n $NAMESPACE $pod -c $cont -- cat $conf_file" > "$conf_filename"

                    local log_file=$(cat "$conf_filename" | grep 'log file' | sed 's/log file\s*=\s*//' | head -1)
                    log_dir="${log_file%/*}"
                    trace_dir="$log_dir/motr_trace_files"

                    # TODO: currently RGW stores addb files in the 'rgw_debug' directory.
                    # It will be changed in the future. Once it is done below code will
                    # be changed accordingly.
                    addb_dir="$log_dir/rgw_debug"
                    rgw_mapping="${srv} ${pod} ${cont} FID ${trace_dir} ${addb_dir} ${log_dir}\n${rgw_mapping}"
                fi

                popd		# $cont
            done
        done

        popd			# $srv
    done

    popd			# $config_dir

    printf "$rgw_mapping" > rgw_map
}

function save_rgw_artifacts() {
    local log_dir="log"
    local m0trace_dir="m0trace"
    local dumps_dir="dumps"

    start_docker_container "cortxserver"

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

    if [[ -n $ADDB_DUMPS ]]; then
        mkdir -p $dumps_dir
        pushd $dumps_dir
        save_rgw_addb
        fiter_addb_dumps "rgw"
        generate_rgw_m0play
        popd			# $dumps_dir
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

function save_rgw_addb() {
    local pod
    local cont
    local serv
    local trace
    local addb_dir
    local lines_n
    local pid
    local addb_stob
    local addb_plugin_dir
    local addb_plugin

    # Temporary solution for cortx-rgw images that don't include rgw_addb_plugin.so
    # Will be removed in the future
    addb_plugin_dir="/opt/seagate/cortx/rgw/bin"
    addb_plugin="$addb_plugin_dir/rgw_addb_plugin.so"

    ssh "$PRIMARY_NODE" "docker exec $DOCKER_CONTAINER_NAME sh -c \"[ -f $addb_plugin ]\"" || {
        echo "copy RGW addb plugin in the container"
        ssh "$PRIMARY_NODE" "docker exec $DOCKER_CONTAINER_NAME sh -c \"mkdir -p $addb_plugin_dir\""
        ssh "$PRIMARY_NODE" "docker cp $PERFLINE_DIR/bin/rgw_addb_plugin.so $DOCKER_CONTAINER_NAME:$addb_plugin"
    }

    set +e

    pid=$RGW_INIT_PID
    lines_n=$(cat ../rgw_map | wc -l)

    for i in $(seq 1 "$lines_n") ; do
        read hostname pod cont serv trace addb_dir log <<< $(awk "NR==$i" ../rgw_map)

        addb_dir=$(echo "$addb_dir" | sed 's|/etc/cortx/|/share/var/|')
        stobs=$( ssh "$PRIMARY_NODE" "docker exec $DOCKER_CONTAINER_NAME ls -1 $addb_dir" | grep addb_)

        for st in $stobs; do
            addb_stob="$addb_dir/$st/o/100000000000000:2"
            ssh "$PRIMARY_NODE" "docker exec $DOCKER_CONTAINER_NAME /bin/bash -c \"m0addb2dump -f -p $addb_plugin -- $addb_stob\"" > dumpc_"${pid}".txt &
            ((pid=pid+1))
        done
    done

    wait
    set -e
}

function generate_rgw_m0play()
{
    if ls dumpc* &> /dev/null; then
        "$TOOLS_DIR"/addb2db_multiprocess.sh --dumps ./dumpc*
        mv m0play.db m0play.rgw.db
    fi
}
