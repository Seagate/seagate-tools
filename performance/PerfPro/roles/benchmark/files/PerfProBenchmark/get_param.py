import os
import sys
import yaml
import urllib.request
import re


conf_yaml = open(sys.argv[1])
parse_conf = yaml.load(conf_yaml , Loader=yaml.FullLoader)
param=parse_conf.get('END_POINTS')

					
print(param)
