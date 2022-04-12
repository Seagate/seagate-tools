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

SCRIPT_NAME=$(echo "$0" | awk -F "/" '{print $NF}')
SCRIPT_PATH="$(readlink -f "$0")"
SCRIPT_DIR="${SCRIPT_PATH%/*}"

PERFLINE_DIR="$SCRIPT_DIR/../../.."
DOCKER_DIR="$PERFLINE_DIR/docker"
CORTX_DIR="$DOCKER_DIR/cortx"
RPM_DIR="$PERFLINE_DIR/rpm"
BUILD_SCRIPT_DIR="$CORTX_DIR/doc/community-build/docker/cortx-all/"

DOCKER_ARTIFACTS_DIR="/var/artifacts"
BUILD_DIR="$DOCKER_ARTIFACTS_DIR/0"

source "$SCRIPT_DIR/../../../perfline.conf"
K8S_SCRIPTS_DIR="$CORTX_K8S_REPO/k8_cortx_cloud"
EX_SRV="pdsh -S -w $NODES"
PRIMARY_NODE=$(echo "$NODES" | cut -d "," -f1)

MOTR_BRANCH=
S3_BRANCH=
HARE_BRANCH=
UTILS_BRANCH=
IMAGE=
BRANCH="kubernetes"

function prepare_env() {
    local status=

    set +e
    systemctl status docker
    status=$?
    set -e

    if [ $status -ne 0 ]; then
        systemctl restart docker
        systemctl enable docker
    fi

    set +e
    systemctl status docker
    status=$?
    set -e

    if [ $status -ne 0 ]; then
        echo "Docker failure, exit"
        exit 1
    fi

    if [ ! -d "$CORTX_DIR" ]; then
        mkdir -p "$DOCKER_DIR"
        pushd "$DOCKER_DIR"
        git clone https://github.com/Seagate/cortx --recursive --depth=1
        docker run --rm -v "${CORTX_DIR}":/cortx-workspace ghcr.io/seagate/cortx-build:centos-7.9.2009 make checkout BRANCH=${BRANCH}
        popd
    fi
}


function checkout() {
    if [ -n "${MOTR_BRANCH}" -a -n "${MOTR_REPO}" ]; then
       cd "$CORTX_DIR"
       rm -rf ./cortx-motr || true
       git clone --recursive "$MOTR_REPO" cortx-motr
       cd "$CORTX_DIR"/cortx-motr
       git fetch --all
       git checkout "$MOTR_BRANCH"
    fi

    if [ -n "${S3_BRANCH}" -a -n "${S3_REPO}" ]; then
       cd "$CORTX_DIR"
       rm -rf ./cortx-s3server || true
       git clone --recursive "$S3_REPO" cortx-s3server
       cd "$CORTX_DIR"/cortx-s3server
       git fetch --all
       git checkout "$S3_BRANCH"
    fi

    if [ -n "${HARE_BRANCH}" -a -n "${HARE_REPO}" ]; then
       cd "$CORTX_DIR"
       rm -rf ./cortx-hare || true
       git clone --recursive "$HARE_REPO" cortx-hare
       cd "$CORTX_DIR"/cortx-hare
       git fetch --all
       git checkout "$HARE_BRANCH"
    fi

    if [ -n "${UTILS_BRANCH}" -a -n "${UTILS_REPO}" ]; then
       cd "$CORTX_DIR"
       rm -rf ./cortx-utils || true
       git clone --recursive "$UTILS_REPO" cortx-utils
       cd "$CORTX_DIR"/cortx-utils
       git fetch --all
       git checkout "$UTILS_BRANCH"
    fi
}

function build_rpms() {
    mkdir -p $BUILD_DIR/
    docker run --rm -v $DOCKER_ARTIFACTS_DIR:$DOCKER_ARTIFACTS_DIR -v "${CORTX_DIR}":/cortx-workspace ghcr.io/seagate/cortx-build:centos-7.9.2009 make clean cortx-all-image
}

function build_image() {

    CONTAINER_ID=$(docker ps | grep "release-packages-server" | awk '{ print $1 }')
    if [[ -n $CONTAINER_ID ]];
    then
        docker rm -f "$CONTAINER_ID"
    fi
    docker run --rm --name release-packages-server -v $BUILD_DIR/:/usr/share/nginx/html:ro -d -p 80:80 nginx
    pushd "$BUILD_SCRIPT_DIR"
    ./build.sh -b http://$(hostname)
    popd
    docker stop release-packages-server
}

function export_docker_image() {
    IMAGE=$(docker images --format='{{.Repository}}:{{.Tag}} {{.CreatedAt}}' cortx-all | awk '{ print $1 }')
    docker save --output cortx-all.tar "$IMAGE"
    for srv in $(echo "$NODES" | tr ',' ' '); do
            scp cortx-all.tar "$srv":/tmp/ &
    done
    wait
}

function load_new_docker_image() {
    echo "Load cotrx-all docker image on all nodes"
    pdsh -S -w "$NODES" 'docker load -i /tmp/cortx-all.tar'
}

function remove_local_tar_docker_image() {
    echo "Remove cotrx-all.tar docker image from all nodes"
    pdsh -S -w "$NODES" 'rm -f /tmp/cortx-all.tar'
}

function destroy_cluster() {
    echo "Destroy LC cluster"
    ssh "$PRIMARY_NODE" "cd $K8S_SCRIPTS_DIR && ./destroy-cortx-cloud.sh"
}

function deploy_cluster() {
    echo "Deploy LC cluster"
    ssh "$PRIMARY_NODE" "cd $K8S_SCRIPTS_DIR && ./deploy-cortx-cloud.sh"
}

function log_docker_image_version() {
    echo "Docker Image Version"
    set +e
    pdsh -S -w "$NODES" 'docker images | grep "cortx-all"'
    set -e
}

function pre_req_deployment() {
    echo "Run pre-requisite for docker image deployment"
    pdsh -S -w "$NODES" "cd $K8S_SCRIPTS_DIR && ./prereq-deploy-cortx-cloud.sh $DISK"

}

function install_custom_docker_image() {
    pdsh -S -w "$NODES" "docker pull $IMAGE"
}

function docker_image_cleanups() {
    for NODE in ${NODES//,/ }
    do
        image_id=$(ssh "$NODE" "docker images | grep cortx-all" | awk '{ print $3 }')
        echo "image_ids: ${image_id[@]}"
        if [[ -n "$image_id" ]];
        then
            for id in "${image_id[@]}"
            do
               ssh "$NODE" "docker rmi $id"
            done
        else
            echo "$NODE : docker images not found"
        fi
    done
    pdsh -S -w "$NODES" "rm -rf /mnt/fs-local-volume/*"

}

function update_solution_file() {
    output=$(python3  <<END
import yaml
import sys
fname = "$K8S_SCRIPTS_DIR/solution.yaml"

with open(fname, 'r') as f:
    data = yaml.safe_load(f)
data['solution']['images']['cortxcontrolprov'] = "$IMAGE"
data['solution']['images']['cortxcontrol'] = "$IMAGE"
data['solution']['images']['cortxdataprov'] = "$IMAGE"
data['solution']['images']['cortxdata'] = "$IMAGE"

with open(fname, 'w') as yaml_file:
    yaml_file.write( yaml.dump(data, sort_keys = False))

print("successfully updated solution.yaml")
END
)

echo "$output"

}

function main() {
    echo "$@"
    destroy_cluster
    log_docker_image_version

    if [[ -n "$IMAGE" ]]; then
        update_solution_file
        docker_image_cleanups
        install_custom_docker_image
    else
        prepare_env
        checkout
        build_rpms
        build_image
        export_docker_image
        docker_image_cleanups
        load_new_docker_image
        update_solution_file
    fi

    log_docker_image_version
    pre_req_deployment
    deploy_cluster
    remove_local_tar_docker_image
}

function validate() {
    local leave=

    if [[ -z "$IMAGE" ]]; then
       if [[ -z "$MOTR_BRANCH" ]]; then
           echo "Motr branch is not specified"
           leave="1"
       fi

       if [[ -z "$S3_BRANCH" ]]; then
           echo "S3 server branch is not specified"
           leave="1"
       fi

       if [[ -z "$HARE_BRANCH" ]]; then
           echo "Hare branch is not specified"
           leave="1"
       fi
    fi

    if [[ -z "$NODES" ]]; then
       echo "Docker Images are not specified"
       leave="1"
    fi

    if [[ -n $leave ]]; then
        exit 1
    fi

}

function check_arg_count() {
    [[ $# -gt 2 ]] || {
        echo -e "Incorrect use of the option $1\nUse --help option"
        exit 1
    }
}

echo "parameters: $@"

while [[ $# -gt 0 ]]; do
    case $1 in
        -m|--motr_id)
            check_arg_count "$1" "$2" "$3"
            MOTR_REPO=$2
            MOTR_BRANCH=$3
            shift
            shift
            ;;
        -h|--hare_id)
            check_arg_count "$1" "$2" "$3"
            HARE_REPO=$2
            HARE_BRANCH=$3
            shift
            shift
            ;;
            -s|--s3_id)
            check_arg_count "$1" "$2" "$3"
            S3_REPO=$2
            S3_BRANCH=$3
            shift
            shift
            ;;
            -u|--utils_id)
            check_arg_count "$1" "$2" "$3"
            UTILS_REPO=$2
            UTILS_BRANCH=$3
            shift
            shift
            ;;
            --nodes)
            NODES=$2
            EX_SRV="pdsh -S -w $NODES"
            shift
            ;;
            --update-resource)
            IMAGE=$2
            shift
            ;;
            --help)
                echo -e "Usage: bash update.sh --motr_id a1b2d3e --s3_id bbccdde --hare_id abcdef1\n"
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
