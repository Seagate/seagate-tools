'''
Task : Push data to mongoDB from user given path and host
(uplaoded in hsbench named local database collection)
(works with any path)
Parses DB details from config.properties file

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

Date : 10 August 2020
modified on: 23 August 2020
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
from jproperties import Properties

# Function to get DB details from config files
'''
Parameters : input - none
             returns(collection) - DB colection name where to push
                    (string) - build number
Must have config.properties file already
'''
def get_DB_details():
    data_config = Properties()
    with open('config.properties','rb') as config_file:
        data_config.load(config_file)
        client = MongoClient(data_config.get("DB_URL").data)  #connecting with mongodb database
        db=client[data_config.get("DB_DATABASE").data]  #database name=performance 
        collection=db[data_config.get("DB_COLLECTION").data]
        build = data_config.get("BUILD").data
    return collection, build

# Function to get the files from use entered filepath
'''
Parameters : input(String) - file path of the folder
             returns(list) - list of filtered files in specified folder
'''
def get_files(filepath):
    files=[]
    for r, _, f in os.walk(filepath):
        for doc in f:
            print(doc)
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
def push_data(files, host, collection, build):
    print(host)
    for doc in files:
        print(doc)
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
                #print(entry['IntervalName'])
                operation = ''
                
                if (entry['Mode'] == 'PUT'):
                    operation = 'write'
                elif (entry['Mode'] == 'GET'):
                    operation = 'read'       

                if(entry['Mode'] == 'PUT' or entry['Mode'] == 'GET') and (entry['IntervalName'] == 'TOTAL'):   
                    # print(buckets,objects,sessions)
                    collection.insert_one({
                        'Build': build.lower(),
                        'HOST' : host,
                        'Name': 'Hsbench',
                        'Operation': operation,
                        'Object_Size' : obj_size,                      
                        'IOPS': entry['Iops'],
                        'Throughput': entry['Mbps'],
                        'Latency' : entry['AvgLat'],
                        'TTFB' : 'null',
                        'Log_file': doc,
                        'Buckets' : buckets,
                        'Objects' : objects,
                        'Sessions' : sessions,
                        }
                    )
                    print(operation + " pushed")

# Main fucntion
'''
parameters : input - (String) folder path to required files
             returns - none
'''
if __name__ == "__main__":
    link = sys.argv[1] #input("Enter the file path - ")
    host =  socket.gethostname() #os.uname()[1]
    collection, build = get_DB_details()
    files = get_files(link)
    push_data(files, host, collection, build)

