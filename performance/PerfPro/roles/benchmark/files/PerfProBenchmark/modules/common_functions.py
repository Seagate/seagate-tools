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

import yaml
from pymongo import MongoClient
import os


def makeconfig(name):
    """Read data from config file"""
    with open(name) as config_file:
        configs = yaml.safe_load(config_file)
    return configs


def makeconnection(main_config, collection, database):
    """Getting collection from mongo DB database"""
    client = MongoClient(main_config['db_url'])
    db = client[main_config['db_database']]

    collection = db[main_config.get(database)[collection]]

    return db, collection


def getallfiles(directory, extension):
    """function to return all file names with perticular extension"""
    flist = []
    for path, _, files in os.walk(directory):
        for name in files:
            if(name.lower().endswith(extension)):
                flist.append(os.path.join(path, name))
    if flist:
        return True, flist
    else:
        return False, flist


def remove_emptys_from_list(data):
    return [x for x in data if x]


def get_metric_value(data):
    return remove_emptys_from_list(data.split(" "))[-1][:-1]
