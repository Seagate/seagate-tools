#!/usr/bin/env python3
import yaml
from pymongo import MongoClient
import os
import csv
import re
import json

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


def get_files_from_directory(directory, extension):
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


def import_perfpro_config():
    fname = "./perfpro_config.yml"
    try:
        with open(fname, 'r') as config_file:
            return yaml.safe_load(config_file)
    except OSError:
        print(f"OS error occurred trying to open {fname}")



## HSbench realted functions
def extract_json(file):

    """
    Function to get bucketops from log files

    Parameters : input(str) - file name to get data from files
                 returns(dataFrame) - pandas dataframe containing bucketOPs details
    """

    json_data = []
    keys = ['Mode', 'Seconds', 'Ops', 'Mbps',
            'Iops', 'MinLat', 'AvgLat', 'MaxLat']
    values = []
    with open(file, 'r') as list_ops:
        json_data = json.load(list_ops)
    for data in json_data:
        value = []
        if(data['IntervalName'] == 'TOTAL'):
            for key in keys:
                value.append(data[key])
            values.append(value)
    table_op = pd.DataFrame(values, columns=keys)
    return table_op

def read_hsbench_results():
    data_dict = None
    try:
        data = extract_json(doc)
        data.reset_index(inplace=False)
        data_dict = data.to_dict("records")
    except (AttributeError, NameError):
        data_dict = 'NA'

    filename = doc
    doc = filename.strip(".json")
    attr = re.split("_", doc)
    obj_size = attr[-7]
    buckets = int(attr[-3])
    objects = int(attr[-5])
    sessions = int(attr[-1])


## Cosbench related funtions
def read_cosbench_results():
    with open(file) as csv_file:
         csv_reader = csv.reader(csv_file, delimiter=',')
         line_count = 0
         for row in csv_reader:
             if line_count == 0:
                 line_count += 1
             else:
                 if(row[1] == "read" or row[1] == "write"):
                 attr = re.split(',|-', filename)
                 obj = attr[1]
                 if('m' in obj) or ('M' in obj):
                     Objsize = int(re.split('m|M', obj)[0])
                 if('k' in obj) or ('K' in obj):
                     Objsize = float(re.split('k|K', obj)[0])*0.001

                 iops = float(row[13])
                 throughput = iops*Objsize
                 lat = {"Max": float(row[12]), "Avg": float(row[5])}
                 operation= row[1]
                 obj_size= attr[1]
                 buckets= int(re.split(" ", attr[2])[1])
                 objects= int(re.split(" ", attr[3])[1])
                 sessions= int(re.split(" ", attr[4])[1])


