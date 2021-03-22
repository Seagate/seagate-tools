# autoperf-v1.1

## Pre-Requisites in order to run AutoPerf: 
1. Create and empty 'hosts' file in AutoPerf home directory (~/seagate-tools/performance/AutoPerf/)


## Example to run AutoPerf: 
$ ansible-playbook -i hosts deploy_autoperf.yml --extra-vars '{ "BENCHMARK":"s3bench_basic", "CONFIGURATION":"short", "SAMPLE":"5", "SKIPCLEANUP":"no", "KEY":"password", "nodes":{"1": "node1.loc.seagate.com", "2": "node2.loc.seagate.com" , "clients":{"1": "client1.loc.seagate.com"}}' -v
