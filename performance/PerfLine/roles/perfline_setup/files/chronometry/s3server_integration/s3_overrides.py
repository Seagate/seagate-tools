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

def parse_args():
    description="""
    s3_overrides.py: Apply overrides to the specified s3config.yaml
    """

    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("overrides", help="Overrides string in format key=value")
    parser.add_argument("s3config", help="s3config.yaml file")

    return parser.parse_args()

def main():
    args = parse_args()

    data = []
    if args.overrides:
        with open(args.s3config, 'r') as f:
            for line in f.readlines():
                data.append(line)

        for kv in args.overrides.split(" "):
            key, value = kv.split('=')
            for idx, line in enumerate(data):
                if key in line.split(': ')[0]:
                    k = line.split(': ')[0]
                    print(f"Overriding {k} with new value: {value}, old value: {line.split(': ')[1].split('#')[0]}")
                    nl='\n'
                    data[idx] = f"{k}: {value} # Override by s3_overrides.py{nl}"

        with open(args.s3config, 'w') as f:
            for line in data:
                f.write(line)

if __name__ == '__main__':
    main()
