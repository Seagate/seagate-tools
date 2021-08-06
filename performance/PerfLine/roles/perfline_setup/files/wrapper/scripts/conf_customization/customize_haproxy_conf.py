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
import re


S3SERVER_ENTRY_FORMAT = "    server s3-instance-{0} {1}:{2} {3}    # s3 instance {0}"


def parse_addr_port_options(line):
    line = line.lstrip()

    comment_pos = line.find('#')
    if comment_pos != -1:
        line = line[0:comment_pos]

    parts = line.split()

    addr_port = parts[2]

    options = ''
    if len(parts) > 3:
        options = ' '.join(parts[3:])

    addr, port = addr_port.split(':')

    return addr, int(port), options


def find_s3server_lines(file_lines):
    line_numbers = list()
    ln = -1
    is_backend_section = False

    for line in file_lines:
        ln += 1

        stripped_line = line.lstrip()

        # ignore empty lines and comments
        if len(stripped_line) == 0 or stripped_line.startswith("#"):
            continue
        
        if not line.startswith(" "):
            # found next section
            if line.startswith("backend s3-main"):
                is_backend_section = True
            else:
                is_backend_section = False

        if is_backend_section:
            if stripped_line.startswith("server"):
                line_numbers.append(ln)

    return line_numbers

def patch_file(file_content, lines_for_delete, instance_nr, addr, port_start, options):
    result = []

    for line_index, line in enumerate(file_content):
        if line_index not in lines_for_delete:
            result.append(line)
        elif line_index == lines_for_delete[0]:
            for i in range(0, instance_nr):
                instance_id = i + 1
                port = port_start + i
                result.append(S3SERVER_ENTRY_FORMAT.format(instance_id, addr, port, options))
    
    return result


def parse_args():
    parser = argparse.ArgumentParser(prog=sys.argv[0],
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description="""
customize_haproxy_conf.py is a tool to generating customized config file for HAProxy.
Script uses some predefined file as a base for changing some parameters.
Using this base file script generates new one that contains updated values
specified by user.
""")

    parser.add_argument("-s", "--src-conf-file", type=str, required=True,
                        help="path to config file used as base")

    parser.add_argument("-d", "--dst-conf-file", type=str, required=True,
                        help="path to store result")

    parser.add_argument("--s3-instance-nr", type=int, required=True,
                        help="number of s3server instances")
    


    return parser.parse_args()


def read_src_config(src_config_path):
    conf_file_content = list()

    with open(src_config_path) as f:
        for line in f:
            conf_file_content.append(line.rstrip())

    return conf_file_content


def write_dst_config(file_path, lines):
    with open(file_path, 'wt') as f:
        for line in lines:
            f.write(f'{line}\n')


def main():
    args = parse_args()
    conf_file_content = read_src_config(args.src_conf_file)
    line_ids = find_s3server_lines(conf_file_content)
    addr, port, opts = parse_addr_port_options(conf_file_content[line_ids[0]])

    result = patch_file(conf_file_content, line_ids, args.s3_instance_nr,
                        addr, port, opts)

    write_dst_config(args.dst_conf_file, result)


if __name__ == '__main__':
    main()
