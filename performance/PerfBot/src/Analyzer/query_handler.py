
from influxdb import client
from src.store_data import connect_database
import json
import os

def read_rulebook():
    filename = os.path.dirname(__file__) + "/../rules.json"
    with open(filename, "r") as f:
        data = json.load(f)

    return data


def query_handler(rules, rulebook):
    rule_outcome_map = {}
    client = connect_database()

    for rule_ID in rules.keys():
        query_result = client.query(rules[rule_ID])
        if rule_ID.startswith("D"):
            measurement = "data"
        else:
            measurement = "logs"

        try:
            count_of_query_result = len(list(query_result)[0])
        except IndexError:
            count_of_query_result = 0

        expected_outcome = rulebook[measurement][int(rule_ID[1:])-1]["output"]
        if str(expected_outcome).lower() == "no" or str(expected_outcome).startswith("n") and count_of_query_result != 0:
                rule_outcome_map[rule_ID] = "fail"
        else:
            rule_outcome_map[rule_ID] = "pass"

    return rule_outcome_map
