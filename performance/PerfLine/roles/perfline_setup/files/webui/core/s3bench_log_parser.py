#!/usr/bin/env python
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

import os.path

S3BENCH_MEASUREMENTS = ('Total Throughput (MB/s)', 'Ttfb Max', 'Ttfb Avg', 'Ttfb Min')

def parse_kv(line):
    line = line.strip()
    if not ':' in line:
        return None, None

    splitted_line = line.split(':')
    t = tuple(map(lambda s: None if len(s) == 0 else s, map(str.strip, splitted_line)))
    
    return t[0], t[1]

def parse_s3bench_log(s3bench_log_path):
    with open(s3bench_log_path) as f:
        tests_results = []
        is_tests_section = False
        current_results = None
        for line in f:
            key, val = parse_kv(line)
            if key == 'Tests':
                is_tests_section = True
                continue

            if not is_tests_section:
                continue

            if key is None:
                continue

            if key == 'Operation':
                current_results = {key: val}
                tests_results.append(current_results)
            elif key in S3BENCH_MEASUREMENTS:
                current_results[key] = val

    return tests_results

def try_parse_s3bench_results(s3bench_log_path):
    if os.path.isfile(s3bench_log_path):
        return parse_s3bench_log(s3bench_log_path)
    else:
        return [{'result': 'N/A'}]

if __name__ == "__main__":
    logfile = 'workload_s3bench.log'
    print(parse_s3bench_log(logfile))
