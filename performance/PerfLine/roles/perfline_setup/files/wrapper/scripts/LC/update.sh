#!/bin/bash

set -e
set -x

SCRIPT_NAME=`echo $0 | awk -F "/" '{print $NF}'`
SCRIPT_PATH="$(readlink -f $0)"
SCRIPT_DIR="${SCRIPT_PATH%/*}"

PERFLINE_DIR="$SCRIPT_DIR/../.."
source "$SCRIPT_DIR/../../../perfline.conf"
K8S_SCRIPTS_DIR="$CORTX_K8S_REPO/k8_cortx_cloud"
EX_SRV="pdsh -S -w $NODES"
PRIMARY_NODE=$(echo "$NODES" | cut -d "," -f1)


function destroy_cluster() {
    echo "Destroy LC cluster"
    ssh $PRIMARY_NODE "cd $K8S_SCRIPTS_DIR && ./destroy-cortx-cloud.sh"
}

function deploy_cluster() {
    echo "Deploy LC cluster"
    ssh $PRIMARY_NODE "cd $K8S_SCRIPTS_DIR && ./deploy-cortx-cloud.sh"
}

function log_docker_image_version() {
    echo "Docker Image Version"
    set +e
    pdsh -S -w $NODES 'docker images | grep "cortx-all"'
    set -e
}

function install_custom_docker_image() {
    pdsh -S -w $NODES "docker pull $IMAGE"
}

function docker_image_cleanups() {
    for NODE in ${NODES//,/ }
    do
        image_id=($(ssh $NODE "docker images | grep cortx-all" | awk '{ print $3 }'))
        echo "image_ids: ${image_id[@]}"
        if [[ -n "$image_id" ]];
        then
            for id in ${image_id[@]}
            do
               ssh $NODE "docker rmi $id"
            done
        else
            echo "$NODE : docker images not found"
        fi
    done
    pdsh -S -w $NODES "rm -rf /mnt/fs-local-volume/*"
  
}

function update_solution_file() {
    output=`python3  <<END
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
END`

echo $output

}

function main() {
    echo $@
    destroy_cluster
    log_docker_image_version

# Below if else statement has been considered for 2 options, 
# 1st for docker images and 2nd for custom docker images, 
# else part will be cover by custom docker images option

    if [[ -n "$IMAGE" ]]; then
        update_solution_file
        docker_image_cleanups
        install_custom_docker_image
    else
        echo "This option will be cover by custom docker build"
    fi

    log_docker_image_version
    deploy_cluster

}

function validate() {
    local leave=

    if [[ -z "$IMAGE" ]]; then
       echo "Docker Images are not specified"
       leave="1"
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
	--nodes)
            NODES=$2
            EX_SRV="pdsh -S -w $NODES"
            shift
            ;;
	--update-resource)
            IMAGE=$2
            shift
            ;;

        *)
            echo -e "Invalid option: $1\n"
            exit 1
            ;;
    esac
    shift
done

validate
main

