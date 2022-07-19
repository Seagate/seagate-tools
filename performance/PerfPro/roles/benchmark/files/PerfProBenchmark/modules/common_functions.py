#!/usr/bin/env python3
import yaml
from pymongo import MongoClient
import os
import csv
import re
import json


# def makeconfig(name):
#     """Read data from config file"""
#     with open(name) as config_file:
#         configs = yaml.safe_load(config_file)
#     return configs


# def makeconnection(main_config, collection, database):
#     """Getting collection from mongo DB database"""
#     client = MongoClient(main_config['build']['url'])
#     db = client[main_config['sanity']['database']['name']]
#     col_stats = db[main_config.get(database)[collection]]

#     return db, col_stats


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


def get_build_info(config):
    """Function To get the build information

    Args:
        config (dict): configuration file

    Returns:
        build information
    """
    if config["build"]["generation_type"] == 'RELEASE.INFO':
        version = get_release_info(obj, 'VERSION')[1:-1]
        ver_strip = re.split('-', version)
        Version = ver_strip[0]
        Build = ver_strip[1]
        Branch = "NA"
        OS = get_release_info(obj, 'OS')[1:-1]
    elif config["build"]["generation_type"] == 'USER_INFO':
        obj.Build = config["build"]["number"]
        obj.Version = config["build"]["version"]
        obj.Branch = config["build"]["branch"]
        obj.OS = config["cluster"]["os"]

    return Build, Version, Branch, OS


def get_release_info(obj, variable):
    """
    Function to get build release information from URL
    Parameters : input(Variable) - Variable from RELEASE.INFO of the Build
                 returns(string) - Value of the Variable
    """
    release_info = os.popen('docker run --rm -it ' +
                            obj.config["docker_info"] + ' cat /opt/seagate/cortx/RELEASE.INFO')
    lines = release_info.readlines()
    for line in lines:
        if variable in line:
            strinfo = line.strip()
            strip_strinfo = re.split(': ', strinfo)
            return(strip_strinfo[1])


def get_solution(obj, config):
    if config["solution"].upper() == 'LC':
        obj.col = config["database"]["collections"]["lc"]
    elif config["solution"].upper() == 'LR':
        obj.col = config["database"]["collections"]["lr"]
    elif config["solution"].upper() == 'LEGACY':
        obj.col = config.get(f"R{obj.Version.split('.')[0]}")
    else:
        print("Error! Can not find suitable collection to upload data")


def get_latest_iteration(query, uri, db_name, collection):
    """Function to find latest iteration

    Args:
        query (dict): data for creating documnets in mongodb
        uri (string): URI of MongoDB database
        db_name (string): Database name
        collection (string): Collection name in database

    Returns:
        [int]: [returns iteration number]
    """
    max_iter = 0
    status, cursor = mapi.find_documents(query, None, uri, db_name, collection)
    for record in cursor:
        if max_iter < record['Iteration']:
            max_iter = record['Iteration']
    return max_iter


def update_or_insert_document(self, primary_set, insertion_set, collection, id_key):
    status, docs = mapi.count_documents(
        primary_set, self.db_uri, self.db_name, getattr(self, collection))
    if status and not docs:
        updation_status, result = mapi.add_document(
            insertion_set, self.db_uri, self.db_name, getattr(self, collection))
        if updation_status:
            setattr(self, id_key, result)
    elif status:
        updation_status, result = mapi.find_documents(
            primary_set, None, self.db_uri, self.db_name, getattr(self, collection))
        if updation_status:
            setattr(self, id_key, docs[0]["_id"])
    else:
        print(
            f"Status {docs[0]} while counting Mongo DB record: ", docs[1])

    if not updation_status:
        print(
            f"Status {result[0]} while inserting Mongo DB record: ", result[1])
        setattr(self, id_key, None)


def get_run_config_id(obj):
    primary_set = set_benchmark_config_primary_set(obj)
    insertion_set = set_bench_config_insertion_set(obj, primary_set)

    update_or_insert_document(
        obj, primary_set, insertion_set, obj.col["config"], "config_id")


# HSbench realted functions
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


# Cosbench related funtions
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
                operation = row[1]
                obj_size = attr[1]
                buckets = int(re.split(" ", attr[2])[1])
                objects = int(re.split(" ", attr[3])[1])
                sessions = int(re.split(" ", attr[4])[1])
