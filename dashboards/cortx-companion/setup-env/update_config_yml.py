import yaml
import os
import sys

cur_dir = os.getcwd()
req_path = "/seagate-tools/dashboards/cortx-companion/Performance/configs.yml"
filepath = cur_dir+req_path


def read_file():
    with open(filepath, 'r') as f:
        y = yaml.safe_load(f)
        return y


data = read_file()

with open(filepath, 'w') as f:
    data['PerfDB']['auth']['full_access_user'] = sys.argv[1]
    data['PerfDB']['auth']['full_access_password'] = sys.argv[2]
    yaml.dump(data, f,  default_flow_style=False, sort_keys=False)

print("*************updated credentials of configs.yml***************")
