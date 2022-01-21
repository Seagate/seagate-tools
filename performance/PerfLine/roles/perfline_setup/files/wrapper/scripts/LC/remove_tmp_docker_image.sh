#!/usr/bin/env bash

set -e
set -x

function main()
{
    local docker_image_tag="$1"

    if [[ -z "$docker_image_tag" ]]; then
        echo 'missed docker image tag'
        return 1
    fi

    local docker_image_id="$(docker images | grep $docker_image_tag | awk '{print $3}')"
    
    if [[ -n "$docker_image_id" ]]; then
        docker rmi $docker_image_id || true
    fi
}

main $@
exit $?