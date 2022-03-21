#!/usr/bin/env python3
'''
python3 hsbench_DBupdate.py <log file path> <main.yaml path> <config.yaml path> 

Task : Push HSBENCH data to mongoDB from user given path and host
'''
import pymongo
from pymongo import MongoClient
import re 
import json
import os
import socket
import sys
import yaml
from datetime import datetime
import pandas as pd
import urllib.request

# Path for yaml files locations
Main_path = sys.argv[2]  # database url
Config_path = sys.argv[3]

# Function for connecting with configuration file
def makeconfig(name):  
    with open(name) as config_file:
        configs = yaml.load(config_file, Loader=yaml.FullLoader)
    return configs

configs_main = makeconfig(Main_path)
configs_config= makeconfig(Config_path)

build_url=configs_config.get('BUILD_URL')
nodes_list=configs_config.get('NODES')
clients_list=configs_config.get('CLIENTS')
pc_full=configs_config.get('PC_FULL')
overwrite=configs_config.get('OVERWRITE')
custom=configs_config.get('CUSTOM')
nodes_num=len(nodes_list)
clients_num=len(clients_list)

# Function to get DB details from config files
'''
Parameters : input - none
             returns(Database) - Databbasen name where to push
                    (string) - build number
Must have main.yml file already
'''
def makeconnection(): 
    client = MongoClient(configs_main['db_url'])  #connecting with mongodb database
    db=client[configs_main['db_database']]  #database name=performance 
    return db

# Function to get build release information from URL
'''
Parameters : input(Variable) - Variable from RELEASE.INFO of the Build
             returns(string) - Value of the Variable
'''

def get_release_info(variable):
    release_info= urllib.request.urlopen(build_url+'RELEASE.INFO')
    for line in release_info:
        if variable in line.decode("utf-8"):
            strinfo=line.decode("utf-8").strip()
            strip_strinfo=re.split(': ',strinfo)
            return(strip_strinfo[1])



# Function to get the files from use entered filepath
'''
Parameters : input(String) - file path of the folder
             returns(list) - list of filtered files in specified folder
'''
def get_files(filepath):
    files=[]
    for r, _, f in os.walk(filepath):
        for doc in f:
            if '.json' in doc:
                files.append(os.path.join(r, doc))
    return files

# Function to get bucketops from log files
'''
Parameters : input(str) - file name to get data from files
             returns(dataFrame) - pandas dataframe containing bucketOPs details
'''
def extract_json(file):
    json_data = []
    keys = ['Mode', 'Seconds', 'Ops', 'Mbps',
            'Iops', 'MinLat', 'AvgLat', 'MaxLat']
    values = []
    with open(file, 'r') as list_ops:
        json_data = json.load(list_ops)
    for data in json_data:
        value = []
        if(data['IntervalName'] == 'TOTAL'):
            for key in keys:
                value.append(data[key])
            values.append(value)
    table_op = pd.DataFrame(values, columns=keys)
    return table_op


def getconfig():
    nodes_list=configs_config.get('NODES')
    clients_list=configs_config.get('CLIENTS')
    build_url=configs_config.get('BUILD_URL')
    execution_type=configs_config.get('EXECUTION_TYPE')
    cluster_pass=configs_config.get('CLUSTER_PASS')
    solution=configs_config.get('SOLUTION')
    end_points=configs_config.get('END_POINTS')
    system_stats=configs_config.get('SYSTEM_STATS')
    pc_full=configs_config.get('PC_FULL')
    custom=configs_config.get('CUSTOM')
    overwrite=configs_config.get('OVERWRITE')
    degraded_read=configs_config.get('DEGRADED_READ')
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
        'BUILD_URL': build_url ,
        'EXECUTION_TYPE': execution_type,
        'CLUSTER_PASS': cluster_pass ,
        'SOLUTION' : solution ,
        'END_POINTS' : end_points ,
        'SYSTEM_STATS' : system_stats ,
        'PC_FULL' : pc_full ,
        'CUSTOM' : custom ,
        'OVERWRITE' : overwrite ,
        'DEGRADED_READ' : degraded_read ,
        'COPY_OBJECT' : copy_object ,
        'NFS_SERVER': nfs_serv ,
        'NFS_EXPORT' : nfs_exp ,
        'NFS_MOUNT_POINT' : nfs_mp ,
        'NFS_FOLDER' : nfs_fol
        }

    return (dic)

##Function to find latest iteration

def get_latest_iteration(query, db, collection):
    max = 0
    cursor = db[collection].find(query)
    for record in cursor:
        if max < record['Iteration']:
            max = record['Iteration']
    return max

#Function to resolve iteration/overwrite etc in multi-client run
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

# Function to push data to DB 
'''
Parameters : input - (list) list containing file names with specified filter, 
                     (String) host name, 
                     (Collection) DB collection where to push
                     (String) build number
             returns - none
'''
def push_data(files, host, db, Build, Version, Branch , OS):
    find_iteration = True
    first_client = True
    delete_data = True
    iteration_number = 0
    global nodes_num, clients_num, pc_full , overwrite, custom
    print("logged in from ", host)
    dic = getconfig()
    if dic['SOLUTION'].upper() == 'LC':
       valid_col=configs_main.get('LC')
    elif dic['SOLUTION'].upper() == 'LR':
       valid_col=configs_main.get('LR')
    elif dic['SOLUTION'].upper() == 'LEGACY':
       valid_col=configs_main.get(f"R{Version.split('.')[0]}")
    else:
        print("Error! Can not find suitable collection to upload data")

    result = db[valid_col['config_collection']].find_one(dic)  # find entry from configurations collection
    Config_ID = "NA"
    if result:
        Config_ID = result['_id'] # foreign key : it will map entry in configurations to results entry
   
    collection=valid_col['db_collection']

    for doc in files:
        data_dict = None
        try:
            data = extract_json(doc)
            data.reset_index(inplace=False)
            data_dict = data.to_dict("records")
        except:
            data_dict = 'NA'

        filename = doc 
        doc = filename.strip(".json")
        attr = re.split("_", doc)
        obj_size = attr[-7]
        buckets = int(attr[-3])
        objects = int(attr[-5])
        sessions = int(attr[-1])
        cluster_state=str(attr[-9])
        try:
            run_health='Successful'
            with open(filename) as json_file:
                data = json.load(json_file)
            
                for entry in data:
                    operation = ''
                
                    if (entry['Mode'] == 'PUT'):
                        operation = 'Write'
                    elif (entry['Mode'] == 'GET'):
                        operation = 'Read'       

                    if(entry['Mode'] == 'PUT' or entry['Mode'] == 'GET') and (entry['IntervalName'] == 'TOTAL'):
                        primary_Set = {
                            'Name': 'Hsbench',
                            'Build': Build,
                            'Version': Version,
                            'Branch': Branch,
                            'OS': OS,
                            'Count_of_Servers': nodes_num, 
                            'Count_of_Clients': clients_num,
                            'Percentage_full' : pc_full ,
                            'Custom' : str(custom).upper()
                            }

                        runconfig_Set = {
                            'Operation': operation,
                            'Object_Size' : str(obj_size.upper()),
                            'Buckets' : buckets,
                            'Objects' : objects,
                            'Sessions' : sessions,
                            'Cluster_State': cluster_state
                            }
                        
                        updation_Set = {  
                            'HOST' : host,
                            'Config_ID':Config_ID,
                            'IOPS': entry['Iops'],
                            'Throughput': entry['Mbps'],
                            'Latency' : entry['AvgLat'],
                            'TTFB' : 'null',
                            'Log_File': doc,
                            'Bucket_Ops' : data_dict, 
                            'Timestamp':datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            'Run_State' : run_health
                        }

                        db_data={}
                        db_data.update(primary_Set)
                        db_data.update(runconfig_Set)
                        db_data.update(updation_Set)

# Function to insert data into db with iterration number
                        def db_update(itr,db_data):
                            db_data.update(Iteration=itr)
                            db[collection].insert_one(db_data)
                            print('Inserted new entries \n' + str(db_data))

                        try:
                            if find_iteration:
                                iteration_number = get_latest_iteration(primary_Set, db, collection)
                                find_iteration = False
                                first_client=check_first_client(primary_Set, db, collection, iteration_number)

                            if iteration_number == 0:
                                db_update(iteration_number+1 , db_data)
                            elif not first_client:
                                db_update(iteration_number, db_data)
                            elif overwrite == True :
                                primary_Set.update(Iteration=iteration_number)
                                if delete_data:
                                    db[collection].delete_many(primary_Set)
                                    delete_data = False
                                    print("'overwrite' is True in config. Hence, old DB entry deleted")
                                db_update(iteration_number,db_data)
                            else :
                                db_update(iteration_number+1 , db_data)

                        except Exception as e:
                            print("Unable to insert/update documents into database. Observed following exception:")
                            print(e)

        except Exception as exc:
            print(f"Encountered error in file: {filename} , and Exeption is" , exc)
            Run_Health = "Failed"


#    update_mega_chain(Build, Version, collection)


def update_mega_chain(build,version, col):
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

# Main fucntion
'''
parameters : input - (String) folder path to required files
             returns - none
'''
if __name__ == "__main__":
    link = sys.argv[1] #input("Enter the file path - ")
    host =  socket.gethostname() #os.uname()[1]

    Build=get_release_info('BUILD')
    Build=Build[1:-1]
    Version=get_release_info('VERSION')
    Version=Version[1:-1]
    Branch=get_release_info('BRANCH')
    Branch=Branch[1:-1]
    OS=get_release_info('OS')
    OS=OS[1:-1]

    db = makeconnection()
    files = get_files(link)

    push_data(files, host, db, Build, Version, Branch , OS) 

# End
