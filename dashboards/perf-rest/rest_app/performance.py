# -*- coding: utf-8 -*-
"""Test Execution endpoint entry functions."""
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

from http import HTTPStatus
from urllib.parse import quote_plus

import flask
from flask_restx import Resource, Namespace

from . import mongodbapi, read_config, validations, global_functions

api = Namespace('Performance', path="/performance",
                description='Endpoints for Performance Operations')

@api.route("/search", doc={"description": "Search performance records in MongoDB."})
@api.response(200, "Success")
@api.response(400, "Bad Request: Missing parameters. Do not retry.")
@api.response(401, "Unauthorized: Wrong db_username/db_password.")
@api.response(403, "Forbidden: User does not have permission for operation.")
@api.response(404, "Not Found: No entry for that query in MongoDB.")
@api.response(503, "Service Unavailable: Unable to connect to mongoDB.")
# @api.doc(params={
#     "db_username": "Database username",
#     "db_password": "Database password",
#     "db_collection": "Database collection to look into",
#     "query": "Seach query to look into database"
# })
class Search(Resource):
    """Search endpoint"""
    @staticmethod
    def get():
        """Search performance records in MongoDB."""
        json_data = flask.request.get_json()
        if not json_data:
            return flask.Response(status=HTTPStatus.BAD_REQUEST,
                                  response="Body is empty")
        if not validations.check_user_pass(json_data):
            return flask.Response(status=HTTPStatus.BAD_REQUEST,
                                  response="db_username/db_password missing in request body")
        if not validations.check_collection(json_data):
            return flask.Response(status=HTTPStatus.BAD_REQUEST,
                                  response="db_collection missing in request body")
        validate_field = validations.validate_search_fields(json_data)
        if not validate_field[0]:
            return flask.Response(status=validate_field[1][0], response=validate_field[1][1])

        uri = read_config.mongodb_uri.format(quote_plus(json_data["db_username"]),
                                             quote_plus(json_data["db_password"]),
                                             read_config.db_hostname)

        # Delete username and password as not needed to add those fields in DB
        del json_data["db_username"]
        del json_data["db_password"]

        # Projection can be used to return certain fields from documents
        projection = None
        # Received request with projection field and projection is not empty dictionary
        if "projection" in json_data and bool(json_data["projection"]):
            projection = json_data["projection"]

        count_results = mongodbapi.count_documents(json_data["query"], uri, read_config.db_name,
                                                   json_data["db_collection"])
        if not count_results[0]:
            return flask.Response(status=count_results[1][0],
                                  response=count_results[1][1])
        if count_results[0] and count_results[1] == 0:
            return flask.Response(status=HTTPStatus.NOT_FOUND,
                                  response=f"No results for query {json_data}")

        query_results = mongodbapi.find_documents(json_data["query"], projection, uri,
                                                  read_config.db_name,
                                                  json_data["db_collection"])
        if query_results[0]:
            output = []
            for results in query_results[1]:
                global_functions.convert_objectids(results)
                output.append(results)
            return flask.jsonify({'result': output})
        return flask.Response(status=query_results[1][0], response=query_results[1][1])


@api.route("/distinct", doc={"description": "Get distinct values for given key."})
@api.response(200, "Success")
@api.response(400, "Bad Request: Missing parameters. Do not retry.")
@api.response(401, "Unauthorized: Wrong db_username/db_password.")
@api.response(403, "Forbidden: User does not have permission for operation.")
@api.response(404, "Not Found: No entry for that query in MongoDB.")
@api.response(503, "Service Unavailable: Unable to connect to mongoDB.")
class Distinct(Resource):
    """Update endpoint"""

    @staticmethod
    def get():
        """Get distinct values for given key."""
        json_data = flask.request.get_json()
        if not json_data:
            return flask.Response(status=HTTPStatus.BAD_REQUEST,
                                  response="Body is empty")
        if not validations.check_user_pass(json_data):
            return flask.Response(status=HTTPStatus.BAD_REQUEST,
                                  response="db_username/db_password missing in request body")
        if not validations.check_collection(json_data):
            return flask.Response(status=HTTPStatus.BAD_REQUEST,
                                  response="db_collection missing in request body")
        validate_field = validations.validate_distinct_fields(json_data)
        if not validate_field[0]:
            return flask.Response(status=validate_field[1][0], response=validate_field[1][1])

        uri = read_config.mongodb_uri.format(quote_plus(json_data["db_username"]),
                                             quote_plus(json_data["db_password"]),
                                             read_config.db_hostname)

        # Delete username and password as not needed to add those fields in DB
        del json_data["db_username"]
        del json_data["db_password"]

        # Projection can be used to return certain fields from documents
        query = {}
        # Received request with projection field and projection is not empty dictionary
        if "query" in json_data and bool(json_data["query"]):
            query = json_data["query"]

        count_results = mongodbapi.distinct_fields(json_data["field"], query, uri,
                                                   read_config.db_name,
                                                   json_data["db_collection"])
        if not count_results[0]:
            return flask.Response(status=count_results[1][0],
                                  response=count_results[1][1])
        return flask.jsonify({'result': count_results[1]})


@api.route("/aggregate", doc={"description": "Get aggregate values as per the query."})
@api.response(200, "Success")
@api.response(400, "Bad Request: Missing parameters. Do not retry.")
@api.response(401, "Unauthorized: Wrong db_username/db_password.")
@api.response(403, "Forbidden: User does not have permission for operation.")
@api.response(404, "Not Found: No entry for that query in MongoDB.")
@api.response(503, "Service Unavailable: Unable to connect to mongoDB.")
class Aggregate(Resource):
    """Update endpoint"""

    @staticmethod
    def get():
        """Get aggregate values as per the query."""
        json_data = flask.request.get_json()
        if not json_data:
            return flask.Response(status=HTTPStatus.BAD_REQUEST,
                                  response="Body is empty")
        if not validations.check_user_pass(json_data):
            return flask.Response(status=HTTPStatus.BAD_REQUEST,
                                  response="db_username/db_password missing in request body")
        if not validations.check_collection(json_data):
            return flask.Response(status=HTTPStatus.BAD_REQUEST,
                                  response="db_collection missing in request body")

        uri = read_config.mongodb_uri.format(quote_plus(json_data["db_username"]),
                                             quote_plus(json_data["db_password"]),
                                             read_config.db_hostname)

        # Delete username and password as not needed to add those fields in DB
        del json_data["db_username"]
        del json_data["db_password"]

        aggregate_results = mongodbapi.aggregate(json_data["aggregate"], uri,
                                                 read_config.db_name,
                                                 json_data["db_collection"])
        if not aggregate_results[0]:
            return flask.Response(status=aggregate_results[1][0],
                                  response=aggregate_results[1][1])
        return flask.jsonify({'result': list(aggregate_results[1])})


@api.route("/count", doc={"description": "Count matching performance records in MongoDB."})
@api.response(400, "Bad Request: Missing parameters. Do not retry.")
@api.response(401, "Unauthorized: Wrong db_username/db_password.")
@api.response(403, "Forbidden: User does not have permission for operation.")
@api.response(404, "Not Found: No entry for that query in MongoDB.")
@api.response(503, "Service Unavailable: Unable to connect to mongoDB.")
class Count(Resource):
    """Search endpoint"""

    @staticmethod
    def get():
        """Count matching performance records in MongoDB."""
        json_data = flask.request.get_json()
        if not json_data:
            return flask.Response(status=HTTPStatus.BAD_REQUEST,
                                  response="Body is empty")
        if not validations.check_user_pass(json_data):
            return flask.Response(status=HTTPStatus.BAD_REQUEST,
                                  response="db_username/db_password missing in request body")
        if not validations.check_collection(json_data):
            return flask.Response(status=HTTPStatus.BAD_REQUEST,
                                  response="db_collection missing in request body")
        validate_field = validations.validate_search_fields(json_data)
        if not validate_field[0]:
            return flask.Response(status=validate_field[1][0], response=validate_field[1][1])

        uri = read_config.mongodb_uri.format(quote_plus(json_data["db_username"]),
                                             quote_plus(json_data["db_password"]),
                                             read_config.db_hostname)

        # Delete username and password as not needed to add those fields in DB
        del json_data["db_username"]
        del json_data["db_password"]

        count_results = mongodbapi.count_documents(json_data["query"], uri, read_config.db_name,
                                                   json_data["db_collection"])
        if not count_results[0]:
            return flask.Response(status=count_results[1][0],
                                  response=count_results[1][1])
        if count_results[0] and count_results[1] == 0:
            return flask.Response(status=HTTPStatus.NOT_FOUND,
                                  response=f"No results for query {json_data}")
        return flask.jsonify({'result': count_results[1]})
