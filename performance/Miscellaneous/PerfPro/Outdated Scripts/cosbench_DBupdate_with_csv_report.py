"""
python3 cosbench_DBupdate.py <log file path> 

Attributes:
_id,Log_File,Name,Operation,IOPS,Throughput,Latency,TTFB,Object_Size,HOST,Objects,Buckets,Session
"""

import csv
import pymongo
from pymongo import MongoClient
import re
import socket
import yaml
import sys
import os
from os import listdir
#import yaml


Main_path = '/root/Modified/main.yml'
Config_path = '/root/Modified/config.yml'
csvFileName = 'cosbenchCSVReport.csv'

def makeconfig(name):  #function for connecting with configuration file
    with open(name) as config_file:
        configs = yaml.load(config_file, Loader=yaml.FullLoader)
    return configs

def makeconnection():  #function for making connection with database
    configs = makeconfig(Main_path)
    client = MongoClient(configs['db_url'])  #connecting with mongodb database
    db=client[configs['db_database']]  #database name=performance 
    col=db[configs['db_collection']]  #collection name = results
    return col

def getBuild():
    configs= makeconfig(Config_path) #getting instance  of config file
    build=""
    version=""
    listbuild=re.split('//|/',configs['BUILD_URL'].strip())
    if len(listbuild) < 7:
        build = listbuild[-2]
        version = "beta"
    else:
        version = listbuild[5]
        if version.lower() == "release":
            build = listbuild[7]
    return [build,version]

def insert_data(file):   #function for retriving required data from log files and update into mongodb
    build = getBuild()
    col = makeconnection()  #getting instance  of collection
    _, filename = os.path.split(file)
    with open(file) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                line_count += 1
            else:
                if(row[1]=="read" or row[1]=="write"):
                    throughput = float(row[13])
                    attr = re.split(',|-',filename)
                    lat={"Max":float(row[12]),"Avg":float(row[5])}
                    #check whether entry with same build -object size -buckets-objects-sessions is presernt or not
                    entry = {"Name" : "Cosbench","Build":build[0].lower(),"Version":build[1],"Object_Size":attr[1],"Buckets":int(re.split(" ", attr[2])[1]),"Objects":int(re.split(" ", attr[3])[1]), "Sessions":int(re.split(" ",attr[4])[1])}
                    try:
                        count_documents= col.count_documents(entry)
                        if count_documents == 0:
                            col.insert_one(entry)
                        col.update_one(entry,{ "$set":{"Log_File" : filename,"Operation" :row[1],"IOPS":float(row[6]),"Throughput":throughput,"Latency":lat,"HOST": socket.gethostname()}})
                    except Exception as e:
                        print("Unable to insert/update documents into database. Observed following exception:")
                        print(e)
                    else:    
                        print('{} : {} {} {} {} {} {} {} {} {} {} {} {}\n'.format("Data Recorded",filename ,"Cosbench",row[1],row[6],throughput,lat,attr[1],build[1],build[0].lower(),int(re.split(" ", attr[2])[1]),int(re.split(" ", attr[3])[1]),int(re.split(" ",attr[4])[1])))

def generateReport(file):
    _, filename = os.path.split(file)
    attr = re.split(',|-',filename)
    objSize = attr[1]
    Buckets = int(re.split(" ", attr[2])[1])
    Objects = int(re.split(" ", attr[3])[1])
    Sessions = int(re.split(" ",attr[4])[1])
    objvalue = float(re.split(" ",objSize)[0])
    objunit = re.split(" ",objSize)[1]
    if objunit == "KB":
        objvalue = objvalue * 0.001
    with open(file) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        gotRead = False
        gotWrite = False
        for row in csv_reader:
            if gotRead and gotWrite:
                break
            if row[1] == "read":
                readThroughput = float(row[13])*objvalue
                gotRead = True
            elif row[1] == "write":
                writeThroughput = float(row[13])*objvalue
                gotWrite = False
    
    return [objSize, writeThroughput, readThroughput, Buckets, Objects, Sessions]


def getallfiles(directory,extension):#function to return all file names with perticular extension
    flist = []
    for path, _, files in os.walk(directory):
        for name in files:
            if(name.lower().endswith(extension)):
                flist.append(os.path.join(path, name))
    return flist


def main(argv): # Call generateReport() to get data from log file 'f' and write into csv

    dic = argv[1] #"w27-5 MB, 50 buckets, 100 objects, 100 workers, MIXED Workloadtype.csv" 
    files = getallfiles(dic,"workloadtype.csv")
    with open(csvFileName, 'w', newline='') as myfile:
        wr = csv.writer(myfile)
        wr.writerow(['ObjectSize','Write Throughput','Read Throughput','Buckets','Objectst','Sessions'])
        for f in files:
            # insert_data(f)
            wr.writerow(generateReport(f)) 
    

if __name__=="__main__":
    main(sys.argv) 
