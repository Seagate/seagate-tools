
# Copyright (c) 2020 Seagate Technology LLC and/or its Affiliates
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# For any questions about this software or licensing,
# please email opensource@seagate.com or cortx-questions@seagate.com.
#

from shutil import copytree, rmtree
import os


def generate_tmp_dir_name(dst_dir):
    result = ''
    path_parts = dst_dir.split('/')

    for path_part in path_parts[1:-1]:
        result += '/' + path_part

    result += '/moving_{}'.format(path_parts[-1])
    return result


def move_dir(orig_dir, src_dir, dst_dir):
    if os.path.exists(dst_dir):
        print(f'{dst_dir} already exists')
        os.rename(src_dir, orig_dir)
        return

    tmp_dst = generate_tmp_dir_name(dst_dir)

    try:
        copytree(src_dir, tmp_dst)
        os.rename(tmp_dst, dst_dir)
        rmtree(src_dir)
    except Exception as e:
        print(e)
        if os.path.exists(tmp_dst):
            rmtree(tmp_dst)

        if os.path.exists(src_dir):
            os.rename(src_dir, orig_dir)
