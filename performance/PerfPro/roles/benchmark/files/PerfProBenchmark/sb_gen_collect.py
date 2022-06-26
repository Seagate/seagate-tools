#!/usr/bin/env python3
#
# Seagate-tools: PerfPro
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
"""
Script to collect Support Bundle from SUT and archive it to NFS repository.
"""

from datetime import datetime as DT
import paramiko
import time
import yaml
user_name = "root"
port = 22
nfs_mount_point = "/mnt/support_bundle/"
nfs_loc = "/mnt/support_bundle/PerfPro/support_bundle/"
support_bundle_loc = "/var/log/seagate/support_bundle/"

now = DT.now()
time_string = now.strftime("%m-%d-%Y-%H:%M:%S")

###Reading conf file######
conf_yaml = open('/root/PerfProBenchmark/config.yml')
parse_conf = yaml.safe_load(conf_yaml)

blocked_operators = [";", "&&", "||"]
user_inputs = [parse_conf.get('NODE1'), parse_conf.get('NODE2'), parse_conf.get('NFS_SERVER'),
               parse_conf.get('NFS_EXPORT'), parse_conf.get('BUILD'), parse_conf.get('CLUSTER_PASS')]
print(user_inputs)

for x in user_inputs:
    if x is None:
        continue
    for y in blocked_operators:
        if y in x:
            raise ValueError("Please Sanitize Your Inputs")


node1 = parse_conf.get('NODE1')
node2 = parse_conf.get('NODE2')
nfs_server = parse_conf.get('NFS_SERVER')
nfs_export = parse_conf.get('NFS_EXPORT')
build = parse_conf.get('BUILD')
passwd = parse_conf.get('CLUSTER_PASS')

########################################Node1################################

try:

    #######################################Generate support bundle###############
    cmd1 = "mkdir {}; mount {}:{} {}; cortxcli support_bundle generate {}; mkdir -p {}".format(
        nfs_mount_point, nfs_server, nfs_export, nfs_mount_point, build, nfs_loc)
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(node1, port, user_name, passwd)
    stdin, stdout, stderr = ssh_client.exec_command(cmd1)
    output1 = stdout.readlines()
    bundle_id = (output1[2].strip('|\n').strip('|').strip())

    print("Generating link for support bundle for bundle bundle_id " +
          bundle_id + " in /tmp/support_bundle")

    remotefilepath1 = "{}{}_{}.tar.gz".format(
        support_bundle_loc, bundle_id, node1)
    remotefilepath2 = "{}{}_{}.tar.gz".format(
        support_bundle_loc, bundle_id, node2)


### Code for checking tar.gz file  in /var/log/seagate/support_bundle/  #########

    timeout = 3600
    endtime = time.time() + timeout
    ftp_client = ssh_client.open_sftp()
    while time.time() <= endtime:
        try:
            ftp_client.stat(remotefilepath1)
            print("Generated support bundlle {}_{}.tar.gz".format(bundle_id, node1))
            print("Generated support bundlle {}_{}.tar.gz".format(bundle_id, node2))
            break
        except Exception:
            print("Waiting for sometime as support bundle is being generated for bundle id {}".format(
                bundle_id))
            time.sleep(60)
    ftp_client.close()

    print("Copying support bundle for {} at NFS location".format(bundle_id))

    cmd2 = "mkdir {}{}_{};cp {} {}{}_{}".format(
        nfs_loc, node1, time_string, remotefilepath1, nfs_loc, node1, time_string)
    stdin, stdout, stderr = ssh_client.exec_command(cmd2)
    output2 = stdout.readlines()

####################################### For Node2#####################################

    ssh_client1 = paramiko.SSHClient()
    ssh_client1.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client1.connect(node2, port, user_name, passwd)

    cmd3 = "mkdir {};mount {}:{} {}".format(
        nfs_mount_point, nfs_server, nfs_export, nfs_mount_point)
    cmd4 = "mkdir {}{}_{};cp {} {}{}_{}".format(
        nfs_loc, node2, time_string, remotefilepath2, nfs_loc, node2, time_string)

    stdin, stdout, stderr = ssh_client1.exec_command(cmd3)
    output3 = stdout.readlines()
    stdin, stdout, stderr = ssh_client1.exec_command(cmd4)
    output4 = stdout.readlines()
    time.sleep(120)

#######################################Printing message for copying##################

    print('copied support bundle using ' + str(build) + ' for ' +
          node1 + ' in /PerfPro/support_bundle folder at NFS location')
    print('copied support bundle using ' + str(build) + ' for ' +
          node2 + ' in /PerfPro/support_bundle folder at NFS location')

### Code for checking status for support bundle id######
    print("Checking status for support bundle " + bundle_id)
    cmd11 = "cortxcli support_bundle status {}".format(bundle_id)
    stdin, stdout, stderr = ssh_client.exec_command(cmd11)
    output11 = stdout.readlines()
    print("Printing status for bundle id " + bundle_id)
    for op in output11:
        print(op)
except paramiko.AuthenticationException:
    print("Please check password")
except IndexError:
    print("Support bundle status is not generated yet")
