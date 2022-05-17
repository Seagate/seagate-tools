
def get_sanity_schema():
    return {
        "motr_repository": "",
        "rgw_repository": "",
        "hare_repository": "",
        "other_repos": [],
        "PR_ID": ""
    }


def get_primary_set():
    return {
        "Name": "",
        "Config_ID": "",
        "run_ID": ""
    }


def get_run_config_set():
    return {
        "HOST": "",
        "Log_File": "",
        "Timestamp": "",
        "Operation": "",
        "Object_Size": "",
        "Buckets": 0,
        "Objects": "",
        "Sessions": ""
    }


def get_performance_results_set():
    return {
        "Throughput": 0,
        "IOPS": 0,
        "Latency": {},
        "TTFB": {},
        "Total_Errors": 0,
        "Total_Ops": 0,
        "Run_State": ""
    }
