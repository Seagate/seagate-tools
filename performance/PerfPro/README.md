# How to run PerfPro
====================

## Pre-Requisites in order to run Perfpro:
1. Verify 'hosts' file is empty in "inventories/" directory (PerfPro/inventories/hosts).  
2. Update config.yml (PerfPro/roles/benchmark/vars/config.yml) with valid information of SUT and build in order to run this.

## Example how to run ansible-playbook directly
$ ansible-playbook perfpro.yml -i inventories/hosts -v

## or simply execute run.sh
$ run.sh

## For Sanity PerfPro execution run either of the following: 
$ ansible-playbook perfpro.yml -i inventories/hosts -v --extra-vars '{ "EXECUTION_TYPE" : "sanity" }'
$ run.sh sanity

## User Guide
https://seagate-systems.atlassian.net/wiki/spaces/PRIVATECOR/pages/339117894/PerfPro#User-Guide

## for detailed documentation on PerfPro, please refer
https://seagate-systems.atlassian.net/wiki/spaces/PRIVATECOR/pages/339117894/PerfPro
