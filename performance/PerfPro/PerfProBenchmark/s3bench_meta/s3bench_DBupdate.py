
#!/usr/bin/env python3
"""
python3 cosbench_DBupdate.py <log file path> <main.yaml path> <config.yaml path>
Attributes: _id,Log_File,Name,Operation,IOPS,Throughput,Latency,TTFB,Object_Size,HOST
"""

import pymongo
from pymongo import MongoClient
import re
import socket
import sys
import os
from os import listdir
import yaml
from datetime import datetime

#Main_path = '/root/Modified/main.yml'
#Config_path = '/root/Modified/config.yml'
Main_path = sys.argv[2]
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
    return db

def getBuild():
    build = "NA"
    version = "NA"
    # os_type = configs_config['OS_TYPE'] # Enable for custom mode
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

    return [build,version]

class s3bench:

    def __init__(self, Log_File, Operation, IOPS, Throughput, Latency, TTFB, Object_Size,build,version,col,Config_ID):
        self.Log_File = Log_File
        self.Operation = Operation
        self.IOPS = IOPS
        self.Throughput = Throughput
        self.Latency = Latency
        self.TTFB = TTFB
        self.Object_Size = Object_Size
        self.build = build
        self.version = version
        self.col = col
        self.Config_ID = Config_ID
        self.Timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


    def insert_update(self):# function for inserting and updating mongodb database
        action= "Updated"
        try:
            pattern = {"Name" : "S3bench","Operation":self.Operation,"Object_Size" : self.Object_Size,"Build" : self.build,"Version":self.version}
            count_documents= self.col.count_documents(pattern)
            if count_documents == 0:
                self.col.insert_one(pattern)
                action = "Inserted"
            entry = {"Log_File" : self.Log_File,"IOPS" : self.IOPS,"Throughput" : self.Throughput,"Latency": self.Latency,"TTFB" : self.TTFB,"Timestamp":self.Timestamp, "Config_ID":self.Config_ID,"HOST" : socket.gethostname()}
            self.col.update_one(pattern, { "$set": entry})
        except Exception as e:
            print("Unable to insert/update documents into database. Observed following exception:")
            print(e)
        else:
            print('Data {} :: {} {}\n'.format(action,pattern,entry))



def insertOperations(file,build,version,col,Config_ID):   #function for retriving required data from log files
    _, filename = os.path.split(file)
    oplist = ["Write" , "Read" , "GetObjTag", "HeadObj" , "PutObjTag"]
    Objsize= 1
    obj = "NA"
 
    f = open(file)
    lines = f.readlines()[-150:]
    count=0
    while count<150:
        if "objectSize(MB):" in lines[count].strip().replace(" ", ""):
            r=lines[count].strip().replace(" ", "").split(":")
            Objsize = float(r[1])
            if(Objsize.is_integer()):
                obj=str(int(Objsize))+"Mb"
            else:
                obj=str(round(Objsize*1024))+"Kb"

        if "Operation:" in lines[count].replace(" ", ""):
            r=lines[count].strip().replace(" ", "").split(":")
            opname = r[1]
            if opname in oplist:
                count-=1
                throughput="NA"
                iops="NA"
                if opname=="Write" or opname=="Read":
                    count+=1
                    throughput = float(lines[count+3].split(":")[1])
                    iops=round((throughput/Objsize),6)
                    throughput = round(throughput,6)
                lat={"Max":float(lines[count+4].split(":")[1]),"Avg":float(lines[count+5].split(":")[1]),"Min":float(lines[count+6].split(":")[1])}
                ttfb={"Max":float(lines[count+7].split(":")[1]),"Avg":float(lines[count+8].split(":")[1]),"Min":float(lines[count+9].split(":")[1])}
                data = s3bench(filename,opname,iops,throughput,lat,ttfb,obj,build,version,col,Config_ID)
                data.insert_update()
                count += 9
        count +=1

def getallfiles(directory,extension):#function to return all file names with perticular extension
    flist = []
    for path, _, files in os.walk(directory):
        for name in files:
            if(name.lower().endswith(extension)):
                flist.append(os.path.join(path, name))
    return flist

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
    return dic

def main(argv):
    dic=argv[1]
    files = getallfiles(dic,".log")#getting all files with log as extension from given directory
    db = makeconnection() #getting instance of database

    build = getBuild()
        
    col_config = db[configs_main['config_collection']]
    dic = getconfig()
    result = col_config.find_one(dic)  # reading entry 
    Config_ID = "NA"
    if result:
        Config_ID = result['_id'] # foreign key : it will map entry in configurations to results entry
    
    col=db[configs_main['db_collection']]

    for f in files:
        insertOperations(f,build[0],build[1], col,Config_ID)
    update_mega_chain(build[0],build[1], col)

if __name__=="__main__":
    main(sys.argv) 
