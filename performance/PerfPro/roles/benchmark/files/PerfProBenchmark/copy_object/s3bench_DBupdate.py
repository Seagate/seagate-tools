
#!/usr/bin/env python3
"""
python3 s3bench_DBupdate.py <log file path> <main.yaml path> <config.yaml path>
Attributes: _id,Log_File,Name,Operation,IOPS,Throughput,Latency,TTFB,Object_Size,HOST
"""

from pymongo import MongoClient
import re
import socket
import sys
import os
import yaml
from datetime import datetime

Main_path = sys.argv[2]
Config_path = sys.argv[3]


def makeconfig(name):  # function for connecting with configuration file
    with open(name) as config_file:
        configs = yaml.safe_load(config_file)
    return configs


configs_main = makeconfig(Main_path)
configs_config = makeconfig(Config_path)

build_info = configs_config.get('BUILD_INFO')
build_url = configs_config.get('BUILD_URL')
docker_info = configs_config.get('DOCKER_INFO')
nodes_list = configs_config.get('NODES')
clients_list = configs_config.get('CLIENTS')
pc_full = configs_config.get('PC_FULL')
overwrite = configs_config.get('OVERWRITE')
custom = configs_config.get('CUSTOM')
nodes_num = len(nodes_list)
clients_num = len(clients_list)


def makeconnection():  # function for making connection with database
    # connecting with mongodb database
    client = MongoClient(configs_main['db_url'])
    db = client[configs_main['db_database']]  # database name=performance
    return db


def get_release_info(variable):
    release_info = os.popen('docker run --rm -it ' +
                            docker_info + ' cat /opt/seagate/cortx/RELEASE.INFO')
    lines = release_info.readlines()
    for line in lines:
        if variable in line:
            strinfo = line.strip()
            strip_strinfo = re.split(': ', strinfo)
            return(strip_strinfo[1])

# Function to find latest iteration


def get_latest_iteration(query, db, collection):
    max_iter = 0
    cursor = db[collection].find(query)
    for record in cursor:
        if max_iter < record['Iteration']:
            max_iter = record['Iteration']
    return max_iter

# Function to resolve iteration/overwrite etc in multi-client run


def check_first_client(query, db, collection, itr):
    query.update(Iteration=itr)
    cursor = db[collection].distinct('HOST', query)
    if (len(cursor) < query["Count_of_Clients"]):
        cur_client = socket.gethostname()
        if cur_client in cursor:
            print(
                f"Multi-Client Run: Re-Upload from client {cur_client} detected. Existing data in DB from this client for current r    un will get overwritten")
            query.update(HOST=cur_client)
            db[collection].delete_many(query)
        return False
    return True


class s3bench:

    def __init__(self, Log_File, Operation, IOPS, Throughput, Latency, TTFB, Object_Size, Build, Version, Branch, OS, Nodes_Num, Clients_Num, Col, Config_ID, Overwrite, Sessions, Objects, PC_Full, Custom, Additional_op, Run_Health):

        self.Log_File = Log_File
        self.Operation = Operation
        self.IOPS = IOPS
        self.Throughput = Throughput
        self.Latency = Latency
        self.TTFB = TTFB
        self.Object_Size = Object_Size
        self.Build = Build
        self.Version = Version
        self.Branch = Branch
        self.OS = OS
        self.Nodes_Num = Nodes_Num
        self.Clients_Num = Clients_Num
        self.Col = Col
        self.Config_ID = Config_ID
        self.Timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.Overwrite = Overwrite
        self.Sessions = Sessions
        self.Objects = Objects
        self.PC_Full = PC_Full
        self.Custom = str(Custom).upper()
        self.Additional_op = Additional_op
        self.Run_State = Run_Health

# Set for uploading to db
        self.Primary_Set = {
            "Name": "S3bench",
            "Build": self.Build,
            "Version": self.Version,
            "Branch": self.Branch,
            "OS": self.OS,
            "Count_of_Servers": self.Nodes_Num,
            "Count_of_Clients": self.Clients_Num,
            "Percentage_full": self.PC_Full,
            "Custom": self.Custom
        }
        self.Runconfig_Set = {
            "Operation": self.Operation,
            "Object_Size": self.Object_Size,
            "Buckets": 1,
            "Objects": self.Objects,
            "Sessions": self.Sessions,
            "Additional_op": self.Additional_op
        }
        self.Updation_Set = {
            "HOST": socket.gethostname(),
            "Config_ID": self.Config_ID,
            "IOPS": self.IOPS,
            "Throughput": self.Throughput,
            "Latency": self.Latency,
            "Log_File": self.Log_File,
            "TTFB": self.TTFB,
            "Timestamp": self.Timestamp,
            "Run_State": self.Run_State
        }

    # function for inserting and updating mongodb database
    def insert_update(self, Iteration):
        db = makeconnection()
        db_data = {}
        db_data.update(self.Primary_Set)
        db_data.update(self.Runconfig_Set)
        db_data.update(self.Updation_Set)
        collection = self.Col

# Function to insert data into db with iteration number

        def db_update(itr, db_data):
            db_data.update(Iteration=itr)
            db[collection].insert_one(db_data)
            print('Inserted new entries \n' + str(db_data))

        try:
            db_update(Iteration, db_data)

        except Exception as e:
            print(
                "Unable to insert/update documents into database. Observed following exception:")
            print(e)


# function for retriving required data from log files
def insertOperations(files, Build, Version, col, Config_ID, Branch, OS, db):
    find_iteration = True
    first_client = True
    delete_data = True
    Run_Health = "Successful"
    for file in files:
        _, filename = os.path.split(file)
        oplist = ["Write", "Read", "GetObjTag",
                  "HeadObj", "PutObjTag", "CopyObject"]
        Objsize = 1
        obj = "NA"
        sessions = 1
        additional_operation = "Copy_op"
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
                        if opname == "Write" or opname == "Read" or opname == "CopyObject":
                            count += 1
                            throughput = float(
                                lines[count+4].split(":")[1].replace(",", ""))
                            iops = round((throughput/Objsize), 6)
                            throughput = round(throughput, 6)

                        lat = {"Max": float(lines[count-4].split(":")[1][:-2]), "Avg": float(
                            lines[count-5].split(":")[1][:-2]), "Min": float(lines[count-3].split(":")[1][:-2])}
                        ttfb = {"Max": float(lines[count+12].split(":")[1][:-2]), "Avg": float(
                            lines[count+11].split(":")[1][:-2]), "Min": float(lines[count+13].split(":")[1][:-2])}
                        data = s3bench(filename, opname, iops, throughput, lat, ttfb, obj, Build, Version, Branch, OS, nodes_num,
                                       clients_num, col, Config_ID, overwrite, sessions, Objects, pc_full, custom, additional_operation, Run_Health)

                        if find_iteration:
                            iteration_number = get_latest_iteration(
                                data.Primary_Set, db, col)
                            find_iteration = False
                            # To prevent data of one client getting overwritten/deleted while another client upload data as primary s    et matches for all client in multi-client run
                            first_client = check_first_client(
                                data.Primary_Set, db, col, iteration_number)

                        if iteration_number == 0:
                            data.insert_update(iteration_number+1)
                        elif not first_client:
                            data.insert_update(iteration_number)
                        elif overwrite == True:
                            data.Primary_Set.update(Iteration=iteration_number)
                            if delete_data:
                                db[col].delete_many(data.Primary_Set)
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


# function to return all file names with perticular extension
def getallfiles(directory, extension):
    flist = []
    for path, _, files in os.walk(directory):
        for name in files:
            if(name.lower().endswith(extension)):
                flist.append(os.path.join(path, name))
    return flist


def update_mega_chain(build, version, col):
    cursor = col.find({'Title': 'Main Chain'})
    beta_chain = cursor[0]['beta']
    release_chain = cursor[0]['release']
    if version == 'release':
        if build not in release_chain:
            print(build)
            release_chain.append(build)
            col.update_one(
                {'Title': 'Main Chain'},
                {
                    '$set': {
                        'release': release_chain,
                    }
                })
            print("...Mega entry has updated with release build ", build)
            return
    else:
        if build not in beta_chain:
            print(build)
            beta_chain.append(build)
            col.update_one(
                {'Title': 'Main Chain'},
                {
                    '$set': {
                        'beta': beta_chain,
                    }
                })
            print("...Mega entry has updated with beta build ", build)
            return
    print("...Mega entry has not updated for build ", build)


def getconfig():
    nodes_list = configs_config.get('NODES')
    clients_list = configs_config.get('CLIENTS')
    build_info = configs_config.get('BUILD_INFO')
    build_url = configs_config.get('BUILD_URL')
    build = configs_config.get('BUILD')
    version = configs_config.get('VERSION')
    branch = configs_config.get('BRANCH')
    os = configs_config.get('OS')
    execution_type = configs_config.get('EXECUTION_TYPE')
    cluster_pass = configs_config.get('CLUSTER_PASS')
    solution = configs_config.get('SOLUTION')
    end_points = configs_config.get('END_POINTS')
    system_stats = configs_config.get('SYSTEM_STATS')
    pc_full = configs_config.get('PC_FULL')
    custom = configs_config.get('CUSTOM')
    overwrite = configs_config.get('OVERWRITE')
    degraded_IO = configs_config.get('DEGRADED_IO')
    copy_object = configs_config.get('COPY_OBJECT')
    nfs_serv = configs_config.get('NFS_SERVER')
    nfs_exp = configs_config.get('NFS_EXPORT')
    nfs_mp = configs_config.get('NFS_MOUNT_POINT')
    nfs_fol = configs_config.get('NFS_FOLDER')

    nodes = []
    clients = []

    for i, _ in enumerate(nodes_list):
        nodes.append(nodes_list[i][i+1])

    for i, _ in enumerate(clients_list):
        clients.append(clients_list[i][i+1])

    dic = {
        'NODES': str(nodes),
        'CLIENTS': str(clients),
        'BUILD_INFO': build_info,
        'BUILD_URL': build_url,
        'BUILD': build,
        'VERSION': version,
        'BRANCH': branch,
        'OS': os,
        'EXECUTION_TYPE': execution_type,
        'CLUSTER_PASS': cluster_pass,
        'SOLUTION': solution,
        'END_POINTS': end_points,
        'SYSTEM_STATS': system_stats,
        'PC_FULL': pc_full,
        'CUSTOM': custom,
        'OVERWRITE': overwrite,
        'DEGRADED_IO': degraded_IO,
        'COPY_OBJECT': copy_object,
        'NFS_SERVER': nfs_serv,
        'NFS_EXPORT': nfs_exp,
        'NFS_MOUNT_POINT': nfs_mp,
        'NFS_FOLDER': nfs_fol
    }

    return (dic)


def main(argv):
    dic = argv[1]
    # getting all files with log as extension from given directory
    files = getallfiles(dic, ".log")
    db = makeconnection()  # getting instance of database

    if build_info == 'RELEASE.INFO':
        version = get_release_info('VERSION')[1:-1]
        ver_strip = re.split('-', version)
        Version = ver_strip[0]
        Build = ver_strip[1]
        Branch = 'main'
        OS = get_release_info('OS')[1:-1]

    elif build_info == 'USER_INPUT':
        Build = configs_config.get('BUILD')
        Version = configs_config.get('VERSION')
        Branch = configs_config.get('BRANCH')
        OS = configs_config.get('OS')

    dic = getconfig()
    if dic['SOLUTION'].upper() == 'LC':
        col = configs_main.get('LC')
    elif dic['SOLUTION'].upper() == 'LR':
        col = configs_main.get('LR')
    elif dic['SOLUTION'].upper() == 'LEGACY':
        col = configs_main.get(f"R{Version.split('.')[0]}")
    else:
        print("Error! Can not find suitable collection to upload data")

    Config_ID = "NA"
    result = db[col['config_collection']].find_one(
        dic)  # find entry from configurations collection
    if result:
        # foreign key : it will map entry in configurations to results entry
        Config_ID = result['_id']
    insertOperations(files, Build, Version,
                     col['db_collection'], Config_ID, Branch, OS, db)


if __name__ == "__main__":
    main(sys.argv)

#!/usr/bin/env python3
