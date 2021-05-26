## Rules

In this section rules are explained. Rules are the instruction set for PerfBot. Those are guidelines for analyzing the data.

### Rule Design

This section is divided in two parts data and logs rules. Data rules are the rules for performance metrics applied on the structured data from parsers. Whereas, logs rules are the rules related to the errors occured during the performance run. Rulebook includes rulebook version and rules.These rules are stored in a rulebook.

#### Rulebook Design

Rulebook has a specific version. When new rule is added or a change is made in current rules then the version upgrades. Date of update is also mentioned. Data and logs are the sections for performance and logs related rules respectively. It is a list of dictionaries consisting each rule. Rulebook has the following schema:

```txt
{
    "version": 1,
    "date_of_update": "DD/MM/YYYY HH:MM:SS",
    "data": [
       {"rule": 1 ...},
       {"rule": 2 ...},
       ...
    ],
    "logs": [
       {"rule": 1 ...},
       {"rule": 2 ...},
       ...
    ]
}
```

Now each rule is a dictionary of some parameters defining the rule. Schema for a rule is as follows:

```json
{
    "rule": int,
    "status": string,
    "label": string,
    "description": string,
    "custom_query": string,
    "query": {
        "filter": {
            "metric": string,
            "operator": string,
            "threshold": string/int/float
        },
        "grouping": {
            "constraint": string,
            "interval": string/int/float
        }
    },
    "output": string
}
```

Description of each placeholder:

* rule: Serial number of the rule
* status: Inclusion of rule in current version of rule
* label: Summary of the impact of defined rule
* description: Detailed illustration of the rule
* custom_query: An option for user to define their own influxDB query. If not NA it is used as it is for analyzer and query section is neglected.
* query: An alternative to custom_query where query is designed using certain options
* filter: filter which part of WHERE clause; set of subjects for the rule. Filter has 2 schema
  * metric: Performance metric(metrices) for evaluation
  * operator:  Comparison operator
  * threshold: threshold with which you have to compare provided metric
  * Instead of metric and threshold it is 'keyword' key for logs based rules which indicates which error related keyword to search for.
* grouping: Approach to select data is certain pattern
* constraint: type of grouping to collect the data points for query
* interval: Range of the groups
* output: Indicator of application of rule gives any results or not

#### Example rule

```json
{
    "rule": 1,
    "status": "ON",
    "label": "IO HALTED",
    "description": "If there is no IO for 10 seconds consecutively, then the run is classified as bad.",
    "custom_query": "NA",
    "query": {
        "filter": {
            "metric": "iops",
            "operator": "<=",
            "threshold": "0"
        },
        "grouping": {
            "constraint": "consecutive",
            "interval": "15 sec"
        }
    },
    "output": "no"
}
```

### How to write a rule?

1. Open the rulebook and decide which rule you are going to add.
2. Inside logs or data section append a dictionary with following rule number.
3. Field "status" has two options ON/OFF.
4. Fill in label and description.
5. If you have a complete influxDB query, write it with "select, from and where clause". If not mention "NA".
6. metric have 3 options: "iops" / "throughput" / "latency".
7. operator can be from = / != / > / < / =~ or any regex operator supported by influxDB and go lang.
8. threshold can be single integer/float or a time with space seperated apporpriate units of "s" or "sec" for seconds, "ms" for milliseconds etc. e.g. "10", "11.50", "5 s", "5000 ms", etc.
9. constraint is any keyword supported by perfBot. Current available keywords are: "consecutive", "any".
10. keyword, in case of logs rules, can be any keyword paired with corresponding regex operator for match case and match word.
11. In case of not aware of regex oeprator, "match_case" and "match_found" as an operator placeholder are supported for logs rules.
12. interval has same rule as threshold.
13. output is "no" or "yes" based on the expectation of results of the query.
14. One can provide comma seperated metric, keyword to look for more than one at a time.

the rule is ready!
