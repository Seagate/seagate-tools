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
                    'required': False,
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
                },
                'motr': {
                    'required': False,
                    'type': 'dict',
                    'schema': {
                        'custom_conf': {'type': 'string', 'required': False, 'empty': False},
                        'params': {
                            'required': False,
                            'type': 'dict',
                            'empty': False
                        }
                    }
                },
                's3': {
                    'required': False,
                    'type': 'dict',
                    'schema': {
                        'custom_conf': {'type': 'string', 'required': False, 'empty': False},
                        'instances_per_node': {'type': 'integer', 'required': False, 'empty': False},
                        'S3_SERVER_CONFIG': {'type': 'dict', 'required': False, 'empty': False},
                        'S3_AUTH_CONFIG': {'type': 'dict', 'required': False, 'empty': False},
                        'S3_MOTR_CONFIG': {'type': 'dict', 'required': False, 'empty': False},
                        'S3_THIRDPARTY_CONFIG': {'type': 'dict', 'required': False, 'empty': False},
                    }
                },
                'haproxy': {
                    'required': False,
                    'type': 'dict',
                    'schema': {
                        'maxconn_total': {'type': 'integer', 'required': False, 'empty': False},
                        'maxconn_per_s3_instance': {'type': 'integer', 'required': False, 'empty': False},
                        'nbproc': {'type': 'integer', 'required': False, 'empty': False, 'excludes': 'nbthread'},
                        'nbthread': {'type': 'integer', 'required': False, 'empty': False, 'excludes': 'nbproc'},
                    }
                },
                'lnet': {
                    'required': False,
                    'type': 'dict',
                    'schema': {
                        'custom_conf': {'type': 'string', 'required': False, 'empty': False},
                    }
                },
                'ko2iblnd': {
                    'required': False,
                    'type': 'dict',
                    'schema': {
                        'custom_conf': {'type': 'string', 'required': False, 'empty': False},
                    }
                },
                'solution': {
                    'required': False,
                    'type': 'dict',
                    'schema': {
                        'custom_conf': {'type': 'string', 'required': False, 'empty': False},
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
            'oneof': [
                {
                    'schema': {
                        'images': {
                            'type': 'dict',
                            'required': True,
                            'keysrules': {
                                'type': 'string',
                                'regex': '^(cortxcontrol|cortxdata|cortxserver|cortxha|cortxclient)$'},
                            'valuesrules': {
                                'type': 'dict',
                                'schema': {
                                    'image':   {'type': 'string', 'required': True, 'empty': False},
                                    'motr_patch': {'type': 'string', 'required': False, 'empty': False},
                                    'hare_patch': {'type': 'string', 'required': False, 'empty': False},
                                }
                            }
                        }
                    }
                },
                {
                    'schema': {
                        'sources': {
                            'type': 'dict',
                            'required': True,
                            'keysrules': {
                                'type': 'string',
                                'regex': '^(ha|hare|k8s|management-portal|manager|monitor|motr|motr-apps|multisite|posix|prvsnr|re|rgw|rgw-integration|utils)$'},
                            'valuesrules': {
                                'type': 'dict',
                                'schema': {
                                    'repo':   {'type': 'string', 'required': True, 'empty': False},
                                    'branch': {'type': 'string', 'required': True, 'empty': False},
                                }
                            }
                        }
                    }
                }
            ]
        },
        'benchmarks': {
             'type': 'list',
             'required': False,
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
                                'iperf': {
                                    'type': 'dict',
                                    'schema': {
                                        'Interval': {'type': 'integer', 'required': False },
                                        'Duration': {'type': 'integer', 'required': True, 'default': 60 },
                                        'Parallel': {'type': 'integer', 'required': False },
                                    }
                                }
                            }
                }]
            }
        },
        'workloads': {
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
        'post_exec_cmds': {
            'type': 'list',
            'required': False,
            'schema': {
                'type': 'dict',
                'schema': {
                    'cmd': {'type': 'string', 'required': True}
                }
            }
        },
        'execution_options': {
            'type': 'dict',
            'schema': {
                'mkfs': {'type': 'boolean'},
                'collect_m0trace': {'type': 'boolean'},
                'collect_addb': {'type': 'boolean'},
                'analyze_addb': {'type': 'boolean', 'required': False},
                'addb_duration': {'type': 'string', 'required': False, 'empty': False, 'regex': '(^all$)|(^\d+((m$)|(h$)|(s$)|(min$)|(sec$)|(hr$)|(hour$)|(minute$)|(second$))$)'},
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
