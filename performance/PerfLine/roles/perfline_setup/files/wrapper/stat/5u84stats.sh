#!/usr/bin/env bash
#
# Copyright (c) 2020 Seagate Technology LLC and/or its Affiliates
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# For any questions about this software or licensing,
# please email opensource@seagate.com or cortx-questions@seagate.com.
#

set -x

cd $1

function collect_strg_ctrlr_config()
{
	echo 'Collecting 5u84 configuration using cmdline'
	sshpass -p ${STRG_CTRLR_PASSWORD} ssh -T ${STRG_CTRLR_USER}@${STRG_CTRLR_CONTROLLER_IP} <<-EOF > 5u84.config
	set cli-parameters Pager Disabled
	show volumes
	show pools
	show disk-groups
	show initiators
	show disks
	EOF
}

function collect_perf_logs()
{
	echo 'Collecting 5u84 perf logs using ftp'
	ftp -in $STRG_CTRLR_CONTROLLER_IP <<-EOF
	user $STRG_CTRLR_USER $STRG_CTRLR_PASSWORD
	get logs:heatmap io_density_heatmap.csv
	get perf perf_log.csv
	bye
	EOF
}

function collect_debug_logs()
{
	echo 'Collecting 5u84 debug logs using ftp'
	ftp -in $STRG_CTRLR_CONTROLLER_IP <<-EOF
	user $STRG_CTRLR_USER $STRG_CTRLR_PASSWORD
	logs debug_logs.zip
	bye
	EOF
}

STRG_CTRLR_USER='manage'
STRG_CTRLR_PASSWORD='!manage'
TAP0_IP=$(ifconfig tap0 | grep '10.0.0' | awk '{print $2}')
if [ $TAP0_IP == '10.0.0.4' ]
then
    STRG_CTRLR_CONTROLLER_IP='10.0.0.2'
else
    STRG_CTRLR_CONTROLLER_IP='10.0.0.3'
fi
collect_strg_ctrlr_config
collect_perf_logs
#collect_debug_logs
