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

SCRIPT_PATH="$(readlink -f "$0")"
SCRIPT_DIR="${SCRIPT_PATH%/*}"
# shellcheck source=/dev/null
source "$SCRIPT_DIR/../../perfline.conf"

echo "Will update statistics for $1 runs"

BUILD_TYPE=$1

mkdir -p "$NIGHT_ARTIFACTS"/"$BUILD_TYPE"/img
mkdir -p "$NIGHT_ARTIFACTS"/"$BUILD_TYPE"/data
mkdir -p "$NIGHT_ARTIFACTS"/"$BUILD_TYPE"/table

list=""
for d in "$ARTIFACTS_DIR"/result*; do
    if [ -f "$d"/perfline_metadata.json ]; then
	set +e
	cat "$d/perfline_metadata.json" | grep "Daemon" | grep "$BUILD_TYPE"
	ret=$?
	set -e
	if [ $ret -eq 0 ]; then
	    list+="$d "
	fi
    fi
done

pushd "$SCRIPT_DIR"
python3 fetch.py "$BUILD_TYPE" "$list"
popd
