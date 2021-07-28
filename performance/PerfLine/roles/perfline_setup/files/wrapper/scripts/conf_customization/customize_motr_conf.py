#!/usr/bin/env python3
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

import argparse
import sys


def parse_args():
    parser = argparse.ArgumentParser(prog=sys.argv[0],
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description="""
customize_motr_conf.py is a tool to generating customized config file for Motr.
Script uses some predefined file as a base for changing some parameters.
Using this base file script generates new one that contains updated values
specified by user.
""")

    parser.add_argument("-s", "--src-conf-file", type=str, required=True,
                        help="path to motr config file used as base")

    parser.add_argument("-d", "--dst-conf-file", type=str, required=True,
                        help="path to store result")
    
    parser.add_argument("-p", "--param", action='append', required=True,
                        help="parameter to be overrided in a form 'PARAM_NAME=PARAM_VALUE'")


    return parser.parse_args()


def read_src_config(src_config_path):
    conf_file_content = list()

    with open(src_config_path) as f:
        for line in f:
            conf_file_content.append(line.strip())

    return conf_file_content

def detect_key(line):
    # ignore comments and empty lines
    if line.startswith('#') or line == '':
        return None

    # remove comments from 'key=value' lines
    comment_position = line.find('#')
    if comment_position != -1:
        line = line[0:comment_position].strip()

    key_value_parts = line.split('=')
    if len(key_value_parts) != 2:
        print(f'invalid format of line: {line}')
        return None

    return key_value_parts[0].strip()

def process_conf_file_content(file_content, params_vals):
    tmp_params_vals = params_vals.copy()
    result = list()

    for line in file_content:
        key = detect_key(line)


        if key is not None and key in tmp_params_vals:
            new_val = tmp_params_vals[key]
            result.append(f'{key}={new_val}  # changed by customize_motr_conf.py script')
            del tmp_params_vals[key]
        else:
            result.append(line)

    if len(tmp_params_vals) > 0:
        result.append('#')
        for k,v in tmp_params_vals.items():
            result.append(f'{k}={v}  # added by customize_motr_conf.py script')

    return result


def write_dst_config(file_path, lines):
    with open(file_path, 'wt') as f:
        for line in lines:
            f.write(f'{line}\n')


def main():
    args = parse_args()
    new_params = dict()

    for key_val in args.param:
        kv = key_val.split('=')
        key = kv[0].strip()
        val = kv[1].strip()
        new_params[key] = val

    conf_file_content = read_src_config(args.src_conf_file)
    result = process_conf_file_content(conf_file_content, new_params)
    write_dst_config(args.dst_conf_file, result)


if __name__ == '__main__':
    main()
