from pymongo import MongoClient
from jproperties import Properties
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
    # col = get_DB_details()
    col = makeconnection()
    cursor = col.find({'Title' : 'Main Chain'})

    return cursor[0][version]

print(get_chain('release'))
# ['2790', '2798', '2801', '2801-ssd', '2809', 'cortx-1.0.0-rc3', 'cortx-1.0.0-rc1']
# ['cortx-1.0.0-32-rc11', 'cortx-1.0.0-33-rc12', 'cortx-1.0.0-34-rc13', 'cortx-1.0.0-35-rc14']
# col = makeconnection()
# col.update_one({'Title' : 'Main Chain'},
#     {
#         "$set":{
#             'release' : ['2790', '2798', '2801', '2801-ssd', '2809','cortx-1.0.0-rc1', 'cortx-1.0.0-rc3'],
#             'GA' : ['cortx-1.0.0-rc1', 'cortx-1.0.0-rc3']
#         }
#     }
# )