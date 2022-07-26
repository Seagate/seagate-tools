# How to run PerfPro

This document explains how to use PerfPro to run perf-regression OR perf-sanity ansible playbook.

## Pre-Requisites

1.  Verify 'hosts' file is empty in "inventories/" directory (~/seagate-tools/performance/PerfPro/inventories/hosts).  
2.  Update config.yml at (~/seagate-tools/performance/PerfPro/roles/benchmark/vars/config.yml) with valid information against all the keys.
3.  Update main.yml at (~/seagate-tools/performance/PerfPro/roles/benchmark/vars/main.yml) with details related to 'MongoDB credentials', 'port', 'database' and 'db_url'.

Notes:
1.  Examples for config.yml and main.yml can be found at [example-config.yml](https://github.com/Seagate/seagate-tools/blob/main/performance/PerfPro/docs/example-config.yml) and [example-main.yml](https://github.com/Seagate/seagate-tools/blob/main/performance/PerfPro/docs/example-main.yml).
2.  It is recommended to remove lines which do not have any field updated.   
3.  "NODES", "CLIENTS" and other entries in main.yml and config.yml need to maintain the case sensitivity.

## Run perf-regression playbook

Once the config.yml and main.yml files are update with required information, run  following command from PerfPro orchestrator.
```txt
ansible-playbook perfpro.yml -i inventories/hosts -v` or simply execute `$ run.sh
```

## Run perf-sanity playbook

To run PerfPro as perf-sanity ansible playbook, run following command from PerfPro orchestrator. Following command supersedes values taken from config.yml and main.yml.
```txt
ansible-playbook perfpro.yml -i inventories/hosts --extra-vars '{ "EXECUTION_TYPE" : "sanity" ,"REPOSITORY":[{ "category": "motr", "repo": "cortx-motr", "branch": "k8s", "commit": "a1234b" }, { "category": "rgw", "repo": "cortx-rgw", "branch": "dev", "commit": "c5678d" }, { "category": "hare", "repo": "cortx-hare", "branch": "main", "commit": "e9876f" }],"PR_ID" : "cortx-rgw/1234" , "USER":"Username","GID" : "1234", "NODES":{"1": "node1.loc.seagate.com", "2": "node2.loc.seagate.com", "3": "node2.loc.seagate.com"} , "CLIENTS":{"1": "client1.loc.seagate.com"} , "main":{"db_server": "db.server.seagate.com", "db_port": "27017", "db_name": "sanity_db", "db_user": "db_username", "db_passwd": "db_password", "db_database": "performance_database", "db_url": "mongodb://db.hostname.seagate.com:27017/"}, "config":{"CLUSTER_PASS": "password", "END_POINTS": "s3.seagate.com", "CUSTOM": "VM" }}' -v
```

Notes:

1.  "NODES", "CLIENTS" and other entries in "main" and "config" dictionaries need to maintain the case sensitivity.
2.  "REPOSITORY" list may vary in size depending upon number of repositories used to create build.

## [User Guide](https://github.com/Seagate/seagate-tools/blob/main/performance/PerfPro/docs/user-guide.md)
