# -*- coding: utf-8 -*-
"""Sanity API to help backend code to execute for Sanity endpoints."""
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

from . import mongodbapi, read_config


def get_run_id(uri, query):
    """Get run ID from the given query."""
    query_results = mongodbapi.find_documents(query, None, uri,
                                              read_config.db_name, read_config.sanity_run_details)
    if query_results[0]:
        return query_results[1][0]['_id']
    else:
        return None


def get_baseline_index(uri):
    """Get Baseline index of latest baseline in database."""
    query_results = mongodbapi.get_highest_value_document({}, "Baseline", None, uri,
                        read_config.db_name, read_config.sanity_results)
    if query_results[0]:
        return query_results[1][0]['Baseline']
    else:
        return None


def calculate_deviation(value, baseline):
    """Calculates % deviation from value and baseline."""
    return (value - baseline) * 100 / baseline


def read_write_routine(**kwargs):
    """Read and Write common code routine to get read and write data from database."""
    kwargs['query']['Operation'] = 'Read'
    query_results = mongodbapi.find_documents(kwargs['query'], None, kwargs['uri'],
                                              read_config.db_name, read_config.sanity_results)
    kwargs['temp_read'][kwargs['obj']] = query_results[1][0][kwargs['metrix']]

    kwargs['query']['Operation'] = 'Write'
    query_results = mongodbapi.find_documents(kwargs['query'], None, kwargs['uri'],
                                              read_config.db_name, read_config.sanity_results)
    kwargs['temp_write'][kwargs['obj']] = query_results[1][0][kwargs['metrix']]


def read_write_routine_for_params(**kwargs):
    """Read and Write common code routine using params to get read and write data from database."""
    kwargs['query']['Operation'] = 'Read'
    query_results = mongodbapi.find_documents(kwargs['query'], None, kwargs['uri'],
                                              read_config.db_name, read_config.sanity_results)
    kwargs['temp_read'][kwargs['obj']
                        ] = query_results[1][0][kwargs['metrix']][kwargs['param']]

    kwargs['query']['Operation'] = 'Write'
    query_results = mongodbapi.find_documents(kwargs['query'], None, kwargs['uri'],
                                              read_config.db_name, read_config.sanity_results)
    kwargs['temp_write'][kwargs['obj']
                         ] = query_results[1][0][kwargs['metrix']][kwargs['param']]


def read_write_routine_for_ttfb(**kwargs):
    """Read and Write for TTFB common code routine to get read and write data from database."""
    kwargs['query']['Operation'] = 'Read'
    query_results = mongodbapi.find_documents(kwargs['query'], None, kwargs['uri'],
                                              read_config.db_name, read_config.sanity_results)
    kwargs['temp_read'][kwargs['obj']
                        ] = query_results[1][0][kwargs['metrix']]['Avg']

    kwargs['temp_write'][kwargs['obj']
                         ] = query_results[1][0][kwargs['metrix']]['99p']
