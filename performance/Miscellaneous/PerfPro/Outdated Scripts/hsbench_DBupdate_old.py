'''
python3 cosbench_DBupdate.py <log file path> <main.yaml path> <config.yaml path>

Task : Push data to mongoDB from user given path and host
(uplaoded in hsbench named local database collection)
(works with any path)
Parses DB details from config.yaml, main.yaml file
Updates entry or creates new one

upload parameters: 
    Log_file:  (file name)
    Name: S3bench,hsbench,cosbench
    Operation: Read/Write
    IOPS:
    Throughput:(in Mb/s)
    Latency:(in ms)
    TTFB:
    Object_Size:
    HOST:
    config_ID:
    Buckets:
    Objects:
    Sessions:
    Timestamp:

Date : 10 August 2020
modified on: 12 September 2020
by  :Sampada Petkar
@Seagate
'''
import pymongo
from pymongo import MongoClient
import re 
import json
import os
import socket
import sys
# from jproperties import Properties
import yaml
from datetime import datetime

# Function to get DB details from config files
'''
Parameters : input - none
             returns(collection) - DB colection name where to push
                    (string) - build number
Must have config.properties file already
'''
#Main_path = '/root/Modified/main.yml'
#Config_path = '/root/Modified/config.yml'
Main_path = sys.argv[2]  # database url
Config_path = sys.argv[3]

def makeconfig(name):  #function for connecting with configuration file
    with open(name) as config_file:
        configs = yaml.load(config_file, Loader=yaml.FullLoader)
    return configs

configs_main = makeconfig(Main_path)
configs_config= makeconfig(Config_path)

def makeconnection():  #function for making connection with database
    client = MongoClient(configs_main['db_url'])  #connecting with mongodb database
    db=client[configs_main['db_database']]  #database name=performance 
    #col=db[configs_main['db_collection']]  #collection name = results
    return db

def getBuild():
    build = "NA"
    version = "NA"
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

    return build,version

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
    print(collection)
    col_config = db[configs_main['config_collection']]
    dic = {}
    for attr,value in configs_config.items():
        dic.update( {attr : value} )
        if attr == "AUTO_DEPLOY_URL":
            break
    result = col_config.find_one(dic)  # find entry from configurations collection
    Config_ID = "NA"
    if result:
        Config_ID = result['_id'] # foreign key : it will map entry in configurations to results entry
    
    for doc in files:
        filename = doc #'NT_32_NB_2048_object_size_16Mb.json'
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
