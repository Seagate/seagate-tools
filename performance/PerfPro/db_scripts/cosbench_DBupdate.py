"""
Attributes:
_id,Log_File,Name,Operation,IOPS,Throughput,Latency,TTFB,Object_Size,HOST
"""

import csv
import pymongo
from pymongo import MongoClient
import re
import socket
import sys
import os
from os import listdir
from jproperties import Properties

def makeconfig():   #function for connecting with configuration file
    configs = Properties()
    with open('config.properties','rb') as config_file:
    	configs.load(config_file)
    return configs

def makeconnection(configs):
    client = MongoClient(configs.get("DB_URL").data)  #connecting with mongodb database
    db=client[configs.get("DB_DATABASE").data]  #database name=performance 
    col=db[configs.get("DB_COLLECTION").data]  #collection name = results
    return col

def insert_data(file):   #function for retriving required data from log files and update into mongodb
    configs = makeconfig()   #getting instance  of config file
    col = makeconnection(configs)  #getting instance  of collection
    head, filename = os.path.split(file)
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
                    col.insert_one({"Log_File" : filename,"Name" : "Cosbench","Operation" :row[1],"IOPS":float(row[6]),"Throughput":throughput,"Latency":lat,"Object_Size":attr[1],"Build":configs.get("BUILD").data.lower(),"HOST": socket.gethostname(),"Buckets":int(re.split(" ", attr[2])[1]),"Objects":int(re.split(" ", attr[3])[1]), "Sessions":int(re.split(" ",attr[4])[1])})
                    print('{} : {} {} {} {} {} {} {} {}'.format("Data Recorded",filename ,"Cosbench",row[1],row[6],throughput,lat,attr[1],configs.get("BUILD").data.lower()))

    
def getallfiles(directory,extension):#function to return all file names with perticular extension
    flist = []
    for path, subdirs, files in os.walk(directory):
        for name in files:
            if(name.lower().endswith(extension)):
                flist.append(os.path.join(path, name))
    return flist


def main(argv):
    dic = argv[1]
    files = getallfiles(dic,"workloadtype.csv")
    for f in files:
        insert_data(f);
    

if __name__=="__main__":
    main(sys.argv) 
