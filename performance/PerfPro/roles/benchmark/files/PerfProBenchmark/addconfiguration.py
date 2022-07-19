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
Script for storing configuration file data into MongoDB
Command line arguments:   [path for main.yml] [path for config.yml]
  Ex: python3 addconfiguration.py <Path of main.yml file> <Path of config.yml file>
Requirements:
pip3 install PyYAML==5.3.1
pip3 install pymongo==3.11.0
"""

from pymongo import MongoClient
import yaml
import sys
import os
import re

Main_path = sys.argv[1]
Config_path = sys.argv[2]


def makeconfig(name):  # function for connecting with configuration file
    ''' Function to connect with configuration file to fetch the details of the file '''
    with open(name) as config_file:
        configs = yaml.safe_load(config_file)
    return configs


configs_config = makeconfig(Config_path)  # getting instance  of config file

build_info = str(configs_config.get('BUILD_INFO'))
solution = configs_config.get('SOLUTION')


def get_release_info(variable):
    '''
    Function to get the release info from the Docker image.
    It returns the value for the variable which is required by the script.
    '''
    release_info = os.popen('cat /root/PerfProBenchmark/RELEASE.INFO')
    lines = release_info.readlines()
    for line in lines:
        if variable in line:
            strinfo = line.strip()
            strip_strinfo = re.split(': ', strinfo)
            return(strip_strinfo[1])


def makeconnection(collection):  # function for making connection with database
    '''
    Function to connect to the Database and fetch the DB details and add data to DB throughout the script execution
    '''
    configs = makeconfig(Main_path)
    client = MongoClient(configs['db_url'])  # connecting with mongodb database
    db = client[configs['db_database']]  # database name=performance
    if solution.upper() == 'LC':
        col_stats = configs.get('LC')[collection]
    elif solution.upper() == 'LR':
        col_stats = configs.get('LR')[collection]
    elif solution.upper() == 'LEGACY':
        if build_info == 'RELEASE.INFO':
            version = get_release_info('VERSION')[1:-1]
            ver_strip = re.split('-', version)
            Version = ver_strip[0]
        elif build_info == 'USER_INPUT':
            Version = configs_config.get('VERSION')
        col_stats = configs.get('R'+Version[0])[collection]
    else:
        print("Error! Can not find suitable collection to upload data")
    col = db[col_stats]  # collection name = configurations
    return col


def storeconfigurations():
    ''' Function to store config data from config.yml to configuration collection '''
    nodes_list = configs_config.get('NODES')
    clients_list = configs_config.get('CLIENTS')
    build_info = configs_config.get('BUILD_INFO')
    build_url = configs_config.get('BUILD_URL')
    build = configs_config.get('BUILD')
    version = configs_config.get('VERSION')
    branch = configs_config.get('BRANCH')
    os = configs_config.get('OS')
    execution_type = configs_config.get('EXECUTION_TYPE')
    cluster_pass = configs_config.get('CLUSTER_PASS')
    solution = configs_config.get('SOLUTION')
    end_points = configs_config.get('END_POINTS')
    system_stats = configs_config.get('SYSTEM_STATS')
    pc_full = configs_config.get('PC_FULL')
    custom = configs_config.get('CUSTOM')
    overwrite = configs_config.get('OVERWRITE')
    degraded_IO = configs_config.get('DEGRADED_IO')
    copy_object = configs_config.get('COPY_OBJECT')
    nfs_serv = configs_config.get('NFS_SERVER')
    nfs_exp = configs_config.get('NFS_EXPORT')
    nfs_mp = configs_config.get('NFS_MOUNT_POINT')
    nfs_fol = configs_config.get('NFS_FOLDER')

    nodes = []
    clients = []

    for i, _ in enumerate(nodes_list):
        nodes.append(nodes_list[i][i+1])

    for i, _ in enumerate(clients_list):
        clients.append(clients_list[i][i+1])

    dic = {
        'NODES': str(nodes),
        'CLIENTS': str(clients),
        'BUILD_INFO': build_info,
        'BUILD_URL': build_url,
        'BUILD': build,
        'VERSION': version,
        'BRANCH': branch,
        'OS': os,
        'EXECUTION_TYPE': execution_type,
        'CLUSTER_PASS': cluster_pass,
        'SOLUTION': solution,
        'END_POINTS': end_points,
        'SYSTEM_STATS': system_stats,
        'PC_FULL': pc_full,
        'CUSTOM': custom,
        'OVERWRITE': overwrite,
        'DEGRADED_IO': degraded_IO,
        'COPY_OBJECT': copy_object,
        'NFS_SERVER': nfs_serv,
        'NFS_EXPORT': nfs_exp,
        'NFS_MOUNT_POINT': nfs_mp,
        'NFS_FOLDER': nfs_fol
    }
    col = makeconnection('config_collection')
    try:
        count_documents = col.count_documents(dic)
        if count_documents == 0:
            col.insert_one(dic)
            print('Configuration Data is Recorded ::')
            print(dic)
        else:
            print('Configuration data already present')
    except Exception as e:
        print(
            "Unable to insert/update documents into database. Observed following exception:")
        print(e)


def main(argv):
    '''Main function for storing configuration data in DB'''
    storeconfigurations()


if __name__ == "__main__":
    main(sys.argv)
