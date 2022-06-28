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
"""
A hsbench parser module

Depends on:
1. run results of performance
2. run log of the tool run
"""
import json
import os
import re
import datetime as dt
import time

from schemas import get_performance_schema


def extract_HSBench_logs(reference_doc, HS_destination_file_path):
    """
    A function to structurize data from raw data files
    arguments: log file path (str), intermediate path to store structured data (str)
    """
    with open(HS_destination_file_path, "w") as modified:
        with open(reference_doc, 'r') as reference_file:

            for line in reference_file:
                if 'Loop:' in line or 'Mode:' in line:
                    modified.write(line)


def clean_the_line(line):
    """
    A function to clear clutter, whitespaces from the given line of the hsbench log
    arguments: line to clean (str)
    returns: list of line components splitted wrt " " & "," (list)
    """
    not_needed_chars = ('', '-', '[', ']', ',')
    stripped_data = re.split(" |,", line)
    for element in stripped_data:
        if element in not_needed_chars:
            stripped_data.remove(element)

    return stripped_data


def get_date_time_object(stripped_data):
    """
    A function to convert string to date time object
    arguments: list of a line component with date at the beginning (list)
    returns: datetime value (datetime object)
    """
    date_time_str = stripped_data[0]+" "+stripped_data[1]
    return dt.datetime.strptime(date_time_str, '%Y/%m/%d %H:%M:%S')


def convert_HSlogs_to_JSON(run_ID, reference_doc, HS_input_file_path, quantum, HS_source_file_path):
    """
    a function to convert raw hsbench run results into a json format
    arguments: run ID (int), data file path (str), path to store json files (str), interval size (int), path of raw data file (str)
    """
    data = []
    time_now = time.time_ns()

    with open(reference_doc, 'r') as reference_file:
        lines = reference_file.readlines()
        num_of_lines = len(lines)
        line = 0

        stripped_data = clean_the_line(lines[line])
        start_time = get_date_time_object(stripped_data)
        end_time = start_time + dt.timedelta(seconds=quantum)

        while line != num_of_lines:
            stripped_data = clean_the_line(lines[line])
            current_line_time = get_date_time_object(stripped_data)
            total_latency = 0
            total_iops = 0
            total_throughput = 0
            initial_line = line
            mode_change = False
            mode = stripped_data[9]

            if current_line_time > end_time:
                samples = 0
            else:
                while end_time > current_line_time and line < num_of_lines:
                    try:
                        total_latency += float(stripped_data[20])
                        total_iops += float(stripped_data[15])
                        total_throughput += float(stripped_data[13])

                        line += 1
                        if line < num_of_lines:
                            stripped_data = clean_the_line(lines[line])
                            if stripped_data[9] != mode:
                                mode_change = True
                                break
                            current_line_time = get_date_time_object(
                                stripped_data)

                    except IndexError:
                        line += 1

                samples = line - initial_line

            if samples == 0:
                average_latency = 0
                total_iops = 0
                total_throughput = 0
            else:
                average_latency = round(total_latency/samples, 5)

            entry = get_performance_schema(time_now, run_ID, average_latency, total_iops, total_throughput, str(
                end_time - dt.timedelta(seconds=quantum)), mode, 'hsbench', HS_source_file_path)
            data.append(entry)
            time_now = time_now + 10

            if not mode_change:
                end_time = end_time + dt.timedelta(seconds=quantum)

    with open(HS_input_file_path, 'w') as jsonfile:
        json.dump(data, jsonfile, indent=4, sort_keys=True)

    os.remove(reference_doc)
