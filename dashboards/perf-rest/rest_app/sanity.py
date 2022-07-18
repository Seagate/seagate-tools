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
"""Sanity endpoint entry functions."""

from copy import deepcopy
from http import HTTPStatus

import flask
from flask_restx import Resource, Namespace

from . import read_config, validations, sanityapi, schemas, global_functions

api = Namespace("Sanity", path="/sanity",
                description="Endpoints for sanity operations")
uri = read_config.mongodb_uri.format(read_config.db_username, read_config.db_password,
                                     read_config.db_hostname)


def validate_inputs(request_runid, json_data):
    if not request_runid:
        return flask.Response(status=HTTPStatus.BAD_REQUEST,
                              response="Body is empty")

    validate_field = validations.validate_sanity_fields(json_data)
    if not validate_field[0]:
        return flask.Response(status=validate_field[1][0], response=validate_field[1][1])


def calculate_perf_tables(p_status, b_status, results, obj, op):
    if p_status and b_status:
        results[op]["difference"][obj] = round(results[op]["value"][obj] - \
            results[op]["baseline"][obj], 3)
        results[op]["deviation"][obj] = sanityapi.calculate_deviation(
            results[op]["value"][obj], results[op]["baseline"][obj])
    else:
        results[op]["difference"][obj] = "NA"
        results[op]["deviation"][obj] = "NA"


def extract_performance_routine(json_data, metrix):
    uri = read_config.mongodb_uri.format(read_config.db_username, read_config.db_password,
                                         read_config.db_hostname)

    results = {"write": deepcopy(schemas.results_format),
               "read": deepcopy(schemas.results_format)}

    _, record_id = sanityapi.get_baseline_index(uri, json_data["run_id"])

    for obj in read_config.sanity_obj_sizes:
        value_query = {"run_ID": json_data["run_id"],
                       "Sessions": read_config.sanity_sessions, "Object_Size": obj}
        base_query = {"Config_ID": record_id,
                      "Sessions": read_config.sanity_sessions, "Object_Size": obj}

        if metrix in ["Throughput", "IOPS"]:
            rp_status, wp_status, rp, wp = sanityapi.read_write_routine(
                uri=uri, query=value_query, metrix=metrix)
            rb_status, wb_status, rb, wb = sanityapi.read_write_routine(
                uri=uri, query=base_query, metrix=metrix)
        elif metrix == "Latency":
            rp_status, wp_status, rp, wp = sanityapi.read_write_routine_for_params(
                uri=uri, query=value_query, metrix=metrix, param="Avg")
            rb_status, wb_status, rb, wb = sanityapi.read_write_routine_for_params(
                uri=uri, query=base_query, metrix=metrix, param="Avg")
        else:
            rp_status, wp_status, rp, wp = sanityapi.read_write_routine_for_ttfb(
                uri=uri, query=value_query, metrix=metrix)
            rb_status, wb_status, rb, wb = sanityapi.read_write_routine_for_ttfb(
                uri=uri, query=base_query, metrix=metrix)

        results["read"]["value"][obj] = rp
        results["read"]["baseline"][obj] = rb
        results["write"]["value"][obj] = wp
        results["write"]["baseline"][obj] = wb
        calculate_perf_tables(rp_status, rb_status, results, obj, "read")
        calculate_perf_tables(wp_status, wb_status, results, obj, "write")

    return flask.jsonify({"result": results})


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
        request_runid = flask.request.args.get("run_id")
        json_data = {"run_id": request_runid}
        validate_inputs(request_runid, json_data)
        return extract_performance_routine(json_data, "Throughput")


@api.route("/iops", doc={"description": "Get iops data endpoints from MongoDB."})
@api.response(200, "Success")
@api.response(400, "Bad Request: Missing parameters. Do not retry.")
@api.response(401, "Unauthorized: Wrong db_username/db_password.")
@api.response(403, "Forbidden: User does not have permission for operation.")
@api.response(404, "Not Found: No entry for that query in MongoDB.")
@api.response(503, "Service Unavailable: Unable to connect to mongoDB.")
class iops(Resource):
    """Sanity iops endpoint"""
    @staticmethod
    def get():
        """Get iops data endpoints from MongoDB for given query."""
        request_runid = flask.request.args.get("run_id")
        json_data = {"run_id": request_runid}
        validate_inputs(request_runid, json_data)
        return extract_performance_routine(json_data, "IOPS")


@api.route("/latency", doc={"description": "Get latency data endpoints from MongoDB."})
@api.response(200, "Success")
@api.response(400, "Bad Request: Missing parameters. Do not retry.")
@api.response(401, "Unauthorized: Wrong db_username/db_password.")
@api.response(403, "Forbidden: User does not have permission for operation.")
@api.response(404, "Not Found: No entry for that query in MongoDB.")
@api.response(503, "Service Unavailable: Unable to connect to mongoDB.")
class latency(Resource):
    """Sanity latency endpoint"""
    @staticmethod
    def get():
        """Get latency data endpoints from MongoDB for given query."""
        request_runid = flask.request.args.get("run_id")
        json_data = {"run_id": request_runid}
        validate_inputs(request_runid, json_data)
        return extract_performance_routine(json_data, "Latency")


@api.route("/ttfb", doc={"description": "Get TTFB data endpoints from MongoDB."})
@api.response(200, "Success")
@api.response(400, "Bad Request: Missing parameters. Do not retry.")
@api.response(401, "Unauthorized: Wrong db_username/db_password.")
@api.response(403, "Forbidden: User does not have permission for operation.")
@api.response(404, "Not Found: No entry for that query in MongoDB.")
@api.response(503, "Service Unavailable: Unable to connect to mongoDB.")
class ttfb(Resource):
    """Sanity TTFB endpoint"""
    @staticmethod
    def get():
        """Get TTFB data endpoints from MongoDB for given query."""
        request_runid = flask.request.args.get("run_id")
        json_data = {"run_id": request_runid}
        validate_inputs(request_runid, json_data)
        return extract_performance_routine(json_data, "TTFB")


@api.route("/config", doc={"description": "Get config of sanity run based on ID from MongoDB."})
@api.response(200, "Success")
@api.response(400, "Bad Request: Missing parameters. Do not retry.")
@api.response(401, "Unauthorized: Wrong db_username/db_password.")
@api.response(403, "Forbidden: User does not have permission for operation.")
@api.response(404, "Not Found: No entry for that query in MongoDB.")
@api.response(503, "Service Unavailable: Unable to connect to mongoDB.")
class sanity_config(Resource):
    """Sanity Config endpoint"""
    @staticmethod
    def get():
        """Get Config data endpoints from MongoDB for given query."""
        request_runid = flask.request.args.get("run_id")
        json_data = {"run_id": request_runid}
        validate_inputs(request_runid, json_data)
        data = sanityapi.get_sanity_config(uri, json_data["run_id"])
        global_functions.convert_objectids(data)

        return data


@api.route("/others", doc={"description": "Get sanity run params from MongoDB."})
@api.response(200, "Success")
@api.response(400, "Bad Request: Missing parameters. Do not retry.")
@api.response(401, "Unauthorized: Wrong db_username/db_password.")
@api.response(403, "Forbidden: User does not have permission for operation.")
@api.response(404, "Not Found: No entry for that query in MongoDB.")
@api.response(503, "Service Unavailable: Unable to connect to mongoDB.")
class sanity_run_params(Resource):
    """Sanity other endpoint"""
    @staticmethod
    def get():
        """Get sanity run params from MongoDB for given query."""
        request_runid = flask.request.args.get("run_id")
        json_data = {"run_id": request_runid}
        validate_inputs(request_runid, json_data)

        results = {"write": deepcopy(schemas.config_format),
                   "read": deepcopy(schemas.config_format)}

        for obj in read_config.sanity_obj_sizes:
            value_query = {"run_ID": json_data["run_id"],
                           "Sessions": read_config.sanity_sessions, "Object_Size": obj}
            sanityapi.get_summary_params(
                uri=uri, query=value_query, metrix="Throughput", obj=obj,
                temp_read=results["read"],
                temp_write=results["write"])

        return flask.jsonify({"result": results})


@api.route("/all", doc={"description": "Get sanity performance data for all matrix from MongoDB."})
@api.response(200, "Success")
@api.response(400, "Bad Request: Missing parameters. Do not retry.")
@api.response(401, "Unauthorized: Wrong db_username/db_password.")
@api.response(403, "Forbidden: User does not have permission for operation.")
@api.response(404, "Not Found: No entry for that query in MongoDB.")
@api.response(503, "Service Unavailable: Unable to connect to mongoDB.")
class highConcurrencyData(Resource):
    """Sanity all metrix endpoint"""
    @staticmethod
    def get():
        """Get sanity all metrix data from MongoDB for given query."""
        request_runid = flask.request.args.get("run_id")
        json_data = {"run_id": request_runid}
        validate_inputs(request_runid, json_data)

        results = deepcopy(schemas.results_format)

        _, record_id = sanityapi.get_baseline_index(uri, request_runid)

        value_query = {"run_ID": json_data["run_id"],
                       "Sessions": read_config.sanity_high_conc_sessions,
                       "Object_Size": read_config.sanity_high_conc_obj_size}
        base_query = {"Config_ID": record_id,
                      "Sessions": read_config.sanity_high_conc_sessions,
                      "Object_Size": read_config.sanity_high_conc_obj_size}
        rp_status, wp_status, results['value'] = sanityapi.get_all_metrics_data(
            uri=uri, query=value_query, metrix="Throughput", obj=value_query["Object_Size"])
        rb_status, wb_status, results['baseline'] = sanityapi.get_all_metrics_data(
            uri=uri, query=base_query, metrix="Throughput", obj=value_query["Object_Size"])

        if rp_status and wp_status:
            results["difference"] = {
                key: results['value'][key] - results['baseline'].get(key, 0) for key in results['value']
            }
        else:
            results["difference"] = {
                key: "NA" for key in results['value']
            }

        if rb_status and wb_status:
            results["deviation"] = {
                key: sanityapi.calculate_deviation(
                    results['value'][key], results['baseline'].get(key, 0)) for key in results['value']
            }
        else:
            results["deviation"] = {
                key: "NA" for key in results['value']
            }

        return flask.jsonify({"result": results})
