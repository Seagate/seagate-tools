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

import argparse
import sys
import yaml
import ast

def parse_args():
    parser = argparse.ArgumentParser(prog=sys.argv[0],
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description="""
customize_s3_conf.py is a tool to generating customized config file for S3 server.
Script uses some predefined file as a base for changing some parameters.
Using this base file script generates new one that contains updated values
specified by user.

Example of usage:
$ ./customize_s3_conf.py -s /opt/seagate/cortx/s3/conf/s3config.yaml
                         -d /opt/seagate/cortx/s3/conf/s3config.yaml
                         --s3-srv-param "S3_DI_DISABLE_DATA_CORRUPTION_IEM=False"
                         --s3-auth-param "S3_AUTH_IP_ADDR='ipv4:127.0.0.1'"
                         --s3-motr-param "S3_MOTR_LOCAL_ADDR='<ipaddress>@tcp:12345:33:100'"
                         --s3-thirdparty-param "S3_LIBEVENT_POOL_BUFFER_SIZE=16384"
""")

    parser.add_argument("-s", "--src-conf-file", type=str, required=True,
                        help="path to config file used as base")

    parser.add_argument("-d", "--dst-conf-file", type=str, required=True,
                        help="path to store result")

    parser.add_argument("--s3-srv-param", action='append', required=False,
                        help="""parameter of S3_SERVER_CONFIG section
                        to be overrided in a form 'PARAM_NAME=PARAM_VALUE'""")

    parser.add_argument("--s3-auth-param", action='append', required=False,
                        help="""parameter of S3_AUTH_CONFIG section
                        to be overrided in a form 'PARAM_NAME=PARAM_VALUE'""")

    parser.add_argument("--s3-motr-param", action='append', required=False,
                        help="""parameter of S3_MOTR_CONFIG section
                        to be overrided in a form 'PARAM_NAME=PARAM_VALUE'""")

    parser.add_argument("--s3-thirdparty-param", action='append', required=False,
                        help="""parameter of S3_THIRDPARTY_CONFIG section
                        to be overrided in a form 'PARAM_NAME=PARAM_VALUE'""")

    return parser.parse_args()


def read_src_config(src_config_path):
    with open(src_config_path) as f:
        return yaml.safe_load(f.read())


def write_dst_config(cdf_data, dst_config_path):
    with open(dst_config_path, 'wt') as f:
        f.write(yaml.dump(cdf_data))


def override_param(conf_data, section_name, param_name, param_val_str):
    param_val = ast.literal_eval(param_val_str)
    print(f'overriding {section_name}:{param_name} to {param_val_str}')
    conf_data[section_name][param_name] = param_val


def main():
    args = parse_args()
    conf_data = read_src_config(args.src_conf_file)

    if args.s3_srv_param is not None:
        for key_val in args.s3_srv_param:
            key, val = key_val.split('=')
            override_param(conf_data, 'S3_SERVER_CONFIG', key, val)

    if args.s3_auth_param is not None:
        for key_val in args.s3_auth_param:
            key, val = key_val.split('=')
            override_param(conf_data, 'S3_AUTH_CONFIG', key, val)

    if args.s3_motr_param is not None:
        for key_val in args.s3_motr_param:
            key, val = key_val.split('=')
            override_param(conf_data, 'S3_MOTR_CONFIG', key, val)

    if args.s3_thirdparty_param is not None:
        for key_val in args.s3_thirdparty_param:
            key, val = key_val.split('=')
            override_param(conf_data, 'S3_THIRDPARTY_CONFIG', key, val)

    write_dst_config(conf_data, args.dst_conf_file)


if __name__ == '__main__':
    main()
