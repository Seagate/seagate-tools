"""
Parser script that filters unstructured data
To execute: 
Parent directory: PerfBot
Command: python ./src/parser.py <hsbench source file path> <cosbench sourcefile path> <s3bench sourcefile path>
e.g. python ./src/parser.py './src/Data/hsbench/hsbench.log' './src/Data/cosbench/s3-5050rw.csv' './src/Data/s3bench/s3bench_Numclients_1_NS_20_size_128Mb.log'
"""
# imports
import os
import sys

from Parsers.hsbench_parser import extract_HSBench_logs, convert_HSlogs_to_JSON
from Parsers.cosbench_parser import convert_COSlogs_to_JSON
from Parsers.s3bench_parser import extract_S3Bench_logs, convert_S3logs_to_JSON


# variables
ID = sys.argv[1]
cwd = os.getcwd()
input_folder_path = cwd + '/src/Input/'
parsed_data_path = cwd + '/src/ParsedData/'
quantum = 5

if not os.path.exists(input_folder_path):
    os.makedirs(input_folder_path)

if not os.path.exists(parsed_data_path):
    os.makedirs(parsed_data_path)

# HS Bench parser
HS_source_file_path = sys.argv[2]
HS_destination_file_path = cwd + '/src/ParsedData/HSBench_Performance.txt'
HS_input_file_path = cwd + '/src/Input/hsbench.json'

extract_HSBench_logs(HS_source_file_path, HS_destination_file_path)
convert_HSlogs_to_JSON(ID, HS_destination_file_path, HS_input_file_path)


# COS Bench parser
COS_source_file_path = sys.argv[3]
COS_input_file_path = cwd + '/src/Input/cosbench.json'

convert_COSlogs_to_JSON(ID, COS_source_file_path, COS_input_file_path, 64)


# S3 Bench parser
S3_source_file_path = sys.argv[4]
S3_destination_file_path = cwd + '/src/ParsedData/S3Bench_Performance.txt'
S3_input_file_path = cwd + '/src/Input/s3bench.json'

S3_objectSize = extract_S3Bench_logs(
    S3_source_file_path, S3_destination_file_path)
convert_S3logs_to_JSON(ID, S3_destination_file_path,
                       S3_input_file_path, quantum, S3_objectSize)

os.removedirs(parsed_data_path)
