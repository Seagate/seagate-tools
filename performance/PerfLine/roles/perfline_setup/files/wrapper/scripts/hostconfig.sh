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

nodes=$1

pdsh -S -w "$nodes" "hostname -i" | sort -n | awk '{print $2, $1}'| awk '{ $2="srvnode-"++i;}1' > hostsfile
for host in ${nodes//,/ }
do
   ssh "$host" "cat /etc/hosts | grep srvnode"
   flag=$?
   if [ $flag -eq 0 ]
   then
       echo "Host entry is already exist in $host"
   else
       scp hostsfile "$host":/tmp
       ssh "$host" "cat /tmp/hostsfile >> /etc/hosts"
       echo "/etc/hosts file configured successfully"
   fi
done
