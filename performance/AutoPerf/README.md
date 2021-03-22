# autoperf-v1.1

Pre-Requisits in order to run AutoPerf: 
1. Create and empty 'hosts' file in AutoPerf home directory (~/seagate-tools/performance/AutoPerf/)


Example to run AutoPerf: 
$ ansible-playbook -i hosts deploy_autoperf.yml --extra-vars '{ "BENCHMARK":"s3bench_basic", "CONFIGURATION":"short", "SAMPLE":"5", "SKIPCLEANUP":"no", "KEY":"Seagate!23", "nodes":{"1": "sm18-r19.pun.seagate.com", "2": "sm18-r19.pun.seagate.com" , "clients":{"1": "iu16-r19-client.pun.seagate.com"}}' -v
