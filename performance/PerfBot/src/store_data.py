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
# Seagate-tools: PerfBot - functions to store data in Database

from influxdb import InfluxDBClient
import yaml
import os

input_folder_path =  "./Input/"


def connect_database():
    file_name = "./perfbot_config.yml"
    with open(file_name, 'r') as config_file:
        configs = yaml.safe_load(config_file)

        host = configs['database']['host']
        port = configs['database']['port']
        db_name = configs['database']['database']

        client = InfluxDBClient(host=host, port=port, database=db_name)
        return client


def update_parsed_data():
    client = connect_database()

    _, _, filenames = next(os.walk(input_folder_path))

    for files in filenames:
        with open(input_folder_path + files, 'r') as bench_file:
            bench_data = yaml.safe_load(bench_file)

        client.write_points(bench_data)
