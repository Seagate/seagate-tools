import re
import os
import time

from store_data import connect_database
from schemas import get_error_schema

cwd = os.getcwd()
keywords = ('error', 'stderr', 'fail', 'unsuccessful', 'err')
false_patterns = ('errors:', 'errors count:', 'transferred', 'errors count')


def get_parsed_errors_from_file(run_ID, file, tool):
    time_now = time.time_ns()
    data = []

    with open(file, 'r') as bench_file:
        lines = bench_file.readlines()
        line = 0
        while line < len(lines):
            false_pattern_not_observed = True

            for pattern in false_patterns:
                if re.search(pattern, lines[line].lower()):
                    false_pattern_not_observed = False
                    break

            if false_pattern_not_observed:
                for pattern in keywords:
                    if re.search(pattern, lines[line].lower()):
                        error_details = lines[line] + lines[line + 1]
                        data.append(get_error_schema(
                            time_now, run_ID, tool, line, pattern, file, error_details))
                        time_now = time_now + 10

            line += 1

    return data


def push_data_To_database(data):
    client = connect_database()
    client.write_points(data)


def parse_errors(run_ID, hsbench_log, cosbench_log, s3bench_log):
    files = []
    if hsbench_log is not None:
        files.append(hsbench_log)
    else:
        print("~ HSbench run log file is not given, skipping...")

    if cosbench_log is not None:
        files.append(cosbench_log)
    else:
        print("~ COSbench run log file is not given, skipping...")

    if s3bench_log is not None:
        files.append(s3bench_log)
    else:
        print("~ S3bench run log file is not given, skipping...")

    for file_name in files:
        if 's3bench' in file_name:
            tool = 's3bench'
        elif 'hsbench' in file_name:
            tool = 'hsbench'
        else:
            tool = 'cosbench'

        data = get_parsed_errors_from_file(run_ID, file_name, tool)
        push_data_To_database(data)
        print("~     {} tool completed".format(tool))
