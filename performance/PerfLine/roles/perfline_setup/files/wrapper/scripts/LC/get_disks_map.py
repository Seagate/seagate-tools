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
import yaml


def main():
    conf_file = sys.argv[1]
    hostname = sys.argv[2]

    with open(conf_file, 'rt') as f:
        data = yaml.safe_load(f.read())

        data_disks = []
        md_disks = []

        for node in data['node'].values():
            if 'storage' in node and hostname in node['hostname']:
               for cvg in node['storage']['cvg']:
                   data_disks.extend(cvg['devices']['data'])
                   md_disks.extend(cvg['devices']['metadata'])

        if len(data_disks) > 0:
            print('IO: {}'.format(" ".join(data_disks)))

        if len(md_disks) > 0:
            print('MD: {}'.format(" ".join(md_disks)))

if __name__ == "__main__":
    main()
