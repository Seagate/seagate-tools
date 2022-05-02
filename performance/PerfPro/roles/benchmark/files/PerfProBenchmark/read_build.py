import sys
import yaml
import urllib.request
import re


conf_yaml = open(sys.argv[1])
parse_conf = yaml.safe_load(conf_yaml)
build_info=str(parse_conf.get('BUILD_INFO'))
build_url=parse_conf.get('BUILD_URL')

def get_build_info(variable):

    if build_url.lower().startswith('http'):
        release_info = urllib.request.urlopen(build_url+'RELEASE.INFO')
    else:
        raise Exception("bad build_url")

    for line in build_info:
        if variable in line.decode("utf-8"):
            strinfo=line.decode("utf-8").strip()
            strip_strinfo=re.split(': ',strinfo)
            return(strip_strinfo[1])

if build_info == 'RELEASE.INFO':
    BUILD=get_build_info('BUILD')
    print(BUILD[1:-1])
elif build_info == 'USER_INPUT':
    BUILD=parse_conf.get('BUILD')
    print(BUILD)

