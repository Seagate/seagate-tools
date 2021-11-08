#!/usr/bin/env python3


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
            if node['type'] != 'storage_node':
                continue
            
            if hostname not in node['hostname']:
                continue

            # print(node['hostname'])

            for cvg in node['storage']['cvg']:
                data_disks.extend(cvg['devices']['data'])
                md_disks.extend(cvg['devices']['metadata'])

            if len(data_disks) > 0:
                print('IO: {}'.format(" ".join(data_disks)))
            
            if len(md_disks) > 0:
                print('MD: {}'.format(" ".join(md_disks)))


if __name__ == "__main__":
    main()
