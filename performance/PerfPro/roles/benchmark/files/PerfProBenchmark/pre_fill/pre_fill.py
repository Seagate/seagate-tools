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
Script helps in filling up SUT upto the given Prefill percentage defined in config.yml
"""

import sys
import paramiko
import yaml
import re
import subprocess

conf_yaml = open(sys.argv[1])
parse_conf = yaml.safe_load(conf_yaml)

nodes = parse_conf.get('NODES')
node1 = nodes[0][1]
passwd = parse_conf.get('CLUSTER_PASS')
PC_full = parse_conf.get('PC_FULL')
endpoints = parse_conf.get('END_POINTS')

prebench = sys.argv[2]

"""
Function to make SSH connection to SUT Node1 run the command
Input : command to run on server
Returns : Response of the the command.
"""


def server(cmd):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=node1, port='22', username='root', password=passwd)
    command = cmd
    _, stdout, _ = ssh.exec_command(command)
    out = stdout.readlines()
    resp = ''.join(out)
    return (resp)


result = server('hctl status --json')

"""
Function to read values of Total and Available disk size.
Input : string with variable and value
Returns : Value
"""


def read_result(value):
    for line in result.split("\n"):
        if (value in line):
            strip = line.strip()
            strip_r = re.split(': |,', strip)
            return(strip_r[1])


total_disk = int(read_result("fs_total_disk"))
avail_disk = int(read_result("fs_avail_disk"))


print('Total_disk (B):', total_disk, '\nAvailble_disk (B):', avail_disk)

pre_fill = int(total_disk*PC_full/100)

print('PC_Full % :', PC_full, '\nPre_Fill data size (B):', pre_fill)

"""
Function to call and run prefill s3bench shell script.
Input : Size of disk needed to filled.
Retuns : NONE
Invokes : Prefill shell script
"""


def fill_data(pre_fill):
    obj_size = 128
    Pre_fill_mb = int(pre_fill/1048576)
    num_obj = int(Pre_fill_mb/obj_size)
    num_bucket = 10
    num_obj_per_bucket = int(num_obj/num_bucket)
    num_clients = 200
    print('pre_fill size(MB) :', Pre_fill_mb,
          '\nNumber of objects per bucket(10 buckets)(128Mb Object size)', num_obj_per_bucket)
    for i in range(num_bucket):
        subprocess.call([f"/{prebench}", "-ep", f"{str(endpoints)}", "-nc", f"{num_clients}",
                        "-ns", f"{num_obj_per_bucket}", "-s", f"{str(obj_size)+'Mb'}", "-nb", f"{i}"])


""" Function to decide if prefill needs to run and prefill size """


def pre_fill_calc():
    if (avail_disk == total_disk):
        PF = pre_fill
        print('System will be filled with size of data: ', PF)

    elif (avail_disk >= total_disk-pre_fill):
        PF = pre_fill-(total_disk-avail_disk)
        print('System will be filled with size of data: ', PF)

    elif (avail_disk < total_disk-pre_fill):
        print(
            'Avail disk space on system is less than or equals to required Pre filled data')
        return

    fill_data(PF)


pre_fill_calc()
