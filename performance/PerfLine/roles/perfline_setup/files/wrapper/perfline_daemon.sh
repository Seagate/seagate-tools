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

set -x
set -e

SCRIPT_NAME=$(echo "$0" | awk -F "/" '{print $NF}')
SCRIPT_PATH="$(readlink -f "$0")"
SCRIPT_DIR="${SCRIPT_PATH%/*}"
source "$SCRIPT_DIR/../perfline.conf"
source "$SCRIPT_DIR/.latest_stable_build"

# Stable builds link for CentOS7.8
# STABLE_BUILD_URL="http://cortx-storage.colo.seagate.com/releases/cortx/github/stable/centos-7.8.2003/"

# Stable builds link for CentOS7.9
STABLE_BUILD_URL="http://cortx-storage.colo.seagate.com/releases/cortx/github/stable/centos-7.9.2009/"

STABLE_WORKLOAD_DIR="$PERFLINE_DIR/wrapper/workload/daemon_runs/stable"
MAIN_WORKLOAD_DIR="$PERFLINE_DIR/wrapper/workload/daemon_runs/main"

function stable_build() {
    BUILD_LIST=$(curl -s $STABLE_BUILD_URL/ | grep href | sed 's/.*href="//' | sed 's/".*//' | grep -o '[[:digit:]]*' | sort -n)
    for build in $BUILD_LIST;
    do
       if [ "$build" -ge "$BUILDNO" ]
       then
           BUILD_URLS=("$STABLE_BUILD_URL/$build/prod/")
           for workload_file in $(ls $STABLE_WORKLOAD_DIR/*.yaml)
           do
	       	python3 - "$workload_file" "$build" "$BUILD_URLS" << EOF
import sys
import yaml

filename = sys.argv[1]
build    = sys.argv[2]
url      = sys.argv[3]

with open(filename, 'r') as fd:
    try:
        data = yaml.safe_load(fd)
    except yaml.YAMLError as err:
        print(err)
        exit(1)

data['common']['description'] = 'Daemon exection for stable {}'.format(build)
data['common']['priority'] = 5
data['common']['user'] = 'daemon_run@seagate.com'

data['custom_build']['url'] = url

with open(filename, 'w') as fd:
    yaml.dump(data, fd)
EOF

               "$SCRIPT_DIR"/perfline.py -a < "$workload_file"
           done
           echo "BUILDNO=$build" > .latest_stable_build
           echo "Successfully triggered for $build"
       fi
    done
}

function main_build() {
    local motr_main=
    local s3server_main=
    local hare_main=
    local pyutils_main=
    local descr_str=""

    pushd "$PERFLINE_DIR"/docker/cortx/

    pushd cortx-motr
    git checkout main
    git reset --hard
    git pull --rebase
    motr_main=$(git log --format="%H" -n 1 | cut -c1-9)
    popd			# from cortx-motr

    pushd cortx-s3server
    git checkout main
    git reset --hard
    git pull --rebase
    s3server_main=$(git log --format="%H" -n 1 | cut -c1-9)
    popd			# from cortx-s3server

    pushd cortx-hare
    git checkout main
    git reset --hard
    git pull --rebase
    hare_main=$(git log --format="%H" -n 1 | cut -c1-9)
    popd			# from cortx-s3server

    pushd cortx-utils
    git checkout main
    git reset --hard
    git pull --rebase
    pyutils_main=$(git log --format="%H" -n 1 | cut -c1-9)
    popd			# from cortx-utils

    popd 			# from docker/cortx

    for workload_file in $(ls $MAIN_WORKLOAD_DIR/template.*.yaml)
    do
	cp -f "$workload_file" "$MAIN_WORKLOAD_DIR/workload.yaml"
	python3 - "$MAIN_WORKLOAD_DIR/workload.yaml" "$motr_main" "$s3server_main" "$hare_main" << EOF
import sys
import yaml

filename = sys.argv[1]
motr     = sys.argv[2]
s3server = sys.argv[3]
hare     = sys.argv[4]

with open(filename, 'r') as fd:
    try:
        data = yaml.safe_load(fd)
    except yaml.YAMLError as err:
        print(err)
        exit(1)

data['common']['description'] = 'Daemon exection for main, motr: {}, s3server {}, hare {}'.format(motr, s3server, hare)
data['common']['priority'] = 5
data['common']['user'] = 'daemon_run@seagate.com'

data['custom_build']['motr']['branch'] = motr
data['custom_build']['s3server']['branch'] = s3server
data['custom_build']['hare']['branch'] = hare

data['post_exec_cmds'] = [{'cmd': '/root/perfline/wrapper/scripts/update_runs_stats.sh main'},]

with open(filename, 'w') as fd:
    yaml.dump(data, fd)
EOF

	"$SCRIPT_DIR"/perfline.py -a < "$MAIN_WORKLOAD_DIR/workload.yaml"
    done
}

function main() {
    #stable_build
    main_build
}

echo "parameters: $@"

while [[ $# -gt 0 ]]; do
    case $1 in
        --help)
            echo -e "Usage: ./perfline_deamon.sh"
            exit 0
            ;;
        *)
            echo -e "Invalid option: $1\nUse --help option"
            exit 1
            ;;
    esac
    shift
done

main

