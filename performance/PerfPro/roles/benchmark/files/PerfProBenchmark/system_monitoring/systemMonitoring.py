
#!/usr/bin/env python3
"""
Script for collecting system data
Command line arguments:   [path for main.yml]
  Ex: python3 systemMonitoring.py <Path of main.yml file> <Path of config.yml file>
Requirements:
pip3 install PyYAML==5.3.1
pip3 install pymongo==3.11.0
"""

import subprocess
import sys
from pymongo import MongoClient
import yaml
import time
import socket
import os
from datetime import datetime
import re


Main_path = sys.argv[1]
Config_path = sys.argv[2]
Object_Size = sys.argv[3]
Name = sys.argv[4]


"""
hostname = socket.gethostname()
backupfile = hostname+"_sar.json"
print(backupfile)

def write_json(data, filename=backupfile):
        with open(filename,'w') as f:
                json.dump(data, f, indent=4)

def addbackup(dataentry):
        if not os.path.exists(backupfile):
                with open(backupfile,'a') as f:
                        json.dump([],f)
        with open(backupfile) as json_file:
                data = json.load(json_file)
                data.append(dataentry)
        write_json(data)



"""

''' Function to connect with configuration file to fetch the details of the file '''
def makeconfig(name):  # function for connecting with configuration file
    with open(name) as config_file:
        configs = yaml.safe_load(config_file)
    return configs


configs_config = makeconfig(Config_path)  # getting instance  of config file

build_info = str(configs_config.get('BUILD_INFO'))
build_url = configs_config.get('BUILD_URL')
overwrite = configs_config.get('OVERWRITE')
custom = configs_config.get('CUSTOM')
solution = configs_config.get('SOLUTION')
docker_info = configs_config.get('DOCKER_INFO')

'''
Function to get the release info from the Docker image.
It returns the value for the variable which is required by the script.
'''
def get_release_info(variable):
    release_info = os.popen('docker run --rm -it ' +
                            docker_info + ' cat /opt/seagate/cortx/RELEASE.INFO')
    lines = release_info.readlines()
    for line in lines:
        if variable in line:
            strinfo = line.strip()
            strip_strinfo = re.split(': ', strinfo)
            return(strip_strinfo[1])


if build_info == 'RELEASE.INFO':
    version = get_release_info('VERSION')[1:-1]
    ver_strip = re.split('-', version)
#    Version=ver_strip[0]
    BUILD = ver_strip[1]

elif build_info == 'USER_INPUT':
    BUILD = configs_config.get('BUILD')
print(BUILD)

''' Function to connect to the Database and fetch the DB details and add data to DB throughout the script execution '''
def makeconnection(collection):  # function for making connection with database
    configs = makeconfig(Main_path)
    client = MongoClient(configs['db_url'])  # connecting with mongodb database
    db = client[configs['db_database']]  # database name=performance
    if solution.upper() == 'LC':
        col_stats = configs.get('LC')[collection]
    elif solution.upper() == 'LR':
        col_stats = configs.get('LR')[collection]
    elif solution.upper() == 'LEGACY':
        if build_info == 'RELEASE.INFO':
            version = get_release_info('VERSION')[1:-1]
            ver_strip = re.split('-', version)
            Version = ver_strip[0]

        elif build_info == 'USER_INPUT':
            Version = configs_config.get('VERSION')
        col_stats = configs.get('R'+Version[0])[collection]
    else:
        print("Error! Can not find suitable collection to upload data")
    col = db[col_stats]  # collection name = configurations
    return col

'''
Function to get all config details from config.yml file and create a collective Dictonary.
This dictonary then will be used to match with existing entries from Configuration collection
'''
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

    dic1 = {
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

    return (dic1)

''' Function to get the latest iteration value from the existing DB entries. '''
# Function to find latest iteration
def get_latest_iteration(query):
    max_iter = 0
    col = makeconnection('db_collection')
    cursor = col.find(query)
    for record in cursor:
        if max_iter < record['Iteration']:
            max_iter = record['Iteration']
    return max_iter

''' Function to add system monitoring data to the DB '''
def adddata(data, device, col):
    find_iteration = True
    delete_data = True

    dict1 = getconfig()
    conf = makeconnection('config_collection')
    Config_ID = "NA"
    result = conf.find_one(dict1)
    if result:
        # foreign key : it will map entry in configurations to systemresults entry
        Config_ID = result['_id']
    # fetching attributes from output lines and storing in a list
    attr = " ".join(data[2].decode("utf-8").split()).split(" ")
    length = len(attr)
    for d in data[3:]:
        # fetching value from output lines and storing in a list
        value = " ".join(d.decode("utf-8").split()).split(" ")
        if value[0] != "":
            if value[2] != "DEV" and value[2] != "IFACE":
                count = 2
                primary_set = {
                    "Name": Name,
                    "Build": str(BUILD),
                    "Custom": str(custom).upper()
                }
                dic = {
                    "Object_Size": Object_Size,
                    "Device": device,
                    "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Time": value[0],
                    "HOST": socket.gethostname(),
                    "Config_ID": Config_ID
                }
                while count < length:
                    # adding respective attribute and value pair in dictionary
                    dic.update({attr[count]: value[count]})
                    count += 1
                sysstats = {}
                sysstats.update(primary_set)
                sysstats.update(dic)
                try:
                    if find_iteration:
                        iteration_number = get_latest_iteration(primary_set)
                        find_iteration = False
                    if iteration_number == 0:
                        sysstats.update(Iteration=iteration_number+1)
                    elif overwrite == True:
                        primary_set.update(Iteration=iteration_number)
                        primary_set.update(Object_Size=Object_Size)
                        if delete_data and device == "CPU":
                            col.delete_many(primary_set)
                            delete_data = False
                            print(
                                "'overwrite' is True in config. Hence, old DB entry deleted")
                        sysstats.update(Iteration=iteration_number)
                    else:
                        sysstats.update(Iteration=iteration_number+1)
                    print(sysstats)
                    # inserting dictionary values in mongodb
                    col.insert_one(sysstats)
                except Exception as e:
                    print(
                        "Unable to insert/update documents into database. Observed following exception:")
                    print(e)
                # else:
                #    print(dic)

''' Function to record system monitoring stats. '''
def addReport():  # function for getting system report accoordiing to 'cmd' argument
    col = makeconnection('sysstat_collection')
    cmd = [[['sar', '5'], 'p1', "CPU"], [['sar', '-r', '5'], 'p2', "MEMORY"], [['sar', '-d', '5'],
                                                                               'p3', "DISK"], [['sar', '-b', '5'], 'p4', "I/O"], [['sar', '-n', 'DEV', '5'], 'p5', "NETWORK"]]
    count = 0
    f = open("pidfile", "w+")
    f.close()
    for c in cmd:
        c[1] = subprocess.Popen(c[0], stdout=subprocess.PIPE)
        count += 1

        # time.sleep(3)
    while os.path.isfile("pidfile"):
        time.sleep(1)

    for c in cmd:
        c[1].kill()
        out, _ = c[1].communicate()
        outs = out.splitlines()
        print("\n"+c[2]+"\n")
        adddata(outs, c[2], col)

''' Function to retive all system stats from database'''
def retriveAll():  # function for retriving all the data from database
    col = makeconnection('systemresults')
    data = col.find()
    for d in data:
        print(d)

''' System monitoring main function. '''
def main():
    if os.path.isfile("pidfile"):
        print("systemstats are already running! Nothing to start. Exiting")
        return
    addReport()


if __name__ == "__main__":
    main()
