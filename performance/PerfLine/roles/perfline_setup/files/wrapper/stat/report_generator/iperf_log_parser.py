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


import sys
import re

IPERF_MEASUREMENTS = ('Duration (s)', 'Transfer', 'Bandwidth')
IPERF_PARAMS = ('Interval', 'Duration', 'Parallel')

def parse_iperf_log(iperf_log_path):
    res = {}
    with open(iperf_log_path, 'r') as f:
      lines = f.read().splitlines()
      DataList = re.split('\s+', lines[-1])
      filename = re.split('\/', iperf_log_path)
      index = [i for i, item in enumerate(filename) if item.endswith('workload.log')][0]
      host = re.split('_',filename[index])
      index1 = [i for i, item in enumerate(host) if item.endswith('seagate.com')][0]
      res['Hostname'] = host[index1]
      for index in range(len(DataList)-6):
           DataList.remove(DataList[0])
      temp = '{}' * 2
      DataList = [temp.format(*ele) for ele in zip(*[iter(DataList)] * 2)]
      for key,value in zip(IPERF_MEASUREMENTS,DataList):
          res[key] = value
      return res

if __name__ == "__main__":
    logfile = sys.argv[1]
    results = parse_iperf_log(logfile)
    
    for key, value in results.items():
        print("{}: {}".format(key,value))

