#!/usr/bin/env python3
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
"""Defect list for Test Execution Callbacks."""

from http import HTTPStatus
import dash_table
import pandas as pd
import requests
from dash.dependencies import Output, Input
from dash.exceptions import PreventUpdate
import common
from common import app
from jira import JIRA


def get_test_executions_from_test_plan(test_plan: str, username: str, password: str) -> [dict]:
    """
    Get test executions from test plan.Returns dictionary of test executions from test plan.


    :param test_plan : Test plan number in JIRA
    :param username : JIRA Username
    :param password : JIRA Password
    :return list of Test execution keys attached to test plan
    """
    jira_url = f'https://jts.seagate.com/rest/raven/1.0/api/testplan/{test_plan}/testexecution'
    response = requests.get(jira_url, auth=(username, password))
    te_ids = []
    if response.status_code == HTTPStatus.OK:
        for each in response.json():
            te_ids.append(each["key"])
    else:
        print("(get_test_executions_from_test_plan)Error: Request: {} Http Status code : {} "
              .format(jira_url, response.status_code))
    return te_ids


@app.callback(
    [Output('table_test_execution_wise_defect', 'children'),
     Output('test_execution_wise_defect_error', 'children')],
    [Input('test_execution_submit_button', 'n_clicks'),
     Input('test_execution_input', 'value')]
)
def create_te_defects(n_clicks, ids):
    """
    Returns the defect details attached to the test execution ids.

    :param n_clicks: Event after submit button clicked.
    :param ids: List of test execution id's
    :return: Datatable
    """
    if n_clicks is None or ids is None:
        raise PreventUpdate
    error_string = "Invalid test plan/test execution id "
    invalid_id = []
    ids_list = ids.split(",")
    df_execution_wise_defect = pd.DataFrame(columns=["issue_no", "issue_comp",
                                                     "issue_name", "issue_priority",
                                                     "test_execution"])
    jira_url = "https://jts.seagate.com/"
    auth_jira = JIRA({'server': jira_url}, basic_auth=(common.jira_username, common.jira_password))
    for input_id in ids_list:
        te_ids = []
        try:
            id_details = auth_jira.issue(input_id)
        except Exception as ex:
            print("(create_te_defects) Exception during Accessing Jira {}".format(ex))
            invalid_id.append(input_id)
        else:
            if id_details.fields.issuetype.name == 'Test Plan':
                tp_id = input_id
                temp_list = get_test_executions_from_test_plan(input_id, common.jira_username,
                                                               common.jira_password)
                if len(temp_list) > 0:
                    te_ids.extend(temp_list)
            elif id_details.fields.issuetype.name == 'Test Execution':
                tp_id = "-"
                te_ids.append(input_id)
            else:
                invalid_id.append(input_id)
                continue

            df_execution_wise_defect = _populate_te_data_frame(df_execution_wise_defect, te_ids,
                                                               tp_id)

    df_execution_wise_defect["issue_no"] = df_execution_wise_defect["issue_no"].apply(common.add_link)
    if common.DEBUG_PRINTS:
        print("create_te_defects : Dataframe : {}".format(df_execution_wise_defect))
    execution_wise_defect = _construct_te_dash_table(df_execution_wise_defect)
    if len(invalid_id) > 0:
        error_string = error_string + str(invalid_id)
    else:
        error_string = ""
    return execution_wise_defect, error_string


def _construct_te_dash_table(df_execution_wise_defect):
    """
    Construct a dash table consisting of TE's with their corresponding defect IDs.
    """
    col = []
    for i in df_execution_wise_defect.columns:
        if i == "issue_no":
            col.append(
                {"name": str(i).upper(), "id": i, "type": 'text', "presentation": "markdown"})
        else:
            col.append({"name": str(i).upper(), "id": i})
    execution_wise_defect = dash_table.DataTable(
        id="execution_wise_defect",
        columns=col,
        data=df_execution_wise_defect.to_dict('records'),
        style_header=common.dict_style_header,
        style_data_conditional=[{'if': {'row_index': 'odd'}, 'backgroundColor': '#F8F8F8'}
                                ],
        style_cell=common.dict_style_cell,
        style_table={
            'width': '100%',
            'overflowX': 'scroll',
            'height': '50%',
            'overflowY': 'auto'
        }
    )
    return execution_wise_defect


def _populate_te_data_frame(df_execution_wise_defect, te_ids, tp_id):
    """
    Construct a dataframe consisting of TE's with their linked defect IDs and TP ID.
    Dataframe contains Priority,Component,Name and Issue id of issues.
    """
    for te_id in te_ids:
        issue_list = []
        jira_link = 'https://jts.seagate.com/rest/raven/1.0/api/testexec/' + \
                    str(te_id) + '/test?detailed=true'
        response = requests.get(jira_link, auth=(common.jira_username,
                                                 common.jira_password))
        test_execution_data = response.json()
        for each in test_execution_data:
            for defect_no in range(len(each['defects'])):
                issue_list.append(each['defects'][defect_no]['key'])
        if common.DEBUG_PRINTS:
            print("Issue List for TE:{} Issue :{}".format(te_id, issue_list))
        te_df = common.get_issue_details(issue_list)

        for _ in te_df:
            te_df["test_execution"] = te_id
            te_df["test_plan"] = tp_id
        df_execution_wise_defect = df_execution_wise_defect.append(te_df)
    return df_execution_wise_defect
