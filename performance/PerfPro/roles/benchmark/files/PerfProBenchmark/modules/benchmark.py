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

import datetime
import socket
import os

import modules.common_functions as cf


class benchmark:
    run_state = "successful"
    s3bench_ops = ["Write", "Read", "GetObjTag", "HeadObj", "PutObjTag"]

    def __init__(self, bench, overwrite_flag, collection) -> None:
        self.bench = bench
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.record_overwritten = overwrite_flag
        self.database_collection = collection
        self.host = socket.gethostname()

        # self.run_id = run_config["run_id"]
        # self.config_id = run_config["config_id"]

    def extract_s3bench_results(self, file):
        _, self.log_file = os.path.split(file)
        with open(file) as report:
            data_obtained = False
            lines = report.readlines()
            for lindex, line in enumerate(lines):
                if data_obtained:
                    break
                if "label" in line:
                    _temp = line.split("_")
                    self.object_size = _temp[1].upper()
                    self.objects = int(_temp[3])
                    self.buckets = int(_temp[5])
                    self.sessions = int(_temp[7][:-1])
                elif "Operation" in line:
                    operation = cf.get_metric_value(line)
                    if operation in self.expected_op:
                        self.operation = operation
                        self.total_ops = int(
                            cf.get_metric_value(lines[lindex+2]))
                        self.total_errors = int(
                            cf.get_metric_value(lines[lindex+3]))
                        self.throughput = round(
                            float(cf.get_metric_value(lines[lindex+4])), 6)
                        self.iops = round(
                            self.throughput/float(self.object_size[:-2]), 6)

                        self.latency = {
                            "Max": round(float(cf.get_metric_value(lines[lindex+7])), 6),
                            "Avg": round(float(cf.get_metric_value(lines[lindex+8])), 6),
                            "Min": round(float(cf.get_metric_value(lines[lindex+9])), 6),
                            "99p": round(float(cf.get_metric_value(lines[lindex+14])), 6)
                        }

                        self.ttfb = {
                            "Max": round(float(cf.get_metric_value(lines[lindex+10])), 6),
                            "Avg": round(float(cf.get_metric_value(lines[lindex+11])), 6),
                            "Min": round(float(cf.get_metric_value(lines[lindex+12])), 6),
                            "99p": round(float(cf.get_metric_value(lines[lindex+16])), 6)
                        }
                    data_obtained = True
