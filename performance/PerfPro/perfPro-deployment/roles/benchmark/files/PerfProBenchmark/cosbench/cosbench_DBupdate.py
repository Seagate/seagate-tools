#!/usr/bin/env python3
"""
python3 cosbench_DBupdate.py <log file path> <main.yaml path> <config.yaml path> <ITR>
Attributes:
_id,Log_File,Name,Operation,IOPS,Throughput,Latency,TTFB,Object_Size,HOST,Objects,Buckets,Session
"""

import csv
import pymongo
from pymongo import MongoClient
import re
import socket
import sys
import os
from os import listdir
import yaml
from datetime import datetime
import urllib.request

Main_path = sys.argv[2]
Config_path = sys.argv[3]
iteration = 1
#sys.argv[4]

def makeconfig(name):  # function for connecting with configuration file
    with open(name) as config_file:
        configs = yaml.load(config_file, Loader=yaml.FullLoader)
    return configs


configs_main = makeconfig(Main_path)  # getting instance  of main file
configs_config = makeconfig(Config_path)  # getting instance  of config file

build_url=configs_config.get('BUILD_URL')
nodes_list=configs_config.get('NODES')
clients_list=configs_config.get('CLIENTS')
pc_full=configs_config.get('PC_FULL')
overwrite=configs_config.get('OVERWRITE')
custom=configs_config.get('CUSTOM')
nodes_num=len(nodes_list)
clients_num=len(clients_list)

def makeconnection():  # function for making connection with database
    # connecting with mongodb database
    client = MongoClient(configs_main['db_url'])
    db = client[configs_main['db_database']]  # database name=performance
    return db



def get_release_info(variable):
    release_info= urllib.request.urlopen(build_url+'RELEASE.INFO')
    for line in release_info:
        if variable in line.decode("utf-8"):
            strinfo=line.decode("utf-8").strip()
            strip_strinfo=re.split(': ',strinfo)
            return(strip_strinfo[1])



def insert_data(file,Build,Version,Config_ID,db,col,Branch,OS):  # function for retriving required data from log files and update into mongodb
    _, filename = os.path.split(file)
    global nodes_num , clients_num , pc_full , iteration , overwrite, custom
    with open(file) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                line_count += 1
            else:
                if(row[1] == "read" or row[1] == "write"):
                    attr = re.split(',|-', filename)
                    obj = attr[1]
                    if('m' in obj) or ('M' in obj):
                        Objsize = int(re.split('m|M', obj)[0])
                    if('k' in obj) or ('K' in obj):
                        Objsize = float(re.split('k|K', obj)[0])*0.001

                    iops = float(row[13])
                    throughput = iops*Objsize
                    lat = {"Max": float(row[12]), "Avg": float(row[5])}
                    # check whether entry with same build -object size -buckets-objects-sessions is presernt or not
                    action = "Updated"
                    operation= row[1]
                    obj_size= attr[1]
                    buckets= int(re.split(" ", attr[2])[1])
                    objects= int(re.split(" ", attr[3])[1])
                    sessions= int(re.split(" ", attr[4])[1])
                    entry = {
                        "Name": "Cosbench", 
                        "Operation": "".join(operation[0].upper() + operation[1:].lower()) , 
                        "Build": Build, 
                        "Version": Version,
                        "Branch": Branch ,
                        "OS": OS, 
                        "Count_of_Servers": nodes_num ,
                        "Count_of_Clients": clients_num , 
                        "Object_Size": str(obj_size.replace(" ","").upper()), 
                        "Buckets": buckets,
                        "Objects": objects, 
                        "Sessions": sessions ,
                        #"Iteration" : iteration ,
                        "Percentage_full" : pc_full ,
                        "Custom" : str(custom).upper()
                        }
                       # 'PKey' : Version[0]+'_'+Branch[0].upper()+'_'+Build+'_ITR'+str(iteration)+'_'+str(nodes_num)+'N_'+str(clients_num)+'C_'+str(pc_full)+'PC_'+str(custom).upper()+'_COS_'+str(obj_size.replace(" ","").upper())+'_'+str(buckets)+'_'+operation[0].upper()+'_'+str(sessions) 
                       # }
                    update_data = {
                        "Log_File": filename, 
                        #"Operation": row[1], 
                        "IOPS": iops, 
                        "Throughput": throughput, 
                        "Latency": lat, 
                        "HOST": socket.gethostname(), 
                        "Config_ID": Config_ID, 
                        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "Iteration" : iteration 
                        }
                    db_data={}
                    db_data.update(entry)
                    db_data.update(update_data)   
                    try:
                        #pattern={'PKey' : entry['PKey']}
                        count_documents = db[col].count_documents(entry)
                        if count_documents == 0:
                            db[col].insert_one(db_data)
                            action = "Inserted"
                        elif overwrite == True: 
                            update_data.update(Iteration=count_documents)
                            db_data.update(update_data)
                            entry.update(Iteration=count_documents)
                            db[col].update_one(entry , {"$set": db_data})
                            action = "Updated"
                        else :
                            update_data.update(Iteration=count_documents+1)
                            db_data.update(update_data)
                            db[col].insert_one(db_data)
                            print("'Overwrite' is false in config. Hence, new DB entry inserted")
                            action = "New iteration inserted"

                    except Exception as e:
                        print("Unable to insert/update documents into database. Observed following exception:")
                        print(e)
                    else:
                        print('Data {} : {}  \n'.format(
                            action, db_data ))
          


# function to return all file names with perticular extension
def getallfiles(directory, extension):
    flist = []
    for path, _, files in os.walk(directory):
        for name in files:
            if(name.lower().endswith(extension)):
                flist.append(os.path.join(path, name))
    return flist

def update_mega_chain(build, version, col):
    cursor = col.find({'Title' : 'Main Chain'})
    beta_chain = cursor[0]['beta']
    #print(beta_chain)
    release_chain = cursor[0]['release']
    #print(release_chain)
    if version == 'release':
        if build not in release_chain:
            print(build)
            release_chain.append(build)
            col.update_one(
                {'Title' : 'Main Chain'},
                {
                    '$set':{
                    'release':release_chain, 
                    }
            })
            print("...Mega entry has updated with release build ", build)
            return
    else:
        if build not in beta_chain:
            print(build)
            beta_chain.append(build)
            col.update_one(
                    {'Title' : 'Main Chain'},
                    {
                        '$set':{
                        'beta':beta_chain, 
                        }
                })
            print("...Mega entry has updated with beta build ", build)
            return
    print("...Mega entry has not updated for build ", build)


def getconfig():
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
    return (dic)


def main(argv):
    dic = argv[1]
    files = getallfiles(dic, "workloadtype.csv")

    Build=get_release_info('BUILD')
    Build=Build[1:-1]
    Version=get_release_info('VERSION')
    Version=Version[1:-1]
    Branch=get_release_info('BRANCH')
    Branch=Branch[1:-1]
    OS=get_release_info('OS')
    OS=OS[1:-1]

    db = makeconnection()  # getting instance  of database
    #col_config = db[configs_main['config_collection']]
    col_config='configurations_'+Version[0]
    dic = getconfig()
    result = db[col_config].find_one(dic)# find entry from configurations collection
    Config_ID = "NA"
    if result:
        Config_ID = result['_id']        # foreign key : it will map entry in configurations to results entry

    #col = db[configs_main['db_collection']]
    col ='results_'+Version[0]

    for f in files:
        insert_data(f,Build,Version,Config_ID,db,col,Branch,OS)
    #update_mega_chain(Build,Version,col)# update mega entry


if __name__ == "__main__":
    main(sys.argv)
