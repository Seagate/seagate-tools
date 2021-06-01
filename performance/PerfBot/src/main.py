"""
Main file for PerfBot
"""
import string
import random
import yaml

from store_data import connect_database, update_parsed_data
from data_parser import parse_data
from Analyzer.rule_handler import rule_handler


def get_random_string(length):
    alphanumeric_set = string.ascii_letters + string.digits
    result_str = ''.join(random.choice(alphanumeric_set) for i in range(length))

    return result_str


def generate_alphanumeric_runID():
    client = connect_database()
    dist_IDs = list(client.query("select distinct run_ID from perfbot;"))[0]

    while True:
        gen_run_ID = get_random_string(8)
        found_ids = list(
            filter(lambda tempID: tempID['distinct'] == gen_run_ID, dist_IDs))
        if not found_ids:
            break

    print("~ Unique ID for run is: " + gen_run_ID)
    return gen_run_ID

def generate_runID():
    client = connect_database()
    latest_run_ID = client.query("select last(run_ID) from data;")
    try:
        gen_run_ID = int(list(latest_run_ID)[0][0]['last']) + 1
    except IndexError:
        gen_run_ID = 1

    print("~ Unique ID for run is: ", gen_run_ID)
    return gen_run_ID


def execute_parsers(run_ID):
    # execute parsers
    with open("./config.yml", 'r') as config_file:
        configs = yaml.safe_load(config_file)

    hsbench_log = configs['logfiles']['hs']
    cosbench_log = configs['logfiles']['cos']
    s3bench_log = configs['logfiles']['s3']
    
    print("~ Parsing data files...")
    try:
        parse_data(run_ID, hsbench_log, cosbench_log, s3bench_log)
        print("~ Done!")

    except Exception as e:
        print("Observed exception: ", e)


def update_database():
    # push data to database
    print("~ Pushing performance data to database...")
    try:
        update_parsed_data()
        print("~ Done!")

    except Exception as e:
        print("Observed exception: ", e)


def analyzer(run_ID):
    print("~ Analyzing data...")
    print("~ PHASE 1: Reading rules...")
    try:
        rules = rule_handler(run_ID)
        print(f"Current rules are: {rules}")
        print("~ Done!")

    except Exception as e:
        print("Observed exception: ", e)



if __name__ == '__main__':
    print("~ Executing PerfBot...")

    run_ID = generate_runID()
    execute_parsers(run_ID)
    update_database()
    analyzer(run_ID)

    print("~ Thanks for using PerfBot!")
