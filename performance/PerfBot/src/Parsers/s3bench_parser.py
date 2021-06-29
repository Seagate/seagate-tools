import datetime as dt
import json
import os
import time

from schemas import get_performance_schema
debug = False


def extract_S3Bench_logs(reference_doc, S3_destination_file_path):
    """
    A function to structurize data from raw data files
    arguments: log file path (str), intermediate path to store structured data (str)
    returns: object size of that file (float)
    """
    with open(S3_destination_file_path, "w") as modified:
        with open(reference_doc, "r") as reference_file:

            for line in reference_file:
                if "operation Read" in line or "operation Write" in line:
                    modified.write(line)
                elif "objectSize (MB):" in line:
                    S3_objectSize = float(line.split(' ')[-1][:-2])

    return S3_objectSize


def get_date_time_object(line):
    """
    A function to get date time object from a line
    arguments: line to extract date time from (str)
    returns: date time from the line (datetime object)
    """
    splits = line.split(' ')

    date_time_str = splits[1] + ' ' + splits[2][:8]
    return dt.datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S')


def convert_S3logs_to_JSON(run_ID, reference_doc, S3_input_file_path, quantum, S3_objectSize, S3_source_file_path):
    """
    a function to convert raw s3bench run results into a json format
    arguments: run ID (int), data file path (str), path to store json files (str), interval size (int), object size (float), path of raw data file (str)
    """
    data = []
    time_now = time.time_ns()

    with open(reference_doc, 'r') as reference_file:
        lines = reference_file.readlines()
        num_of_lines = len(lines)

        start_time = get_date_time_object(lines[0])
        end_time = start_time + dt.timedelta(seconds=quantum)

        if debug:
            print("-- S3bench Time-series Metrics --")
            print(
                "-- Start Time             Avg Latency (ms)     IOPS (Op/s)   Throughput(MB/s)")
        line = 0
        while line != num_of_lines:
            current_line_time = get_date_time_object(lines[line])
            total_latency = 0
            initial_line = line
            op = lines[line].split(' ')[8]
            if op[0] == 'R':
                operation = 'read'
            else:
                operation = 'write'

            while end_time > current_line_time and line < num_of_lines:
                string = lines[line].split(' ')
                total_latency = total_latency + float(string[11].split('s')[0])

                line += 1
                if line < num_of_lines:
                    current_line_time = get_date_time_object(lines[line])

            samples = line - initial_line
            if samples == 0:
                average_latency = 0
                RPS = 0
                MBPS = 0
            else:
                average_latency = round(total_latency/samples, 5)*1000
                RPS = samples / quantum
                MBPS = RPS * S3_objectSize

            if debug:
                print("-- {},   {},             {},         {} --".format(end_time,
                                                                          average_latency, RPS, MBPS))

            entry = get_performance_schema(time_now, run_ID, average_latency, RPS, MBPS, str(
                end_time - dt.timedelta(seconds=quantum)), operation, 's3bench', S3_source_file_path)
            data.append(entry)
            time_now = time_now + 10

            end_time = end_time + dt.timedelta(seconds=quantum)

    with open(S3_input_file_path, 'w') as jsonfile:
        json.dump(data, jsonfile, indent=4, sort_keys=True)

    os.remove(reference_doc)
