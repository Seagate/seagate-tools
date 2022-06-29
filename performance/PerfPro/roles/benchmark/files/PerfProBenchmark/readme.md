# PerfPro Benchmark

This directory is being copied by PerfPro orchestrator and contains artefacts required to run PerfPro playbooks like perf-sanity and perf-regression. To run the various performance tests, we need the benchmarking tool and its configurations as per test scenarios. PerfPro uses S3Bench, HSBench and COSBench to run performance tests.

PerfPro manages installation, configurations and execution of these benchmarking tools. Post execution, the test results are required to be pushed to MongoDB for further processing by PerfPro Dashboard. The db_scripts consists of python scripts which pushes these test results by benchmarking tools to MongoDB mentioned in main.yml at PerfPro\\roles\\benchmark\\vars\\ directory.

To run the benchmarking tools without PerfPro orchestrator, use manual execution method as described below

## Installation

1.  Install `go` language

```txt
	yum install go
```

## Steps to run benchmark wrapper scripts

### S3Bench

1.  Go to s3bench directory
2.  Run `run_s3benchmark.sh` script as

```txt
	./run_s3benchmark.sh -nc 32,64,128 -ns 1024,2048 -s 1Mb,4Mb,128Mb
```

### HSBench

1.  Go to hsbench directory
2.  Run `run_benchmark.sh` script as

```txt
	./run_benchmark.sh -b 32,64,128 -o 1024,2048 -s 1Mb,4Mb,128Mb -t 32,64,128 -d 600
```

### COSBench

1.  Go to cosbench directory
2.  Create a file "driver-nodes-list" where you have to list out clients fqdn like below

```txt
	S3CLIENT1.example.com
	S3CLIENT2.example.com
```

3.  Installing cosbench on controller and driver nodes

```txt
	sh cosbench.sh install --controller <CONTROLLER-FQDN> --drivers driver-nodes-list
```

4.  Configuring cosbench

```txt
	sh cosbench.sh configure --controller <CONTROLLER-FQDN> --drivers driver-nodes-list
```

5.  Starting cosbench on controller and driver nodes

```txt
	sh cosbench.sh start --controller <CONTROLLER-FQDN> --drivers driver-nodes-list
```

6.  Now you can run cosbench wrapper script like

```txt
    ./s3cosbench_benchmark.sh -nc 8,16,32 -ns 1024,2048,4096 -s 1Mb,4Mb,16Mb -b 8,16,32 -w read -t 600
```

7.  To Stop cosbench service on controller and driver nodes

```txt
	sh cosbench.sh stop --controller <CONTROLLER-FQDN> --drivers driver-nodes-list
```

Reference to COSBench documentation:
<https://usermanual.wiki/Pdf/COSBenchUserGuide.1196297168.pdf>

## Other wrapper scripts

Like benchmark wrapper scripts above, there are other scripts which do one or the other feature on top of wrapper scripts
e.g.

```txt
	sanity: wrapper over s3bench which helps in running perf-sanity on mentioned s3_endpoint
	copy_oject: wrapper over s3bench which copies objects from a bucket to another
	degraded_IO: wrapper over s3bench which captures performance stats under degraded state of cluster serving s3_endpoint
```

## System_monitoring

These are the scripts which capture system stats like CPU, Memory, Disk and Network utilization from system under test during PerfPro runs and push them on mentioned MongoDB server in main.yml
