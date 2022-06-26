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
"""Read config file for database."""

import yaml
import sys

with open("config.yml") as file:
    config = yaml.load(file, Loader=yaml.SafeLoader)
    try:
        db_hostname = config["MongoDB"]["db_hostname"]
        db_name = config["MongoDB"]["db_name"]
        results_collection = config["MongoDB"]["results_collection"]

        sanity_config = config["Sanity"]["database"]["config"]
        sanity_run_details = config["Sanity"]["database"]["run_details"]
        sanity_results = config["Sanity"]["database"]["results"]

        sanity_obj_sizes = config["Sanity"]["workload"]["primary"]["object_sizes"]
        sanity_sessions = config["Sanity"]["workload"]["primary"]["sessions"]

        sanity_high_conc_obj_size = config["Sanity"]["workload"]["secondary"]["object_sizes"]
        sanity_high_conc_sessions = config["Sanity"]["workload"]["secondary"]["sessions"]

        db_username = config["Authentication"]["db_username"]
        db_password = config["Authentication"]["db_password"]
    except KeyError:
        print("Could not start REST server. Please verify config.ini file")
        sys.exit(1)

mongodb_uri = "mongodb://{0}:{1}@{2}"
