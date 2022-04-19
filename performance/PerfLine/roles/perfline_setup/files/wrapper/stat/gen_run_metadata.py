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
import json
import argparse

from os.path import isfile, join


PIDS_FILE_PATH = 'pids.txt'


def parse_args():
    parser = argparse.ArgumentParser(prog=sys.argv[0])
    parser.add_argument("-a", "--artifacts-dir", type=str, required=True,
                        help="path to artifacts directory")
    parser.add_argument("-o", "--output-file", type=str, required=True,
                        help="path to output file")
    return parser.parse_args()


def get_pids(artifacts_dir):
    pids_file = join(artifacts_dir, PIDS_FILE_PATH)

    if not isfile(pids_file):
        print(f'file not found: {pids_file}')
        return None

    result = dict()

    with open(pids_file) as f:
        for line in f:
            line = line.strip()

            if line == '':
                continue

            line_parts = line.split()

            if len(line_parts) != 3:
                print('invalid format')
                return None

            hostname, app_name, pid = line_parts

            if hostname not in result:
                result[hostname] = dict()

            if app_name not in result[hostname]:
                result[hostname][app_name] = list()

            result[hostname][app_name].append(int(pid))

    return result


def main():
    args = parse_args()
    artifacts_dir = args.artifacts_dir
    md_file_path = args.output_file

    run_metadata = dict()
    pids = get_pids(artifacts_dir)

    if pids:
        run_metadata['pids'] = pids

    with open(md_file_path, 'wt') as f:
        f.write(json.dumps(run_metadata))


if __name__ == "__main__":
    main()
