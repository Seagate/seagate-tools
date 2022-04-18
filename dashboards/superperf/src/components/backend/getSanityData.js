import axios from 'axios';

const host_url = "http://cftic2.pun.seagate.com:5050/sanity/";

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
        "deviation": "Deviation (%)"
    };
    if(key in mapper) {
        return mapper[key];
    }
    else {
        return "NA";
    }
}


export function get_header_of_sanity(data){
    var keys = Object.keys(data['read']["baseline"]);
    var header = [{ text: "Index", value: "index" }];
    for(var key in keys) {
        header.push(
            { "text": split_object_size(keys[key]), "value": keys[key]}
        )
    }
    return header;
}
