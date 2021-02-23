#!/usr/bin/python3
'''
Return disk partitions on servernodes provided cluster file and 
python3 extract_disks.py <cluster config file> <assigned ips>
python3 extract_disks.py /var/lib/hare/cluster.yaml $(ifconfig | grep inet | awk '{print $2}')
'''
import sys
import yaml

cluster_config_file = sys.argv[1] 
assigned_IPs = sys.argv[2:]
hosts_file_path = '/etc/hosts'

def check_IPs(hosts_file_path): # function to check IPs present for all nodes
    host_file_lines = open(hosts_file_path).readlines()
    
    ips_map = {}
    node = 0
    for line in host_file_lines:
        if 'srvnode' in line:
            node+=1
            try:
                ips_map['srvnode-{}'.format(node)] = line.split()[0]
            except Exception as e:
                # print("IP not found for node {}, occured Exception : {}".format(node,e))
                ips_map['srvnode-{}'.format(node)] = None # add None if not found
    return ips_map

def get_disks(ips_map, ips): # returns disks from cluster config file
    for node in range(1, len(ips_map)+1):
        ip = ips_map['srvnode-{}'.format(node)]
        try:
            if ip and ip in ips: # checks for ips in assigned ips
                with open(sys.argv[1], 'r') as config_file:
                    config = yaml.safe_load(config_file)
                disks = config['nodes'][node-1]['m0_servers'][1]['io_disks']['data']

                return disks, node
        except Exception as e:
            # print("Exception during getting disks : {}".format(e))
            pass
    return None # returns none if not found
  
    
def main():
    ips_map = check_IPs(hosts_file_path)
    disks, node = get_disks(ips_map, assigned_IPs)
    if disks:
        print(node)
        print(' '.join(disks))
if __name__ == "__main__":
    main()
