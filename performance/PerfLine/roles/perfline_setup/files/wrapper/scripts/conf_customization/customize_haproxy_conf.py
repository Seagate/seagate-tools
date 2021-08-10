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

    options = []
    if len(parts) > 3:
        options = parts[3:]

    addr, port = addr_port.split(':')

    return addr, int(port), options


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

    parser.add_argument("--maxconn-per-s3-instance", type=int, required=False,
                        help="max connections number per s3 server instance")

    parser.add_argument("--maxconn-total", type=int, required=False,
                        help="total max connections number")

    parser.add_argument("--nbproc", type=int, required=False,
                        help="""run HAProxy in multiprocess mode
                                using the specified number of processes""")

    parser.add_argument("--nbthread", type=int, required=False,
                        help="""run HAProxy in multithread mode
                                using the specified number of threads""")

    return parser.parse_args()


def read_src_config(src_config_path):
    file_content = list()

    with open(src_config_path) as f:
        for line in f:
            file_content.append(line.rstrip())

    return file_content


def write_dst_config(file_path, lines):
    with open(file_path, 'wt') as f:
        for line in lines:
            f.write(f'{line}\n')


def find_section(file_content, section_name):
    section_start = None
    section_end = None

    for ln, line in enumerate(file_content):
        line = line.strip()

        if line.startswith('#') or line == '':
            continue

        if line.startswith(section_name):
            section_start = ln
            continue

        if section_start is not None:
            for s in ('global', 'defaults', 'frontend', 'backend'):
                if line.startswith(s):
                    section_end = ln
                    break
            if section_end is not None:
                break
    
    if section_start is None:
        raise Exception(f'section {section_name} not found')

    if section_end is None:
        section_end = len(file_content)

    return section_start, section_end


def get_option_args(file_content, section_name, option_name):
    section_start, section_end = find_section(file_content, section_name)
    option_ln = None

    for ln in range(section_start, section_end):
        line = file_content[ln].strip()
        
        if line.startswith(option_name):
            option_ln = ln
            break

    if option_ln is None:
        return None

    option_line = file_content[option_ln].strip()

    comment_position = option_line.find("#")
    if comment_position != -1:
        option_line = option_line[0:comment_position].strip()
    
    return option_line.split()[1:]


def put_option(file_content, section_name, option_name, args = None):
    section_start, section_end = find_section(file_content, section_name)
    option_ln = None

    for ln in range(section_start, section_end):
        line = file_content[ln].strip()
        
        if line.startswith(option_name):
            option_ln = ln
            break

    new_val = f'    {option_name}'
    if args is not None:
        new_val += ' ' + ' '.join(args)

    if option_ln is not None:
        file_content[option_ln] = f'{new_val} # overrided by customize_haproxy_conf.py'
    else:
        file_content.insert(section_start + 1, f'{new_val} # added by customize_haproxy_conf.py')


def put_lines(file_content, position, lines):
    for line in lines:
        file_content.insert(position, line)
        position += 1


def del_options(file_content, section_name, option_name):
    section_start, section_end = find_section(file_content, section_name)
    option_line_indexes = []

    for ln in range(section_start, section_end):
        line = file_content[ln].strip()
        
        if line.startswith(option_name):
            option_line_indexes.append(ln)

    deleted_lines_nr = 0
    first_deleted_line = None

    for del_ln in option_line_indexes:
        line_index = del_ln - deleted_lines_nr
        d_line = file_content.pop(line_index)
        if first_deleted_line is None:
            first_deleted_line = d_line
        deleted_lines_nr += 1

    if len(option_line_indexes) > 0:
        return option_line_indexes[0], first_deleted_line
    else:
        return None, None


def prepare_server_items(instance_nr, addr, port_start, options,
                         new_maxconn_val = None):
    result = []

    if new_maxconn_val is not None:
        try:
            maxconn_index = options.index('maxconn')
            options[maxconn_index + 1] = str(new_maxconn_val)
        except ValueError:
            options.append('maxconn')
            options.append(str(new_maxconn_val))

    options_str = ' '.join(options)

    for i in range(0, instance_nr):
        instance_id = i + 1
        port = port_start + i
        result.append(S3SERVER_ENTRY_FORMAT.format(instance_id, addr, port,
                                                   options_str))

    return result


def process_maxconn_total_arg(file_content, maxconn_total):
    put_option(file_content, 'frontend s3-main', 'maxconn', [str(maxconn_total)])

    # We need to have global:maxconn value equal or bigger
    # than frontend:maxconn.
    # All details may be found here:
    # https://www.haproxy.com/blog/protect-servers-with-haproxy-connection-limits-and-queues/

    # check global:maxconn value
    global_maxconn_args = get_option_args(file_content, 'global', 'maxconn')
    if global_maxconn_args is None:
        print(f'added global:maxconn option with value {maxconn_total}')
        put_option(file_content, 'global', 'maxconn', [str(maxconn_total)])
    else:
        global_maxconn_val = int(global_maxconn_args[0])
        if global_maxconn_val < maxconn_total:
            print(f'overrided global:maxconn option from {global_maxconn_val} to {maxconn_total}')
            put_option(file_content, 'global', 'maxconn', [str(maxconn_total)])


def process_nbproc_arg(file_content, nbproc):
    del_options(file_content, 'global', 'nbthread')
    print(f'set global:nbproc to {nbproc}')
    put_option(file_content, 'global', 'nbproc', [str(nbproc)])


def process_nbthread_arg(file_content, nbthread):
    del_options(file_content, 'global', 'nbproc')
    print(f'set global:nbthread to {nbthread}')
    put_option(file_content, 'global', 'nbthread', [str(nbthread)])


def process_s3_instance_nr_arg(file_content, s3_instance_nr,
                               maxconn_per_s3_instance):
    # remove old 'server' options from 'backend' section
    position, srv_desc = del_options(file_content, 'backend s3-main', 'server')
    # parse addr, port and options from old 'server' record
    addr, port, opts = parse_addr_port_options(srv_desc)
    servers = prepare_server_items(s3_instance_nr, addr, port, opts,
                                   new_maxconn_val=maxconn_per_s3_instance)

    put_lines(file_content, position, servers)


def main():
    args = parse_args()
    file_content = read_src_config(args.src_conf_file)

    if args.nbproc is not None and args.nbthread is not None:
        raise Exception('Incompatible arguments. Please choose only one option from --nbproc/--nbthread')

    if args.maxconn_total is not None:
        process_maxconn_total_arg(file_content, args.maxconn_total)

    if args.nbproc is not None:
        process_nbproc_arg(file_content, args.nbproc)

    if args.nbthread is not None:
        process_nbthread_arg(file_content, args.nbthread)

    process_s3_instance_nr_arg(file_content, args.s3_instance_nr,
                               args.maxconn_per_s3_instance)

    write_dst_config(args.dst_conf_file, file_content)


if __name__ == '__main__':
    main()
