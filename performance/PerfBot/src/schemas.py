#!/usr/bin/env python3
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
"""Schemas to store data in influxDB."""

def get_performance_schema(time_now, run_ID, latency, iops, throughput, timestamp, mode, tool, filename):
    entry = {
        "measurement": "data",
        "time": time_now,
        "fields":
        {
            "timestamp": timestamp,
            "run_ID": run_ID,
            "tool": tool,
            "latency": float(latency),
            "iops": float(iops),
            "throughput": float(throughput),
            "mode": mode,
            "datafile": filename
        }
    }
    return entry


def get_error_schema(time_now, run_ID, tool, line_number, keyword_matched, file_path, error_details):
    entry = {
        "measurement": "logs",
        "time": time_now,
        "fields":
            {
                "run_ID": run_ID,
                "tool": tool,
                "line_in_file": line_number,
                "keyword": keyword_matched,
                "log_file": file_path,
                "details": error_details
            }
    }

    return entry


def get_results_schema(time_now, sr_no, date, run_ID, functionality, result, rulebook_version, rerun):
    entry = {
        "measurement": "results",
        "time": time_now,
        "fields":
        {
            "sr_no": sr_no,
            "date": date,
            "run_ID": run_ID,
            "functionality": functionality,
            "result": result,
            "rulebook": rulebook_version,
            "rerun": rerun
        }
    }

    return entry
