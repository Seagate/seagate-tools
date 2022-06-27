# Performance

This directory carries the source code for all the tools

-   PerfBot - Heuristic analytics tool to identify quality of performance runs
-   PerfLine - Tool for i/o profiling
-   PerfPro - Tool for running performance tests

## PerfBot

-   Heuristic analytics tool to identify quality of performance runs

## PerfLine

PerfLine is primarily a cortx Profiler. It has extended capabilities of running different benchmarks and microbenchmarks and other custom workloads in multi-user shared environment.

It consists of three modules:

-   wrapper - Executables including report generator, statistic gather scripts
-   webui - Web server based PerfLine UI for interacting with PerfLine
-   ansible playbook - Ansible based PerfLine Installation.

## PerfPro

PerfPro tool is an End-to-End Performance Test Harness; workflow of which starts at re-imaging of Cortx nodes and ends at updating Performance stats onto MongoDB which further enables statistical and comparative analysis using graphical user interface (GUI).

-   It is based on Ansible framework
-   Validates and installs the benchmark tools if not present on client node
-   It runs benchmarking tools with pre-defined parameters
-   It collects the S3 performance data like throughput, latency, IOPS, ttfb, etc
-   It pushes benchmark's test data to MongoDB for reports and comparison
