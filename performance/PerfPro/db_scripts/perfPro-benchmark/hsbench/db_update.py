'''Task : Push data to mongoDB from user given path and host
(uplaoded in hsbench named local database collection)
(works with any path)

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
modified on: 18 August 2020
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

client = MongoClient("mongodb://sampada:password@cftic1.pun.seagate.com:27017,cftic2.pun.seagate.com:27017,apollojenkins.pun.seagate.com:27017/test?authSource=performance_db&replicaSet=rs0&readPreference=primary&appname=MongoDB%20Compass%20Community&ssl=false")
db = client['performance_db']
def get_files(filepath):
    files=[]
    for r, _, f in os.walk(filepath):
        for doc in f:
            if '.json' in doc:
                files.append(os.path.join(r, doc))
    return files

def push_data(files, host):
    print(host)
    for doc in files:
        print(doc)
        filename = doc #'NT_32_NB_2048_object_size_16Mb.json'
        doc = filename.strip(".json")
        attr = re.split("_", doc)
        obj_size = attr[-1]

        with open(filename) as json_file:
            data = json.load(json_file)
            for entry in data:
                #print(entry['IntervalName'])
                operation = ''
                
                if (entry['Mode'] == 'PUT'):
                    operation = 'Write'
                elif (entry['Mode'] == 'GET'):
                    operation = 'Read'       

                if(entry['Mode'] == 'PUT' or entry['Mode'] == 'GET') and (entry['IntervalName'] == 'TOTAL'):            
                    db.results.insert_one({
                        #'build': build,
                        'Log_file': doc,
                        'Name': 'Hsbench',
                        'Operation': operation,
                        'IOPS': entry['Iops'],
                        'Throughput': entry['Mbps'],
                        'Latency' : entry['AvgLat'],
                        'TTFB' : 'null',
                        'Object_Size' : obj_size,
                        'HOST' : host
                        }
                    )
                    print(operation + " pushed")

if __name__ == "__main__":
    link = sys.argv[1] #input("Enter the file path - ")
    host =  socket.gethostname() #os.uname()[1]
    files = get_files(link)
    push_data(files, host)
