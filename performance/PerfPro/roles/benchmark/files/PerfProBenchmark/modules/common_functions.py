#!/usr/bin/env python3
import yaml
from pymongo import MongoClient
import os
import mongodbapi as mapi
from modules.schemas import get_bench_config_insertion_set, set_bench_config_insertion_set

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


def get_build_info(obj, config):
    if config["build"]["generation_type"] == 'RELEASE.INFO':
        version = get_release_info('VERSION')[1:-1]
        ver_strip = re.split('-', version)
        obj.Version = ver_strip[0]
        obj.Build = ver_strip[1]
        obj.OS = get_release_info('OS')[1:-1]
    elif config["build"]["generation_type"] == 'USER_INFO':
        obj.Build = config["build"]["number"]
        obj.Version = config["build"]["version"]
        obj.Branch = config["build"]["branch"]
        obj.OS = config["cluster"]["os"]


def get_release_info(variable):

    """
    Function to get build release information from URL
    Parameters : input(Variable) - Variable from RELEASE.INFO of the Build
                 returns(string) - Value of the Variable
    """
    release_info=os.popen('docker run --rm -it ' + docker_info +' cat /opt/seagate/cortx/RELEASE.INFO')
    lines=release_info.readlines()
    for line in lines:
        if variable in line:
            strinfo=line.strip()
            strip_strinfo=re.split(': ',strinfo)
            return(strip_strinfo[1])


def get_solution(obj,config):
    if config["solution"].upper() == 'LC':
        obj.col = config["database"]["collection"]["lc"]
    elif config["solution"].upper()  == 'LR':
        obj.col = config["database"]["collection"]["lr"]
    elif config["solution"].upper()  == 'LEGACY':
        obj.col = config.get(f"R{self.Version.split('.')[0]}")
    else:
        print("Error! Can not find suitable collection to upload data")


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
    primary_set = set_bench_config_primary_set(obj)
    insertion_set = set_bench_config_insertion_set(obj, primary_set)

    update_or_insert_document(obj, primary_set, insertion_set, obj.col["config"], "config_id")

