#!/usr/bin/env python3
#
# Seagate-tools: PerfPro
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
"""
Script to archive PerfPro logs to NFS repository
Input : config.yml and logs location
"""

import os
import shutil
import sys
import yaml

conf_yaml = open(sys.argv[1])
parse_conf = yaml.safe_load(conf_yaml)

'''Below configuration parameters are collected from config.yml file'''
nfs_server = parse_conf.get('NFS_SERVER')
nfs_export = parse_conf.get('NFS_EXPORT')
mount_point = parse_conf.get('NFS_MOUNT_POINT')
log_dest = parse_conf.get('NFS_FOLDER')

log_source = sys.argv[2]


class collect_logs:
    '''Class to collect logs and archive them in NFS repository'''
    @classmethod
    def mount_nfs(cls):
        """Mounts the NFS export on the mountpoint to copy the collected logs"""

        if str(os.system('mount|grep ' + mount_point)) == '0':
            logs.unmount_nfs()
            print('unmounting dedicated perftool mountpoint')
        os.system('mkdir -p ' + mount_point)
        os.system('mount ' + nfs_server + ':' + nfs_export + ' ' + mount_point)
        return 'Export mounted'

    @classmethod
    def zip_logs(cls):
        """Create the Zipped copy of recently collected logs by benchmarking tool"""

        os.system(' tar -cvzf ' + mount_point + '/' + log_dest +
                  '/' + log_source + '.tar.gz' + ' -P ' + log_source)
        return 'logs collected and zipped as ' + log_source + '.tar.gz'

    @classmethod
    def copy_logs(cls, source_zip_prefix=None, time_string=None):
        """Copy the Zipped copy to NFS Repo"""

        shutil.copy(source_zip_prefix + time_string +
                    '.tar.gz', mount_point + '/' + log_dest)
        return 'Logs copied to NFS Repo.'

    @classmethod
    def show_logs(cls):
        """Show the contents of NFS Repo for verification of code"""

        return os.listdir(mount_point + '/' + log_dest)

    @classmethod
    def delete_tarfile(cls, source_zip_prefix=None, time_string=None):
        """Delete tar.gz file from current location"""

        return os.remove(source_zip_prefix + time_string + '.tar.gz')

    @classmethod
    def unmount_nfs(cls):
        """Unmounts the NFS export and deleted the mountpoint"""

        os.system('umount -l ' + mount_point)
        #        os.system('rmdir '+mount_point)
        return 'Exiting after log collection.'


logs = collect_logs()
print(logs.mount_nfs())
print(logs.zip_logs())
# print(logs.copy_logs())
# print(logs.delete_tarfile())
# print(logs.show_logs())
print(logs.unmount_nfs())
