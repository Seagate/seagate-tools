
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
from jproperties import Properties

def makeconfig():
	configs = Properties()
	with open('config.properties','rb') as config_file:
		configs.load(config_file)
	return configs

def makeconnection(configs):  #function for making connection with database
	client = MongoClient(configs.get("DB_URL").data)  #connecting with mongodb database
	db=client[configs.get("DB_DATABASE").data]  #database name=performance 
	col=db[configs.get("DB_COLLECTION").data]  #collection name = results
	return col

class s3bench:
	configs = makeconfig()
	col = makeconnection(configs) #getting instance of collection
	def __init__(self,Log_File,Operation, IOPS,Throughput,Latency,TTFB,Object_Size):
		self.Log_File = Log_File
		self.Operation = Operation
		self.IOPS = IOPS
		self.Throughput = Throughput
		self.Latency = Latency
		self.TTFB = TTFB
		self.Object_Size = Object_Size

	def insert_update(self):# function for inserting and updating mongodb database
		self.col.insert_one({"Log_File" : self.Log_File,"Name" : "S3bench","Operation" : self.Operation,"IOPS" : self.IOPS,"Throughput" : self.Throughput,"Latency": self.Latency,"TTFB" : self.TTFB,"Object_Size" : self.Object_Size,"Build" : self.configs.get("BUILD").data.lower(),"HOST" : socket.gethostname()})
		print('Log_File:{}  Name:{}  Operation:{}  IOPS:{}  Throughput:{}  Latency:{}  TTFB:{}  Object_Size:{} Build:{}'.format(self.Log_File,"S3bench",self.Operation,self.IOPS,self.Throughput,self.Latency,self.TTFB,self.Object_Size,self.configs.get("BUILD").data.lower()))


def insertOperations(file):   #function for retriving required data from log files
	head, filename = os.path.split(file)
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
    for path, subdirs, files in os.walk(directory):
        for name in files:
            if(name.lower().endswith(extension)):
                flist.append(os.path.join(path, name))
    return flist

def main(argv):
	dic=argv[1]
	files = getallfiles(dic,".log")#getting all files with log as extension from given directory
	for f in files:
		insertOperations(f)


if __name__=="__main__":
	main(sys.argv) 


