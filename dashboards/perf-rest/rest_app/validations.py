# -*- coding: utf-8 -*-
"""Functions used to validate REST requests."""
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

from http import HTTPStatus
from typing import Union
from bson.objectid import ObjectId


mongodb_operators = ["$and", "$nor", "$or"]


def check_user_pass(json_data: dict) -> bool:
    """
    Check if mandatory username and password present in request

    Args:
        json_data: Data from request

    Returns:
        bool
    """
    if "db_username" in json_data and "db_password" in json_data:
        return True
    return False


def check_collection(json_data: dict) -> bool:
    """
    Check if mandatory collection present in request

    Args:
        json_data: Data from request

    Returns:
        bool
    """
    if "db_collection" in json_data:
        return True
    return False


def validate_search_fields(json_data: dict) -> Union[bool, tuple]:
    """Validate search fields"""
    if "query" not in json_data:
        return False, (HTTPStatus.BAD_REQUEST, "Please provide query key")
    if not isinstance(json_data["query"], dict):
        return False, (HTTPStatus.BAD_REQUEST,
                       "Please provide query key as dictionary")
    if "projection" in json_data and not isinstance(json_data["projection"], dict):
        return False, (HTTPStatus.BAD_REQUEST,
                       "Please provide projection keys as dictionary")
    return True, None


def validate_sanity_fields(json_data: dict) -> Union[bool, tuple]:
    """Validate search fields"""
    if "run_id" not in json_data:
        return False, (HTTPStatus.BAD_REQUEST, "Please provide query with proper run ID.")
    if not ObjectId.is_valid(json_data['run_id']):
        return False, (HTTPStatus.BAD_REQUEST,
                       "Given run_id is not a valid ObjectId, it must be a 12-byte \
                           input or a 24-character hex string.")
    elif isinstance(json_data["run_id"], str):
        json_data["run_id"] = ObjectId(json_data["run_id"])

    return True, None


def validate_distinct_fields(json_data: dict) -> Union[bool, tuple]:
    """Validate search fields"""
    if "query" in json_data and not isinstance(json_data["query"], dict):
        return False, (HTTPStatus.BAD_REQUEST,
                       "Please provide query key as dictionary")
    # for key in json_data["query"]:
    #     if key not in db_keys and key not in extra_db_keys and key not in mongodb_operators:
    #         return False, (HTTPStatus.BAD_REQUEST,
    #                        f"{key} is not correct db field")
    if "field" not in json_data:
        return False, (HTTPStatus.BAD_REQUEST,
                       "Please provide field key")
    if not isinstance(json_data["field"], str):
        return False, (HTTPStatus.BAD_REQUEST,
                       "Please provide field key as string")
    return True, None
