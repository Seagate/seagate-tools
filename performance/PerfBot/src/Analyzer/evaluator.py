import csv
from datetime import datetime
import time
import ast

from Analyzer.rule_handler import read_rulebook
from store_data import connect_database
from schemas import get_results_schema
rulebook = read_rulebook()


def read_lookuptable():
    lookup_table = []
    with open("./Analyzer/lookup.csv", "r") as csv_file:
        lookup_table_file = csv.reader(csv_file, delimiter=',')
        for logic in lookup_table_file:
            lookup_table.append(logic)

    return lookup_table


def validator(logic, outcome_map, rule_results_map):
    formula = logic[3]
    for key in outcome_map.keys():
        if outcome_map[key] == 0:
            state = True
        else:
            state = False

        rule_results_map[key] = state
        formula = formula.replace(key, str(state))

    result = ast.literal_eval(formula)
    if result:
        return "Good"
    else:
        return "Bad"


def display_rules(rule_results_map, run_ID, functionality, result):
    obs_not_found = True
    print("~ Observations: ")

    for rule in rule_results_map.keys():
        if not rule_results_map[rule]:
            if rule.upper().startswith("D"):
                rule_type = 'data'
            else:
                rule_type = 'logs'

            print(
                f"~ {rulebook[rule_type][int(rule[1:]) -1]['label']} - {rulebook[rule_type][int(rule[1:]) -1]['description']}")
            obs_not_found = False

    if obs_not_found:
        print("~ No violations found.")
    update_results(run_ID, functionality, result, rulebook['version'])


def update_results(run_ID, functionality, result, rulebook_version):
    client = connect_database()
    latest_sr_no = client.query("select last(sr_no) from results;")
    try:
        gen_sr_no = int(list(latest_sr_no)[0][0]['last']) + 1
    except IndexError:
        gen_sr_no = 1

    date = str(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))

    result_dict = get_results_schema(time.time_ns(),
                                     gen_sr_no, date, run_ID, functionality, result.lower(), rulebook_version, False)

    client.write_points([result_dict])


def predictor(outcome_map, run_ID):
    lookup_table = read_lookuptable()
    lookup_table = lookup_table[1:]
    rule_results_map = {}

    for logic in lookup_table:
        functionality = logic[1]

        if functionality.lower() == 'validation':
            result = validator(logic, outcome_map, rule_results_map)
            print("~ PHASE 4: Done")

            print("\n\n~ Run report:-")
            print("~ ==================================")
            print(f"~ Functionality: {logic[1]}\n")
            display_rules(rule_results_map, run_ID, functionality, result)
            print(f"\n~ Final Run Result: {result}")
            print("~ ==================================")
