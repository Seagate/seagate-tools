import axios from "axios";

let hostUrl = "http://127.0.0.1:5050/sanity/";

export function fetchDataFromResponse(run_id, endpoint) {
    const params = new URLSearchParams([["run_id", run_id]]);
    return axios.get(`${hostUrl}${endpoint}`,
    { params });
}


export function getDataForSanityTables(rawData) {
    var results = [];
    for(var key in rawData) {
        if (Object.prototype.hasOwnProperty.call(rawData, key)) {
            results.push(
                Object.assign({}, {"index": getSanityTableMapper(key)}, rawData[key]));
        }
    }
    return results;
}


export function splitObjectSize(obj) {
    return obj.slice(0, -2).concat(" ", obj.slice(-2));
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
    if(key in mapper) {
        return mapper[key];
    }
    else {
        return "NA";
    }
}


export function getHeaderOfSanity(data, sub_key){
    var keys = Object.keys(data["read"][sub_key]).reverse();
    var header = [{ text: "Index", value: "index" }];
    for(var key in keys) {
        if (Object.prototype.hasOwnProperty.call(keys, key)) {
            header.push(
                { "text": splitObjectSize(keys[key]), "value": keys[key]}
            );
        }
    }
    return header;
}
