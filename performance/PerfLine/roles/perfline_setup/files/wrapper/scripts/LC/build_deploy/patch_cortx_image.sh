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

source "$SCRIPT_DIR/../../../../perfline.conf"

SANDBOX_DIR="$ARTIFACTS_DIR/docker_img_patch"
FILES_TO_REPLACE=()


function parse_args()
{
    while [[ $# -gt 0 ]]; do
        case $1 in
            --base-image)
                BASE_IMAGE="$2"
                shift
                ;;
            --new-image)
                NEW_IMAGE="$2"
                shift
                ;;
            --container)
                TMP_CONTAINER_NAME="$2"
                shift
                ;;
            --motr-repo)
                MOTR_REPO="$2"
                shift
                ;;
            --hare-repo)
                HARE_REPO="$2"
                shift
                ;;
            *)
                echo -e "Invalid option: $1"
                exit 1
                ;;
        esac
        shift
    done
}

function check_args()
{
    if [ -z "$BASE_IMAGE" ] || [ -z "$NEW_IMAGE" ] || [ -z "$TMP_CONTAINER_NAME" ]; then
        echo "missed required parameters"
        exit 1
    fi

    if [ -z "$MOTR_REPO" ] && [ -z "$HARE_REPO" ]; then
        echo "it is required to specify at least one of: --motr-repo/--hare-repo"
        exit 1
    fi
}


function patch_motr_files()
{
    local motr_dir="$SANDBOX_DIR/motr"

    # create a directory for Motr installation
    if [[ -d "$motr_dir" ]]; then
        rm -rf "$motr_dir"
    fi

    mkdir -p "$motr_dir"

    # install Motr
    pushd "$MOTR_REPO"
    make DESTDIR="$motr_dir" install
    popd

    local src_dir="usr/local/bin"
    local dst_dir="/usr/bin"

    for file in $(ls "$motr_dir/$src_dir" | grep -v -P 'm0gentestds|m0gccxml2xcode|m0kut|m0ut|m0ub|m0ff2c'); do
        FILES_TO_REPLACE+=("$motr_dir/$src_dir/$file $dst_dir/$file")
    done

    src_dir="usr/local/sbin"
    dst_dir="/usr/sbin"

    for file in $(ls "$motr_dir/$src_dir" | grep -v -P 'm0run'); do
        FILES_TO_REPLACE+=("$motr_dir/$src_dir/$file $dst_dir/$file")
    done


    src_dir="usr/local/lib"
    dst_dir="/usr/lib64"

    for file in $(ls "$motr_dir/$src_dir" | grep -v -P '\.la|libmotr-ut|libtestlib|libmotr-xcode-ff2c|pkgconfig'); do
                
        # ignore symlinks and directories
        if [[ -h "$motr_dir/$src_dir/$file" || -d "$motr_dir/$src_dir/$file" ]]; then
            continue
        fi
                
        FILES_TO_REPLACE+=("$motr_dir/$src_dir/$file $dst_dir/$file")
    done
}


function patch_hare_files()
{
    local hare_dir="$SANDBOX_DIR/hare"

    # create a directory for hare installation
    if [[ -d "$hare_dir" ]]; then
        rm -rf "$hare_dir"
    fi

    mkdir -p "$hare_dir"

    # install hare
    pushd "$HARE_REPO"
    make install DESTDIR="$hare_dir"
    sed -i -e 's@^#!.*\.py3venv@#!/usr@' "$hare_dir"/opt/seagate/cortx/hare/bin/*
    popd

    local items="opt/seagate/cortx/hare/bin opt/seagate/cortx/hare/lib64/python3.6/site-packages/libhax.cpython-36m-x86_64-linux-gnu.so"

    for item in $items; do
        if [[ -f "$hare_dir/$item" ]]; then
            FILES_TO_REPLACE+=("$hare_dir/$item /$item")
        elif [[ -d "$hare_dir/$item" ]]; then
            local dir="$item"
            for file in $(ls "$hare_dir/$dir"); do

                if [[ -f "$hare_dir/$dir/$file" ]]; then
                    FILES_TO_REPLACE+=("$hare_dir/$dir/$file /$dir/$file")
                fi
            done
        fi
    done
}


function main()
{
    parse_args $@
    check_args

    if [[ -n "$MOTR_REPO" ]]; then
        patch_motr_files
    fi

    if [[ -n "$HARE_REPO" ]]; then
        patch_hare_files
    fi

    # generate a new docker image
    files_args=()

    for ((j = 0; j < $((${#FILES_TO_REPLACE[*]})); j++)); do
        local src_dst=${FILES_TO_REPLACE[((j))]}
        local src_file=$(echo "$src_dst" | awk '{print $1}')
        local dst_file=$(echo "$src_dst" | awk '{print $2}')
        files_args+=("--file" "$src_file" "$dst_file")
    done

    "$SCRIPT_DIR"/../update_docker_image.sh \
        --nodes "$NODES" \
        --base-image "$BASE_IMAGE" \
        --image "$NEW_IMAGE" \
        --tmp-container "$TMP_CONTAINER_NAME" "${files_args[@]}"

}


main $@
exit $?