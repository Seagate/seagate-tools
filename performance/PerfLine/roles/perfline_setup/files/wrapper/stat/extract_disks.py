#!/usr/bin/python3
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
        if not line.startswith("#"):
           match_res = re.search(srv_node_pattern, line)
           if match_res:
               try:
                   ips_map['srvnode-{}'.format(match_res.group('node_id'))] = line.split()[0]
               except Exception as e:
                   pass
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
            pass
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
