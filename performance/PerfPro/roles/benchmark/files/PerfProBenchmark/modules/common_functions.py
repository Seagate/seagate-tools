#!/usr/bin/env python3
import yaml
from pymongo import MongoClient
import os


def makeconfig(name):
    """Read data from config file"""
    with open(name) as config_file:
        configs = yaml.safe_load(config_file)
    return configs


def makeconnection(main_config, collection, database):
    """Getting collection from mongo DB database"""
    client = MongoClient(main_config['db_url'])
    db = client[main_config['db_database']]

    collection = db[main_config.get(database)[collection]]

    return db, collection


def getallfiles(directory, extension):
    """function to return all file names with perticular extension"""
    flist = []
    for path, _, files in os.walk(directory):
        for name in files:
            if(name.lower().endswith(extension)):
                flist.append(os.path.join(path, name))
    if flist:
        return True, flist
    else:
        return False, flist


def remove_emptys_from_list(data):
    return [x for x in data if x]


def get_metric_value(data):
    return remove_emptys_from_list(data.split(" "))[-1][:-1]
