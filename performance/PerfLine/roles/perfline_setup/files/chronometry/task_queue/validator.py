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
#

from cerberus import Validator

def get_schema_s3():
    schema_s3 = {
        'common': {
            'type': 'dict',
            'schema': {
                'version'    : {'type': 'integer', 'allowed': [ 1 ] },
                'description': {'required': False, 'nullable': True},
                'priority'   : {'type': 'integer', 'min': 1},
                'batch_id'   : {'required': False, 'nullable': True},
                'type'       : {'type': 'string', 'allowed' : ['s3client', 's3corrupt']},
                'timeout'    : {'required': False, 'type': 'string', 'regex': '[0-9]+(d|h|m|s)'},
                'user'       : {'type': 'string', 'regex': '.*@seagate\.com'},
                'send_email' : {'type': 'boolean'},
                'nodes'      : {'type': 'list',
                                'schema': {
                                    'type' : 'dict',
                                    'schema': {
                                        'srv' : {'type' : 'string', 'nullable': True},
                                        'cli' : {'type' : 'string', 'nullable': True}
                                    }
                                }
                            }
            }
        },
        'workload': {
            'type'  : 'list',
            'schema': {
                'type'  : 'dict',
                'schema': {
                    'app'  : {'type' : 'string', 'allowed': ['s3bench', 'sleep', 'exit']},
                    'param': {'type': 'dict',
                              'schema': {
                                  'cli_options': {'type' : 'string'}
                              }
                          }
                }
            }
        },
        's3server' : {
            'type'     : 'dict',
            'schema' : {
                'git'              : {'oneof': [{'allowed' : ['dev']},
                                                {'type' : 'string', 'regex' : '^[0-9a-f]{7,40}$'},
                                                {'type' : 'integer', 'min': 1000000, 'max': 9999999}]},
                'num_instances'    : {'type' : 'integer', 'min' : 1},
                'cmd_line_options' : {'type' : 'string', 'nullable': True},
                'config_overrides' : {'type' : 'dict', 'nullable' : True}
            }
        },
        'ha' : {'type' : 'string', 'allowed' : ['halon', 'hare']},
        'motr' : {
            'type'   : 'dict',
            'schema' : {
                'git'           : {'oneof': [{'allowed' : ['dev']},
                                             {'type' : 'string', 'regex' : '^[0-9a-f]{7,40}$'},
                                             {'type' : 'integer', 'min': 1000000, 'max': 9999999}]},
                'build_options' : {'type' : 'string', 'nullable' : True},
                'config_overrides' : {'type' : 'dict', 'nullable' : True}
            }
        },
        'execution_options' : {
            'type'   : 'dict',
            'schema' : {
                'no_motr_trace'    : {'type' : 'boolean'},
                'no_m0trace_files' : {'type' : 'boolean'},
                'no_m0trace_dumps' : {'type' : 'boolean'},
                'no_addb_stobs'    : {'type' : 'boolean'},
                'no_addb_dumps'    : {'type' : 'boolean'},
                'no_m0play_db'     : {'type' : 'boolean'}
            }
        }
    }

    return schema_s3

def get_schema_motr():
    schema_motr = {
        'common': {
            'type': 'dict',
            'schema': {
                'version'    : {'type': 'integer', 'allowed': [ 1 ] },
                'description': {'required': False, 'nullable': True},
                'priority'   : {'type': 'integer', 'min': 1},
                'batch_id'   : {'required': False, 'nullable': True},
                'user'       : {'type': 'string', 'regex': '.*@seagate\.com'},
                'type'       : {'type': 'string', 'allowed' : ['m0crate', 'm0corrupt']},
                'timeout'    : {'required': False, 'type': 'string', 'regex': '[0-9]+(d|h|m|s)'},
                'nodes'      : {'type': 'list',
                                'schema': {
                                    'type' : 'dict',
                                    'schema': {
                                        'srv' : {'type' : 'string', 'nullable': True},
                                        'cli' : {'type' : 'string', 'nullable': True}
                                    }
                                }
                            }
            }
        },
        'workload': {
            'type'  : 'list',
            'schema': {
                'type'  : 'dict',
                'schema': {
                    'app'  : {'type' : 'string', 'allowed': ['m0crate', 'sleep', 'exit']},
                    'param': {'type': 'dict',
                              'schema': {
                                  'config_overrides' : {'type' : 'dict', 'nullable' : True, 'required': False}
                              }
                          }
                }
            }
        },
        'ha' : {'type' : 'string', 'allowed' : ['halon', 'hare']},
        'motr' : {
            'type'   : 'dict',
            'schema' : {
                'git'           : {'oneof': [{'allowed' : ['dev']},
                                             {'type' : 'string', 'regex' : '^[0-9a-f]{7,40}$'},
                                             {'type' : 'integer', 'min': 1000000, 'max': 9999999}]},
                'build_options' : {'type' : 'string', 'nullable' : True},
                'config_overrides' : {'type' : 'dict', 'nullable' : True}
            }
        },
        'execution_options' : {
            'type'   : 'dict',
            'schema' : {
                'no_motr_trace'    : {'type' : 'boolean'},
                'no_m0trace_files' : {'type' : 'boolean'},
                'no_m0trace_dumps' : {'type' : 'boolean'},
                'no_addb_stobs'    : {'type' : 'boolean'},
                'no_addb_dumps'    : {'type' : 'boolean'},
                'no_m0play_db'     : {'type' : 'boolean'}
            }
        }
    }
    return schema_motr

def validate_config(config):
    v = Validator(allow_unknown=True, require_all=True)
    errors = []

    v.validate(config, get_schema_s3());
    errors.append({"S3 requirements" : v.errors})

    v.validate(config, get_schema_motr())
    errors.append({"Motr requirements": v.errors})

    return errors
