"""
Parser script that filters unstructured data
To execute: 
Parent directory: PerfBot
Command: python ./parser.py <run run_ID> <hsbench source file path> <cosbench sourcefile path> <s3bench sourcefile path>
e.g. python df1jxl ./parser.py './Data/hsbench/hsbench.log' './Data/cosbench/s3-5050rw.csv' './Data/s3bench/s3bench_Numclients_1_NS_20_size_128Mb.log'
"""
# imports
import os
import time

from Parsers.hsbench_parser import extract_HSBench_logs, convert_HSlogs_to_JSON
from Parsers.cosbench_parser import convert_COSlogs_to_JSON
from Parsers.s3bench_parser import extract_S3Bench_logs, convert_S3logs_to_JSON
from Parsers.errors_parser import parse_errors


# variables
input_folder_path = './Input/'
parsed_data_path = './ParsedData/'
quantum = 5


def check_os_paths():
    if not os.path.exists(input_folder_path):
        os.makedirs(input_folder_path)

    if not os.path.exists(parsed_data_path):
        os.makedirs(parsed_data_path)


def run_hsbench_parser(run_ID, HS_source_file_path):
    # HS Bench parser
    HS_destination_file_path = './ParsedData/HSBench_Performance.txt'
    HS_input_file_path = './Input/hsbench.json'

    extract_HSBench_logs(HS_source_file_path, HS_destination_file_path)
    convert_HSlogs_to_JSON(run_ID, HS_destination_file_path,
                           HS_input_file_path, quantum)
    time.sleep(1)


def run_cosbench_parser(run_ID, COS_source_file_path):
    # COS Bench parser
    COS_input_file_path = './Input/cosbench.json'

    convert_COSlogs_to_JSON(run_ID, COS_source_file_path, COS_input_file_path, 64)
    time.sleep(1)


def run_s3bench_parser(run_ID, S3_source_file_path):
    # S3 Bench parser
    S3_destination_file_path = './ParsedData/S3Bench_Performance.txt'
    S3_input_file_path = './Input/s3bench.json'

    S3_objectSize = extract_S3Bench_logs(
        S3_source_file_path, S3_destination_file_path)
    convert_S3logs_to_JSON(run_ID, S3_destination_file_path,
                           S3_input_file_path, quantum, S3_objectSize)


def parse_data(run_ID, hsbench_log, cosbench_log, s3bench_log):
    check_os_paths()

    run_hsbench_parser(run_ID, hsbench_log)
    print("~ collected performance data from HSBench run directories")
    run_cosbench_parser(run_ID, cosbench_log)
    print("~ collected performance data from COSBench run directories")
    run_s3bench_parser(run_ID, s3bench_log)
    print("~ collected performance data from S3Bench run directories")
    print("~ Parsing run logs for the errors")
    parse_errors(run_ID, hsbench_log, cosbench_log, s3bench_log)
    print("~ Collected Error logs and pushed to database")
    os.removedirs(parsed_data_path)
