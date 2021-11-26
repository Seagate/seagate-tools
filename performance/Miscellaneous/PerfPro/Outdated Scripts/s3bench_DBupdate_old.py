
# python3 s3bench_DBupdate.py benchmark.log main.yml config.yml
"""
_id,Log_File,Name,Operation,IOPS,Throughput,Latency,TTFB,Object_Size,HOST
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
	#col=db[configs_main['db_collection']]  #collection name = results
	return db

class s3bench:
	db = makeconnection() #getting instance of database
	def __init__(self, Log_File, Operation, IOPS, Throughput, Latency, TTFB, Object_Size):
		self.Log_File = Log_File
		self.Operation = Operation
		self.IOPS = IOPS
		self.Throughput = Throughput
		self.Latency = Latency
		self.TTFB = TTFB
		self.Object_Size = Object_Size
		self.build = ""
		self.version = ""
		self.Timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

	def getBuild(self):
		listbuild=re.split('//|/',configs_config['BUILD_URL'].strip())
		if len(listbuild) < 7:
			self.build = listbuild[-2]
			self.version = "beta"
		else:
			self.version = listbuild[5]
			if self.version.lower() == "release":
				self.build = listbuild[7]


	def insert_update(self):# function for inserting and updating mongodb database
		self.getBuild()
		
		col_config = self.db["configurations"]
		result = col_config.find_one(configs_config)  # reading entry 
		Config_ID = "NA"
		if result:
			Config_ID = result['_id'] # foreign key : it will map entry in configurations to results entry
		action= "Updated"
		col=self.db[configs_main['db_collection']]

		update_mega_chain(self.build.lower(), self.version, col)
		try:
			count_documents= col.count_documents({"Log_File" : self.Log_File,"Operation":self.Operation,"Build" : self.build.lower(),"Version":self.version})
			if count_documents == 0:
				col.insert_one({"Log_File" : self.Log_File,"Name" : "S3bench","Operation" : self.Operation,"Object_Size" : self.Object_Size,"Build" : self.build.lower(),"Version":self.version,"HOST" : socket.gethostname()})
				action = "Inserted"
			entry = { "IOPS" : self.IOPS,"Throughput" : self.Throughput,"Latency": self.Latency,"TTFB" : self.TTFB,"Timestamp":self.Timestamp, "Config_ID":Config_ID}
			col.update_one({ "Log_File" : self.Log_File,"Operation" : self.Operation }, { "$set": entry})
		except Exception as e:
			print("Unable to insert/update documents into database. Observed following exception:")
			print(e)
		else:
			print('Data {} :: Log_File:{}  Name:{}  Operation:{} {}\n'.format(action,self.Log_File,"S3bench",self.Operation,entry))


def insertOperations(file):   #function for retriving required data from log files
	_, filename = os.path.split(file)
	oplist = ["Write" , "Read" , "GetObjTag", "HeadObj" , "PutObjTag"]
	obj = filename.split("_")[2]
	if('m' in obj) or ('M' in obj):
		Objsize =int(re.split('m|M',obj)[0])
	if('k' in obj) or ('K' in obj):
		Objsize =float(re.split('k|K',obj)[0])*0.001
	f = open(file)
	lines = f.readlines()[-100:]
	count=0
	while count<100:
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
					iops=round((throughput/Objsize),3)
					throughput = round(throughput,3)
				lat={"Max":float(lines[count+4].split(":")[1]),"Avg":float(lines[count+5].split(":")[1]),"Min":float(lines[count+6].split(":")[1])}
				ttfb={"Max":float(lines[count+7].split(":")[1]),"Avg":float(lines[count+8].split(":")[1]),"Min":float(lines[count+9].split(":")[1])}
				data = s3bench(filename,opname,iops,throughput,lat,ttfb,obj)
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
            col.find_and_update_one(   
                {'Title' : 'Main Chain'},
                {
                    'release':release_chain      
            })
            print("...Mega entry has updated with release build ", build)
            return
    else:
        if build not in beta_chain:
            print(build)
            beta_chain.append(build)
            col.find_and_update_one(   
                {'Title' : 'Main Chain'},
                {
                    'beta':beta_chain  
            })
            print("...Mega entry has updated with beta build ", build)
            return
    print("...Mega entry has not updated for build ", build)

def main(argv):
	dic=argv[1]
	files = getallfiles(dic,".log")#getting all files with log as extension from given directory
	for f in files:
		insertOperations(f)


if __name__=="__main__":
	main(sys.argv) 
