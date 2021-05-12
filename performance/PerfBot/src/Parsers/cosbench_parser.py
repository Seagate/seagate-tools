import re
import json

def convert_COSlogs_to_JSON(reference_doc, COS_input_file_path, objectSize):
    data = []
    filename = reference_doc.split("/")[-1]

    with open(reference_doc, 'r') as reference_file:
        lines = reference_file.readlines()
        lines = lines[2:]

        for line in lines:
            splits = line.split(",")

            if 'rw' in filename:
                entry = {
                "latency" : splits[5],
                "iops" : float(splits[9]),
                "throughput" : float(float(splits[11])/1000000/objectSize),
                "time" : str(splits[0]), 
                "mode" : 'read'
                }
                data.append(entry)
                
                entry = {
                "latency" : splits[6],
                "iops" : float(splits[10]),
                "throughput" : float(float(splits[12])/1000000/objectSize),
                "time" : str(splits[0]), 
                "mode" : 'write'
                }
                data.append(entry)

            elif 'r' in filename:
                entry = {
                "latency" : splits[3],
                "iops" : float(splits[5]),
                "throughput" : float(float(splits[7])/1000000/objectSize),
                "time" : str(splits[0]), 
                "mode" : 'read'
                }
                data.append(entry)

            elif 'w' in filename:
                entry = {
                "latency" : splits[3],
                "iops" : float(splits[5]),
                "throughput" : float(float(splits[7])/1000000/objectSize),
                "time" : str(splits[0]), 
                "mode" : 'write'
                }
                data.append(entry)

    with open(COS_input_file_path, 'w') as jsonfile:
        json.dump(data, jsonfile, indent=4, sort_keys=True)