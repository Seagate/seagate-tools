#!/usr/bin/env python3
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

import os.path
import sys

S3BENCH_MEASUREMENTS = ('Total Throughput (MB/s)', 'Ttfb Max', 'Ttfb Avg', 'Ttfb Min')
S3BENCH_PARAMS = ('numClients', 'numSamples', 'objectSize (MB)', 'bucket')

def parse_kv(line):
    line = line.strip()
    if not ':' in line:
        return None, None

    splitted_line = line.split(':')
    t = tuple(map(lambda s: None if len(s) == 0 else s, map(str.strip, splitted_line)))

    return t[0], t[1]

current_results = None

def process_result_record(key, val, results):
    if key is None:
        return

    global current_results

    if key == 'Operation':
        current_results = {key: val}
        results.append(current_results)
    elif key in S3BENCH_MEASUREMENTS:
        current_results[key] = val

def process_param_record(key, val, params):
    if key is None:
        return

    if key in S3BENCH_PARAMS:
        params[key] = val

def parse_s3bench_log(s3bench_log_path):
    with open(s3bench_log_path) as f:
        test_params = {}
        tests_results = []
        is_params_section = False
        is_tests_section = False

        for line in f:
            key, val = parse_kv(line)
            if key == 'Tests':
                is_tests_section = True
                is_params_section = False
                continue
            elif key == 'Parameters':
                is_tests_section = False
                is_params_section = True
                continue

            if is_tests_section:
                process_result_record(key, val, tests_results)
            elif is_params_section:
                process_param_record(key, val, test_params)

    return {'params': test_params, 'results': tests_results}

def try_parse_s3bench_results(s3bench_log_path):
    if os.path.isfile(s3bench_log_path):
        return parse_s3bench_log(s3bench_log_path)
    else:
        return [{'result': 'N/A'}]

if __name__ == "__main__":
    logfile = sys.argv[1]
    results = parse_s3bench_log(logfile)

    for test in results['results']:
        op = "Operation"
        print("{}: {}".format(op,test[op]))
        for m in S3BENCH_MEASUREMENTS:
            if m in test:
                print("{}: {}".format(m,test[m]))
        print('')
