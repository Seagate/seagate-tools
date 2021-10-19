#!/usr/bin/env python3
import json
import pandas as pd
import glob
import os
import sys
from datetime import datetime

def extractFile(filepath):
    files=[]
    for r, d, f in os.walk(filepath):
        for file in f:
            if '.json' in file:
                files.append(os.path.join(r, file))
    return files

def extract_json(file):
    json_data = []
    keys=['Mode','Seconds','Ops','Mbps','Iops','MinLat','AvgLat','MaxLat']
    values=[]
    with open(file, 'r') as list_ops:
            json_data=json.load(list_ops)
    for data in json_data:
        value=[]
        if(data['IntervalName']=='TOTAL'):
            for key in keys:
                value.append(data[key])
            values.append(value)
    table_op = pd.DataFrame(values,columns=keys)
    return table_op

if __name__=='__main__':
    files = extractFile(sys.argv[1])
    for IO_SIZE in files:
        print('=============IO_SIZE: {}============='.format(IO_SIZE))
        print(extract_json(IO_SIZE))
