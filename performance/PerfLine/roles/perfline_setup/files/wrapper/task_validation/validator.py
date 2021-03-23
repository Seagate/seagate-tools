#
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

from cerberus import Validator


def get_schema_motr():
    schema_motr = {
        'common': {
            'type': 'dict',
            'schema': {
                'version': {'type': 'integer', 'allowed': [1]},
                'description': {'required': False, 'nullable': True},
                'priority': {'type': 'integer', 'min': 1},
                'batch_id': {'required': False, 'nullable': True},
                'user': {'type': 'string', 'regex': '.*@seagate\.com'},
            }
        },
        'workload': {
            'type': 'list',
            'schema': {
                'type': 'dict',
                'schema': {
                    'cmd': {'type': 'string'},
        
                }
            }
        },
        'stats_collection': {
            'type': 'dict',
            'schema': {
                'iostat': {'type': 'boolean'},
                'dstat': {'type': 'boolean'},
                'blktrace': {'type': 'boolean'},
                'glances': {'type': 'boolean'},
                
            }
         },
        'custom_build': {
            'type': 'dict',
            'schema': {
                'deploybuild': {'type': 'boolean'}, 
                'motr_repo_path': {'type': 'string', 'required': False, 'nullable': True },
                'hare_repo_path': {'type': 'string', 'required': False, 'nullable': True },
                's3server_repo_path': {'type': 'string', 'required': False, 'nullable': True },
                'hare_commit_id': {'type': 'string', 'required': False, 'nullable': True },
                'motr_commit_id': {'type': 'string', 'required': False, 'nullable': True },
                's3server_commit_id': {'type': 'string', 'required': False, 'nullable': True },
            }
         },
        'benchmark': {
            'type': 'dict',
            'schema': {
                'fio': {'type': 'boolean'},
                's3bench': {'type': 'boolean' },
            }
        },
        'parameter': {
            'type': 'dict',
            'schema': {
                'BucketName': {'type': 'string', 'required': False, 'nullable': True },
                'NumClients': {'type': 'integer', 'required': False, 'nullable': True },
                'NumSample': {'type': 'integer', 'required': False, 'nullable': True },
                'ObjSize': {'type': 'string', 'required': False, 'nullable': True },
            }
        },
        'execution_options': {
            'type': 'dict',
            'schema': {
                'm0trace_files': {'type': 'boolean'},
                'm0trace_dumps': {'type': 'boolean'},
                'addb_stobs': {'type': 'boolean'},
                'addb_dumps': {'type': 'boolean'},
                'm0play_db': {'type': 'boolean'}
            }
        }
    }
    return schema_motr


def validate_config(config):
    v = Validator(allow_unknown=True, require_all=True)
    errors = []
    v.validate(config, get_schema_motr())
    errors.append({"Motr requirements": v.errors})

    return errors
