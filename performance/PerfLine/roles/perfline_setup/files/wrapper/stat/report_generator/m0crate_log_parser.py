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

M0CRATE_MEASUREMENTS = ('Throughput',)
M0CRATE_PARAMS = ('LAYOUT_ID', 'OPCODE', 'IOSIZE', 'BLOCK_SIZE',
                  'BLOCKS_PER_OP', 'MAX_NR_OPS', 'NR_OBJS', 'NR_THREADS',
                  'RAND_IO', 'MODE', 'THREAD_OPS')


def parse_m0crate_log(m0crate_log_path):
    with open(m0crate_log_path) as f:

        parameters = {}
        results = []

        for line in f:
            if line.startswith('info: W:'):
                metrics = line.strip().split(',')
                throughput = metrics[2].strip()
                results.append({'Operation': 'Write', 'Throughput': throughput})
            elif line.startswith('info: R:'):
                metrics = line.strip().split(',')
                throughput = metrics[2].strip()
                results.append({'Operation': 'Read', 'Throughput': throughput})
            elif line.startswith("set parameter:"):
                kv = line.strip().split()[-1].split('=')
                param_name = kv[0]
                param_val = kv[1]
                if param_name in M0CRATE_PARAMS:
                    parameters[param_name] = param_val

    return {'params': parameters, 'results': results}


if __name__ == "__main__":
    logfile = sys.argv[1]
    results = parse_m0crate_log(logfile)

    for test in results['results']:
        op = "Operation"
        print("{}: {}".format(op,test[op]))
        for m in M0CRATE_MEASUREMENTS:
            if m in test:
                print("{}: {}".format(m,test[m]))
        print('')
