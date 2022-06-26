#!/bin/bash
#
# Seagate-tools: PerfPro
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


echo "$1" > driver-nodes-list
if [ ! -d "/root/cos" ] ; then
   echo "Installing cosbench"
   sh cosbench.sh install --controller "$1" --drivers driver-nodes-list
   sh cosbench.sh configure --controller "$1" --drivers driver-nodes-list
   sh cosbench.sh start --controller "$1" --drivers driver-nodes-list
else
   echo -e "cosbench tools is already installed on $1"
fi

ps -ef | grep -v grep | grep "driver-tomcat-server.xml" > /dev/null
status=$?
if [ $status -eq 0 ]; then
   echo "cosbench is running on $1"
else
   echo "Starting cosbench..."
#   sh cosbench.sh start --controller $1 --drivers driver-nodes-list
   cd ~/cos/; sh stop-all.sh; sh start-all.sh 
fi

