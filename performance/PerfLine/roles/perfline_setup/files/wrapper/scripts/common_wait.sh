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

function validate() {
    local status

    if [ -z "$TASK_ID" ] ; then
	echo "Task ID is not specified"
	usage
	exit 1
    fi

    pushd "$SCRIPT_DIR"
    set +e
    ./perfline.py -r | grep -q "$TASK_ID"
    status=$?
    set -e
    if [ "$status" -eq 0 ] ; then
	popd
	echo "Task $TASK_ID has already finished"
	exit 1
    fi

    set +e
    ./perfline.py -l | grep -q "$TASK_ID"
    status=$?
    set -e
    if [ "$status" -ne 0 ] ; then
	popd
	echo "Task $TASK_ID not found"
	exit 1
    fi

    set +e
    ./perfline.py -l | grep "$TASK_ID" | grep "user_action" -A1 | grep -q "wait"
    status=$?
    set -e
    if [ "$status" -ne 0 ] ; then
	popd
	echo "Task $TASK_ID is not waiting for user actions"
	exit 1
    fi

    popd
}
