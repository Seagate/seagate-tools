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
        "Object_Size": "",
        "Buckets": "",
        "Objects": "",
        "Sessions": ""
    }


def get_system_monitoring_config_set():
    return {**get_s3bench_primary_set(),
            **{
        'cluster_pass': "",
        'solution': "",
        'end_points': "",
        'system_stats': "",
        'overwrite': "",
        'degarded_IO': "",
        'copy_object': "",
        'nfs_server': "",
        'nfs_export': "",
        'nfs_mount_point': "",
        'nfs_folder': ""
    }
    }


def set_system_monitoring_config_set(self):
    primary_set = get_system_monitoring_config_set()
    primary_set["Build"] = self.main_config['build']['generation_type']
    primary_set["Version"] = self.main_config['build']['version']
    primary_set["Branch"] = self.main_config['build']['branch']
    primary_set["OS"] = self.main_config['build']['os']
    primary_set["Count_of_Servers"] = len(self.main_config["cluster"]["nodes"])
    primary_set["Count_of_Clients"] = len(
        self.main_config["cluster"]["clients"])
    primary_set["Percentage_full"] = self.config["cluster"]["fill_percent"]
    primary_set["Custom"] = self.main_config["cluster"]["custom_label"]
    primary_set["cluster_pass"] = self.main_config['cluster_pass']
    primary_set["solution"] = self.main_config['solution']
    primary_set["end_points"] = self.main_config['end_points']
    primary_set["systems_stats"] = self.main_config['system_stats']
    primary_set["overwrite"] = self.main_config['overwrite']
    primary_set["degarded_IO"] = self.main_config['degarded_IO']
    primary_set["copy_object"] = self.main_config['copy_object']
    primary_set["nfs_server"] = self.main_config['nfs_server']
    primary_set["nfs_export"] = self.main_config['nfs_export']
    primary_set["nfs_mount_point"] = self.main_config['nfs_mount_point']
    primary_set["nfs_folder"] = self.main_config['nfs_folder']

    return primary_set


def get_system_monitoring_insertion_set(self):
    return{
        "Object_Size": "",
        "Device": "",
        "Timestamp": "",
        "Time": "",
        "HOST": "",
        "Config_ID": ""
    }


def set_system_monitoring_insertion_set(self, value):
    insertion_set = get_system_monitoring_insertion_set()
    insertion_set["Object_Size"]: self.Object_Size,
    insertion_set["Device"]: self.device,
    insertion_set["Timestamp"]: datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    insertion_set["Time"]: value
    insertion_set["HOST"]: socket.gethostname(),
    insertion_set["Config_ID"]: self.Config_ID

    return insertion_set


def get_system_monitoring_primary_set(self):
    return{
        "Name": "",
        "Build": "",
        "Custom": ""
    }


def set_system_monitoring_primary_set(self):
    primary_set = get_system_monitoring_primary_set()
    primary_set["Name"]: self.Name
    primary_set["Build"]: str(self.build)
    primary_set["Custom"]: str(self.main_config['custom_label']).upper()

    return primary_set
