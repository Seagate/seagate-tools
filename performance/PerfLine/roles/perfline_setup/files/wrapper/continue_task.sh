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

SCRIPT_PATH="$(readlink -f "$0")"
SCRIPT_DIR="${SCRIPT_PATH%/*}"

TASK_ID="$1"

source "$SCRIPT_DIR"/../perfline.conf
source "$SCRIPT_DIR"/scripts/common_wait.sh

function usage() {
    cat << HEREDOC
Usage : $0 task_id
where,
    task_id - ID of PerfLine task to continue
HEREDOC
}

function continue_perfline() {
    pushd "$LOCK_DIR"
    if [ ! -f "$TASK_ID.lock" ] ; then
	echo "Task $TASK_ID is not locked, exit"
	exit 1
    fi

    rm -rf "$TASK_ID.lock"
    touch "$TASK_ID.release"
    popd

    echo "Continue Task $TASK_ID"
}

function main() {
    validate
    continue_perfline
}

main
