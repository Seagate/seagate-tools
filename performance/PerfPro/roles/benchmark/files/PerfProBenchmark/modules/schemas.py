# sanity schemas


def get_sanity_details_schema():
    return {
        "motr_repository": "",
        "rgw_repository": "",
        "hare_repository": "",
        "other_repos": [],
        "PR_ID": ""
    }


def get_sanity_config_schema():
    return {
        "User": "",
        "GID": "",
        "run_ID": "",
        "Nodes": [],
        "Nodes_Count": 0,
        "Clients": [],
        "Clients_Count": 0,
        "Cluster_Fill": 0,
        "Custom_Label": "NA",
        "Baseline": -1,
        "Comment": "NA"
    }


def get_sanity_primary_set():
    return {
        "Tool": "",
        "Config_ID": "",
        "run_ID": "",
        "Operation": "",
        "Object_Size": "",
        "Buckets": 0,
        "Objects": "",
        "Sessions": ""
    }


def set_sanity_primary_set(self, operation):
    primary_set = get_sanity_primary_set()
    primary_set["Tool"] = self.bench
    primary_set["Config_ID"] = self.config_id
    primary_set["run_ID"] = self.run_id
    primary_set["Object_Size"] = self.object_size
    primary_set["Buckets"] = self.buckets
    primary_set["Objects"] = self.objects
    primary_set["Sessions"] = self.sessions
    primary_set["Operation"] = operation

    return primary_set


def get_sanity_results_schema():
    return {**get_sanity_primary_set(),
            **{
            "Timestamp": "",
            "Host": "",
            "Log_File": ""
            },
            **get_performance_results_schema()
            }


def set_sanity_results_schema(self, primary_set, file):
    insertion_set = get_sanity_results_schema()
    insertion_set.update(primary_set)
    insertion_set["Timestamp"] = self.timestamp
    insertion_set["Host"] = self.host
    insertion_set["Log_File"] = file
    insertion_set["Throughput"] = self.throughput
    insertion_set["IOPS"] = self.iops
    insertion_set["Latency"] = self.latency
    insertion_set["TTFB"] = self.ttfb
    insertion_set["Total_Errors"] = self.total_errors
    insertion_set["Total_Ops"] = self.total_ops
    insertion_set["Run_State"] = self.run_state

    return insertion_set


def get_performance_results_schema():
    return {
        "Throughput": 0,
        "IOPS": 0,
        "Latency": {},
        "TTFB": {},
        "Total_Errors": 0,
        "Total_Ops": 0,
        "Run_State": ""
    }


def get_s3bench_primary_set():
    return {
        "Build": "",
        "Version": "",
        "Branch": "",
        "OS": "",
        "Count_of_Servers": 0,
        "Count_of_Clients": 0,
        "Percentage_full": 0,
        "Custom": ""
    }

def get_performance_config_set():
    return{
        "Operation": "",
        "Object_Size" : "",
        "Buckets" : "",
        "Objects" : "",
        "Sessions" : ""
    }

