import datetime as dt
import json
import os

debug = False


def extract_S3Bench_logs(reference_doc, S3_destination_file_path):
    with open(S3_destination_file_path, "w") as modified:
        with open(reference_doc, "r") as reference_file:

            for line in reference_file:
                if "operation Read" in line or "operation Write" in line:
                    modified.write(line)
                elif "objectSize (MB):" in line:
                    S3_objectSize = float(line.split(' ')[-1][:-2])

    return S3_objectSize


def get_date_time_object(line):
    splits = line.split(' ')

    date_time_str = splits[1] + ' ' + splits[2][:8]
    return dt.datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S')


def convert_S3logs_to_JSON(reference_doc, S3_input_file_path, quantum, S3_objectSize):
    data = []

    with open(reference_doc, 'r') as reference_file:
        lines = reference_file.readlines()
        start_time = get_date_time_object(lines[0])
        end_time = start_time + dt.timedelta(seconds=quantum)

        if debug:
            print("-- S3bench Time-series Metrics --")
            print(
                "-- Start Time             Avg Latency (ms)     IOPS (Op/s)   Throughput(MB/s)")
        line = 0
        while line != len(lines):
            current_line_time = get_date_time_object(lines[line])
            total_latency = 0
            initial_line = line
            op = lines[line].split(' ')[8]
            if op[0] == 'R':
                operation = 'read'
            else:
                operation = 'write'

            while end_time > current_line_time and line < len(lines):
                string = lines[line].split(' ')
                total_latency = total_latency + float(string[11].split('s')[0])

                line += 1
                if line < len(lines):
                    current_line_time = get_date_time_object(lines[line])

            samples = line - initial_line
            if samples == 0:
                average_latency = -1
                RPS = -1
                MBPS = -1
            else:
                average_latency = round(total_latency/samples, 5)
                RPS = samples / quantum
                MBPS = RPS * S3_objectSize

            if debug:
                print("-- {},   {},             {},         {} --".format(end_time,
                                                                          average_latency, RPS, MBPS))
            entry = {
                "latency": average_latency,
                "iops": RPS,
                "throughput": MBPS,
                "time": str(end_time - dt.timedelta(seconds=quantum)),
                "mode": operation
            }
            data.append(entry)

            end_time = end_time + dt.timedelta(seconds=quantum)

    with open(S3_input_file_path, 'w') as jsonfile:
        json.dump(data, jsonfile, indent=4, sort_keys=True)

    os.remove(reference_doc)
