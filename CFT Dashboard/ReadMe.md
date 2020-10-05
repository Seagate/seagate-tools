# CORTX CFT Dashboard
This is a web-based application tool for the data generalization, the data representation and the data analysis. 
The datapoints are the outcomes of CFT and Performance tests harness and regression at Seagate.

## Layout
The application is devided into 4 major sections, namely:
- Executive report: The summary of the tests harness.
- Engineer's report: The details staitstics of the tests harness.
- Test execution-wise Defect list: A tool to get all the defects / bugs occured during test executions.
- Performance: The graphical representaion and buildwise comparison of performance observed.

## Human Interactions
The code triggers when user enters input as follows,
- For first two tabs the comman input at the top is the build number.
	The dropdown helps to select a version / a available version of product (*Cortx-1.0-Beta/Release/Cortx-1.0*).
	This triggers the following list of dropdown specific for the selected version.
	Choose the build to get the results.
	
- For Defects list, one must enter a comma seperated Test Execution IDs to get the results.
	The results are available for multiple test executions.
	eg. TEST-1234,TEST-5678

- For performance statistics, there are four options as,
	1. Choose a version (*Cortx-1.0-Beta/Release/Cortx-1.0*) - compulsary
	2. Then choose first build to compare, from the dropdown list - compulsary
	3. Build2 is also available for comparison of builds - optional
	4. Choose the operation to fetch statistics - compulsary

## Access
The webpage is accessible at [this location](http://cftic2.pun.seagate.com:5002/). 
One can provide the build name in the URL itself by adding /report/build. 
eg. `http://cftic2.pun.seagate.com:5002/report/108`

## Prerequisites
The following third-party libraries are used.

| Library | Version | Command to install |
| ----------- | ----------- | ----------- |
| Dash 	| 1.13.4 | `pip3 install dash==1.13.4` |
| Flask | 1.1.2 | `pip3 install Flask==1.1.2` |
| Future | 0.18.2 | - |
| Jira | 2.0.0 | `pip3 install jira==2.0.0` |
| Multipledispatch | 0.6.0 | `pip3 install multipledispatch==0.6.0` |
| Pandas | 1.0.5 | `pip3 install pandas==1.0.5` |
| Plotly | 4.8.2 | `pip3 install plotly==4.8.2` |
| Pymongo | 3.10.1 | `pip3 install pymongo==3.10.1` |
| Python3 | 3.7.8 | - |
| Re | 2.2.1 | - |
| Requests | 2.24.0 | - |
| Sys | - | - |
| Yaml | 5.3.1 | `pip3 install pyyaml==5.3.1` |

*Apart from that concurrent.futures a built-in python module is also used.*
User must choose *pip3 or pip* according to compiler specifications.

## Execution
To install packages use `pip3 install -r requirements.txt` command.
To run the python script use `python3 Main_app.py` command in the parent directory.

