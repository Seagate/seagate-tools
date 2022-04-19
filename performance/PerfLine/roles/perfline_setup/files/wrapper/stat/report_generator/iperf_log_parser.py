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
      index = [i for i, item in enumerate(filename) if 'iperf-' in item ][0]
      host = re.split('_',filename[index])
      index1 = [i for i, item in enumerate(host) if 'seagate.com' in item ][0]
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

