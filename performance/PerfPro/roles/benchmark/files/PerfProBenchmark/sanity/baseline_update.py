from pymongo import MongoClient
from bson.objectid import ObjectId
import yaml
import sys

Main_path = sys.argv[1]
Config_path = sys.argv[2]
Config_ID = sys.argv[3]
objInstance = ObjectId(Config_ID)


def makeconfig(name):  # function for connecting with configuration file
    with open(name) as config_file:
        configs = yaml.safe_load(config_file)
    return configs


configs_main = makeconfig(Main_path)
configs_config = makeconfig(Config_path)


def makeconnection(collection):  # function for making connection with database
    # connecting with mongodb database
    client = MongoClient(configs_main['db_url'])
    db = client[configs_main['db_database']]  # database name=performance
    col = configs_main.get('SANITY')[collection]
    sanity_col = db[col]
    return sanity_col


def baseline_update(sanity_config, query):
    baseline = sanity_config.distinct('Baseline')
    latest_baseline = max(baseline)
    if (latest_baseline >= 1):
        baseline = latest_baseline+1
    else:
        baseline = 1
    sanity_config.update_one(
        query, {"$set": {'Baseline': baseline, 'Comment': 'highest throughput observed'}})
    entry = sanity_config.find_one(query)
    print(entry)


sanity_config = makeconnection('sanity_config_collection')
query = {'_id': objInstance}
baseline_update(sanity_config, query)
