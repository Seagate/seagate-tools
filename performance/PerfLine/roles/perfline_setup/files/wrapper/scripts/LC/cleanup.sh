#!/usr/bin/env bash

set -e
set -x

SCRIPT_NAME=`echo $0 | awk -F "/" '{print $NF}'`
SCRIPT_PATH="$(readlink -f $0)"
SCRIPT_DIR="${SCRIPT_PATH%/*}"
source "$SCRIPT_DIR/../../../perfline.conf"

# TODO: move it to some constants.sh file
CUSTOM_DOCKER_IMAGE_TAG_PREFIX="perfline_"


function parse_params()
{
    while [[ $# -gt 0 ]]; do
        case $1 in
            --task-id)
                TASK_ID="$2"
                shift
                ;;
            *)
                echo "unsupported parameter $1"
                exit 1
                ;;
        esac

        shift
    done
}

function remove_custom_docker_image()
{
    local docker_image_tag="${CUSTOM_DOCKER_IMAGE_TAG_PREFIX}${TASK_ID}"
    pdsh -R ssh -S -w $NODES $SCRIPT_DIR/remove_tmp_docker_image.sh $docker_image_tag
}

function main()
{
    parse_params $@
    remove_custom_docker_image
}

main $@
exit $?
