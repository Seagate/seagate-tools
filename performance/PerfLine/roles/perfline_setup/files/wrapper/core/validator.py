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
                'send_email': {'type': 'boolean', 'required': False}
            }
        },
        'configuration': {
            'required': False,
            'type': 'dict',
            'schema': {
                'hare': {
                    'type': 'dict',
                    'schema': {
                        'custom_cdf': {'type': 'string', 'required': False, 'empty': False},
                        'sns': {
                            'required': False,
                            'type': 'dict',
                            'schema': {
                                'data_units': {'type': 'integer', 'empty': False},
                                'parity_units': {'type': 'integer', 'empty': False},
                                'spare_units': {'type': 'integer', 'empty': False},
                            }
                        },
                        'dix': {
                            'required': False,
                            'type': 'dict',
                            'schema': {
                                'data_units': {'type': 'integer', 'empty': False},
                                'parity_units': {'type': 'integer', 'empty': False},
                                'spare_units': {'type': 'integer', 'empty': False},
                            }
                        }
                    }
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
            'required': False,
            'schema': {
                'github_PAT': {'type': 'string', 'empty': False},
                'github_username': {'type': 'string', 'empty': False},
                'build_machine': {'type': 'string', 'empty': False},
                'motr_repo_path': {'type': 'string', 'empty': False},
                'hare_repo_path': {'type': 'string', 'empty': False},
                's3server_repo_path': {'type': 'string', 'empty': False},
                'hare_commit_id': {'type': 'string', 'empty': False},
                'motr_commit_id': {'type': 'string', 'empty': False},
                's3server_commit_id': {'type': 'string', 'empty': False},
            }
         },
         'benchmarks': {
             'type': 'list',
             'schema': {
                'type': 'dict', 
                'oneof': [{
                            'schema': {
                                'custom': {
                                    'type': 'dict',
                                    'schema': {
                                        'cmd': {'type': 'string', 'required': True}
                                    }
                                }
                            }
                },
                {
                            'schema': {
                                'lnet': {
                                    'type': 'dict',
                                    'schema': {
                                        'LNET_OPS': {'type': 'string', 'required': True, 'empty': False},
                                        }
                                }
                            }
                },
                {
                            'schema': {
                                'fio': {
                                    'type': 'dict',
                                    'schema': {
                                        'Duration': {'type': 'integer', 'required': True},
                                        'BlockSize': {'type': 'string', 'required': True, 'empty': False},
                                        'NumJobs': {'type': 'integer', 'required': True},
                                        'Template': {'type': 'string', 'required': True, 'empty': False},
                                        }
                                }
                            }
                },
                {
                            'schema': {
                                's3bench': {
                                    'type': 'dict',
                                    'schema': {
                                        'BucketName': {'type': 'string', 'required': True, 'empty': False},
                                        'NumClients': {'type': 'integer', 'required': True},
                                        'NumSample': {'type': 'integer', 'required': True},
                                        'ObjSize': {'type': 'string', 'required': True, 'empty': False},
                                        'EndPoint': {'type': 'string', 'required': True, 'empty': False},
                                    }
                                }
                            }
                },
                {
                            'schema': {
                                'iperf': {
                                    'type': 'dict',
                                    'schema': {
                                        'Interval': {'type': 'integer', 'required': False },
                                        'Duration': {'type': 'integer', 'required': True, 'default': 60 },
                                        'Parallel': {'type': 'integer', 'required': False },
                                    }
                                }
                            } 
                },
                {
                            'schema': {
                                'm0crate': {
                                    'type': 'dict',
                                    'schema': {
                                        'NR_INSTANCES_PER_NODE': {'type': 'integer', 'required': False},
                                        'LAYOUT_ID': {'type': 'integer', 'required': False},
                                        'OPCODE': {'type': 'integer', 'required': False},
                                        'IOSIZE': {'type': 'string', 'required': False, 'empty': False},
                                        'BLOCK_SIZE': {'type': 'string', 'required': False, 'empty': False},
                                        'BLOCKS_PER_OP': {'type': 'integer', 'required': False},
                                        'MAX_NR_OPS': {'type': 'integer', 'required': False},
                                        'NR_OBJS': {'type': 'integer', 'required': False},
                                        'NR_THREADS': {'type': 'integer', 'required': False},
                                        'RAND_IO': {'type': 'integer', 'required': False},
                                        'MODE': {'type': 'integer', 'required': False},
                                        'THREAD_OPS': {'type': 'string', 'required': False, 'empty': False},
                                    }
                                }
                            }
                }]
             }    
         },
        'execution_options': {
            'type': 'dict',
            'schema': {
                'mkfs': {'type': 'boolean'},
                'collect_m0trace': {'type': 'boolean'},
                'collect_addb': {'type': 'boolean'},
                'backup_result': {'type': 'boolean'}
            }
        }
    }
    return schema_motr


def validate_config(config):
    v = Validator(allow_unknown=False, require_all=True)
    errors = []
    v.validate(config, get_schema_motr())
    errors.append({"User workload": v.errors})
    return errors