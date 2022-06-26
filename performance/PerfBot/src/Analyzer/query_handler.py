#!/usr/bin/env python3
#
# Copyright (c) 2022 Seagate Technology LLC and/or its Affiliates
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
#
# For any questions about this software or licensing,
# please email opensource@seagate.com or cortx-questions@seagate.com.
#
# -*- coding: utf-8 -*-
# Seagate-tools: PerfBot - Query handler for decision block

from store_data import connect_database
from Analyzer.evaluator import read_lookuptable


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
