"""
Parser script that filters unstructured data
"""
# imports
import os
from Parsers.hsbench_parser import extract_HSBench_logs, convert_HSlogs_to_JSON
from Parsers.cosbench_parser import convert_COSlogs_to_JSON
from Parsers.s3bench_parser import extract_S3Bench_logs, convert_S3logs_to_JSON


# variables
cwd = os.getcwd()

# HS Bench
HS_source_file_path = cwd + '/src/Data/hsbench/hsbench.log'
HS_destination_file_path = cwd + '/src/ParsedData/HSBench_Performance.txt'
HS_input_file_path = cwd + '/src/Input/hsbench.json'

extract_HSBench_logs(HS_source_file_path, HS_destination_file_path)
convert_HSlogs_to_JSON(HS_destination_file_path, HS_input_file_path)


# COS Bench
COS_source_file_path = cwd + '/src/Data/cosbench/s3-5050rw.csv'
COS_input_file_path = cwd + '/src/Input/cosench.json'
convert_COSlogs_to_JSON(COS_source_file_path, COS_input_file_path, 64)


# S3 Bench
S3_source_file_path = cwd + '/src/Data/s3bench/s3bench_Numclients_1_NS_20_size_128Mb.log'
S3_destination_file_path = cwd + '/src/ParsedData/S3Bench_Performance.txt'
S3_input_file_path = cwd + '/src/Input/s3bench.json'
quantum = 1

S3_objectSize = extract_S3Bench_logs(S3_source_file_path, S3_destination_file_path)
convert_S3logs_to_JSON(S3_destination_file_path, S3_input_file_path, quantum, S3_objectSize)