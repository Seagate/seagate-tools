#!/usr/bin/env python3
"""
python3 cosbench_DBupdate.py <log file path> <main.yaml path> <config.yaml path>
Attributes:
_id,Log_File,Name,Operation,IOPS,Throughput,Latency,TTFB,Object_Size,HOST,Objects,Buckets,Session
"""

import csv
from pymongo import MongoClient
import re
import socket
import sys
import os
import yaml
from datetime import datetime

Main_path = sys.argv[2]
Config_path = sys.argv[3]

def makeconfig(name):  # function for connecting with configuration file
    with open(name) as config_file:
        configs = yaml.safe_load(config_file)
    return configs


configs_main = makeconfig(Main_path)  # getting instance  of main file
configs_config = makeconfig(Config_path)  # getting instance  of config file

build_info=str(configs_config.get('BUILD_INFO'))
build_url=configs_config.get('BUILD_URL')
nodes_list=configs_config.get('NODES')
clients_list=configs_config.get('CLIENTS')
pc_full=configs_config.get('PC_FULL')
overwrite=configs_config.get('OVERWRITE')
custom=configs_config.get('CUSTOM')
docker_info=configs_config.get('DOCKER_INFO')
nodes_num=len(nodes_list)
clients_num=len(clients_list)

def makeconnection():  # function for making connection with database
    # connecting with mongodb database
    client = MongoClient(configs_main['db_url'])
    db = client[configs_main['db_database']]  # database name=performance
    return db



def get_release_info(variable):
    release_info=os.popen('docker run --rm -it ' + docker_info +' cat /opt/seagate/cortx/RELEASE.INFO')
    lines=release_info.readlines()
    for line in lines:
        if variable in line:
            strinfo=line.strip()
            strip_strinfo=re.split(': ',strinfo)
            return(strip_strinfo[1])


##Function to find latest iteration
def get_latest_iteration(query, db, collection):
    max_iter = 0
    cursor = db[collection].find(query)
    for record in cursor:
        if max_iter < record['Iteration']:
            max_iter = record['Iteration']
    return max_iter

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
                                "Count_of_Clients": clients_num,
                                "Percentage_full" : pc_full,
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

    for i, _ in enumerate(nodes_list):
        nodes.append(nodes_list[i][i+1])

    for i, _ in enumerate(clients_list):
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
    return (dic)


def main(argv):
    dic = argv[1]
    files = getallfiles(dic, "workloadtype.csv")

    if build_info == 'RELEASE.INFO':
        version=get_release_info('VERSION')[1:-1]
        ver_strip=re.split('-',version)
        Version=ver_strip[0]
        Build=ver_strip[1]
        Branch='main'
        OS=get_release_info('OS')
        OS=OS[1:-1]
    elif build_info == 'USER_INPUT':
        Build=configs_config.get('BUILD')
        Version=configs_config.get('VERSION')
        Branch=configs_config.get('BRANCH')
        OS=configs_config.get('OS')

    db = makeconnection()  # getting instance  of database
    dic = getconfig()
    if dic['SOLUTION'].upper() == 'LC':
       col=configs_main.get('LC')
    elif dic['SOLUTION'].upper() == 'LR':
       col=configs_main.get('LR')
    elif dic['SOLUTION'].upper() == 'LEGACY':
       col=configs_main.get(f"R{Version.split('.')[0]}")
    else:
        print("Error! Can not find suitable collection to upload data")

    result = db[col['config_collection']].find_one(dic)# find entry from configurations collection
    Config_ID = "NA"
    if result:
        Config_ID = result['_id']        # foreign key : it will map entry in configurations to results entry

    insert_data(files,Build,Version,Config_ID,db,col['db_collection'],Branch,OS )

if __name__ == "__main__":
    main(sys.argv)
