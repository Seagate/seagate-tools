
from store_data import connect_database
from Analyzer.predictor import read_lookuptable


def validator_handler(rule_ID, client, rules, rule_outcome_map):
    query_result = client.query(rules[rule_ID])

    try:
        count_of_query_result = len(list(query_result)[0])
    except IndexError:
        count_of_query_result = 0

    rule_outcome_map[rule_ID] = count_of_query_result


def query_handler(rules):
    rule_outcome_map = {}
    client = connect_database()
    lookup_table = read_lookuptable()

    for rule_ID in rules.keys():
        for logic in lookup_table:
            if rule_ID in logic[3]:
                functionality = logic[1]
                break

        if functionality.lower() == 'validation':
            validator_handler(rule_ID, client, rules, rule_outcome_map)
        else:
            pass

    return rule_outcome_map
