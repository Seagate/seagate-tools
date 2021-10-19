import os
import sys
import yaml
import urllib.request
import re


conf_yaml = open(sys.argv[1])
parse_conf = yaml.load(conf_yaml , Loader=yaml.FullLoader)
build_url=parse_conf.get('BUILD_URL')

def get_build_info(variable):
    build_info= urllib.request.urlopen(build_url+'RELEASE.INFO')
    for line in build_info:
        if variable in line.decode("utf-8"):
            strinfo=line.decode("utf-8").strip()
            strip_strinfo=re.split(': ',strinfo)
            return(strip_strinfo[1])
						
BUILD=get_build_info('BUILD')
print(BUILD[1:-1])
