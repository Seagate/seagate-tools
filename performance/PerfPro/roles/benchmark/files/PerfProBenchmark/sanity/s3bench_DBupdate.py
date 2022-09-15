#!/usr/bin/env python3
#
# Seagate-tools: PerfPro
# Copyright (c) 2022 Seagate Technology LLC and/or its Affiliates
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
#
# For any questions about this software or licensing,
# please email opensource@seagate.com or cortx-questions@seagate.com.
#
# -*- coding: utf-8 -*-

"""
python3 s3bench_DBupdate.py <log file path> <main.yaml path> <config.yaml path>
Attributes: _id,Log_File,Name,Operation,IOPS,Throughput,Latency,TTFB,Object_Size,HOST
"""

from pymongo import MongoClient
import socket
import ast
import sys
import os
import yaml
from datetime import datetime

Main_path = sys.argv[2]
Config_path = sys.argv[3]
# collecting runtime entries
Repository = sys.argv[4]
PR_ID = sys.argv[5]
User = sys.argv[6]
GID = sys.argv[7]

sanity_schema = {
    "motr_repository": "",
    "rgw_repository": "",
    "hare_repository": "",
    "other_repos": [],
    "PR_ID": " "
}


def makeconfig(name):  # function for connecting with configuration file
    ''' Function to connect with configuration file to fetch the details of the file '''
    with open(name) as config_file:
        configs = yaml.safe_load(config_file)
    return configs


''' configuration values are loaded in respective variables '''
configs_main = makeconfig(Main_path)
configs_config = makeconfig(Config_path)

''' Configuration variables to be used in the script '''
nodes_list = configs_config.get('NODES')
clients_list = configs_config.get('CLIENTS')
pc_full = configs_config.get('PC_FULL')
overwrite = configs_config.get('OVERWRITE')
custom = configs_config.get('CUSTOM')
nodes_num = len(nodes_list)
clients_num = len(clients_list)

''' Function to connect to the Database and fetch the DB details and add data to DB throughout the script execution '''


def makeconnection(collection):  # function for making connection with database
    '''Function to connect to the Database and fetch the DB details and
    add data to DB throughout the script execution'''
    client = MongoClient(
        configs_main['db_url'])  # connecting with mongodb database
    db = client[configs_main['db_database']]  # database name=performance
#    return db
    col = configs_main.get('SANITY')[collection]
    sanity_col = db[col]
    return sanity_col

# Function to find latest iteration


def get_latest_iteration(query, db_collection):
    ''' Function to get the latest iteration value from the existing DB entries. '''
    max_iter = 0
    cursor = db_collection.find(query)
    for record in cursor:
        if max_iter < record['Iteration']:
            max_iter = record['Iteration']
    return max_iter

# Function to resolve iteration/overwrite etc in multi-client run


def check_first_client(query, db_collection, itr):
    ''' Function returns if the client trying to push DB entries is First client from the list of clients. '''
    query.update(Iteration=itr)
    cursor = db_collection.distinct('HOST', query)
    if (len(cursor) < query["Clients_Count"]):
        cur_client = socket.gethostname()
        if cur_client in cursor:
            print(
                f"Multi-Client Run: Re-Upload from client {cur_client} detected. Existing data in DB from this client for current run will get overwritten")
            query.update(HOST=cur_client)
            db_collection.delete_many(query)
        return False
    return True


''' Below class created the Database object for S3bench data entry and will be used to push them in the DB'''


class s3bench:

    def __init__(self, Log_File, Operation, IOPS, Throughput, Total_Errors, Total_Ops, Latency, TTFB, Object_Size, db_collection, run_ID, Config_ID, Overwrite, Sessions, Objects, run_health):

        self.Log_File = Log_File
        self.Operation = Operation
        self.IOPS = IOPS
        self.Throughput = Throughput
        self.Total_Errors = Total_Errors
        self.Total_Ops = Total_Ops
        self.Latency = Latency
        self.TTFB = TTFB
        self.Object_Size = Object_Size
        self.db_collection = db_collection
        self.run_ID = run_ID
        self.Config_ID = Config_ID
        self.Timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.Overwrite = Overwrite
        self.Sessions = Sessions
        self.Objects = Objects
        self.Run_State = run_health

# Set for uploading to db
        self.Primary_Set = {
            "Tool": "S3bench",
            "Config_ID": self.Config_ID,
            "run_ID": self.run_ID
        }
        self.Runconfig_Set = {
            "Operation": self.Operation,
            "Object_Size": self.Object_Size,
            "Buckets": 1,
            "Objects": self.Objects,
            "Sessions": self.Sessions
        }
        self.Updation_Set = {
            "HOST": socket.gethostname(),
            # "Config_ID":self.Config_ID,
            "IOPS": self.IOPS,
            "Throughput": self.Throughput,
            "Total_Errors": self.Total_Errors,
            "Total_Ops": self.Total_Ops,
            "Latency": self.Latency,
            "Log_File": self.Log_File,
            "TTFB": self.TTFB,
            "Timestamp": self.Timestamp,
            "Run_State": self.Run_State
        }

    def insert_update(self, Iteration):
        ''' Function for inserting and updating mongodb database '''
        # db = makeconnection()
        db_data = {}
        db_data.update(self.Primary_Set)
        db_data.update(self.Runconfig_Set)
        db_data.update(self.Updation_Set)
        # collection = self.Col
        db_collection = self.db_collection

        def db_update(itr, db_data):
            '''Function to insert data into db with iteration number '''
            db_data.update(Iteration=itr)
            db_collection.insert_one(db_data)
            print('Inserted new entries \n' + str(db_data))

        try:
            db_update(Iteration, db_data)

        except Exception as e:
            print(
                "Unable to insert/update documents into database. Observed following exception:")
            print(e)

# function for retriving required data from log files


def insertOperations(files, db_collection, run_ID, Config_ID):
    ''' Function helps in collecting the data from log files and insert in the DB. '''
    find_iteration = True
    first_client = True
    delete_data = True
    Run_Health = "Successful"
    for file in files:
        _, filename = os.path.split(file)
        oplist = ["Write", "Read", "GetObjTag", "HeadObj", "PutObjTag"]
        Objsize = 1
        obj = "NA"
        sessions = 1
        f = open(file)
        linecount = len(f.readlines())
        f = open(file)
        lines = f.readlines()[-linecount:]
        count = 0
        try:
            Run_Health = "Successful"
            while count < linecount:
                if '''"numSamples":''' in lines[count].strip().replace(" ", ""):
                    r = lines[count].strip().replace(" ", "").split(":")
                    Objects = int(r[1].replace(",", ""))
                if '''"numClients":''' in lines[count].strip().replace(" ", ""):
                    r = lines[count].strip().replace(" ", "").split(":")
                    sessions = int(r[1].replace(",", ""))
                if '''"objectSize(MB)":''' in lines[count].strip().replace(" ", ""):
                    r = lines[count].strip().replace(" ", "").split(":")
                    Objsize = float(r[1].replace(",", ""))
                    if(Objsize.is_integer()):
                        obj = str(int(Objsize))+"MB"
                    else:
                        obj = str(round(Objsize*1024))+"KB"

                if '''"Operation":''' in lines[count].replace(" ", ""):
                    r = lines[count].strip().replace(" ", "").split(":")
                    opname = r[1].replace(",", "").strip('"')
                    if opname in oplist:
                        count -= 1
                        throughput = "NA"
                        iops = "NA"
                        if opname == "Write" or opname == "Read":
                            count += 1
                            throughput = float(
                                lines[count+4].split(":")[1].replace(",", ""))
                            iops = round((throughput/Objsize), 6)
                            throughput = round(throughput, 6)

                            error_count = int(
                                lines[count-1].split(":")[1].replace(",", ""))
                            ops_count = int(
                                lines[count+3].split(":")[1].replace(",", ""))

                        lat = {"Max": float(lines[count-4].split(":")[1][:-2]), "Avg": float(
                            lines[count-5].split(":")[1][:-2]), "Min": float(lines[count-3].split(":")[1][:-2])}
                        ttfb = {"Max": float(lines[count+12].split(":")[1][:-2]), "Avg": float(lines[count+11].split(":")[
                            1][:-2]), "Min": float(lines[count+13].split(":")[1][:-2]), "99p": float(lines[count+10].split(":")[1][:-2])}
                        data = s3bench(filename, opname, iops, throughput, error_count, ops_count, lat, ttfb,
                                       obj, db_collection, run_ID, Config_ID, overwrite, sessions, Objects, Run_Health)
# Build,Version,Branch,OS,nodes_num,clients_num,col,Config_ID,overwrite,sessions,Objects,pc_full,custom,Run_Health)

                        if find_iteration:
                            iteration_number = get_latest_iteration(
                                data.Primary_Set, db_collection)
                            find_iteration = False
                            # To prevent data of one client getting overwritten/deleted while another client upload data as primary set matches for all client in multi-client run
                            # first_client=check_first_client(data.Primary_Set, db_collection, iteration_number)
                            # the query needs to be updated hence marking this commented.
                        if iteration_number == 0:
                            data.insert_update(iteration_number+1)
                        elif not first_client:
                            data.insert_update(iteration_number)
                        elif overwrite == True:
                            data.Primary_Set.update(Iteration=iteration_number)
                            if delete_data:
                                db_collection.delete_many(data.Primary_Set)
                                delete_data = False
                                print(
                                    "'overwrite' is True in config. Hence, old DB entry deleted")
                            data.insert_update(iteration_number)
                        else:
                            data.insert_update(iteration_number+1)

                        count += 9
                count += 1

        except Exception as e:
            print(
                f"Encountered error in file: {filename} , and Exeption is", e)
            Run_Health = "Failed"


def getallfiles(directory, extension):
    ''' Function to return all file names with perticular extension '''
    flist = []
    for path, _, files in os.walk(directory):
        for name in files:
            if(name.lower().endswith(extension)):
                flist.append(os.path.join(path, name))
    return flist


def insert_run_details(run_details, repo_details, PR_ID):
    ''' Function to insert run details in mongo DB '''
    sanity_schema["other_repos"] = list(repo_details)
    sanity_schema["PR_ID"] = PR_ID
    for repo in list(repo_details):
        if repo["category"].lower() == "motr":
            key = "motr_repository"
        elif repo["category"].lower() == "rgw":
            key = "rgw_repository"
        elif repo["category"].lower() == "hare":
            key = "hare_repository"
        else:
            continue

        sanity_schema[key] = repo["repo"]

    try:
        count_documents = run_details.count_documents(sanity_schema)
        if count_documents == 0:
            run_details.insert_one(sanity_schema)
            print("Sanity Run details recorded \n" + str(sanity_schema))
            result = run_details.find_one(sanity_schema)
            if result:
                run_ID = result['_id']
        else:
            print("Sanity Run details already present \n" + str(sanity_schema))
            result = run_details.find_one(sanity_schema)
            if result:
                run_ID = result['_id']
    except Exception as e:
        print(
            "Unable to insert/update documents into database. Observed following exception:")
        print(e)
    return(run_ID)


def insert_config_details(sanity_config, run_ID):
    ''' Function to insert Config details in mongo DB. '''
    global User, GID, nodes_num, clients_num, nodes_list, clients_list
    nodes = []
    clients = []
    for i, _ in enumerate(nodes_list):
        nodes.append(nodes_list[i][i+1])

    for i, _ in enumerate(clients_list):
        clients.append(clients_list[i][i+1])

    config_data = {
        "User": User,
        "GID": GID,
        "run_ID": run_ID,
        "Nodes": nodes,
        "Nodes_Count": nodes_num,
        "Clients": clients,
        "Clients_Count": clients_num,
        "Cluster_Fill": configs_config.get('PC_FULL'),
        "Custom_Label": configs_config.get('CUSTOM'),
        "Baseline": int(-1),
        "Comment": "NA"
    }
    try:
        count_documents = sanity_config.count_documents(config_data)
        if count_documents == 0:
            sanity_config.insert_one(config_data)
            print("Config details recorded \n" + str(config_data))
            result = sanity_config.find_one(config_data)
            if result:
                Config_ID = result['_id']
        else:
            print("Config details already present \n" + str(config_data))
            result = sanity_config.find_one(config_data)
            if result:
                Config_ID = result['_id']
    except Exception as e:
        print(
            "Unable to insert/update documents into database. Observed following exception:")
        print(e)
    return(Config_ID)


def main(argv):
    ''' Main Function for S3bench DB update '''
    dic = argv[1]
    # getting all files with log as extension from given directory
    files = getallfiles(dic, ".log")

    run_details = makeconnection('sanity_details_collection')
    sanity_config = makeconnection('sanity_config_collection')
    db_collection = makeconnection('sanity_dbcollection')

# insert DB entries
    run_ID = insert_run_details(run_details, list(
        ast.literal_eval(argv[4])), PR_ID)
    Config_ID = insert_config_details(sanity_config, run_ID)

    insertOperations(files, db_collection, run_ID, Config_ID)


if __name__ == "__main__":
    main(sys.argv)
