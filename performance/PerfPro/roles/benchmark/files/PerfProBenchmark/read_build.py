import os
import sys
import yaml
import re

conf_yaml = open(sys.argv[1])
parse_conf = yaml.safe_load(conf_yaml)
release_info = str(parse_conf.get('BUILD_INFO'))
build_url = parse_conf.get('BUILD_URL')
docker_info = parse_conf.get('DOCKER_INFO')


def get_build_info(variable):
    release_info = os.popen('docker run --rm -it ' +
                            docker_info + ' cat /opt/seagate/cortx/RELEASE.INFO')
    lines = release_info.readlines()
    for line in lines:
        if variable in line:
            strinfo = line.strip()
            strip_strinfo = re.split(': ', strinfo)
            return(strip_strinfo[1])


if release_info == 'RELEASE.INFO':
    version = get_build_info('VERSION')[1:-1]
    ver_strip = re.split('-', version)
    BUILD = ver_strip[1]
    print(BUILD)
elif release_info == 'USER_INPUT':
    BUILD = parse_conf.get('BUILD')
    print(BUILD)
