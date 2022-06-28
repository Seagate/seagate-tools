#!/usr/bin/env python3
#
#
# Copyright (c) 2022 Seagate Technology LLC and/or its Affiliates
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
#
# For any questions about this software or licensing,
# please email opensource@seagate.com or cortx-questions@seagate.com.
#
# -*- coding: utf-8 -*-

import sys
import argparse
import yaml


POD_IMAGETYPE_MAP = {
    'cortxcontrol': 'cortx-all',
    'cortxdata': 'cortx-all',
    'cortxserver': 'cortx-rgw',
    'cortxha': 'cortx-all',
    'cortxclient': 'cortx-all'
    }


def parse_args():
    parser = argparse.ArgumentParser(prog=sys.argv[0],
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description="")

    parser.add_argument("-s", "--src-file", type=str, required=True,
                        help="path to config file used as base")

    parser.add_argument("-d", "--dst-file", type=str, required=True,
                        help="path to store result")

    parser.add_argument("--pod", action='append', default=list(), required=False)
    parser.add_argument("--image", action='append', default=list(), required=False)
    parser.add_argument("--rgw-thread-pool-size", type=str, required=False)
    parser.add_argument("--rgw-max-concurrent-request", type=str, required=False)

    return parser.parse_args()


def parse_file(file_path):
    with open(file_path, 'rt') as f:
        data = yaml.safe_load(f.read())

    return data


def save_file(data, file_path):
    with open(file_path, 'wt') as f:
        f.write(yaml.safe_dump(data, sort_keys=False))


def find_pods_by_docker_img_type(conf, image_type):
    pods = list()

    for pod, img_type in POD_IMAGETYPE_MAP.items():
        if image_type == img_type:
            pods.append(pod)

    return pods


def update_docker_image_type(conf, image_descr):
    values = image_descr.split('=', maxsplit=1)

    if len(values) != 2:
        raise ValueError(f'invalid format of --image option: {image_descr}')

    image_type, docker_img = values
    pods = find_pods_by_docker_img_type(conf, image_type)

    for pod_name in pods:
        print(f'set {pod_name} to {docker_img}')
        conf['solution']['images'][pod_name] = docker_img



def update_pod_value(conf, pod_descr):
    values = pod_descr.split('=', maxsplit=1)

    if len(values) != 2:
        raise ValueError(f'invalid format of --pod option: {pod_descr}')

    pod_name, docker_img = values
    images = conf['solution']['images']

    if pod_name not in images:
        raise ValueError(f'{pod_name} not found in the solution.yaml file')

    print(f'set {pod_name} to {docker_img}')
    images[pod_name] = docker_img


def update_rgw_config_params(data,thread_pool_size, max_concurrent_request):
    if thread_pool_size is None:
       thread_pool_size = 10  # default value assigned

    if max_concurrent_request is None:
       max_concurrent_request = 10  # default value assigned

    params = f"thread_pool_size: {thread_pool_size}\\nmax_concurrent_request: {max_concurrent_request}\\n"

    data['solution']['common']['s3']['extra_configuration'] = params


def replaceAll(file):
    with open(file) as f:
        content = f.read()

    with open(file, 'wt') as f_new:
        f_new.write(content.replace("'", '"'))


def main():
    args = parse_args()
    data = parse_file(args.src_file)

    for image_descr in args.image:
        update_docker_image_type(data, image_descr)

    for pod_descr in args.pod:
        update_pod_value(data, pod_descr)

    if args.rgw_thread_pool_size is not None or args.rgw_max_concurrent_request is not None:
        update_rgw_config_params(data,args.rgw_thread_pool_size, args.rgw_max_concurrent_request)

    save_file(data, args.dst_file)
    replaceAll(args.dst_file)

if __name__ == '__main__':
    main()
