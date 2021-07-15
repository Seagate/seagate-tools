import json
import os.path

from src.data_parser import quantum


def read_rulebook():
    filename = os.path.dirname(__file__) + "/../rules.json"
    with open(filename, "r") as f:
        data = json.load(f)

    return data


def get_no_of_occurances(given_thresh):
    try:
        unit = given_thresh.split(" ")
        if unit[1].lower() == "ms":
            threshold_value = float(unit[0])
        elif unit[1].lower().startswith("s"):
            threshold_value = float(unit[0])*1000
        else:
            threshold_value = float(unit[0])
    except IndexError:
        threshold_value = float(unit[0])

    return threshold_value


def get_consecutive_grouping_query(rule, run_ID):
    if rule['query']['filter']['operator'] == "<=" and int(rule['query']['filter']['threshold']) == 0:
        operator = "="
    else:
        operator = rule['query']['filter']['operator']

    occurance = int(get_no_of_occurances(
        rule['query']['grouping']['interval'])/quantum/1000)
    select_clause = f"SELECT round(moving_average({rule['query']['filter']['metric']}, {occurance})*1000)/1000"
    from_clause = "FROM data"
    where_clause = f"WHERE run_ID = {run_ID}"
    threshold = get_no_of_occurances(rule['query']['filter']['threshold'])

    query = f"SELECT * from ({select_clause} {from_clause} {where_clause}) WHERE round {operator} {threshold}"
    return query


def get_any_grouping_query(rule, run_ID):
    query = ""
    select_clause = "SELECT *"
    from_clause = "FROM data"

    threshold_value = get_no_of_occurances(
        rule['query']['filter']['threshold'])
    where_clause = f"WHERE run_ID = {run_ID} AND {rule['query']['filter']['metric']} {rule['query']['filter']['operator']} {threshold_value}"

    query = " ".join([select_clause, from_clause, where_clause])

    return query


def get_db_query_for_data(rule, run_ID):
    if rule['custom_query'].upper() != 'NA':
        return rule['custom_query']

    else:
        grouping = rule['query']['grouping']['constraint'].lower()

        if grouping == 'consecutive':
            query = get_consecutive_grouping_query(rule, run_ID)
        else:
            query = get_any_grouping_query(rule, run_ID)

        return query


def get_db_query_for_logs(rule, run_ID):
    if rule['custom_query'].upper() != 'NA':
        return rule['custom_query']

    else:
        query = ""
        select_clause = "SELECT *"
        from_clause = "FROM logs"

        operator = rule['query']['filter']['operator']
        keyword = rule['query']['filter']['keyword']

        if operator == "=" and keyword[0] != "'" and keyword[0] != "'":
            keyword = "'" + keyword + "'"
        elif operator in ["=~", "!~"] and keyword[0] != "/" and keyword[0] != "/":
            keyword = "/" + keyword + "/"

        where_clause = f"WHERE run_ID = {run_ID} AND keyword {operator} {keyword}"

        query = " ".join([select_clause, from_clause, where_clause])
        return query


def rule_handler(run_ID):
    rule_query_pairs = {}
    rulebook = read_rulebook()
    data_rules = rulebook['data']

    for rule in data_rules:
        if rule['status'] == 'ON':
            query = get_db_query_for_data(rule, run_ID)
            rule_query_pairs[f"D{rule['rule']}"] = query

    logs_rules = rulebook['logs']

    for rule in logs_rules:
        if rule['status'] == 'ON':
            query = get_db_query_for_logs(rule, run_ID)
            rule_query_pairs[f"L{rule['rule']}"] = query

    return rule_query_pairs
