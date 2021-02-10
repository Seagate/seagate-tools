"""
Script for storing configuration file data into MongoDB
Command line arguments:   [path for main.yml] [path for config.yml]
  Ex: python3 addconfiguration.py <Path of main.yml file> <Path of main.yml file>
Requirements:
pip3 install PyYAML==5.3.1
pip3 install pymongo==3.11.0
"""

import pymongo
from pymongo import MongoClient
import yaml
import sys

Main_path = sys.argv[1]
Config_path = sys.argv[2]


def makeconfig(name):  #function for connecting with configuration file
	with open(name) as config_file:
		configs = yaml.load(config_file, Loader=yaml.FullLoader)
	return configs

def makeconnection():  #function for making connection with database
	configs = makeconfig(Main_path)
	client = MongoClient(configs['db_url'])  #connecting with mongodb database
	db=client[configs['db_database']]  #database name=performance 
	col=db[configs['config_collection']]  #collection name = configurations
	return col

def storeconfigurations():  # Fuction will store the configuration details into mongodb
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

	col = makeconnection()
	try:
		count_documents= col.count_documents(dic)
		if count_documents == 0:
			col.insert_one(dic)
			print('Configuration Data is Recorded ::')
			print(dic)
		else:
			print('Configuration data already present')
	except Exception as e:
		print("Unable to insert/update documents into database. Observed following exception:")
		print(e)
		



def main(argv):
	storeconfigurations()


if __name__=="__main__":
	main(sys.argv) 
