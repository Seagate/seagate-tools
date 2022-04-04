# -*- coding: utf-8 -*-
"""Sanity endpoint entry functions."""
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

import flask
from flask_restx import Resource, Namespace

from . import read_config, validations, sanityapi, schemas

api = Namespace('Sanity', path="/sanity",
                description='Endpoints for sanity operations')


@api.route("/throughput", doc={"description": "Get throughput data endpoints from MongoDB."})
@api.response(200, "Success")
@api.response(400, "Bad Request: Missing parameters. Do not retry.")
@api.response(401, "Unauthorized: Wrong db_username/db_password.")
@api.response(403, "Forbidden: User does not have permission for operation.")
@api.response(404, "Not Found: No entry for that query in MongoDB.")
@api.response(503, "Service Unavailable: Unable to connect to mongoDB.")
class throughput(Resource):
    """Sanity throughput endpoint"""
    @staticmethod
    def get():
        """Get throughput data endpoints from MongoDB for given query."""
        json_data = flask.request.get_json()
        if not json_data:
            return flask.Response(status=HTTPStatus.BAD_REQUEST,
                                  response="Body is empty")

        validate_field = validations.validate_sanity_fields(json_data)
        if not validate_field[0]:
            return flask.Response(status=validate_field[1][0], response=validate_field[1][1])

        uri = read_config.mongodb_uri.format(read_config.db_username, read_config.db_password,
                                             read_config.db_hostname)

        run_id = sanityapi.get_run_id(uri, json_data["query"])
        results = {'write': schemas.results_format,
                   'read': schemas.results_format}

        base_index = sanityapi.get_baseline_index(uri)

        for obj in read_config.sanity_obj_sizes:
            value_query = {"run_ID": run_id,
                 "Sessions": read_config.sanity_sessions, 'Object_Size': obj}
            base_query = {'Baseline': base_index,
                 "Sessions": read_config.sanity_sessions, 'Object_Size': obj}
            sanityapi.read_write_routine(
                uri=uri, query=value_query, metrix='Throughput', obj=obj, 
                temp_read=results['read']['value'], 
                temp_write=results['write']['value'])
            sanityapi.read_write_routine(
                uri=uri, query=base_query, metrix='Throughput', obj=obj, 
                temp_read=results['read']['baseline'], 
                temp_write=results['write']['baseline'])

            results['read']['diff'][obj] = results['read']['value'][obj] - \
                results['read']['baseline'][obj]
            results['write']['diff'][obj] = results['write']['value'][obj] - \
                results['write']['baseline'][obj]

            results['read']['deviation'][obj] = sanityapi.calculate_deviation(
                results['read']['value'][obj], results['read']['baseline'][obj])
            results['write']['deviation'][obj] = sanityapi.calculate_deviation(
                results['write']['value'][obj], results['write']['baseline'][obj])

        return flask.jsonify({'result': results})
        # return flask.Response(status=query_results[1][0], response=query_results[1][1])


@api.route("/iops", doc={"description": "Get iops data endpoints from MongoDB."})
@api.response(200, "Success")
@api.response(400, "Bad Request: Missing parameters. Do not retry.")
@api.response(401, "Unauthorized: Wrong db_username/db_password.")
@api.response(403, "Forbidden: User does not have permission for operation.")
@api.response(404, "Not Found: No entry for that query in MongoDB.")
@api.response(503, "Service Unavailable: Unable to connect to mongoDB.")
class throughput(Resource):
    """Sanity iops endpoint"""
    @staticmethod
    def get():
        """Get iops data endpoints from MongoDB for given query."""
        json_data = flask.request.get_json()
        if not json_data:
            return flask.Response(status=HTTPStatus.BAD_REQUEST,
                                  response="Body is empty")

        validate_field = validations.validate_sanity_fields(json_data)
        if not validate_field[0]:
            return flask.Response(status=validate_field[1][0], response=validate_field[1][1])

        uri = read_config.mongodb_uri.format(read_config.db_username, read_config.db_password,
                                             read_config.db_hostname)

        run_id = sanityapi.get_run_id(uri, json_data["query"])
        results = {'write': schemas.results_format,
                   'read': schemas.results_format}

        base_index = sanityapi.get_baseline_index(uri)

        for obj in read_config.sanity_obj_sizes:
            value_query = {"run_ID": run_id,
                 "Sessions": read_config.sanity_sessions, 'Object_Size': obj}
            base_query = {'Baseline': base_index,
                 "Sessions": read_config.sanity_sessions, 'Object_Size': obj}
            sanityapi.read_write_routine(
                uri=uri, query=value_query, metrix='IOPS', obj=obj, 
                temp_read=results['read']['value'], 
                temp_write=results['write']['value'])
            sanityapi.read_write_routine(
                uri=uri, query=base_query, metrix='IOPS', obj=obj, 
                temp_read=results['read']['baseline'], 
                temp_write=results['write']['baseline'])

            results['read']['diff'][obj] = results['read']['value'][obj] - \
                results['read']['baseline'][obj]
            results['write']['diff'][obj] = results['write']['value'][obj] - \
                results['write']['baseline'][obj]

            results['read']['deviation'][obj] = sanityapi.calculate_deviation(
                results['read']['value'][obj], results['read']['baseline'][obj])
            results['write']['deviation'][obj] = sanityapi.calculate_deviation(
                results['write']['value'][obj], results['write']['baseline'][obj])

        return flask.jsonify({'result': results})
        # return flask.Response(status=query_results[1][0], response=query_results[1][1])



@api.route("/latency", doc={"description": "Get latency data endpoints from MongoDB."})
@api.response(200, "Success")
@api.response(400, "Bad Request: Missing parameters. Do not retry.")
@api.response(401, "Unauthorized: Wrong db_username/db_password.")
@api.response(403, "Forbidden: User does not have permission for operation.")
@api.response(404, "Not Found: No entry for that query in MongoDB.")
@api.response(503, "Service Unavailable: Unable to connect to mongoDB.")
class throughput(Resource):
    """Sanity latency endpoint"""
    @staticmethod
    def get():
        """Get latency data endpoints from MongoDB for given query."""
        json_data = flask.request.get_json()
        if not json_data:
            return flask.Response(status=HTTPStatus.BAD_REQUEST,
                                  response="Body is empty")

        validate_field = validations.validate_sanity_fields(json_data)
        if not validate_field[0]:
            return flask.Response(status=validate_field[1][0], response=validate_field[1][1])

        uri = read_config.mongodb_uri.format(read_config.db_username, read_config.db_password,
                                             read_config.db_hostname)

        run_id = sanityapi.get_run_id(uri, json_data["query"])
        results = {'write': schemas.results_format,
                   'read': schemas.results_format}

        base_index = sanityapi.get_baseline_index(uri)

        for obj in read_config.sanity_obj_sizes:
            value_query = {"run_ID": run_id,
                 "Sessions": read_config.sanity_sessions, 'Object_Size': obj}
            base_query = {'Baseline': base_index,
                 "Sessions": read_config.sanity_sessions, 'Object_Size': obj}
            sanityapi.read_write_routine(
                uri=uri, query=value_query, metrix='IOPS', param='Avg', obj=obj, 
                temp_read=results['read']['value'], 
                temp_write=results['write']['value'])
            sanityapi.read_write_routine(
                uri=uri, query=base_query, metrix='IOPS', param='Avg', obj=obj, 
                temp_read=results['read']['baseline'], 
                temp_write=results['write']['baseline'])

            results['read']['diff'][obj] = results['read']['value'][obj] - \
                results['read']['baseline'][obj]
            results['write']['diff'][obj] = results['write']['value'][obj] - \
                results['write']['baseline'][obj]

            results['read']['deviation'][obj] = sanityapi.calculate_deviation(
                results['read']['value'][obj], results['read']['baseline'][obj])
            results['write']['deviation'][obj] = sanityapi.calculate_deviation(
                results['write']['value'][obj], results['write']['baseline'][obj])

        return flask.jsonify({'result': results})
        # return flask.Response(status=query_results[1][0], response=query_results[1][1])



@api.route("/ttfb", doc={"description": "Get TTFB data endpoints from MongoDB."})
@api.response(200, "Success")
@api.response(400, "Bad Request: Missing parameters. Do not retry.")
@api.response(401, "Unauthorized: Wrong db_username/db_password.")
@api.response(403, "Forbidden: User does not have permission for operation.")
@api.response(404, "Not Found: No entry for that query in MongoDB.")
@api.response(503, "Service Unavailable: Unable to connect to mongoDB.")
class throughput(Resource):
    """Sanity TTFB endpoint"""
    @staticmethod
    def get():
        """Get TTFB data endpoints from MongoDB for given query."""
        json_data = flask.request.get_json()
        if not json_data:
            return flask.Response(status=HTTPStatus.BAD_REQUEST,
                                  response="Body is empty")

        validate_field = validations.validate_sanity_fields(json_data)
        if not validate_field[0]:
            return flask.Response(status=validate_field[1][0], response=validate_field[1][1])

        uri = read_config.mongodb_uri.format(read_config.db_username, read_config.db_password,
                                             read_config.db_hostname)

        run_id = sanityapi.get_run_id(uri, json_data["query"])
        results = {'write': schemas.results_format,
                   'read': schemas.results_format}

        base_index = sanityapi.get_baseline_index(uri)

        for obj in read_config.sanity_obj_sizes:
            value_query = {"run_ID": run_id,
                 "Sessions": read_config.sanity_sessions, 'Object_Size': obj}
            base_query = {'Baseline': base_index,
                 "Sessions": read_config.sanity_sessions, 'Object_Size': obj}
            sanityapi.read_write_routine_for_ttfb(
                uri=uri, query=value_query, metrix='TTFB', obj=obj, 
                temp_read=results['read']['value'], 
                temp_write=results['write']['value'])
            sanityapi.read_write_routine_for_ttfb(
                uri=uri, query=base_query, metrix='TTFB', obj=obj, 
                temp_read=results['read']['baseline'], 
                temp_write=results['write']['baseline'])

            results['read']['diff'][obj] = results['read']['value'][obj] - \
                results['read']['baseline'][obj]
            results['write']['diff'][obj] = results['write']['value'][obj] - \
                results['write']['baseline'][obj]

            results['read']['deviation'][obj] = sanityapi.calculate_deviation(
                results['read']['value'][obj], results['read']['baseline'][obj])
            results['write']['deviation'][obj] = sanityapi.calculate_deviation(
                results['write']['value'][obj], results['write']['baseline'][obj])

        return flask.jsonify({'result': results})
        # return flask.Response(status=query_results[1][0], response=query_results[1][1])