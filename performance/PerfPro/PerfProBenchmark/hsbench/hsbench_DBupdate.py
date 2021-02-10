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
    # col=db[configs_main['db_collection']]  #collection name = results
    return db

# Function to get build and version from URL
'''
Parameters : input(None) - none
             returns(string) - build name
                    (string) - version of build : beta / release
'''
def getBuild(): 
    build = "NA"
    version = "NA"
    # os_type = configs_config['OS_TYPE']
    buildurl = configs_config['BUILD_URL'].strip()
    listbuild=re.split('//|/',buildurl)
    if "releases/eos" in buildurl:
        version="beta"
    else:
        version="release"

    for e in listbuild[::-1]:
        if "cortx" in e.lower() and "rc" in e.lower():
            build = e.lower()
            break
        if e.isdigit():
            build = e
            break
    
    # if build != 'NA':
    #     build = "{}_{}".format(os_type,build.lower())    
    return build,version

# Function to get the files from use entered filepath
'''
Parameters : input(String) - file path of the folder
             returns(list) - list of filtered files in specified folder
'''
def get_files(filepath):
    files=[]
    for r, _, f in os.walk(filepath):
        for doc in f:
            # print(doc)
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
    configs = open(Config_path,"r")
    lines = configs.readlines()
    key=""
    dic={}
    value=""
    count=0
    for l in lines:
        l=l.strip()
        count+=1
        if "#END" in l:
            dic[key]=value
            break
        elif "#" in l :
            continue
        elif not ":" in l:
            value=value+l
        else:
            dic[key]=value
            data = l.split(":",1)
            key = data[0].strip()
            value = data[1].strip()
            
    dic.pop("","key not found")


# Function to push data to DB 
'''
Parameters : input - (list) list containing file names with specified filter, 
                     (String) host name, 
                     (Collection) DB collection where to push
                     (String) build number
             returns - none
'''
def push_data(files, host, db, build, version):
    print("logged in from ", host)
    collection=db[configs_main['db_collection']]
    col_config = db[configs_main['config_collection']]
    dic = getconfig()
    result = col_config.find_one(dic)  # find entry from configurations collection
    Config_ID = "NA"
    if result:
        Config_ID = result['_id'] # foreign key : it will map entry in configurations to results entry
    
    for doc in files:
        data_dict = None
        try:
            data = extract_json(doc)
            data.reset_index(inplace=False)
            data_dict = data.to_dict("records")
        except:
            data_dict = 'NA'

        #print(data_dict)
        filename = doc 
        doc = filename.strip(".json")
        attr = re.split("_", doc)
        obj_size = attr[-1]
        buckets = int(attr[-4])
        objects = int(attr[-6])
        sessions = int(attr[-8])

        with open(filename) as json_file:
            data = json.load(json_file)
            
            for entry in data:
                operation = ''
                
                if (entry['Mode'] == 'PUT'):
                    operation = 'write'
                elif (entry['Mode'] == 'GET'):
                    operation = 'read'       

                if(entry['Mode'] == 'PUT' or entry['Mode'] == 'GET') and (entry['IntervalName'] == 'TOTAL'):
                    primary_Set = {
                        'Build': build,
                        'Version': version,
                        'Name': 'Hsbench',
                        'Operation': operation,
                        'Object_Size' : obj_size,
                        'Buckets' : buckets,
                        'Objects' : objects,
                        'Sessions' : sessions,
                    }
                    updation_Set = {  
                        'HOST' : host,
                        'IOPS': entry['Iops'],
                        'Throughput': entry['Mbps'],
                        'Latency' : entry['AvgLat'],
                        'TTFB' : 'null',
                        'Log_file': doc,
                        'Bucket_Ops' : data_dict, 
                        'Config_ID':Config_ID,
                        'Timestamp':datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    action = "updated"
                    try:
                        count_documents= collection.count_documents(primary_Set)
                        if count_documents == 0:
                            collection.insert_one(primary_Set)
                            action = "inserted"
                        
                        collection.update_one(primary_Set,{ "$set": updation_Set})
                    except Exception as e:
                        print("Unable to insert/update documents into database. Observed following exception:")
                        print(e)

                    print(operation+ " " + action + ' - ' + doc)
    update_mega_chain(build, version, collection)


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
    build, version = getBuild() # get_DB_details()
    db = makeconnection()
    files = get_files(link)
    push_data(files, host, db, build, version)

# End