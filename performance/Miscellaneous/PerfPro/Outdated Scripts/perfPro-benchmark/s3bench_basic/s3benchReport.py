import os
import pandas as pd
import sys

def extractFile(filepath):
    files=[]
    for r, d, f in os.walk(filepath):
        for file in f:
            if '.log' in file:
                files.append(os.path.join(r, file))
    return files

def extractData(filename):
     allData={}
     readData={}
     writeData={}
     with open(filename, 'r') as f:
        read_read = False
        read_write = False
        for _ in f:
            if _.startswith('objectSize'):
               data = [_.strip() for _ in _.split(":") if _]
               allData[data[0]]=data[1]
            if _.startswith('numSamples'):
               data = [_.strip() for _ in _.split(":") if _]
               allData[data[0]]=data[1]
            if _.startswith('numClients'):
               data = [_.strip() for _ in _.split(":") if _]
               allData[data[0]]=data[1]

            if read_read:
               data = [_.strip() for _ in _.split(":") if _]
               readData[data[0]]=data[1]
               allData['Read Ops']=readData
            if read_write:
               data = [_.strip() for _ in _.split(":") if _]
               writeData[data[0]]=data[1]
               allData['Write Ops']=writeData
            if "Results Summary for Read Operation(s)" in _:
               read_read = True
            if "Results Summary for Write Operation(s)" in _:
               read_write = True
            if _.startswith("Number of Errors:"):
               read_read = False
               read_write = False
     return allData

def collectData(allData):
    allvalues=[]
    data=[]
    for key, value in allData.items():
        if key == 'objectSize':
           data.append(value)
        if key == 'numSamples':
           data.append(value)
        if key == 'numClients':
           data.append(value)
        if key == 'Read Ops':
           data.insert(3, value['Total Transferred'])
        if key == 'Write Ops':
           data.insert(4, value['Total Transferred'])
        if key == 'Read Ops':
           data.insert(5, value['Total Duration'])
        if key == 'Write Ops':
           data.insert(6, value['Total Duration'])
        if key == 'Read Ops':
           data.insert(7, value['Total Throughput'])
        if key == 'Write Ops':
           data.insert(8, value['Total Throughput'])
        if key == 'Read Ops':
           try:
               rd_iops=float(value['Total Throughput'].split(' ')[0])/float(data[0].split(' ')[0])
               data.insert(9, str(round(rd_iops,3)))
               data.insert(11, str(round((1000/rd_iops), 3)))
               data.insert(13, value['Number of Errors'])
           except ZeroDivisionError as error:
               print("division by zero: exception handled")

        if key == 'Write Ops':
           try:
               wrt_iops=float(value['Total Throughput'].split(' ')[0])/float(data[0].split(' ')[0])
               data.insert(10, str(round(wrt_iops,3)))
               data.insert(12, str(round((1000/wrt_iops), 3)))
               data.insert(13, value['Number of Errors'])
           except ZeroDivisionError as error:
               print("division by zero: exception handled")

    return data
   

if __name__ == "__main__":
    files=extractFile(sys.argv[1])
    count=0
    out_header=['obj_size','Ops','users','rd_Data(MB)','wrt_Data(MB)','rd_runtime','wrt_runtime','rd_th','wrt_th','rd_IOPS','wrt_IOPS','rd_lat','wrt_lat','rd_Err','wrt_Err']
    allData=[]
    data=[]
    for filename in files:
        print(filename)
        data=collectData(extractData(filename))
        allData.append(data)
    table_op = pd.DataFrame(allData, columns=out_header)
    print(table_op)
