#!/usr/bin/env python3
#
# Copyright (c) 2021 Seagate Technology LLC and/or its Affiliates
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

import re
import datetime
import argparse

from os.path import basename

MEAS_LABEL="[MEAS]"

sm_names_map = {
    "Session states" : "session-state",
    "Conn states"    : "conn-state"
}

def get_pid(file_path):
    file_name = basename(file_path)
    pid = file_name.split('.')[0].split('_')[-1]
    return pid

def format_ts(ts):
    dt = datetime.datetime.fromtimestamp(ts / 1e9)
    return '{}.{:09.0f}'.format(dt.strftime('%Y-%m-%d-%H:%M:%S'), ts % 1e9)

def consume_data(input_file):
    pid = get_pid(input_file)
    out_file_name="m0trace_" + str(pid) + ".txt"

    print("Input  file: {}".format(input_file))
    print("Output file: {}".format(out_file_name))
    print("Writing data into {} ... ".format(out_file_name), end='')

    out_file = open(out_file_name, 'w')

    with open(input_file) as file_in:
        for line_in in file_in:
            res = line_in.find(MEAS_LABEL)
            if res != -1:
                line = line_in[res + len(MEAS_LABEL) + 1:]
                words = line.split()

                ts = words[0]
                meas_name = words[1]

                line = line[len(ts) + 1:]

                if meas_name == "state-trace-enable" or meas_name == "state-set":
                    sm_name = re.search('\[(.+?)\]', line).group(1)
                    line = sm_names_map[sm_name] + line[line.find(']') + 1:]

                line_out = "* " + format_ts(int(ts)) + " " + line
                out_file.write(line_out)

    out_file.close()
    print("done")

def args_parse():
    parser = argparse.ArgumentParser(description="""
m0trace2addb.py: parses measurement lines of textual m0trace dumps into ADDB2-like dump output
    """)
    parser.add_argument('--dumps', nargs='+', type=str, required=True,
                        default=[],
                        help="""
A bunch of m0trace.dumps can be passed here for processing:
python3 m0trace2addb.py --dumps m0trace_1.dump m0trace_2.dump ...
""")

    return parser.parse_args()

if __name__ == '__main__':
    args=args_parse()

    for m0trace_dump in args.dumps:
        consume_data(m0trace_dump)
