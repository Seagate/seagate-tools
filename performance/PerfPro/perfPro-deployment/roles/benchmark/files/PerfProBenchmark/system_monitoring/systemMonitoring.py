#!/usr/bin/env python3
"""
Script for collecting system data 
Command line arguments:   [path for main.yml]
  Ex: python3 systemMonitoring.py <Path of main.yml file> <Path of config.yml file>
Requirements:
pip3 install PyYAML==5.3.1
pip3 install pymongo==3.11.0
"""

import subprocess
import sys
import pymongo
from pymongo import MongoClient
import yaml
import time
import socket
import os
import json
from datetime import datetime
import urllib.request
import re


#SysConfig_path = sys.argv[1]
Main_path = sys.argv[1]
Config_path = sys.argv[2]


"""
hostname = socket.gethostname()
backupfile = hostname+"_sar.json"
print(backupfile)

def write_json(data, filename=backupfile): 
	with open(filename,'w') as f: 
		json.dump(data, f, indent=4)

def addbackup(dataentry):
	if not os.path.exists(backupfile):
		with open(backupfile,'a') as f:
			json.dump([],f)
	with open(backupfile) as json_file:
		data = json.load(json_file)
		data.append(dataentry)
	write_json(data)



"""
def makeconfig(name):  #function for connecting with configuration file
	with open(name) as config_file:
		configs = yaml.load(config_file, Loader=yaml.FullLoader)
	return configs

configs_config = makeconfig(Config_path)  # getting instance  of config file

build_url=configs_config.get('BUILD_URL')

def get_release_info(variable):
    release_info= urllib.request.urlopen(build_url+'RELEASE.INFO')
    for line in release_info:
        if variable in line.decode("utf-8"):
            strinfo=line.decode("utf-8").strip()
            strip_strinfo=re.split(': ',strinfo)
            return(strip_strinfo[1])



def makeconnection():  #function for making connection with database   
    configs = makeconfig(Main_path)
    client = MongoClient(configs['db_url'])  #connecting with mongodb database
    db=client[configs['db_database']]  #database name=performance 
    Version=get_release_info('VERSION')
    Version=Version[1:-1]
    col_stats='systemresults_'+Version[0]
    col=db[col_stats]  #collection name = systemresults
    return col
       

def adddata(data,device,col):
    attr = " ".join( data[2].decode("utf-8").split()).split(" ") #fetching attributes from output lines and storing in a list	
    length=len(attr)
    for d in data[3:]:
        value=" ".join(d.decode("utf-8").split()).split(" ")#fetching value from output lines and storing in a list
        if value[0] !="":
            if value[2]!="DEV" and value[2]!="IFACE":
                count=2
                dic = {"Device":device,"Timestamp":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"Time":value[0],"HOST" : socket.gethostname()}
                while count<length:
                    dic.update( {attr[count] : value[count]} ) # adding respective attribute and value pair in dictionary
                    count+=1
                print(dic)
                try:
                    col.insert_one(dic)  #inserting dictionary values in mongodb
                except Exception as e:
                    print("Unable to insert/update documents into database. Observed following exception:")
                    print(e)
                else:
                    print(dic)
		


def addReport(): #function for getting system report accoordiing to 'cmd' argument
    col = makeconnection()
    cmd = [['sar 5','p1',"CPU"],['sar -r 5','p2',"MEMORY"],['sar -d 5','p3',"DISK"],['sar -b 5','p4',"I/O"],['sar -n DEV 5','p5',"NETWORK"]]
    count =0
    f = open("pidfile","w+")
    f.close()
    for c in cmd:
        c[1] =subprocess.Popen(c[0], shell=True, stdout=subprocess.PIPE)
        count+=1

	#time.sleep(3)
    while os.path.isfile("pidfile"):
        time.sleep(1)

    for c in cmd:
        c[1].kill()
        out,err = c[1].communicate()
        outs = out.splitlines()
        print("\n"+c[2]+"\n")
        adddata(outs,c[2],col)


def retriveAll():   #function for retriving all the data from database
    col = makeconnection()
    data = col.find()
    for d in data:
        print(d)

def main():
    addReport() 

if __name__=="__main__":
    main() 
