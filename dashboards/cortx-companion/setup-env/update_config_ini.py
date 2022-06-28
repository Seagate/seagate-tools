import configparser
import os
import sys

cur_dir = os.getcwd()
req_path = "/seagate-tools/dashboards/cortx-companion/config.ini"
filepath = cur_dir+req_path

parser = configparser.ConfigParser()
parser.read(filepath)

t = open(filepath, 'w')

parser.set('PERF_DB', 'db_username', sys.argv[3])
parser.set('PERF_DB', 'db_password', sys.argv[4])

parser.set('REST', 'db_username', sys.argv[1])
parser.set('REST', 'db_password', sys.argv[2])

parser.set('MONGODB_URI', 'db_username', sys.argv[1])
parser.set('MONGODB_URI', 'db_password', sys.argv[2])

parser.set('JIRA', 'jira_username', sys.argv[5])
parser.set('JIRA', 'jira_password', sys.argv[6])
parser.write(t)

t.close()

print("*************updated credentials of config.ini****************")
