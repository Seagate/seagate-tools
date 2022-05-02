import sys
import yaml


conf_yaml = open(sys.argv[1])
parse_conf = yaml.safe_load(conf_yaml)
param=parse_conf.get('END_POINTS')

					
print(param)
