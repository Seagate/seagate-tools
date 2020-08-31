'''
Task: Insert BucketOps params to MongoDB
reference : hsbenchReport.py
Date : 25 August 2020
by : Sampada Petkar
@Seagate
'''
import json
import pandas as pd
import glob
import os
import sys
import socket
import pymongo
from pymongo import MongoClient
import re
from jproperties import Properties

# Function to get the files from use entered filepath
'''
Parameters : input(String) - file path of the folder
             returns(list) - list of filtered files in specified folder
'''
def extractFile(filepath):
    files = []
    for r, _, f in os.walk(filepath):
        for file in f:
            if '.json' in file:
                files.append(os.path.join(r, file))
    return files


# Function to get DB details from config files
'''
Parameters : input - none
             returns(collection) - DB colection name where to push
                    (string) - build number
Must have config.properties file already
'''
def get_DB_details():
    data_config = Properties()
    with open('config.properties', 'rb') as config_file:
        data_config.load(config_file)
        # connecting with mongodb database
        client = MongoClient(data_config.get("DB_URL").data)
        # database name=performance
        db = client[data_config.get("DB_DATABASE").data]
        collection = db[data_config.get("DB_COLLECTION").data]
        build = data_config.get("BUILD").data
    return collection, build


# Function to extract details from JSON and convert to pandas Dataframe
'''
Parameters - input : (string) filename
             returns : (Dataframe) pandas dataframe
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


# Function to push data to DB
'''
Parameters : input - (list) list containing file names with specified filter, 
                     (String) host name, 
                     (Collection) DB collection where to push
                     (String) build number
             returns - none
'''
def push_db_data(files, host, collection, build):
    for IO_SIZE in files:
        doc = IO_SIZE.strip(".json")
        attr = re.split("_", doc)
        obj_size = attr[-1]
        buckets = int(attr[-4])
        objects = int(attr[-6])
        sessions = int(attr[-8])

        data = extract_json(IO_SIZE)
        data.reset_index(inplace=False)
        data_dict = data.to_dict("records")
        collection.insert_one({
            'Name': 'Hsbench',
            'Build': build.lower(),
            'Object_Size': obj_size,
            'Buckets': buckets,
            'Objects': objects,
            'Sessions': sessions,
            "data": data_dict,
            'HOST': host,
            'Log_file': IO_SIZE,
        })
        print("data pushed for - {}".format(IO_SIZE))
        #print('=============IO_SIZE: {}============='.format(IO_SIZE))
        # print(data)


# Main function
'''
parameters : input - (String) folder path to required files
             returns - none
'''
if __name__ == '__main__':
    files = extractFile(sys.argv[1])
    host = socket.gethostname()
    collection, build = get_DB_details()
    push_db_data(files, host, collection, build)
