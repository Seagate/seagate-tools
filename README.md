[![license](https://img.shields.io/badge/License-AGPL%203.0-blue.svg)](https://github.com/Seagate/seagate-tools/blob/main/LICENSE.txt)
[![CORTX inclusive words scan](https://github.com/Seagate/seagate-tools/actions/workflows/alex_reviewdog.yml/badge.svg)](https://github.com/Seagate/seagate-tools/actions/workflows/alex_reviewdog.yml)

# Disclaimer: This project is not maintained anymore
# Seagate-tools

Seagate-tools is a common repository of tools developed in-house by the Seagate Engineers for testing object storage. It consists of majorly Performance benchmarking, profiling, and analytic tools along with multi-utility dashboards.

## Overview

> Dashboards section carries the source code of web-based user interfaces such as Cortx-Companion, Perf-Rest, and SuperPerf. This directory consists of sub-directories for:

### Cortx-Companion

[Cortx-companion](https://github.com/Seagate/seagate-tools/blob/main/dashboards/cortx-companion/README.md) includes Performance tabs that summarize Benchmark results of all Performance testbed, H/W, custom runs with a wide range of filters. Moreover, the Performance graphs tab facilitates the comparison of any run data with any previous Perf results. Along with, QA tabs that brief executive and engineering summary of a build tested by CFT.

### Perf-Rest

[Perf-Rest](https://github.com/Seagate/seagate-tools/blob/main/dashboards/perf-rest/README.md) is a REST API providing Performance endpoints for accessing performance metrics, Sanity Data, and endpoints needed for SuperPerf.

### SuperPerf

[SuperPerf](https://github.com/Seagate/seagate-tools/blob/main/dashboards/superperf/README.md) is a superset of all performance tools. It consists of the source code of Perf-Sanity, to begin with. Perf-Sanity is a Jenkins-based Perf CI/CD that captures performance results for various kinds of builds.

> Performance section holds source code for Performance benchmarking and I/O profiling. It includes:

### PerfLine

[PerfLine](https://github.com/Seagate/seagate-tools/blob/main/performance/PerfLine/README.md) is primarily a cortx Profiler. It has extended capabilities of running different benchmarks and microbenchmarks and other custom workloads in a multi-user shared environment.

There are three parts:

-   wrapper - Executables including report generator, statistic gather scripts
-   WebUI - Web server-based PerfLine UI for interacting with PerfLine
-   ansible-playbook - Ansible-based PerfLine Installation

### PerfPro

[PerfPro](https://github.com/Seagate/seagate-tools/blob/main/performance/PerfPro/README.md) is an ansible orchestrated End-to-End Performance test harness that starts with configuring clients and ends at updating Performance stats into MongoDB that further enables statistical and comparative analysis. It validates and installs the benchmark tools if not present on the client node. Moreover, it runs Performance benchmarks with pre-defined parameters by collecting the S3 performance metrics viz throughput, latency, IOPS, TTFB, etc.
