### PerfBot

PerfBot is the tool to analyze performance run. Performance logs of different benchmarks are taken as the source. Predefined rules are applied on run logs to predict the behaviour of the run. If any violations are occured then the observations are displayed as the result at the end.

The tool is divided into three sections: **Parsers, Rules & Analyzer**.

1. Parser includes run log parser files for different benchmarking tools which converts data into a structured format and stores in the database.
2. [Rules](https://github.com/Seagate/seagate-tools/blob/main/performance/PerfBot/docs/rules.md) are the guidelines for analyzer in decision making.
3. [Analyzer](https://github.com/Seagate/seagate-tools/blob/main/performance/PerfBot/docs/analyzer.md) concludes the run results based on the provided rules.

![](docs/architecture.png)
