"""
A Cosbench parser module

Depends on: 
1. run results of performance
2. run log of the tool run
3. Object size associated in the run
4. rw / r / w in the run dir file name to identify the workload type
"""
import json
import time
import csv

from schemas import get_performance_schema


def get_throughput(bandwidth, objectSize):
    """
    Function to return throughput from bandwidth
    arguments: bandwidth (float), objectsize (int)
    return: throughput (float)
    """
    return float(bandwidth)/1000000/objectSize


def convert_COSlogs_to_JSON(run_ID, reference_doc, COS_input_file_path, objectSize):
    """
    a function to convert raw cosbench run results into a json format
    arguments: run ID (int), data file path (str), path to store json files (str), object size (int)
    """
    data = []
    filename = reference_doc.split("/")[-1]
    time_now = time.time_ns()

    with open(reference_doc, 'r') as reference_file:
        lines = csv.reader(reference_file, delimiter=',')
        next(lines)
        next(lines)

        for line in lines:
            try:
                if 'rw' in filename:
                    entry = get_performance_schema(time_now, run_ID, line[5], line[9], get_throughput(line[11], objectSize), str(
                        line[0]), 'read', 'cosbench', reference_doc)
                    data.append(entry)

                    entry = get_performance_schema(
                        time_now+1, run_ID, line[6], line[10], get_throughput(line[12], objectSize), str(line[0]), 'write', 'cosbench', reference_doc)
                    data.append(entry)

                elif 'r' in filename:
                    entry = get_performance_schema(time_now, run_ID, line[3], line[5], get_throughput(line[7], objectSize), str(
                        line[0]), 'read', 'cosbench', reference_doc)
                    data.append(entry)

                elif 'w' in filename:
                    entry = get_performance_schema(time_now, run_ID, line[3], line[5], get_throughput(line[7], objectSize), str(
                        line[0]), 'write', 'cosbench', reference_doc)
                    data.append(entry)

                time_now = time_now + 10

            except IndexError:
                next(lines)

    with open(COS_input_file_path, 'w') as jsonfile:
        json.dump(data, jsonfile, indent=4, sort_keys=True)
