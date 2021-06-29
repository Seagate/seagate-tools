import json
import time
import csv

from schemas import get_performance_schema


def get_metrics(iops, latency, throughput, objectSize):
    if float(iops) == 0.0:
        return 0, 0, 0
    else:
        return iops, latency, float(throughput)/1000000/objectSize


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
                    iops, latency, throughput = get_metrics(
                        line[9], line[5], line[11], objectSize)
                    entry = get_performance_schema(time_now, run_ID, latency, iops, throughput, str(
                        line[0]), 'read', 'cosbench', reference_doc)
                    data.append(entry)

                    iops, latency, throughput = get_metrics(
                        line[10], line[6], line[12], objectSize)
                    entry = get_performance_schema(
                        time_now+1, run_ID, latency, iops, throughput, str(line[0]), 'write', 'cosbench', reference_doc)
                    data.append(entry)

                elif 'r' in filename:
                    iops, latency, throughput = get_metrics(
                        line[5], line[3], line[7], objectSize)
                    entry = get_performance_schema(time_now, run_ID, latency, iops, throughput, str(
                        line[0]), 'read', 'cosbench', reference_doc)
                    data.append(entry)

                elif 'w' in filename:
                    iops, latency, throughput = get_metrics(
                        line[5], line[3], line[7], objectSize)
                    entry = get_performance_schema(time_now, run_ID, latency, iops, throughput, str(
                        line[0]), 'write', 'cosbench', reference_doc)
                    data.append(entry)

                time_now = time_now + 10

            except IndexError:
                next(lines)

    with open(COS_input_file_path, 'w') as jsonfile:
        json.dump(data, jsonfile, indent=4, sort_keys=True)
