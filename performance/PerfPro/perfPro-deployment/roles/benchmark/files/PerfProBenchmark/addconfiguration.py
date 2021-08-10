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

build_url=configs_config.get('BUILD_URL')

def get_release_info(variable):
    release_info= urllib.request.urlopen(build_url+'RELEASE.INFO')
    for line in release_info:
        if variable in line.decode("utf-8"):
            strinfo=line.decode("utf-8").strip()
            strip_strinfo=re.split(': ',strinfo)
            return(strip_strinfo[1])


def makeconnection():  #function for making connection with database
    configs = makeconfig(Main_path)
    client = MongoClient(configs['db_url'])  #connecting with mongodb database
    db=client[configs['db_database']]  #database name=performance 
    Version=get_release_info('VERSION')
    Version=Version[1:-1]
#    col_conf='configurations_'+Version[0]
    col_conf=configs.get('R'+Version[0])['config_collection']
    col=db[col_conf]  #collection name = configurations
    return col


def storeconfigurations():
    build_url=configs_config.get('BUILD_URL')
    nodes_list=configs_config.get('NODES')
    clients_list=configs_config.get('CLIENTS')
    pc_full=configs_config.get('PC_FULL')
    custom=configs_config.get('CUSTOM')
    overwrite=configs_config.get('OVERWRITE')
    #iteration=configs_config.get('ITERATION')
    cluster_pass=configs_config.get('CLUSTER_PASS')
    change_pass=configs_config.get('CHANGE_PASS')
    prv_cli=configs_config.get('PRVSNR_CLI_REPO')
    prereq_url=configs_config.get('PREREQ_URL')
    srv_usr=configs_config.get('SERVICE_USER')
    srv_pass=configs_config.get('SERVICE_PASS')
    nfs_serv=configs_config.get('NFS_SERVER')
    nfs_exp=configs_config.get('NFS_EXPORT')
    nfs_mp=configs_config.get('NFS_MOUNT_POINT')
    nfs_fol=configs_config.get('NFS_FOLDER')

    dic={'NODES' :str(nodes_list) , 'CLIENTS' : str(clients_list) ,'BUILD_URL': build_url ,'CLUSTER_PASS': cluster_pass ,'CHANGE_PASS': change_pass ,'PRVSNR_CLI_REPO': prv_cli ,'PREREQ_URL': prereq_url ,'SERVICE_USER': srv_usr ,'SERVICE_PASS': srv_pass , 'PC_FULL': pc_full , 'CUSTOM': custom , 'OVERWRITE':overwrite , 'NFS_SERVER': nfs_serv ,'NFS_EXPORT' : nfs_exp ,'NFS_MOUNT_POINT' : nfs_mp , 'NFS_FOLDER' : nfs_fol }
    col = makeconnection()
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
