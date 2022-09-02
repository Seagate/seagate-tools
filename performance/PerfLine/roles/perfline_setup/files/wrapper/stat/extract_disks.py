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

'''
Return disk partitions on servernodes provided cluster file and
python3 extract_disks.py <cluster config file>
python3 extract_disks.py /var/lib/hare/cluster.yaml
'''
import sys
import yaml

cluster_config_file = sys.argv[1]

def get_disks(): # returns disks from cluster config file
        try:
           with open(sys.argv[1], 'r') as config_file:
               config = yaml.safe_load(config_file)

           disks = []
           md_disks = []

           for machine in config['cluster']['storage_set'][0]['nodes']:
               if "cvg" in config['node'][machine]:
                   for m0_server in config['node'][machine]['cvg']:
                       disks.extend(m0_server['devices']['data'])
                       if 'metadata' in m0_server['devices']:
                           md_disk = m0_server['devices']['metadata']
                           if md_disk:
                               md_disks.extend(md_disk)

           return disks, md_disks
        except Exception as e:
            print(f"Error: {e}")

def main():
    disks, md_disks = get_disks()
    if disks:
        print('IO:' + ' '.join(set(disks)))
        print('MD:' + ' '.join(set(md_disks)))

if __name__ == "__main__":
    main()
