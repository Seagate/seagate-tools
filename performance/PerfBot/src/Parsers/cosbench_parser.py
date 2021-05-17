import re
import json
import datetime as dt
import time


def get_a_row(time_now, ID, latency, iops, throughput, timestamp, mode):
    entry = {
        "measurement": "perfbot",
        "time": time_now,
        "fields":
        {
            "timestamp": timestamp,
            "run_ID": ID,
            "tool": "cosbench",
            "latency": float(latency),
            "iops": float(iops),
            "throughput": float(throughput),
            "mode": mode
        }
    }
    return entry


def convert_COSlogs_to_JSON(ID, reference_doc, COS_input_file_path, objectSize):
    data = []
    filename = reference_doc.split("/")[-1]
    time_now = time.time_ns()

    with open(reference_doc, 'r') as reference_file:
        lines = reference_file.readlines()
        lines = lines[2:]

        for line in lines:
            splits = line.split(",")

            if 'rw' in filename:
                entry = get_a_row(time_now, ID, splits[5], splits[9], float(
                    splits[11])/1000000/objectSize, str(splits[0]), 'read')
                data.append(entry)

                entry = get_a_row(time_now, ID, splits[6], splits[10], float(
                    splits[12])/1000000/objectSize, str(splits[0]), 'write')
                data.append(entry)

            elif 'r' in filename:
                entry = get_a_row(time_now, ID, splits[3], splits[5], float(
                    splits[7])/1000000/objectSize, str(splits[0]), 'read')
                data.append(entry)

            elif 'w' in filename:
                entry = get_a_row(time_now, ID, splits[3], splits[5], float(
                    splits[7])/1000000/objectSize, str(splits[0]), 'write')
                data.append(entry)

            time_now = time_now + 10

    with open(COS_input_file_path, 'w') as jsonfile:
        json.dump(data, jsonfile, indent=4, sort_keys=True)
