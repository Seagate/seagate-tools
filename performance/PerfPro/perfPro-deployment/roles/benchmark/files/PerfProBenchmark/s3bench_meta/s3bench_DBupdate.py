
#!/usr/bin/env python3
"""
python3 s3bench_DBupdate.py <log file path> <main.yaml path> <config.yaml path> <ITR>
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
import urllib.request

#Main_path = '/root/Modified/main.yml'
#Config_path = '/root/Modified/config.yml'
Main_path = sys.argv[2]
Config_path = sys.argv[3]
iteration = sys.argv[4]

def makeconfig(name):  #function for connecting with configuration file
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

def makeconnection():  #function for making connection with database
    client = MongoClient(configs_main['db_url'])  #connecting with mongodb database
    db=client[configs_main['db_database']]  #database name=performance 
    return db

def get_release_info(variable):
    release_info= urllib.request.urlopen(build_url+'RELEASE.INFO')
    for line in release_info:
        if variable in line.decode("utf-8"):
            strinfo=line.decode("utf-8").strip()
            strip_strinfo=re.split(': ',strinfo)
            return(strip_strinfo[1])


class s3bench:

    def __init__(self, Log_File, Operation, IOPS, Throughput, Latency, TTFB, Object_Size,Build,Version,Branch,OS,Nodes_Num,Clients_Num,Col,Config_ID,PKey,Overwrite,Sessions,Objects):
        self.Log_File = Log_File
        self.Operation = Operation
        self.IOPS = IOPS
        self.Throughput = Throughput
        self.Latency = Latency
        self.TTFB = TTFB
        self.Object_Size = Object_Size
        self.Build = Build
        self.Version = Version
        self.Branch = Branch
        self.OS = OS
        self.Nodes_Num = Nodes_Num
        self.Clients_Num = Clients_Num
        self.Col = Col
        self.Config_ID = Config_ID
        self.Timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.PKey = PKey
        self.Overwrite = Overwrite
        self.Sessions = Sessions
        self.Objects = Objects


    def insert_update(self):# function for inserting and updating mongodb database
        db = makeconnection()
        action= "Updated"
        insertentry={} 
        collection = db[self.Col]
        try:
            pattern = {"PKey" : self.PKey}
            count_documents= collection.count_documents(pattern)
            if count_documents == 0:
                insertentry={
                        "Name" : "S3bench" , 
                        "Log_File" : self.Log_File,
                        "IOPS" : self.IOPS,
                        "Throughput" : self.Throughput,
                        "Latency": self.Latency,
                        "TTFB" : self.TTFB,
                        "Timestamp":self.Timestamp, 
                        "Config_ID":self.Config_ID,
                        "HOST" : socket.gethostname(), 
                        "Operation" : self.Operation , 
                        "Object_Size" : self.Object_Size ,
                        "Sessions": self.Sessions ,
                        "Objects" : self.Objects ,
                        "Buckets": "1" ,
                        "Build" : self.Build , 
                        "Version" : self.Version , 
                        "Branch" : self.Branch ,
                        "OS" : self.OS , 
                        "Count_of_Servers": self.Nodes_Num , 
                        "Count_of_Clients" : self.Clients_Num , 
                        "PKey" : self.PKey  
                        }
                collection.insert_one(insertentry)
                action = "Inserted"
            elif self.Overwrite == True : 
                insertentry = {
                        "Log_File" : self.Log_File,
                        "IOPS" : self.IOPS,
                        "Throughput" : self.Throughput,
                        "Latency": self.Latency,
                        "TTFB" : self.TTFB,
                        "Timestamp":self.Timestamp, 
                        "Config_ID":self.Config_ID,
                        "HOST" : socket.gethostname()
                        }
                collection.update_one(pattern, { "$set": insertentry})
                action = "Updated"
            else:
                print("'Overwrite' is false in config. Hence, DB not updated")
                action = "Not Updated"
        except Exception as e:
            print("Unable to insert/update documents into database. Observed following exception:")
            print(e)
        else:
            print('Data {} :: {} {}\n'.format(action,pattern,insertentry))

           


def insertOperations(file,Build,Version,col,Config_ID,Branch,OS):   #function for retriving required data from log files
    _, filename = os.path.split(file)
    global nodes_num, clients_num , pc_full, iteration , overwrite, custom
    oplist = ["Write" , "Read" , "GetObjTag", "HeadObj" , "PutObjTag"]
    Objsize= 1
    obj = "NA"
    sessions=1
    f = open(file)
    lines = f.readlines()[-150:]
    count=0
    while count<150:
        if "numSamples:" in lines[count].strip().replace(" ", ""):
            r=lines[count].strip().replace(" ", "").split(":")
            Objects=r[1]
        if "numClients:" in lines[count].strip().replace(" ", ""):
            r=lines[count].strip().replace(" ", "").split(":")
            sessions=r[1]
        if "objectSize(MB):" in lines[count].strip().replace(" ", ""):
            r=lines[count].strip().replace(" ", "").split(":")
            Objsize = float(r[1])
            if(Objsize.is_integer()):
                obj=str(int(Objsize))+"MB"
            else:
                obj=str(round(Objsize*1024))+"KB"

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
                PKey=Version[0]+'_'+Branch[0].upper()+'_'+Build+'_ITR'+str(iteration)+'_'+str(nodes_num)+'N_'+str(clients_num)+'C_'+str(pc_full)+'PC_'+str(custom).upper()+'_S3B_'+str(obj)+'_1_'+opname[0].upper()+'_'+sessions
                data = s3bench(filename,opname,iops,throughput,lat,ttfb,obj,Build,Version,Branch,OS,nodes_num,clients_num,col,Config_ID,PKey,overwrite,sessions,Objects)
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
    build_url=configs_config.get('BUILD_URL')
    nodes_list=configs_config.get('NODES')
    clients_list=configs_config.get('CLIENTS')
    pc_full=configs_config.get('PC_FULL')
    custom=configs_config.get('CUSTOM')
    overwrite=configs_config.get('OVERWRITE')
    iteration=configs_config.get('ITERATION')
    cluster_pass=configs_config.get('CLUSTER_PASS')
    change_pass=configs_config.get('CHANGE_PASS')
    prv_cli=configs_config.get('PRVSNR_CLI_REPO')
    prereq_url=configs_config.get('PREREQ_URL')
    srv_usr=configs_config.get('SERVICE_USER')
    srv_pass=configs_config.get('SERVICE_PASS')
    nfs_serv=configs_config.get('NFS_SERVER')
    nfs_exp=configs_config.get('NFS_EXPORT')
    nfs_mp=configs_config.get('NFS_MOUNT_POINT')
    nfs_fol=configs_config.get('NFS_FOLDER')

    dic={'NODES' :str(nodes_list) , 'CLIENTS' : str(clients_list) ,'BUILD_URL': build_url ,'CLUSTER_PASS': cluster_pass ,'CHANGE_PASS': change_pass ,'PRVSNR_CLI_REPO': prv_cli ,'PREREQ_URL': prereq_url ,'SERVICE_USER': srv_usr ,'SERVICE_PASS': srv_pass , 'PC_FULL': pc_full , 'CUSTOM': custom , 'OVERWRITE':overwrite , 'ITERATION': iteration,'NFS_SERVER': nfs_serv ,'NFS_EXPORT' : nfs_exp ,'NFS_MOUNT_POINT' : nfs_mp , 'NFS_FOLDER' : nfs_fol }
    return (dic)



def main(argv):
    dic=argv[1]
    files = getallfiles(dic,".log")#getting all files with log as extension from given directory
    db = makeconnection() #getting instance of database

    Build=get_release_info('BUILD')
    Build=Build[1:-1]    
    Version=get_release_info('VERSION')
    Version=Version[1:-1]
    Branch=get_release_info('BRANCH')    
    Branch=Branch[1:-1]
    OS=get_release_info('OS')
    OS=OS[1:-1]

    #col_config = db[configs_main['config_collection']]
    col_config='configurations_'+Version[0]
    dic = getconfig()
    Config_ID = "NA"
    result = db[col_config].find_one(dic)    
    if result:
        Config_ID = result['_id'] # foreign key : it will map entry in configurations to results entry
    
    #col=db[configs_main['db_collection']]
    col='results_'+Version[0]

    for f in files:
        insertOperations(f,Build,Version,col,Config_ID,Branch,OS)
    #update_mega_chain(Build,Version, col)

if __name__=="__main__":
    main(sys.argv) 

#!/usr/bin/env python3
