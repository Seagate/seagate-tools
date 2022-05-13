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
$ ansible-playbook perfpro.yml -i inventories/hosts --extra-vars '{ "EXECUTION_TYPE" : "sanity" ,"REPOSITORY":{"motr":"cortx-motr","rgw":"cortx-rgw"} , "COMMIT_ID": { "main" : "d1234c" , "dev" : "a5678b"},"PR_ID" : "cortx-rgw/1234" , "USER":"Username","GID" : "1234" }' -v

## User Guide
https://seagate-systems.atlassian.net/wiki/spaces/PRIVATECOR/pages/339117894/PerfPro#User-Guide

## for detailed documentation on PerfPro, please refer
https://seagate-systems.atlassian.net/wiki/spaces/PRIVATECOR/pages/339117894/PerfPro
