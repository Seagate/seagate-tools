"""
Main file for PerfBot
"""
import os
import string
import random
import influxdb
from store_data import connect_database

cwd = os.getcwd()
hsbench_log = cwd + '/src/Data/hsbench/hsbench.log'
cosbench_log = cwd + '/src/Data/cosbench/s3-5050rw.csv'
s3bench_log = cwd + '/src/Data/s3bench/s3bench_Numclients_1_NS_20_size_128Mb.log'


def get_random_string(length):
    letters = string.ascii_letters + string.digits
    result_str = ''.join(random.choice(letters) for i in range(length))

    return result_str
print("~ Executing PerfBot...")

def generate_runID():
    client = connect_database()
    result = client.query(" select distinct run_ID from perfbot;")
    dist_IDs = list(result)[0]

    while True:
        ID = get_random_string(8)
        found_ids = list(
            filter(lambda tempID: tempID['distinct'] == ID, dist_IDs))
        if not found_ids:
            break

    print("~ Unique ID for run is: " + ID)
    return ID


def execute_parsers(ID):
    # execute parsers
    print("~ Parsing data files...")
    try:
        os.system("python {}/src/parser.py {} {} {} {}".format(cwd,
                                                               ID, hsbench_log, cosbench_log, s3bench_log))
        print("~ Done!")

    except Exception as e:
        print("Observed exception: ", e)


def update_database():
    # push data to database
    print("~ Pushing data to database...")
    try:
        os.system("python {}/src/store_data.py".format(cwd))
        print("~ Done!")

    except Exception as e:
        print("Observed exception: ", e)


if __name__ == '__main__':
    print("~ Executing PerfBot...")

    ID = generate_runID()
    execute_parsers(ID)
    update_database()

    print("~ Thanks for using PerfBot!")
