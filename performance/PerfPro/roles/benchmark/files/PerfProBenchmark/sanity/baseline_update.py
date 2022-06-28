#!/usr/bin/env python3
#
# Seagate-tools: PerfPro
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

from pymongo import MongoClient
from bson.objectid import ObjectId
import yaml
import sys

Main_path = sys.argv[1]
Config_path = sys.argv[2]
Config_ID = sys.argv[3]
objInstance = ObjectId(Config_ID)


def makeconfig(name):  # function for connecting with configuration file
    with open(name) as config_file:
        configs = yaml.safe_load(config_file)
    return configs


configs_main = makeconfig(Main_path)
configs_config = makeconfig(Config_path)


def makeconnection(collection):  # function for making connection with database
    # connecting with mongodb database
    client = MongoClient(configs_main['db_url'])
    db = client[configs_main['db_database']]  # database name=performance
    col = configs_main.get('SANITY')[collection]
    sanity_col = db[col]
    return sanity_col


def baseline_update(sanity_config, query):
    baseline = sanity_config.distinct('Baseline')
    latest_baseline = max(baseline)
    if (latest_baseline >= 1):
        baseline = latest_baseline+1
    else:
        baseline = 1
    sanity_config.update_one(
        query, {"$set": {'Baseline': baseline, 'Comment': 'highest throughput observed'}})
    entry = sanity_config.find_one(query)
    print(entry)


sanity_config = makeconnection('sanity_config_collection')
query = {'_id': objInstance}
baseline_update(sanity_config, query)
