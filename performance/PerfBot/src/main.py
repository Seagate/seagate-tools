"""
Main file for PerfBot
"""
import string
import random
import yaml
import sys

from store_data import connect_database, update_parsed_data
from data_parser import parse_data
from Analyzer.rule_handler import rule_handler
from Analyzer.query_handler import query_handler
from Analyzer.predictor import predictor


def get_random_string(length):
    alphanumeric_set = string.ascii_letters + string.digits
    result_str = ''.join(random.choice(alphanumeric_set)
                         for i in range(length))

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


def execute_parsers(run_ID, config_file_path):
    # execute parsers
    with open(config_file_path, 'r') as config_file:
        configs = yaml.safe_load(config_file)

    print("\n~ PHASE 1: Parsing data files...")
    # try:
    run_directories = [configs['runfiles']['hs'], configs['runfiles']['cos'], configs['runfiles']['s3']]
    logging_files = [configs['logger']['hs'], configs['logger']['cos'], configs['logger']['s3']]

    parse_data(run_ID, run_directories, logging_files, configs['cos_object_size'])

    # except Exception as e:
    #     print("Observed exception: ", e)


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
    try:
        print("\n~ PHASE 2: Reading rules...")
        rules = rule_handler(run_ID)
        # print(f"Current rules are: {rules}")
        print("~ Done!")

        print("\n~ PHASE 3: Applying rules...")
        outcome_map = query_handler(rules)
        # print(f"Rule outcome map: {outcome_map}")
        print("~ Done!")

        print("\n~ PHASE 4: Analyzing results...")
        print("~ ----------------------------------")
        predictor(outcome_map, run_ID)
        print("~ ----------------------------------")

    except Exception as e:
        print("Observed exception: ", e)


if __name__ == '__main__':
    print("~ Executing PerfBot...")

    config_file_path = sys.argv[1]
    run_ID = generate_runID()
    execute_parsers(run_ID, config_file_path)
    update_database()
    analyzer(run_ID)

    print("\n")
