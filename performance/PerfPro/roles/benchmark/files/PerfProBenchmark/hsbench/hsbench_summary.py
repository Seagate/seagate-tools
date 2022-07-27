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

import os
import sys
import json
import re
import pandas as pd
from tabulate import tabulate

hsbench_results=sys.argv[1]

headers=['Obj_size','Buckets','Objects','Sessions','Write Tput(MB/s)','Read Tput(MB/s)','Write IOPS','Read IOPS','Write Latency(ms)','Read Latency(ms)']

Data=[]


def get_files(filepath):
    """Function to get the files from specified directory

    Parameters : input(String) - path of the directory
                 returns(list) - list of filtered files in specified directory
    """

    files = []
    for r, _, f in os.walk(filepath):
        for doc in f:
            if '.json' in doc:
                files.append(os.path.join(r, doc))
    return files


def extract_json(file):
    """
    Function to extract json files

    Parameters : input(str) - file name to fetch data from
                 returns(dataFrame) - pandas dataframe containing performance parameters
    """

    json_data = []
    keys = ['Mode', 'Seconds', 'Ops', 'Mbps', 'Iops', 'MinLat', 'AvgLat', 'MaxLat']
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

def summary_table(files):
    """
    Function to extract required statistics from specified log files

    Parameters : input(str) - list of files get fetch data from
                 returns(dataFrame) - list of performance parameters and their respective values
    """
    global Data

    for doc in files:
        filename = doc
        doc = filename.strip(".json")
        attr = re.split("_", doc)
        obj_size = attr[-7]
        buckets = int(attr[-3])
        objects = int(attr[-5])
        sessions = int(attr[-1])
        try:
            with open(filename) as json_file:
                data = json.load(json_file)
                for entry in data:
                    if(entry['Mode'] == 'PUT') and (entry['IntervalName'] == 'TOTAL'):
                        Write_IOPS=round(entry['Iops'],2)
                        Write_Throughput=round(entry['Mbps'],2)
                        Write_Latency=round(entry['AvgLat'],2)
                    elif(entry['Mode'] == 'GET') and (entry['IntervalName'] == 'TOTAL'):
                        Read_IOPS=round(entry['Iops'],2)
                        Read_Throughput=round(entry['Mbps'],2)
                        Read_Latency=round(entry['AvgLat'],2)
                        result=[obj_size,buckets,objects,sessions,Write_Throughput,Read_Throughput,Write_IOPS,Read_IOPS,Write_Latency,Read_Latency]
                        Data.append(result)
        except Exception as exc:
            print(f"Encountered error in file: {filename} , and Exeption is", exc)
    return Data


files = get_files(hsbench_results)
Data = summary_table(files)
print(tabulate(Data,headers=headers,tablefmt='psql'))

