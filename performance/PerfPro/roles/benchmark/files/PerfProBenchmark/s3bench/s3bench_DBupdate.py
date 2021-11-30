
#!/usr/bin/env python3
"""
python3 s3bench_DBupdate.py <log file path> <main.yaml path> <config.yaml path> 
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
Main_path = sys.argv[2]
Config_path = sys.argv[3]

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

iteration_number = 0

##Function to find latest iteration
def get_latest_iteration(query, db, collection):
    max = 0
    cursor = db[collection].find(query)
    for record in cursor:
        if max < record['Iteration']:
            max = record['Iteration']
    return max

##Function to resolve iteration/overwrite etc in multi-client run
def check_first_client(query, db, collection, itr):
    query.update(Iteration=itr)
    cursor = db[collection].distinct('HOST', query)
    if (len(cursor) < query["Count_of_Clients"]):
        cur_client = socket.gethostname()
        if cur_client in cursor:
            print(f"Multi-Client Run: Re-Upload from client {cur_client} detected. Existing data in DB from this client for current run will get overwritten")
            query.update(HOST=cur_client)
            db[collection].delete_many(query)
        return False
    return True


class s3bench:

    def __init__(self, Log_File, Operation, IOPS, Throughput, Latency, TTFB, Object_Size,Build,Version,Branch,OS,Nodes_Num,Clients_Num,Col,Config_ID,Overwrite,Sessions,Objects,PC_Full,Custom,run_health):

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
        self.Overwrite = Overwrite
        self.Sessions = Sessions
        self.Objects = Objects
        self.PC_Full = PC_Full
        self.Custom = str(Custom).upper()
        self.Run_State = run_health

# Set for uploading to db
        self.Primary_Set = {
                "Name" : "S3bench" ,
                "Build" : self.Build ,
                "Version" : self.Version ,
                "Branch" : self.Branch ,
                "OS" : self.OS ,
                "Count_of_Servers": self.Nodes_Num ,
                "Count_of_Clients" : self.Clients_Num,
                "Percentage_full" : self.PC_Full ,
                "Custom" : self.Custom
                }
        self.Runconfig_Set = {
                "Operation" : self.Operation ,
                "Object_Size" : self.Object_Size ,
                "Buckets": 1 ,
                "Objects" : self.Objects ,
                "Sessions": self.Sessions
                }
        self.Updation_Set= {
                "HOST" : socket.gethostname(),
                "Config_ID":self.Config_ID,
                "IOPS" : self.IOPS,
                "Throughput" : self.Throughput,
                "Latency": self.Latency,
                "Log_File" : self.Log_File,
                "TTFB" : self.TTFB,
                "Timestamp":self.Timestamp,
                "Run_State":self.Run_State
                }

    def insert_update(self,Iteration):# function for inserting and updating mongodb database 
        db = makeconnection()
        db_data={}
        db_data.update(self.Primary_Set)
        db_data.update(self.Runconfig_Set)
        db_data.update(self.Updation_Set)
        collection = self.Col

# Function to insert data into db with iteration number

        def db_update(itr,db_data):
            db_data.update(Iteration=itr)
            db[collection].insert_one(db_data)
            print('Inserted new entries \n' + str(db_data))

        try:
            db_update(Iteration,db_data)

        except Exception as e:
            print("Unable to insert/update documents into database. Observed following exception:")
            print(e)

def insertOperations(files,Build,Version,col,Config_ID,Branch,OS,db): #function for retriving required data from log files
    find_iteration = True
    first_client = True
    delete_data = True
    Run_Health = "Successful"
#    try: 
    for file in files:    
        _, filename = os.path.split(file)
        global nodes_num, clients_num , pc_full, iteration , overwrite, custom
        oplist = ["Write" , "Read" , "GetObjTag", "HeadObj" , "PutObjTag"]
        Objsize= 1
        obj = "NA"
        sessions=1
        f = open(file)
        linecount=len(f.readlines())
        f = open(file)
        lines = f.readlines()[-linecount:]
        count=0
        try:
            Run_Health = "Successful"
            while count<linecount:
                if '''"numSamples":''' in lines[count].strip().replace(" ", ""):
                    r=lines[count].strip().replace(" ", "").split(":")
                    Objects = int(r[1].replace(",", ""))
                if '''"numClients":''' in lines[count].strip().replace(" ", ""):
                    r=lines[count].strip().replace(" ", "").split(":")
                    sessions = int(r[1].replace(",", ""))
                if '''"objectSize(MB)":''' in lines[count].strip().replace(" ", ""):
                    r=lines[count].strip().replace(" ", "").split(":")
                    Objsize = float(r[1].replace(",", ""))
                    if(Objsize.is_integer()):
                        obj=str(int(Objsize))+"MB"
                    else:
                        obj=str(round(Objsize*1024))+"KB"

                if '''"Operation":''' in lines[count].replace(" ", ""):
                    r=lines[count].strip().replace(" ", "").split(":")
                    opname = r[1].replace(",", "").strip('"')
                    if opname in oplist:
                        count-=1
                        throughput="NA"
                        iops="NA"
                        if opname=="Write" or opname=="Read":
                            count+=1
                            throughput = float(lines[count+4].split(":")[1].replace(",", ""))
                            iops=round((throughput/Objsize),6)
                            throughput = round(throughput,6)

                        lat={"Max":float(lines[count-4].split(":")[1][:-2]),"Avg":float(lines[count-5].split(":")[1][:-2]),"Min":float(lines[count-3].split(":")[1][:-2])}
                        ttfb={"Max":float(lines[count+12].split(":")[1][:-2]),"Avg":float(lines[count+11].split(":")[1][:-2]),"Min":float(lines[count+13].split(":")[1][:-2]),"99p":float(lines[count+10].split(":")[1][:-2])}
                        data = s3bench(filename,opname,iops,throughput,lat,ttfb,obj,Build,Version,Branch,OS,nodes_num,clients_num,col,Config_ID,overwrite,sessions,Objects,pc_full,custom,Run_Health)
                    
                        if find_iteration:
                            iteration_number = get_latest_iteration(data.Primary_Set, db, col)
                            find_iteration = False
                            # To prevent data of one client getting overwritten/deleted while another client upload data as primary set matches for all client in multi-client run
                            first_client=check_first_client(data.Primary_Set, db, col, iteration_number)

                        if iteration_number == 0:
                            data.insert_update(iteration_number+1)
                        elif not first_client:
                            data.insert_update(iteration_number)
                        elif overwrite == True :
                            data.Primary_Set.update(Iteration=iteration_number)
                            if delete_data:
                                db[col].delete_many(data.Primary_Set)
                                delete_data = False
                                print("'overwrite' is True in config. Hence, old DB entry deleted")
                            data.insert_update(iteration_number)
                        else :
                            data.insert_update(iteration_number+1)
                
                        count += 9
                count +=1

        except Exception as e:
            print(f"Encountered error in file: {filename} , and Exeption is" , e)
            Run_Health = "Failed"           
            '''print(filename,obj,sessions,Objects)
            #iteration_number = get_latest_iteration(data.Primary_Set, db, col)
            if overwrite == True: 
                iteration=iteration_number
            else:
                iteration=iteration_number+1
            query=data.Primary_Set.copy()
            query.update(Object_Size=obj)
            query.update(Objects=Objects)
            query.update(Sessions=sessions)
            query.update(Iteration=iteration)
            print(query)
            db[col].update_many(query , {"$set" : {"Run_State" : Run_Health}})
            results=db[col].find(query) 
            for result in results:
                print(result)'''


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

    dic={'NODES' :str(nodes_list) , 'CLIENTS' : str(clients_list) ,'BUILD_URL': build_url ,'CLUSTER_PASS': cluster_pass ,'CHANGE_PASS': change_pass ,'PRVSNR_CLI_REPO': prv_cli ,'PREREQ_URL': prereq_url ,'SERVICE_USER': srv_usr ,'SERVICE_PASS': srv_pass , 'PC_FULL': pc_full , 'CUSTOM': custom , 'OVERWRITE':overwrite ,'NFS_SERVER': nfs_serv ,'NFS_EXPORT' : nfs_exp ,'NFS_MOUNT_POINT' : nfs_mp , 'NFS_FOLDER' : nfs_fol }
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
    col_config=configs_main.get('R'+Version[0])['config_collection']
    dic = getconfig()
    Config_ID = "NA"
    result = db[col_config].find_one(dic)    
    if result:
        Config_ID = result['_id'] # foreign key : it will map entry in configurations to results entry
    col=configs_main.get('R'+Version[0])['db_collection']
    insertOperations(files,Build,Version,col,Config_ID,Branch,OS,db)

if __name__=="__main__":
    main(sys.argv) 
