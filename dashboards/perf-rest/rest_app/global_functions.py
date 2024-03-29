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
"""Global Functions for REST Server."""

def convert_objectids(results):
    """Converting ObjectID datatype to string."""
    results["_id"] = str(results["_id"])
    if "run_ID" in results:
        results["run_ID"] = str(results["run_ID"])
    if "Config_ID" in results:
        results["Config_ID"] = str(results["Config_ID"])


def covert_query_to_readable(**kwargs):
    """Converting query to another form."""
    input_vals = {}
    major_repos = ["motr", "rgw", "hare"]
    for repo in major_repos:
        repo_pair = dict(kwargs["Commit_ID"][kwargs["Repository"].index(
            kwargs[f"{repo}_repository"])])
        input_vals[repo] = {
            "repository": kwargs[f"{repo}_repository"],
            "branch": list(repo_pair.keys())[0],
            "commit": list(repo_pair.values())[0]
        }

    return input_vals
