"""
Main file for PerfBot
"""
import os
import string
import random

cwd = os.getcwd()
hsbench_log = cwd + '/src/Data/hsbench/hsbench.log'
cosbench_log = cwd + '/src/Data/cosbench/s3-5050rw.csv'
s3bench_log = cwd + '/src/Data/s3bench/s3bench_Numclients_1_NS_20_size_128Mb.log'

print("~ Executing PerfBot...")


def get_random_string(length):
    letters = string.ascii_letters + string.digits
    result_str = ''.join(random.choice(letters) for i in range(length))

    return result_str


ID = get_random_string(6)
print("~ Unique ID for run is: " + ID)

# execute parsers
print("~ Parsing data files...")
os.system("python {}/src/parser.py {} {} {} {}".format(cwd,
                                                       ID, hsbench_log, cosbench_log, s3bench_log))

print("~ Done!")

# push data to database
print("~ Pushing data to database...")
os.system("python {}/src/store_data.py".format(cwd))
print("~ Done!")

print("~ Thanks for using PerfBot!")
