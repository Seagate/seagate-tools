import re
import json
import datetime as dt
import time

from Parsers.schemas import get_performance_schema


def convert_COSlogs_to_JSON(run_ID, reference_doc, COS_input_file_path, objectSize):
    data = []
    filename = reference_doc.split("/")[-1]
    time_now = time.time_ns()

    with open(reference_doc, 'r') as reference_file:
        lines = reference_file.readlines()
        lines = lines[2:]

        for line in lines:
            splits = line.split(",")

            if 'rw' in filename:
                entry = get_performance_schema(time_now, run_ID, splits[5], splits[9], float(
                    splits[11])/1000000/objectSize, str(splits[0]), 'read', 'cosbench', filename)
                data.append(entry)

                entry = get_performance_schema(time_now, run_ID, splits[6], splits[10], float(
                    splits[12])/1000000/objectSize, str(splits[0]), 'write', 'cosbench', filename)
                data.append(entry)

            elif 'r' in filename:
                entry = get_performance_schema(time_now, run_ID, splits[3], splits[5], float(
                    splits[7])/1000000/objectSize, str(splits[0]), 'read', 'cosbench', filename)
                data.append(entry)

            elif 'w' in filename:
                entry = get_performance_schema(time_now, run_ID, splits[3], splits[5], float(
                    splits[7])/1000000/objectSize, str(splits[0]), 'write', 'cosbench',filename)
                data.append(entry)

            time_now = time_now + 10

    with open(COS_input_file_path, 'w') as jsonfile:
        json.dump(data, jsonfile, indent=4, sort_keys=True)
