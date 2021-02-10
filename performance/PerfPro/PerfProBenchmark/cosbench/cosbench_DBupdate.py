"""
python3 cosbench_DBupdate.py <log file path> <main.yaml path> <config.yaml path>
Attributes:
_id,Log_File,Name,Operation,IOPS,Throughput,Latency,TTFB,Object_Size,HOST,Objects,Buckets,Session
"""

import csv
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


def makeconfig(name):  # function for connecting with configuration file
    with open(name) as config_file:
        configs = yaml.load(config_file, Loader=yaml.FullLoader)
    return configs


configs_main = makeconfig(Main_path)  # getting instance  of main file
configs_config = makeconfig(Config_path)  # getting instance  of config file


def makeconnection():  # function for making connection with database
    # connecting with mongodb database
    client = MongoClient(configs_main['db_url'])
    db = client[configs_main['db_database']]  # database name=performance
    # col=db[configs['db_collection']]  #collection name = results
    return db


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
    return [build,version]


def insert_data(file,build,Config_ID,col):  # function for retriving required data from log files and update into mongodb
    _, filename = os.path.split(file)
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
                    action = "Updated"
                    entry = {"Name": "Cosbench", "Operation": row[1], "Build": build[0], "Version": build[1], "Object_Size": attr[1], "Buckets": int(
                        re.split(" ", attr[2])[1]), "Objects": int(re.split(" ", attr[3])[1]), "Sessions": int(re.split(" ", attr[4])[1])}
                    
                    
                    try:
                        count_documents = col.count_documents(entry)
                        if count_documents == 0:
                            col.insert_one(entry)
                            action = "Inserted"
                        update_data = {"Log_File": filename, "Operation": row[1], "IOPS": iops, "Throughput": throughput, "Latency": lat, "HOST": socket.gethostname(),
                        "Config_ID": Config_ID, "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
                        col.update_one(entry, {"$set": update_data})
                    except Exception as e:
                        print(
                            "Unable to insert/update documents into database. Observed following exception:")
                        print(e)
                    else:
                        print('Data {} : {} {} \n'.format(
                            action, entry, update_data))


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
    #print(beta_chain)
    release_chain = cursor[0]['release']
    #print(release_chain)
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

def main(argv):
    dic = argv[1]
    files = getallfiles(dic, "workloadtype.csv")
    build = getBuild()
    db = makeconnection()  # getting instance  of database
    col_config = db[configs_main['config_collection']]
    dic = getconfig()
    result = col_config.find_one(dic)# find entry from configurations collection
    Config_ID = "NA"
    if result:
        Config_ID = result['_id']        # foreign key : it will map entry in configurations to results entry

    col = db[configs_main['db_collection']]
    print(col)
    for f in files:
        insert_data(f,build,Config_ID,col)
    update_mega_chain(build[0],build[1],col)# update mega entry




if __name__ == "__main__":
    main(sys.argv)
