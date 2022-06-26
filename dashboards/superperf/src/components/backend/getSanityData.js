// Copyright (c) 2022 Seagate Technology LLC and/or its Affiliates
//  
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU Affero General Public License as published
// by the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
// GNU Affero General Public License for more details.
// You should have received a copy of the GNU Affero General Public License
// along with this program. If not, see <https://www.gnu.org/licenses/>.
//  
// For any questions about this software or licensing,
// please email opensource@seagate.com or cortx-questions@seagate.com.
//  
// -*- coding: utf-8 -*-
// Backend functions for fetching Sanity related data

import axios from "axios";

export function fetchDataFromResponse(run_id, endpoint) {
    const params = new URLSearchParams([["run_id", run_id]]);
    return axios.get(`${process.env.VUE_APP_REST_URI}${endpoint}`,
        { params });
}


function getSanityTableMapper(key) {
    const mapper = {
        "baseline": "Baseline",
        "value": "Value",
        "difference": "Difference",
        "deviation": "Deviation (%)",
        "objects": "Objects",
        "total_ops": "Total Operations",
        "total_errors": "Total Errors"
    };
    if (key in mapper) {
        return mapper[key];
    }
    else {
        return "NA";
    }
}


export function getDataForSanityTables(rawData) {
    var results = [];
    for (var key in rawData) {
        if (Object.prototype.hasOwnProperty.call(rawData, key)) {
            results.push(
                Object.assign({}, { "index": getSanityTableMapper(key) }, rawData[key]));
        }
    }
    return results;
}


export function splitObjectSize(obj) {
    return obj.slice(0, -2).concat(" ", obj.slice(-2));
}


export function getHeaderOfSanityfromObjects(data) {
    let keys = [];
    let header = [{ text: "Index", value: "index" }];

    keys = Object.keys(data["read"]["objects"]).reverse();
    for (let [, value] of Object.entries(keys)) {
        header.push(
            { "text": splitObjectSize(value), value }
        );
    }

    return header;
}


export function getHeaderOfSanityfromBaseline(data) {
    let keys = [];
    let header = [{ text: "Index", value: "index" }];

    keys = Object.keys(data["read"]["baseline"]).reverse();
    for (let [, value] of Object.entries(keys)) {
        header.push(
            { "text": splitObjectSize(value), value }
        );
    }

    return header;
}


export function getHeaderOfSanityforMaxSessions(data) {
    let keys = [];
    let header = [{ text: "Index", value: "index" }];

    keys = Object.keys(data["baseline"]);
    for (let [, value] of Object.entries(keys)) {
        header.push(
            { "text": value, value }
        );
    }

    return header;
}
