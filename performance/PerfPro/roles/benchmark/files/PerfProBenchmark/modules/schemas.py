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
        "Objects": 0,
        "Sessions": 0
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
        "Name": "",
        "Build": "",
        "Version": "",
        "Branch": "",
        "OS": "",
        "Count_of_Servers": 0,
        "Count_of_Clients": 0,
        "Percentage_full": 0,
        "Custom": "",
        "Operation": "",
        "Object_Size": "",
        "Buckets": 0,
        "Objects": 0,
        "Sessions": 0
    }


def set_s3bench_primary_set(self, operation):
    primary_set = get_sanity_primary_set()
    primary_set["Name"] = self.bench
    primary_set["Build"] = self.Build
    primary_set["Version"] = self.Version
    primary_set["Branch"] = self.Branch
    primary_set["OS"] = self.OS
    primary_set["Count_of_Servers"] = len(self.config["cluster"]["nodes"])
    primary_set["Count_of_Clients"] = len(self.config["cluster"]["clients"])
    primary_set["Percentage_full"] = self.config["cluster"]["fill_percent"]
    primary_set["Custom"] = self.config["cluster"]["custom_label"]
    primary_set["Object_Size"] = self.object_size
    primary_set["Buckets"] = self.buckets
    primary_set["Objects"] = self.objects
    primary_set["Sessions"] = self.sessions
    primary_set["Operation"] = operation

    return primary_set


def get_copy_object_primary_set():
   return {**get_s3bench_primary_set(),
            **{
            "Additional_op": "",
            }
            }


def set_copy_object_set(self,operation):
    primary_set = get_s3bench_primary_set(operation)
    primary_set["Name"] = self.bench
    primary_set["Build"] = self.Build
    primary_set["Version"] = self.Version
    primary_set["Branch"] = self.Branch
    primary_set["OS"] = self.OS
    primary_set["Count_of_Servers"] = len(self.config["cluster"]["nodes"])
    primary_set["Count_of_Clients"] = len(self.config["cluster"]["clients"])
    primary_set["Percentage_full"] = self.config["cluster"]["fill_percent"]
    primary_set["Custom"] = self.config["cluster"]["custom_label"]
    primary_set["Object_Size"] = self.object_size
    primary_set["Buckets"] = self.buckets
    primary_set["Objects"] = self.objects
    primary_set["Sessions"] = self.sessions
    primary_set["Operation"] = operation
    primary_set["Additional_op"] = self.additional_op

    return primary_set


def get_copy_object_insertion_schema(): 
    return {**get_copy_object_primary_set(),
            **{
            "Timestamp": "",
            "Host": "",
            "Log_File": ""
            },
            **get_performance_results_schema()
            }


def get_s3bench_insertion_schema():
    return {**get_s3bench_primary_set(),
            **{
            "Timestamp": "",
            "Host": "",
            "Log_File": ""
            },
            **get_performance_results_schema()
            }


def set_s3bench_insertion_set(self, primary_set, file):
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

#till here

def get_benchmark_config_primary_set():
    return {
        'NODES': [],
        'CLIENTS' : [],
        'BUILD_INFO': "",
        'BUILD_URL': "",
        'BUILD': "",
        'VERSION': "",
        'BRANCH': "",
        'OS': "",
        'EXECUTION_TYPE': "",
        'END_POINTS' : "",
        'PC_FULL' : 0,
        'CUSTOM' : ""
        }


def set_benchmark_config_primary_set(obj):
    config_set = get_benchmark_config_set()
    config_set["NODES"] = obj.config["Cluster"]["nodes"]
    config_set["CLIENTS"] = obj.config["Cluster"]["clients"]
    config_set["BUILD_INFO"] = obj.config["build"]["generation_type"]
    config_set["BUILD_URL"] = obj.config["build"]["url"]
    config_set["BUILD"] = obj.config["build"]["number"]
    config_set["VERSION"] = obj.config["build"]["version"]
    config_set["BRANCH"] = obj.config["build"]["branch"]
    config_set["OS"] = obj.config["cluster"]["url"]
    config_set["EXECUTION_TYPE"] = obj.config["execution_type"]
    config_set["END_POINTS"] = obj.config["cluster"]["endpoint"]
    config_set["PC_FULL"] = obj.config["cluster"]["fill_percent"]
    config_set["CUSTOM"] = obj.config["custom_label"]

    return config_set    


def get_bench_config_insertion_set():
    return {
        **get_s3bench_primary_set(),
        **{
        'CLUSTER_PASS': "",
        "SOLUTION": "",
        'SYSTEM_STATS' : False,
        'OVERWRITE' : False,
        'DEGRADED_IO' : False,
        'COPY_OBJECT' : False,
        'NFS_SERVER': "",
        'NFS_EXPORT' : "",
        'NFS_MOUNT_POINT' : "",
        'NFS_FOLDER' : ""
        }
    }


def set_config_insertion_set(obj, primary_set):
    config_set = get_benchmark_config_set()
    config_set.update(primary_set)
    config_set["CLUSTER_PASS"] = obj.config["cluster"]["password"]
    config_set["SOLUTION"] = obj.config["solution"]
    config_set["BUILD_URL"] = obj.config["build"]["url"]
    config_set["OVERWRITE"] = obj.config["run"]["overwrite"]
    config_set["SYSTEM_STATS"] = obj.config["run"]["system_stats"]
    config_set["DEGRADED_IO"] = obj.config["run"]["degraded_io"]
    config_set["COPY_OBJECT"] = obj.config["run"]["copy_object"]
    config_set["NFS_SERVER"] = obj.config["archive"]["server"]
    config_set["NFS_EXPORT"] = obj.config["archive"]["share"]
    config_set["NFS_MOUNT_POINT"] = obj.config["archive"]["mountpoint"]
    config_set["NFS_FOLDER"] = obj.config["archive"]["target_dir"]

    return config_set
