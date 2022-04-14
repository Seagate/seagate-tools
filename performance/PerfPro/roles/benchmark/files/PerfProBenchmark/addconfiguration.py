#!/usr/bin/env python3
"""
Script for storing configuration file data into MongoDB
Command line arguments:   [path for main.yml] [path for config.yml]
  Ex: python3 addconfiguration.py <Path of main.yml file> <Path of config.yml file>
Requirements:
pip3 install PyYAML==5.3.1
pip3 install pymongo==3.11.0
"""

import pymongo
from pymongo import MongoClient
import yaml
import sys
import urllib.request
import re

Main_path = sys.argv[1]
Config_path = sys.argv[2]


def makeconfig(name):  #function for connecting with configuration file
	with open(name) as config_file:
		configs = yaml.load(config_file, Loader=yaml.FullLoader)
	return configs


configs_config = makeconfig(Config_path)  # getting instance  of config file

build_info=str(configs_config.get('BUILD_INFO'))
build_url=configs_config.get('BUILD_URL')
solution=configs_config.get('SOLUTION')

def get_release_info(variable):
    release_info= urllib.request.urlopen(build_url+'RELEASE.INFO')
    for line in release_info:
        if variable in line.decode("utf-8"):
            strinfo=line.decode("utf-8").strip()
            strip_strinfo=re.split(': ',strinfo)
            return(strip_strinfo[1])


def makeconnection(collection):  #function for making connection with database
    configs = makeconfig(Main_path)
    client = MongoClient(configs['db_url'])  #connecting with mongodb database
    db=client[configs['db_database']]  #database name=performance
    if solution.upper() == 'LC':
        col_stats=configs.get('LC')[collection]
    elif solution.upper() == 'LR':
        col_stats=configs.get('LR')[collection]
    elif solution.upper() == 'LEGACY':
       if build_info == 'RELEASE.INFO':
           Version=get_release_info('VERSION')
           Version=Version[1:-1]
       elif build_info == 'USER_INPUT':
           Version=configs_config.get('VERSION')
       col_stats=configs.get('R'+Version[0])[collection]
    else:
        print("Error! Can not find suitable collection to upload data")
    col=db[col_stats]  #collection name = configurations
    return col


def storeconfigurations():
    nodes_list=configs_config.get('NODES')
    clients_list=configs_config.get('CLIENTS')
    build_info=configs_config.get('BUILD_INFO')
    build_url=configs_config.get('BUILD_URL')
    build=configs_config.get('BUILD')
    version=configs_config.get('VERSION')
    branch=configs_config.get('BRANCH')
    os=configs_config.get('OS')
    execution_type=configs_config.get('EXECUTION_TYPE')
    cluster_pass=configs_config.get('CLUSTER_PASS')
    solution=configs_config.get('SOLUTION')
    end_points=configs_config.get('END_POINTS')
    system_stats=configs_config.get('SYSTEM_STATS')
    pc_full=configs_config.get('PC_FULL')
    custom=configs_config.get('CUSTOM')
    overwrite=configs_config.get('OVERWRITE')
    degraded_IO=configs_config.get('DEGRADED_IO')
    copy_object=configs_config.get('COPY_OBJECT')
    nfs_serv=configs_config.get('NFS_SERVER')
    nfs_exp=configs_config.get('NFS_EXPORT')
    nfs_mp=configs_config.get('NFS_MOUNT_POINT')
    nfs_fol=configs_config.get('NFS_FOLDER')

    nodes=[]
    clients=[]

    for i in range(len(nodes_list)):
        nodes.append(nodes_list[i][i+1])

    for i in range(len(clients_list)):
        clients.append(clients_list[i][i+1])

    dic={
        'NODES' :str(nodes) , 
        'CLIENTS' : str(clients) ,
        'BUILD_INFO': build_info ,
        'BUILD_URL': build_url ,
        'BUILD': build ,
        'VERSION': version ,
        'BRANCH': branch ,
        'OS': os ,
        'EXECUTION_TYPE': execution_type,
        'CLUSTER_PASS': cluster_pass ,
        'SOLUTION' : solution ,
        'END_POINTS' : end_points ,
        'SYSTEM_STATS' : system_stats ,
        'PC_FULL' : pc_full ,
        'CUSTOM' : custom ,
        'OVERWRITE' : overwrite ,
        'DEGRADED_IO' : degraded_IO ,
        'COPY_OBJECT' : copy_object ,
        'NFS_SERVER': nfs_serv ,
        'NFS_EXPORT' : nfs_exp ,
        'NFS_MOUNT_POINT' : nfs_mp , 
        'NFS_FOLDER' : nfs_fol 
        }
    col = makeconnection('config_collection')
    try:
        count_documents= col.count_documents(dic)
        if count_documents == 0:
            col.insert_one(dic)
            print('Configuration Data is Recorded ::')
            print(dic)
        else:
            print('Configuration data already present')
    except Exception as e:
        print("Unable to insert/update documents into database. Observed following exception:")
        print(e)


def main(argv):
    storeconfigurations()
if __name__=="__main__":
    main(sys.argv) 
