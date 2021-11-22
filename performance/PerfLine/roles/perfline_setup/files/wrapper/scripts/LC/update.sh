#!/bin/bash

#set -e
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

function check_docker_image_version() {
    echo "Docker Image Version"
    pdsh -S -w $NODES 'docker images | grep "cortx-all"'
}

function install_custom_docker_image() {
    pdsh -S -w $NODES "docker pull $URL"
}

function docker_image_cleanups() {
    for NODE in ${NODES//,/ }
    do
        image_id=($(ssh $NODE "docker images | grep cortx-all" | awk '{ print $3 }'))
        echo "image_ids: ${image_id[@]}"
        for id in ${image_id[@]}
        do
           ssh $NODE "docker rmi $id"
        done
    done
    pdsh -S -w $NODES "rm -rf /mnt/fs-local-volume/*"
  
}
function update_solution_file() {
    output=`python3  <<END
import yaml
import sys
fname = "$K8S_SCRIPTS_DIR/solution.yaml.bak"

stream = open(fname, 'r')
data = yaml.safe_load(stream)
data['solution']['images']['cortxcontrolprov'] = "$URL"
data['solution']['images']['cortxcontrol'] = "$URL"
data['solution']['images']['cortxdataprov'] = "$URL"
data['solution']['images']['cortxdata'] = "$URL"

with open(fname, 'w') as yaml_file:
    yaml_file.write( yaml.dump(data, sort_keys = False))

print("successfully updated solution.yaml")
END`

echo $output

}



function main() {
    echo $@
    destroy_cluster
    check_docker_image_version

    update_solution_file
    
    if [[ -n "$URL" ]]; then
        docker_image_cleanups
        install_custom_docker_image
    fi

    check_docker_image_version
    deploy_cluster

}

function validate() {
    local leave=

    if [[ -z "$URL" ]]; then
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
	    check_arg_count $1 $2 $3
	    MOTR_REPO=$2
            MOTR_BRANCH=$3
            shift
            shift
            ;;
        -h|--hare_id)
	    check_arg_count $1 $2 $3
	    HARE_REPO=$2
            HARE_BRANCH=$3
            shift
            shift
            ;;
    --use-lnet)
        BUILD_MOTR_WITH_LNET='1'
        ;;
	-s|--s3_id)
	    check_arg_count $1 $2 $3
            S3_REPO=$2
            S3_BRANCH=$3
            shift
	    shift
            ;;
	-u|--utils_id)
	    check_arg_count $1 $2 $3
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
	--url)
            URL=$2
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
main

