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

"""
Script for storing configuration file data into MongoDB
Command : python3 addconfiguration.py
Requirements:
pip3 install PyYAML==5.3.1
pip3 install pymongo==3.11.0
"""


import modules.common_functions as cf
import modules.schemas as schemas
import mongodbapi as mapi


class Configuration_Store:

    def __init__(self):
        self.main_config = cf.import_perfpro_config()
        self.config_set = schemas.set_system_monitoring_config_set(self)
        self.db_uri = self.main_config["sanity"]["database"]["url"]
        self.db_name = self.main_config["sanity"]["database"]["name"]
        self.insert_or_update_documents()

    def insert_or_update_documents(self):
        """Update or insert the configuration in the required DB collection
        """
        try:
            _, count_documents = mapi.count_documents(
                self.config_set, self.db_uri, self.db_name, 'config_collection')
            if count_documents == 0:
                mapi.add_document(self.config_set, self.db_uri,
                                  self.db_name, 'config_collection')
                print('Configuration Data is Recorded ::')
                print(self.config_set)
            else:
                print('Configuration data already present')
        except Exception as e:
            print(
                "Unable to insert/update documents into database. Observed following exception:")
            print(e)


def main():
    Configuration_Store()


if __name__ == "__main__":
    main()
