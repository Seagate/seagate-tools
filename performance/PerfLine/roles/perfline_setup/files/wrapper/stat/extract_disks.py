#!/usr/bin/env python3
#
# Copyright (c) 2020 Seagate Technology LLC and/or its Affiliates
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
# For any questions about this software or licensing,
# please email opensource@seagate.com or cortx-questions@seagate.com.
#

'''
Return disk partitions on servernodes provided cluster file and
python3 extract_disks.py <cluster config file> <assigned ips>
python3 extract_disks.py /var/lib/hare/cluster.yaml $(ifconfig | grep inet | awk '{print $2}')
'''
import sys
import yaml
import re

cluster_config_file = sys.argv[1]
assigned_IPs = sys.argv[2:]
hosts_file_path = '/etc/hosts'

def check_IPs(hosts_file_path): # function to check IPs present for all nodes
    host_file_lines = open(hosts_file_path).readlines()

    srv_node_pattern = r'srvnode-(?P<node_id>[0-9]+)'

    ips_map = {}
    for line in host_file_lines:
        if not line.strip().startswith("#"):
           match_res = re.search(srv_node_pattern, line)
           if match_res:
               try:
                   ips_map['srvnode-{}'.format(match_res.group('node_id'))] = line.split()[0]
               except Exception as e:
                   print(f"Error: {e}")
    return ips_map

def get_disks(ips_map, ips): # returns disks from cluster config file
    for node in range(1, len(ips_map)+1):
        ip = ips_map['srvnode-{}'.format(node)]
        try:
            if ip and ip in ips: # checks for ips in assigned ips
                with open(sys.argv[1], 'r') as config_file:
                    config = yaml.safe_load(config_file)

                disks = []
                md_disks = []

                for m0_server in config['nodes'][node-1]['m0_servers']:
                    disks.extend(m0_server['io_disks']['data'])

                    if 'meta_data' in m0_server['io_disks']:
                        md_disk = m0_server['io_disks']['meta_data']
                        if md_disk:
                            md_disks.append(md_disk)

                return disks, md_disks, node
        except Exception as e:
            print(f"Error: {e}")
    return None # returns none if not found


def main():
    ips_map = check_IPs(hosts_file_path)
    disks, md_disks, node = get_disks(ips_map, assigned_IPs)
    if disks:
        print(node)
        print('IO:' + ' '.join(disks))
        print('MD:' + ' '.join(md_disks))
if __name__ == "__main__":
    main()
