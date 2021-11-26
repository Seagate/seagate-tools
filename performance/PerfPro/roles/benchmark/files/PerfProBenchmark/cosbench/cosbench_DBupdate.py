#!/usr/bin/env python3
"""
python3 cosbench_DBupdate.py <log file path> <main.yaml path> <config.yaml path> 
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

##Function to find latest iteration
def get_latest_iteration(query, db, collection):
    max = 0
    cursor = db[collection].find(query)
    for record in cursor:
        if max < record['Iteration']:
            max = record['Iteration']
    return max

##Function to resolve iteration/overwrite etc in multi-client run
def check_first_client(query, db, collection, itr):
    query.update(Iteration=itr)
    cursor = db[collection].distinct('HOST', query)
    if (len(cursor) < query["Count_of_Clients"]):
        cur_client = socket.gethostname()
        if cur_client in cursor:
            print(f"Multi-Client Run: Re-Upload from client {cur_client} detected. Existing data in DB from this client for current run will get overwritten")
            query.update(HOST=cur_client)
            db[collection].delete_many(query)
        return False
    return True

def insert_data(files,Build,Version,Config_ID,db,col,Branch,OS):  # function for retriving required data from log files and update into mongodb
    find_iteration = True
    first_client = True
    delete_data = True
    iteration_number = 0
    global nodes_num , clients_num , pc_full  , overwrite, custom
    for file in files:
        _, filename = os.path.split(file)
        try:
            Run_Health = "Successful"
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
                            operation= row[1]
                            obj_size= attr[1]
                            buckets= int(re.split(" ", attr[2])[1])
                            objects= int(re.split(" ", attr[3])[1])
                            sessions= int(re.split(" ", attr[4])[1])
                            primary_Set = {
                                "Name": "Cosbench", 
                                "Build": Build, 
                                "Version": Version,
                                "Branch": Branch ,
                                "OS": OS, 
                                "Count_of_Servers": nodes_num ,
                                "Count_of_Clients": clients_num , 
                                "Percentage_full" : pc_full ,
                                "Custom" : str(custom).upper()
                                }
                            runconfig_Set = {
                                "Operation": "".join(operation[0].upper() + operation[1:].lower()) ,
                                "Object_Size": str(obj_size.replace(" ","").upper()),
                                "Buckets": buckets,
                                "Objects": objects, 
                                "Sessions": sessions
                                }
                            updation_Set = {
                                "HOST": socket.gethostname(), 
                                "Config_ID": Config_ID, 
                                "IOPS": iops, 
                                "Throughput": throughput, 
                                "Latency": lat, 
                                "Log_File": filename, 
                                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                "Run_State": Run_Health
                                }
                            db_data={}
                            db_data.update(primary_Set)
                            db_data.update(runconfig_Set)
                            db_data.update(updation_Set)

# Function to insert data into db with iterration number

                            def db_update(itr,db_data):
                                db_data.update(Iteration=itr)
                                db[col].insert_one(db_data)
                                print('Inserted new entries \n' + str(db_data))

                            try:
                                if find_iteration:
                                    iteration_number = get_latest_iteration(primary_Set, db, col)
                                    find_iteration = False
                                    first_client=check_first_client(primary_Set, db, col, iteration_number)

                                if iteration_number == 0:
                                    db_update(iteration_number+1 , db_data)
                                elif not first_client:
                                    db_update(iteration_number, db_data)
                                elif overwrite == True :
                                    primary_Set.update(Iteration=iteration_number)
                                    if delete_data:
                                        db[col].delete_many(primary_Set)
                                        delete_data = False
                                        print("'overwrite' is True in config. Hence, old DB entry deleted")
                                    db_update(iteration_number,db_data)
                                else :
                                    db_update(iteration_number+1 , db_data)

                            except Exception as e:
                                print("Unable to insert/update documents into database. Observed following exception:")
                                print(e)
        except Exception as e:
            print(f"Encountered error in file: {filename} , and Exeption is" , e)
            Run_Health = "Failed"


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
    release_chain = cursor[0]['release']
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
    col_config=configs_main.get('R'+Version[0])['config_collection']
    dic = getconfig()
    result = db[col_config].find_one(dic)# find entry from configurations collection
    Config_ID = "NA"
    if result:
        Config_ID = result['_id']        # foreign key : it will map entry in configurations to results entry

    col =configs_main.get('R'+Version[0])['db_collection']
    insert_data(files,Build,Version,Config_ID,db,col,Branch,OS )

if __name__ == "__main__":
    main(sys.argv)

# End
