# How to run PerfPro
====================

## Pre-Requisites in order to run Perfpro:
1. Verify 'hosts' file is empty in "inventories/" directory (PerfPro/inventories/hosts).  
2. Update config.yml (PerfPro/roles/benchmark/vars/config.yml) with valid information of SUT and build in order to run this.
3.  Update main.yml (PerfPro/roles/benchmark/vars/main.yml) with details related to 'MongoDB credentials', 'port', 'database' and 'db_url'.

## Example how to run ansible-playbook directly
$ ansible-playbook perfpro.yml -i inventories/hosts -v

## or simply execute run.sh
$ run.sh

## For Sanity PerfPro execution run either of the following: 
$ ansible-playbook perfpro.yml -i inventories/hosts --extra-vars '{ "EXECUTION_TYPE" : "sanity" ,"REPOSITORY":{{ "category": "motr", "repo": "cortx-motr", "branch": "k8s", "commit": "a1234b" }, { "category": "rgw", "repo": "cortx-rgw", "branch": "dev", "commit": "c5678d" }, { "category": "hare", "repo": "cortx-hare", "branch": "main", "commit": "e9876f" }},"PR_ID" : "cortx-rgw/1234" , "USER":"Username","GID" : "1234", "NODES":{"1": "node1.loc.seagate.com", "2": "node2.loc.seagate.com", "3": "node2.loc.seagate.com"} , "CLIENTS":{"1": "client1.loc.seagate.com"} , "main":{"db_server": "db.server.seagate.com", "db_port": "27017", "db_name": "sanity_db", "db_user": "db_username", "db_passwd": "db_password", "db_database": "performance_database", "db_url": "mongodb://db.hostname.seagate.com:27017/"}, "config":{"CLUSTER_PASS": "password", "END_POINTS": "s3.seagate.com" }}' -v 

NB: "NODES", "CLIENTS" and other "main" and "config" entries need to maintain the case sensitivity for dictonary keys. "REPOSITORY" list may vary in size depending upon number of Repositories used to create CI build. 

## User Guide
https://seagate-systems.atlassian.net/wiki/spaces/PRIVATECOR/pages/339117894/PerfPro#User-Guide

## for detailed documentation on PerfPro, please refer
https://seagate-systems.atlassian.net/wiki/spaces/PRIVATECOR/pages/339117894/PerfPro
