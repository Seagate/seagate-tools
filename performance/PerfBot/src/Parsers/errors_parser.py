import re
import os
import time

from influxdb import client

from store_data import connect_database
from Parsers.schemas import get_error_schema

cwd = os.getcwd()
keywords = ('error', 'stderr', 'fail', 'unsuccessful')


def get_parsed_errors_from_file(run_ID, file, tool):
    time_now = time.time_ns()
    data = []

    with open(file, 'r') as bench_file:
        lines = bench_file.readlines()
        line = 0
        while line < len(lines):
            for pattern in keywords:
                if re.search(pattern, lines[line]):
                    error_details = lines[line] + lines[line + 1]
                    data.append(get_error_schema(time_now, run_ID, tool, line, pattern, file, error_details))
                    time_now = time_now + 10

            line +=1
    
    return data

def push_data_To_database(data):
    client = connect_database()
    client.write_points(data)


def parse_errors(run_ID, hsbench_log, cosbench_log, s3bench_log):
    files = [hsbench_log, cosbench_log, s3bench_log]

    for file_name in files:
        if 's3bench' in file_name:
            tool = 's3bench'
        elif 'hsbench' in file_name:
            tool = 'hsbench'
        else:
            tool = 'cosbench'

        data = get_parsed_errors_from_file(run_ID, file_name, tool)
        push_data_To_database(data)
        print("~ Done for {}".format(tool))
