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
