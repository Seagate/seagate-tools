#!/usr/bin/env python3
#
# Seagate-tools: PerfPro
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

def get_sanity_schema():
    return {
        "motr_repository": "",
        "rgw_repository": "",
        "hare_repository": "",
        "other_repos": [],
        "PR_ID": ""
    }


def get_primary_set():
    return {
        "Name": "",
        "Config_ID": "",
        "run_ID": ""
    }


def get_run_config_set():
    return {
        "HOST": "",
        "Log_File": "",
        "Timestamp": "",
        "Operation": "",
        "Object_Size": "",
        "Buckets": 0,
        "Objects": "",
        "Sessions": ""
    }


def get_performance_results_set():
    return {
        "Throughput": 0,
        "IOPS": 0,
        "Latency": {},
        "TTFB": {},
        "Total_Errors": 0,
        "Total_Ops": 0,
        "Run_State": ""
    }
