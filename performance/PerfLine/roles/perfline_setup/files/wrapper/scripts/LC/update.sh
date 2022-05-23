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

SCRIPT_PATH="$(readlink -f "$0")"
SCRIPT_DIR="${SCRIPT_PATH%/*}"

source "$SCRIPT_DIR/../../../perfline.conf"

DOCKER_BUILD_DIR="$ARTIFACTS_DIR/docker_build"
CORTX_SRC_DIR="$DOCKER_BUILD_DIR/cortx"
RPM_DIR="$DOCKER_BUILD_DIR/rpm"
DOCKER_IMAGES_BUILD_TOOLS_DIR="$CORTX_RE_REPO/docker/cortx-deploy"

K8S_SCRIPTS_DIR="$CORTX_K8S_REPO/k8_cortx_cloud"
SOLUTION_FILE="$K8S_SCRIPTS_DIR/solution.yaml"
SOLUTION_FILE_BACKUP="$K8S_SCRIPTS_DIR/.perfline__solution.yaml__backup"

EX_SRV="pdsh -R ssh -S -w $NODES"
PRIMARY_NODE=$(echo "$NODES" | cut -d "," -f1)

BRANCH="main"

PODS=()
SOURCES=()
PATCHED_CORTX_IMAGES=()

function prepare_env() {
    if [ ! -d "$CORTX_SRC_DIR" ]; then
        mkdir -p "$DOCKER_BUILD_DIR"
        pushd "$DOCKER_BUILD_DIR"
        git clone https://github.com/Seagate/cortx --recursive --depth=1
        docker run --rm -v "${CORTX_SRC_DIR}":/cortx-workspace "$CORTX_BUILD_IMAGE" make checkout BRANCH="${BRANCH}"
        popd
    fi
}

function checkout_repo()
{
    local cortx_component="$1"
    local repo="$2"
    local branch="$3"

    if [[ -h "$cortx_component" ]]; then
        # delete the symlink
        rm "$cortx_component"
    elif [[ -d "$cortx_component" ]]; then
        # delete the directory recursively
        rm -rf "$cortx_component"
    fi

    if [[ "$repo" == "http"* ]]; then
        # clone remote git repo
        git clone --recursive "$repo" "$cortx_component"
    elif [[ "$repo" == "/"* ]]; then
        # create a symlink for local repo
        ln -s "$repo" "$cortx_component"
    else
        echo "invlaid format of repo: $repo"
        exit 1
    fi

    pushd "$cortx_component"
    git checkout "$branch"
    popd
}

function checkout() {

    if [[ -z "$SOURCES" ]]; then
        return 0
    fi

    pushd "$CORTX_SRC_DIR"

    for ((i = 0; i < $((${#SOURCES[*]})); i++)); do
        local src_descr=${SOURCES[((i))]}

        local component="cortx-$(echo "$src_descr" | awk '{print $1}')"
        local repo=$(echo "$src_descr" | awk '{print $2}')
        local commit=$(echo "$src_descr" | awk '{print $3}')

        checkout_repo "$component" "$repo" "$commit"
    done

    popd
}

function build_rpms() {
    local repo_3rd_party=""
    local rpmbuild_dir="$DOCKER_BUILD_DIR/rpmbuild"

    # 'Clean' phase
    if [[ -d "$rpmbuild_dir" ]]; then
        rm -rf "$rpmbuild_dir"
    fi

    if [[ -d "$RPM_DIR" ]]; then
        rm -rf "$RPM_DIR"
    fi

    mkdir -p "$rpmbuild_dir"
    mkdir -p "$RPM_DIR/0/cortx_iso"
    # 'Clean' phase end

    # 'Build' phase
    docker run --rm \
        -v "$rpmbuild_dir":/root/rpmbuild \
        -v "$RPM_DIR":/var/artifacts \
        -v "$CORTX_SRC_DIR":/cortx-workspace \
        $CORTX_BUILD_IMAGE sh -c "yum-config-manager --add-repo=$repo_3rd_party \
            && yum --nogpgcheck -y --disablerepo='baseos' --disablerepo='powertools' \
            install libfabric libfabric-devel \
            && make cortx-all-rockylinux-image"
}

function build_image() {
    CONTAINER_ID=$(docker ps | grep "release-packages-server" | awk '{ print $1 }')

    if [[ -n "$CONTAINER_ID" ]]; then
        docker rm -f "$CONTAINER_ID"
    fi

    docker run --rm --name release-packages-server -v "$RPM_DIR/0":/usr/share/nginx/html:ro -d -p 80:80 nginx

    # wait for nginx to start
    sleep 10

    # update 'BUILD' value
    sed -i "s/BUILD:.*/BUILD: \"$TASK_ID\"/" "$RPM_DIR/0/RELEASE.INFO"

    pushd "$DOCKER_IMAGES_BUILD_TOOLS_DIR"
    ./build.sh -p no -b http://$(hostname) -o rockylinux-8.4 -s all -e opensource-ci
    popd
    docker stop release-packages-server
}

function export_docker_images() {

    local nodes="$(echo $NODES | sed "s/$(hostname)//g" | sed "s/^,//" | sed "s/,$//" | sed "s/,,/,/g")"
    local nodes_nr="$(echo \"$nodes\" | tr ',' ' ' | wc -w)"

    if [[ "$nodes_nr" -eq 0 ]]; then
        # there is no other nodes to export
        return 0
    fi

    local pdsh_cmd="pdsh -R ssh -S -w"

    pushd "$DOCKER_BUILD_DIR"

    for image in $@; do

        # check if the image still exists
        docker images --format='{{.Repository}}:{{.Tag}}' | grep "$image" || {
            echo "image $image does not exist. It may be caused by low free disk space"
            return 1
        }

        # save image as a .tar file
        local img_location="$(pwd)"
        local filename="$image.tar"
        local filepath="$img_location/$filename"
        docker save --output "$filename" "$image" || return 1

        local failed=""

        # copy/load on the nodes
        $pdsh_cmd "$nodes" "mkdir -p \"$img_location\" && scp \"$(hostname):$filepath\" \"$filepath\"" && \
        $pdsh_cmd "$nodes" "docker load --input \"$filepath\"" || {
            failed="true"
        }

        # remove tar files
        $pdsh_cmd "$nodes" "if [[ -f \"$filepath\" ]]; then rm -f \"$filepath\"; fi;"
        rm -f "$filepath"

        if [[ -n "$failed" ]]; then
            return 1
        fi
    done

    popd
}

function destroy_cluster() {
    echo "Destroy LC cluster"
    ssh "$PRIMARY_NODE" "cd $K8S_SCRIPTS_DIR && ./destroy-cortx-cloud.sh"
}

function pre_req_deployment() {
    echo "Run pre-requisite for docker image deployment"
    $EX_SRV "cd $K8S_SCRIPTS_DIR && ./prereq-deploy-cortx-cloud.sh $DISK"
}

function save_original_solution_config()
{
    # TODO: this function should be a part of
    # separate 'save_orig_configs.sh' script in the
    # future version of PerfLine. It is required because
    # config files changing might be done during both
    # 'build and deploy' and 'update configs' phase.

    cp -f "$SOLUTION_FILE" "$SOLUTION_FILE_BACKUP"
}

function update_images_in_solution_yaml()
{
    save_original_solution_config
    local args=""

    for docker_img in $@; do
        local docker_img_type=$(echo "$docker_img" | awk -F ':' '{print $1}' | awk -F "/" '{print $NF}')
        args="$args --image $docker_img_type=$docker_img"
    done

    ssh "$PRIMARY_NODE" "$SCRIPT_DIR/build_deploy/update_solution_yaml.py \
        --src-file $SOLUTION_FILE --dst-file $SOLUTION_FILE $args"
}

function update_pods_in_solution_yaml()
{
    save_original_solution_config
    local pod_args=""

    for pod_descr in $@; do
        pod_args="$pod_args --pod $pod_descr"
    done

    ssh "$PRIMARY_NODE" "$SCRIPT_DIR/build_deploy/update_solution_yaml.py \
        --src-file $SOLUTION_FILE --dst-file $SOLUTION_FILE $pod_args"
}

function pull_docker_images()
{
    for image in $@; do
        $EX_SRV docker pull "$image"
    done
}

function patch_cortx_image()
{
    local base_img="$1"
    local motr_repo="$2"
    local hare_repo="$3"

    # find an image in the list
    local patched_img_name=""

    for ((j = 0; j < $((${#PATCHED_CORTX_IMAGES[*]})); j++)); do
        cortx_img_descr=${PATCHED_CORTX_IMAGES[((j))]}

        local img=$(echo "$cortx_img_descr" | awk '{print $1}')

        if [[ "$base_img" != "$img" ]]; then
            continue
        fi

        local repo=$(echo "$cortx_img_descr" | awk '{print $2}')

        if [[ "$motr_repo" != "$repo" ]]; then
            continue
        fi

        repo=$(echo "$cortx_img_descr" | awk '{print $3}')

        if [[ "$hare_repo" != "$repo" ]]; then
            continue
        fi

        patched_img_name=$(echo "$cortx_img_descr" | awk '{print $4}')
        break
    done

    if [[ -n "$patched_img_name" ]]; then
        NEW_DOCKER_IMG="$patched_img_name"
        return
    fi

    # patch a new cortx image
    local new_img="${docker_img}_perfline_$(mktemp -u XXXXXXX)_$TASK_ID"
    local args=()

    if [[ "$motr_repo" != "none" ]]; then
        args+=("--motr-repo" "$motr_repo")
    fi

    if [[ "$hare_repo" != "none" ]]; then
        args+=("--hare-repo" "$hare_repo")
    fi

    "$SCRIPT_DIR"/build_deploy/patch_cortx_image.sh \
        --base-image "$base_img" --new-image "$new_img" \
        --container tmp_perfline_"$TASK_ID" "${args[@]}"

    # save description of new cortx image
    PATCHED_CORTX_IMAGES+=("$base_img $motr_repo $hare_repo $new_img")

    NEW_DOCKER_IMG="$new_img"
}

function deploy_pre_built_images()
{
    local images=""
    local args=""

    for ((i = 0; i < $((${#PODS[*]})); i++)); do
        pod=${PODS[((i))]}

        local pod_name=$(echo "$pod" | awk '{print $1}')
        local docker_img=$(echo "$pod" | awk '{print $2}')

        local fields_nr=$(echo "$pod" | awk '{print NF}')

        # check if patching is required
        if [[ "$fields_nr" -gt 2 ]]; then

            local motr_repo="none"
            local hare_repo="none"

            for patch_descr in $(echo "$pod" | cut -f 3- -d ' '); do
                if echo "$patch_descr" | grep -P '^patch_motr::' > /dev/null; then
                    motr_repo=$(echo "$patch_descr" | sed 's/patch_motr:://')
                elif echo "$patch_descr" | grep -P '^patch_hare::' > /dev/null; then
                    hare_repo=$(echo "$patch_descr" | sed 's/patch_hare:://')
                fi
            done;

            NEW_DOCKER_IMG=""
            patch_cortx_image "$docker_img" "$motr_repo" "$hare_repo"

            if [[ -z "$NEW_DOCKER_IMG" ]]; then
                echo 'Patching of Cortx docker image failed'
                exit 1
            fi

            args="$args $pod_name=$NEW_DOCKER_IMG"

        else
            images="$images $docker_img"
            args="$args $pod_name=$docker_img"
        fi
    done

    pull_docker_images $images
    update_pods_in_solution_yaml $args
    # pre_req_deployment
}


function build_images_from_sources()
{
    prepare_env
    checkout
    build_rpms
    build_image
}

function build_and_deploy_images()
{
    build_images_from_sources

    local images=$(docker images --format='{{.Repository}}:{{.Tag}}' | grep "$TASK_ID")

    export_docker_images $images
    update_images_in_solution_yaml $images
}


function main() {
    destroy_cluster

    if [[ -n "$PODS" ]]; then
        deploy_pre_built_images
    else
        build_and_deploy_images
    fi
}

function validate() {
    if [[ -z "$TASK_ID" ]]; then
        echo "--task-id argument is required"
        exit 1
    fi

    if [[ -z "$PODS" && -z "$SOURCES" ]]; then
        echo '--pod/--source arguments are required'
        exit 1
    fi
}

function parse_patch_arg()
{
    local param="$1"
    local val="$2"

    if [[ "$param" == "--patch-motr" ]]; then
        PATCH_ARG="patch_motr::$val"
    elif [[ "$param" == "--patch-hare" ]]; then
        PATCH_ARG="patch_hare::$val"
    else
        return 1
    fi

    return 0
}

while [[ $# -gt 0 ]]; do
    case $1 in
        --pod)
            pod_descr="$2 $3"
            shift
            shift
            while true; do
                PATCH_ARG=""
                if parse_patch_arg "$2" "$3"; then
                    pod_descr="$pod_descr $PATCH_ARG"
                    shift
                    shift
                else
                    break
                fi
            done
            PODS+=("$pod_descr")
            ;;
        --source)
            SOURCES+=("$2 $3 $4")
            shift
            shift
            shift
            ;;
        --task-id)
            TASK_ID="$2"
            shift
            ;;
        --help)
            echo -e "Usage: bash update.sh --source motr motr_repo motr_commit\n"
            exit 0
            ;;
        *)
            echo -e "Invalid option: $1\nUse --help option"
            exit 1
             ;;
    esac
    shift
done

validate
main "$@"
