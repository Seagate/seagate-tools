# PerfPro User Guide

## Introduction

PerfPro tool is an End-to-End Performance Test Harness which starts at performance tests on mentioned S3 endpoint and ends at updating Performance stats onto MongoDB which further enables statistical and comparative analysis on Dashboard.

-   It is based on Ansible framework
-   It does cluster nodes' re-image, install pre-requisite and deploys build
-   It configures CSM Admin and S3 Account
-   It runs benchmarking tools with pre-defined parameters
-   It collects the S3 performance data like throughput, latency, IOPS, ttfb, etc
-   It pushes benchmark's test data to MongoDB for reports and comparison
-   It has flexibility on whether to consider re-image OR skip it and do just build deployment
-   Establishes password-less authentication to S3 Server & Client once triggered
-   Validates if the benchmark tools are not deployed, it will go ahead and deploy it

## Capabilities

-   Able to execute and differentiate between LR-R1 and LR-R2
-   It can skip re-image of nodes and just go ahead with build deployment followed by benchmark runs
-   Can be run on special setups like with PODs, with SSDs with mentioning a field "Custom" in config.yml to differentiate between performance data
-   Works on any branch of build i.e. Dev, Custom, Release, Stable OR Main
-   Optional parameter to re-write DB records in case user want to run same test on same system with same build
-   Multiple iterations of runs to get repetitive performance stats
-   Captures and saves ansible logs for future references

## Limitations

Test parameters are fixed, meaning user can not change the test parameters on the fly. User needs to go through code to change the test parameters.

## Pre-requisites

1.   Running MongoDB instance to push performance data
2.   yum packages

```txt
    ansible
    pip
```
3.   pip packages

```txt
    PyYaml
    requests
    jsonschema
    pymongo
    paramiko
```

## System Requirements

```txt
    CentOS-7.8, x86_64, 8 GB Ram, 2 CPUs, 50 GB free space
```

## Installation guide

1.   Clone the repo from source code location mentioned above

```txt
    git clone https://github.com/Seagate/seagate-tools/
```

2.   Install "ansible", "pip3" and other required packages mentioned in pre-requisites section

```txt
    yum install ansible
    yum install python3-pip
    yum install python-pip
    pip install PyYaml
    pip install requests
    pip3 install jsonschema
    pip3 install pymongo
    pip3 install paramiko
```

3.   Make sure empty hosts file is present at

```txt
    ~/seagate-tools/performance/PerfPro/inventories/hosts"
```

4.   Update "config.yml" and "main.yml" with required parameters present at

```txt
    ~/seagate-tools/performance/PerfPro/roles/benchmark/vars/
```
