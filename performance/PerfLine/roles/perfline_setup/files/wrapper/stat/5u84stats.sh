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
