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


def parse_args():
    parser = argparse.ArgumentParser(prog=sys.argv[0],
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description="""
customize_hare_conf.py is a tool to generating customized CDF file.
Script uses some predefined CDF file as a base for changing some parameters.
Using this base file script generates new CDF with updated values
specified by user.
""")

    parser.add_argument("-s", "--src-conf-file", type=str, required=True,
                        help="path to hare config file used as base CDF")

    parser.add_argument("-d", "--dst-conf-file", type=str, required=True,
                        help="path to store result")

    parser.add_argument("--sns-data-units", type=int,
                        help="set new value for sns data units")

    parser.add_argument("--sns-parity-units", type=int,
                        help="set new value for sns parity units")

    parser.add_argument("--sns-spare-units", type=int,
                        help="set new value for sns spare units")

    parser.add_argument("--dix-data-units", type=int,
                        help="set new value for dix data units")

    parser.add_argument("--dix-parity-units", type=int,
                        help="set new value for dix parity units")

    parser.add_argument("--dix-spare-units", type=int,
                        help="set new value for dix spare units")

    parser.add_argument("--s3-instance-nr", type=int,
                        help="set new s3 instances number")

    return parser.parse_args()


def read_src_config(src_config_path):
    with open(src_config_path) as f:
        return yaml.safe_load(f.read())


def write_dst_config(cdf_data, dst_config_path):
    with open(dst_config_path, 'wt') as f:
        f.write(yaml.dump(cdf_data))


def find_pool(cdf_data, pool_type):
    pools = cdf_data['pools']

    for pool in pools:
        if pool['type'] == pool_type:
            return pool

    return None


def override_units_value(cdf_data, pool_type, units_type, new_value):
    pool = find_pool(cdf_data, pool_type)

    if pool is None:
        print(f'pool not found: {pool_type}')
        return

    print(f'update {units_type} to {new_value} for {pool_type} pool')
    pool[units_type] = new_value


def override_s3_instance_nr(cdf_data, s3_instance_nr):
    for node in cdf_data['nodes']:
        node['m0_clients']['s3'] = s3_instance_nr


def main():
    args = parse_args()
    cdf_data = read_src_config(args.src_conf_file)

    if args.sns_data_units is not None:
        override_units_value(cdf_data, 'sns', 'data_units', args.sns_data_units)

    if args.sns_parity_units is not None:
        override_units_value(cdf_data, 'sns', 'parity_units', args.sns_parity_units)

    if args.sns_spare_units is not None:
        override_units_value(cdf_data, 'sns', 'spare_units', args.sns_spare_units)

    if args.dix_data_units is not None:
        override_units_value(cdf_data, 'dix', 'data_units', args.dix_data_units)

    if args.dix_parity_units is not None:
        override_units_value(cdf_data, 'dix', 'parity_units', args.dix_parity_units)

    if args.dix_spare_units is not None:
        override_units_value(cdf_data, 'dix', 'spare_units', args.dix_spare_units)

    if args.s3_instance_nr is not None:
        override_s3_instance_nr(cdf_data, args.s3_instance_nr)

    write_dst_config(cdf_data, args.dst_conf_file)


if __name__ == '__main__':
    main()
