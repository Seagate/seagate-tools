import re
import json


def get_a_row(ID, latency, iops, throughput, time, mode):
    entry = {
        "measurement": ID + "_cosbench",
        "time": time,
        "fields":
        {
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

    with open(reference_doc, 'r') as reference_file:
        lines = reference_file.readlines()
        lines = lines[2:]

        for line in lines:
            splits = line.split(",")

            if 'rw' in filename:
                entry = get_a_row(ID, splits[5], splits[9], float(
                    splits[11])/1000000/objectSize, str(splits[0]), 'read')
                data.append(entry)

                entry = get_a_row(ID, splits[6], splits[10], float(
                    splits[12])/1000000/objectSize, str(splits[0]), 'write')
                data.append(entry)

            elif 'r' in filename:
                entry = get_a_row(ID, splits[3], splits[5], float(
                    splits[7])/1000000/objectSize, str(splits[0]), 'read')
                data.append(entry)

            elif 'w' in filename:
                entry = get_a_row(ID, splits[3], splits[5], float(
                    splits[7])/1000000/objectSize, str(splits[0]), 'write')
                data.append(entry)

    with open(COS_input_file_path, 'w') as jsonfile:
        json.dump(data, jsonfile, indent=4, sort_keys=True)
