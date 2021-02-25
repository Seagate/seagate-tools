# PerfPro

## Introduction
```
This directory contains 2 sub directories for deployment and benchmarking tools.
1.  PerfProBenchmark
      addconfiguration.py
      collect_logs.py
      cosbench
      hsbench
      README.md
      s3bench_meta
      S3UserCreation
      support_bundle_generate.py
      system_monitoring

2.  perfPro-deployment
      ansible.cfg
      inventories
      perfpro_deploy.yml
      roles
```
## perfPro-deployment:
```
It is a directory on ansible framework that contains artifacts which enable user to aciheve following things in sequence.

01. Starts capturing ansible.log via a role. This log file is copied on NFS location post run is completed.
02. Re-image of the CORTX cluster nodes through RedHat Satellite
03. Installation of CORTX pre-requisites packages required for CORTX-Provisioner
04. CORTX build deployment using CORTX-Provisioner's auto_deploy method
05. CSM Admin user creation (Login: admin / Password: Seagate@1)
06. S3account creation (Login: S3account / Password: Seagate@1)
07. Copying credentials from above step to ~/.aws/credentials file on mentioned client machine
08. Triggering of benchmarks with S3Bench, HSBench and COSBench
09. Pushing benchmark test results to MongoDB hosted on CFT-IC1/2 for CFT Dashboard
10. Pushing benchmark test logs to shared network storage
11. Collecting and pushing CORTX support bundle to shared network storage
12. Copying ansible.log with appending timestamp to its name at end and keeping on NFS location where other test artifacts are kept.
```
## Installation


Install required packages in activated virtual environment.
```

pip install PyYAML==5.3.1
pip install requests==2.24.0
pip install jsonschema==3.2.0
pip3 install pymongo==3.11.0

```

## Running Scripts
```
For inserting all s3bench log file data into MongoDb Database

python3 s3bench_DBupdate.py [dir path] [main.yml path] [config.yml path]
```
```
For inserting all cosbench csv file data into MongoDb Database

python3 cosbench_DBupdate.py [dir path] [main.yml path] [config.yml path]
```
```
For inserting all hsbench json file data into MongoDb Database

python3 hsbench_DBupdate.py [dir path] [main.yml path] [config.yml path]
```
```
For inserting Syatem data into MongoDb Database

python3 systemreport.py [timestamp][benchmark][main.yml path]
```
```
For inserting configuration data into MongoDb Database

python3 addconfiguration.py [main.yml path][config.yml path]
```
```
For creating S3 user with predefined credentials
it will create csm admin if not present

python3 main_createusers.py
```
