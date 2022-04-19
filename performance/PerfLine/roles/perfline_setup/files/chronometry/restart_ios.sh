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
#set -x

status=$(hctl status)
addr="([0-9]+[.][0-9]+[.][0-9]+[.][0-9]+)"
host=$(hostname -s)

NODE_IP=`echo "$status" | grep "$host" -A 1 | grep -E -o "$addr"`
IOS_FID=`echo "$status" | grep "\[.*\].*ioservice" | grep ${NODE_IP} \
        | awk '{print $3}'`

# Wait before kill
sleep_before=$((( RANDOM % 60 ) + 120))
echo "waiting $sleep_before before killing ioservice"
sleep $sleep_before

hctl status

ios_pid=$(ps ax | grep -v grep | grep $IOS_FID | awk '{print $1}')

if [[ -z "$ios_pid" ]]; then
    echo "m0d ioservice process is not alive"
    exit 0
fi

kill -9 $ios_pid

# Wait after kill
sleep_after=$((( RANDOM % 30 ) + 10))
echo "waiting $sleep_after before starting ioservice"
sleep $sleep_after
hctl status

echo "IOS_FID: $IOS_FID"
systemctl start m0d@$IOS_FID || echo "ioservice starting failed"

sleep 10
hctl status
