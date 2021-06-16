import json
import time
import csv

from schemas import get_performance_schema


def convert_COSlogs_to_JSON(run_ID, reference_doc, COS_input_file_path, objectSize):
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
                    entry = get_performance_schema(time_now, run_ID, line[5], line[9], float(
                        line[11])/1000000/objectSize, str(line[0]), 'read', 'cosbench', reference_doc)
                    data.append(entry)

                    entry = get_performance_schema(time_now, run_ID, line[6], line[10], float(
                        line[12])/1000000/objectSize, str(line[0]), 'write', 'cosbench', reference_doc)
                    data.append(entry)

                elif 'r' in filename:
                    entry = get_performance_schema(time_now, run_ID, line[3], line[5], float(
                        line[7])/1000000/objectSize, str(line[0]), 'read', 'cosbench', reference_doc)
                    data.append(entry)

                elif 'w' in filename:
                    entry = get_performance_schema(time_now, run_ID, line[3], line[5], float(
                        line[7])/1000000/objectSize, str(line[0]), 'write', 'cosbench',reference_doc)
                    data.append(entry)

                time_now = time_now + 10

            except IndexError:
                next(lines)

    with open(COS_input_file_path, 'w') as jsonfile:
        json.dump(data, jsonfile, indent=4, sort_keys=True)
