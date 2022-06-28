#! /bin/bash
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

if [ ! -f "/root/go/bin/s3bench.old" ] ; then
   echo "Installing s3bench tools"
   cd ~; go get github.com/igneous-systems/s3bench
   cd /root/go/src/github.com/igneous-systems/s3bench; go build
   yes | cp /root/go/src/github.com/igneous-systems/s3bench/s3bench ~/go/bin/s3bench.old
else
   cp ~/go/bin/s3bench.old s3bench
   echo "S3benchmark Tools is already configured"
fi

