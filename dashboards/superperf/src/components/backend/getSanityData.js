import axios from 'axios';

let host_url = "http://10.230.244.46:5050//sanity/";

export function fetch_data_from_respose(run_id, endpoint) {
    const params = new URLSearchParams([['run_id', run_id]]);
    return axios.get(`${host_url}${endpoint}`,
    { params })
}


export function get_data_for_sanity_tables(raw_data) {
    var results = [];
    for(var key in raw_data) {
        results.push(Object.assign({}, {"index": get_table_mapper_of_sanity(key)}, raw_data[key]));
    }
    return results;
}


export function split_object_size(obj) {
    return obj.slice(0, -2).concat(" ", obj.slice(-2))
}


function get_table_mapper_of_sanity(key) {
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


export function get_header_of_sanity(data, sub_key){
    var keys = Object.keys(data['read'][sub_key]).reverse();
    var header = [{ text: "Index", value: "index" }];
    for(var key in keys) {
        header.push(
            { "text": split_object_size(keys[key]), "value": keys[key]}
        )
    }
    return header;
}
