from pymongo import MongoClient
import yaml
Main_path = 'environments.yml'

def makeconfig(name):  #function for connecting with configuration file
    with open(name) as config_file:
        configs = yaml.load(config_file, Loader=yaml.FullLoader)
    return configs

configs_main = makeconfig(Main_path)

def makeconnection():  #function for making connection with database
    client = MongoClient(configs_main['db_url'])  #connecting with mongodb database
    db=client[configs_main['db_database']]  #database name=performance 
    col=db[configs_main['db_collection']]  #collection name = results
    return col

def get_chain(version):
    col = makeconnection()
    cursor = col.find({'Title' : 'Main Chain'})
    chain = cursor[0][version]
    return chain

def get_database():
    client = MongoClient(configs_main['db_url'])  #connecting with mongodb database
    db=client[configs_main['db_database']]  #database name=performance 
    return db
