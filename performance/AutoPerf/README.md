# autoperf-v1.1

## Pre-Requisites in order to run AutoPerf: 
1. Create and empty 'hosts' file in AutoPerf home directory (~/seagate-tools/performance/AutoPerf/)


## Example to run AutoPerf: 
$ ansible-playbook -i hosts deploy_autoperf.yml --extra-vars '{ "BENCHMARK":"s3bench_basic", "CONFIGURATION":"short", "SAMPLE":"5", "SKIPCLEANUP":"no", "KEY":"password", "nodes":{"1": "node1.loc.seagate.com", "2": "node2.loc.seagate.com"} , "clients":{"1": "client1.loc.seagate.com"}}' -v


## Example to collect only system stats(without any benchmark): 
$  ansible-playbook -i hosts deploy_autoperf.yml --extra-vars '{ "BENCHMARK":"NONE", "WAIT":"5" ,"CONFIGURATION":"short", "SAMPLE":"5", "SKIPCLEANUP":"no", "KEY":"password", "nodes":{"1": "node1.loc.seagate.com", "2": "node2.loc.seagate.com"} , "clients":{"1": "client1.loc.seagate.com"}}' -v

## Sanity check covers below tasks on client:
tasks:
1) Check 's3.seagate.com' entry is present in '/etc/hosts' file.
2) Check 's3.seagate.com' is reachable.
3) Check 'aws' package is installed.
4) Check 'awscli' is configured.


