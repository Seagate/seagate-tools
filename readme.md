[![Codacy Badge](https://app.codacy.com/project/badge/Grade/587e3b6c6a214ee3a57cc007d8f97f42)](https://www.codacy.com?utm_source=github.com&utm_medium=referral&utm_content=Seagate/seagate-tools&utm_campaign=Badge_Grade)
[![license](https://img.shields.io/badge/License-AGPL%203.0-blue.svg)](https://github.com/Seagate/seagate-tools/blob/main/LICENSE.txt)
[![CORTX inclusive words scan](https://github.com/Seagate/seagate-tools/actions/workflows/alex_reviewdog.yml/badge.svg)](https://github.com/Seagate/seagate-tools/actions/workflows/alex_reviewdog.yml)

# Seagate-tools

Seagate-tools is a common repository of the tools developed inhouse by the Seagate Engineers for testing object storage. It consists majorly Performance benchmarking, profiling and analytic tools along with multi-utility dashbaords.

## Overview

> Dashboards section carries the source code of web based user interfaces such as Cortx-Companion, Perf-Rest and SuperPerf. This directory consists sub-directories for:

### Cortx-Companion

[Cortx-companion](https://github.com/Seagate/seagate-tools/blob/main/dashboards/cortx-companion/readme.md) includes Performance tabs that summarizes Benchmark results of all Performance testbed, H/W, custom runs with a wide range of filters. Moreover, Performance graphs tab facilitates comparison of any run data with any previous Perf results. Alongwith, QA tabs that briefs executive and engineering summary of a build executed by CFT.

### Perf-Rest

[Perf-Rest](https://github.com/Seagate/seagate-tools/blob/main/dashboards/perf-rest/readme.md) is a REST API providing Performance endpoints for accessing performance metrics, Sanity Data and endpoints needed for SuperPerf.

### SuperPerf

[SuperPerf](https://github.com/Seagate/seagate-tools/blob/main/dashboards/superperf/readme.md) is a superset of all performance tools. It consists of the source code of Perf-Sanity to begin with. Perf-Sanity is a jenkins based Perf CI/CD that captures performance results for various kinds of builds.

> Performance section holds source code for Performance benchmarking and I/O profiling. It includes:

### PerfLine

[PerfLine](https://github.com/Seagate/seagate-tools/blob/main/performance/PerfLine/readme.md) is primarily a cortx Profiler. It has extended capabilities of running different benchmarks and microbenchmarks and other custom workloads in multi-user shared environment.

There are three parts:

-   wrapper - Executables including report generator, statistic gather scripts
-   webui - Web server based PerfLine UI for interacting with PerfLine
-   ansible playbook - Ansible based PerfLine Installation

### PerfPro

[PerfPro](https://github.com/Seagate/seagate-tools/blob/main/performance/PerfPro/readme.md) is an ansible orchestrated End-to-End Performance test harness that starts with configuring clients and ends at updating Performance stats into MongoDB that further enables statistical and comparative analysis. It validates and installs the benchmark tools if not present on the client node. Moreover, it runs Performance benchmarks with pre-defined parameters by collecting the S3 performance metrics viz throughput, latency, IOPS, TTFB, etc.
