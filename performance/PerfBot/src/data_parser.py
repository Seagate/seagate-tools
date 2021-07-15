"""
Parser script that filters unstructured data
To execute: 
Parent directory: PerfBot
Command: python ./parser.py <run_ID> <hsbench source file path> <cosbench sourcefile path> <s3bench sourcefile path>
e.g. python 3 ./parser.py './Data/hsbench/hsbench.log' './Data/cosbench/s3-5050rw.csv' './Data/s3bench/s3bench_Numclients_1_NS_20_size_128Mb.log'
"""
# imports
import os
import time
import yaml

from Parsers.hsbench_parser import extract_HSBench_logs, convert_HSlogs_to_JSON
from Parsers.cosbench_parser import convert_COSlogs_to_JSON
from Parsers.s3bench_parser import extract_S3Bench_logs, convert_S3logs_to_JSON
from Parsers.logs_parser import parse_errors


# variables
input_folder_path = './Input/'
parsed_data_path = './ParsedData/'

with open("perfbot_config.yml", "r") as perfbot_config:
    configs = yaml.safe_load(perfbot_config)
    quantum = configs['quantum']


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
                           HS_input_file_path, quantum, HS_source_file_path)
    time.sleep(1)


def run_cosbench_parser(run_ID, COS_source_file_path, cos_obj_size):
    # COS Bench parser
    COS_input_file_path = './Input/cosbench.json'

    convert_COSlogs_to_JSON(run_ID, COS_source_file_path,
                            COS_input_file_path, cos_obj_size)
    time.sleep(1)


def run_s3bench_parser(run_ID, S3_source_file_path):
    # S3 Bench parser
    S3_destination_file_path = './ParsedData/S3Bench_Performance.txt'
    S3_input_file_path = './Input/s3bench.json'

    S3_objectSize = extract_S3Bench_logs(
        S3_source_file_path, S3_destination_file_path)
    convert_S3logs_to_JSON(run_ID, S3_destination_file_path,
                           S3_input_file_path, quantum, S3_objectSize, S3_source_file_path)


def parse_data(run_ID, run_dirs, log_files, cos_obj_size):
    check_os_paths()

    print("~ Parsing performance data...")
    if run_dirs[0] is not None:
        run_hsbench_parser(run_ID, run_dirs[0])
        print("~     hsbench completed")
    else:
        print("~ HSbench run data file is not given, skipping...")

    if run_dirs[1] is not None:
        if cos_obj_size is None:
            print("~ object size is not provided for COSbench, skipping...")
        else:
            run_cosbench_parser(run_ID, run_dirs[1], cos_obj_size)
            print("~     cosbench completed")
    else:
        print("~ COSbench run data file is not given, skipping...")

    if run_dirs[2] is not None:
        run_s3bench_parser(run_ID, run_dirs[2])
        print("~     s3bench completed")
    else:
        print("~ S3bench run data file is not given, skipping...")

    if log_files[0] is not None and log_files[1] is not None and log_files[2] is not None:
        print("~ Parsing run logs...")
        parse_errors(run_ID, log_files[0], log_files[1], log_files[2])

        os.removedirs(parsed_data_path)
    else:
        print("~ Run log files are not provided for at least 1 tool, skipping...")
