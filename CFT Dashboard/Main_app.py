'''
CORTX CFT Dashboard Script
@ Seagate Pune
last Modification: 10 February 2020
Version: 6
'''
### ====================================================================================
import re
import os
import concurrent.futures
# --------------------------------------------------------------------------------------
import dash
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Output, State, Input
import dash_table
from dash.exceptions import PreventUpdate
import flask
# --------------------------------------------------------------------------------------
import requests
import getpass
from pymongo import MongoClient
import pandas as pd
from jira import JIRA
# --------------------------------------------------------------------------------------
import plotly.graph_objs as go
### ====================================================================================
import mongodbAPIs as mapi
import timingAPIs
import db_details as dd
from support import get_DB_details, get_IOsizewise_data, get_x_axis, get_buildwise_data

### ====================================================================================
# global declarations
external_stylesheets = [dbc.themes.COSMO]
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "CORTX Test Status"
server = app.server
perfDb = dd.get_database()

username = '' # <insert your JIRA Username here > # input("JIRA username: ")
password = '' # <insert your JIRA password here > # getpass.getpass("JIRA password: ")

__version__ = "6.13"
### ====================================================================================

@server.route('/favicon.ico')
def favicon():
    return flask.send_from_directory(os.path.join(server.root_path, 'static'), 'favicon.ico')
# --------------------------------------------------------------------------------------
toast = html.Div(
    [
        dbc.Toast(
            "Please verify and enter correct build number. Data is not there for this build number.",
            id="positioned-toast",
            header="Wrong build number",
            is_open=False,
            dismissable=True,
            icon="danger",
            duration=6000,
            # top: 66 positions the toast below the navbar
            style={"position": "fixed", "top": 25, "right": 10, "width": 350},
        ),
    ]
)
# two buttons on top right # ------------------------------------------------------------
search_bar = dbc.Row(
    [
        dbc.Col([
            dbc.Button("Cortx Sharepoint", color="light", size="lg", className="mr-1", outline=True,
                       href="https://seagatetechnology.sharepoint.com/sites/gteamdrv1/tdrive1224",
                       target="_blank"),
            dbc.Button("CFT Sharepoint", color="light", size="lg", className="mr-1", outline=True,
                       href="https://seagatetechnology.sharepoint.com/:f:/r/sites/gteamdrv1/tdrive1224/Shared%20Documents/CFT_IntegrationTeam?csf=1&web=1&e=9Wgzsx",
                       target="_blank")],
                width="auto",
                ),
    ],
    no_gutters=True,
    className="ml-auto flex-nowrap mt-3 mt-md-0",
    align="center",
)
# --------------------------------------------------------------------------------------
navbar = dbc.Navbar(
    [
        html.A(
            dbc.Row([
                    dbc.Col(html.Img(src=app.get_asset_url(
                        "seagate.png"), height="100px")),
                    dbc.Col(dbc.NavbarBrand("CORTX CFT Dashboard",
                                            className="ml-2", style={'font-size': 40}))
                    ],
                    align="center",
                    no_gutters=True,
                    ),
        ),
        dbc.NavbarToggler(id="navbar-toggler"),
        dbc.Collapse(search_bar, id="navbar-collapse", navbar=True),
    ],
    color="dark",
    dark=True,
)

### ====================================================================================
# Eng report page - Table 1 : Report bugs
### ====================================================================================
t1_caption = [
    html.Caption(html.Tr([html.Th("Reported Bugs")])),
]
t1r1 = html.Tr([html.Td("Total"),html.Td(None, id="eng_total_test"),html.Td(None, id="eng_total_product")], id="eng_total")
t1r2 = html.Tr([html.Td("Blocker"),html.Td(None, id="eng_blocker_test"),html.Td(None, id="eng_blocker_product")],id="eng_blocker")
t1r3 = html.Tr([html.Td("Critical"),html.Td(None, id="eng_critical_test"),html.Td(None, id="eng_critical_product")],id="eng_critical")
t1r4 = html.Tr([html.Td("Major"),html.Td(None, id="eng_major_test"),html.Td(None, id="eng_major_product")],id="eng_major")
t1r5 = html.Tr([html.Td("Minor"),html.Td(None, id="eng_minor_test"),html.Td(None, id="eng_minor_product")],id="eng_minor")
t1r6 = html.Tr([html.Td("Trivial"),html.Td(None, id="eng_trivial_test"),html.Td(None, id="eng_trivial_product")], id="eng_trivial")
t1_head = [
    html.Thead(html.Tr([html.Th("Priority"),html.Th("Test Infra Issues"),html.Th("CORTX SW Issues")]))
]

### ====================================================================================
# Eng report page - Table 2 : Overall QA report
### ====================================================================================
t2_caption = [
    html.Caption(html.Tr([html.Th("Overall QA Report")])),
]
t2r1 = html.Tr([html.Td("Total"),html.Td(None, id = "eng_qa_total_current"),html.Td(None, id="eng_qa_total_previous")], id="eng_qa_total")
t2r2 = html.Tr([html.Td("Pass"),html.Td(None, id="eng_qa_pass_current"),html.Td(None, id="eng_qa_pass_previous")],id="eng_qa_pass")
t2r3 = html.Tr([html.Td("Fail"),html.Td(None, id="eng_qa_fail_current"),html.Td(None, id="eng_qa_fail_previous")],id="eng_qa_fail")
t2r4 = html.Tr([html.Td("Aborted"),html.Td(None, id="eng_qa_aborted_current"),html.Td(None, id="eng_qa_aborted_previous")],id="eng_qa_aborted")
t2r5 = html.Tr([html.Td("Blocked"),html.Td(None, id="eng_qa_blocked_current"),html.Td(None, id="eng_qa_blocked_previous")],id="eng_qa_blocked")
t2r6 = html.Tr([html.Td("To Do"),html.Td(None, id="eng_qa_todo_current"),html.Td(None, id="eng_qa_todo_previous")],id="eng_qa_todo")
t2_head = [
    html.Thead(html.Tr([html.Th("Category"),html.Th("Current",id="qa_current_eng"),html.Th("Previous", id="qa_previous_eng")]))
]

### ====================================================================================
# Eng report page - Table 3 : Component Level Summary
### ====================================================================================
t3_caption = [
    html.Caption(html.Tr([html.Th("Component Level Summary")])),
]
t3_head = [
    html.Thead(html.Tr([html.Th("Component", rowSpan=2),html.Th("Current Build",id='component_build_current', colSpan=2),html.Th("Previous Build", colSpan=2,id= "component_previous")])),
    html.Thead(html.Tr([html.Th(" "),html.Th("Pass"), html.Th("Fail"),html.Th("Pass"), html.Th("Fail")]))
]
t3r1 = html.Tr([html.Td("S3",id="S3"),html.Td(None, id="S3_1_pass"),html.Td(None, id="S3_1_fail"),html.Td(None, id="S3_2_pass"),html.Td(None, id="S3_2_fail")])
t3r2 = html.Tr([html.Td("Provisioner",id="Provisioner"),html.Td(None, id="provision_1_pass"),html.Td(None, id="provision_1_fail"),html.Td(None, id="provision_2_pass"),html.Td(None, id="provision_2_fail")])
t3r3 = html.Tr([html.Td("CSM",id="CSM"),html.Td(None, id="csm_1_pass"),html.Td(None, id="csm_1_fail"),html.Td(None, id="csm_2_pass"),html.Td(None, id="csm_2_fail")])
t3r4 = html.Tr([html.Td("RAS",id="SSPL"),html.Td(None, id="sspl_1_pass"),html.Td(None, id="sspl_1_fail"),html.Td(None, id="sspl_2_pass"),html.Td(None, id="sspl_2_fail")])
t3r5 = html.Tr([html.Td("Motr",id="Motr"),html.Td(None, id="motr_1_pass"),html.Td(None, id="motr_1_fail"),html.Td(None, id="motr_2_pass"),html.Td(None, id="motr_2_fail")])
t3r6 = html.Tr([html.Td("HA",id="HA"),html.Td(None, id="ha_1_pass"),html.Td(None, id="ha_1_fail"),html.Td(None, id="ha_2_pass"),html.Td(None, id="ha_2_fail")])
t3r7 = html.Tr([html.Td("Locust",id="Locust"),html.Td(None, id="loc_1_pass"),html.Td(None, id="loc_1_fail"),html.Td(None, id="loc_2_pass"),html.Td(None, id="loc_2_fail")])
t3r8 = html.Tr([html.Td("Cosbench",id="Cosbench"),html.Td(None, id="cos_1_pass"),html.Td(None, id="cos_1_fail"),html.Td(None, id="cos_2_pass"),html.Td(None, id="cos_2_fail")])
t3r10 = html.Tr([html.Td("Data Recovery",id="data_recovery"),html.Td(None, id="dr_1_pass"),html.Td(None, id="dr_1_fail"),html.Td(None, id="dr_2_pass"),html.Td(None, id="dr_2_fail")])
t3r11 = html.Tr([html.Td("Node Recovery",id="node_recovery"),html.Td(None, id="nr_1_pass"),html.Td(None, id="nr_1_fail"),html.Td(None, id="nr_2_pass"),html.Td(None, id="nr_2_fail")])

t3r9 = html.Tr([html.Td("Total",id="Total"),html.Td(None, id="total_1_pass"),html.Td(None, id="total_1_fail"),html.Td(None, id="total_2_pass"),html.Td(None, id="total_2_fail")])

### ====================================================================================
# Eng report page - Table 4 : Timing tables
### ====================================================================================
t5_caption = [
    html.Caption(html.Tr([html.Th("Timing Summary (seconds)")])),
]
t5_head = [
    html.Thead(html.Tr([html.Th(" ", rowSpan=2),html.Th("Current Build",id='timing_build_current'),html.Th("Prev Build",id= "timing_build_prev_2"),html.Th("Prev Build",id= "timing_build_prev_3"),html.Th("Prev Build",id= "timing_build_prev_4"),html.Th("Prev Build",id= "timing_build_prev_5")])),
]
t5r1 = html.Tr([html.Td("Update",id="update"),html.Td(None, id="update_min_1"),html.Td(None, id="update_min_2"),html.Td(None, id="update_min_3"),html.Td(None, id="update_min_4"),html.Td(None, id="update_min_5")])
t5r2 = html.Tr([html.Td("Deployment",id="deploy"),html.Td(None, id="deploy_min_1"),html.Td(None, id="deploy_min_2"),html.Td(None, id="deploy_min_3"),html.Td(None, id="deploy_min_4"),html.Td(None, id="deploy_min_5")])
t5r3 = html.Tr([html.Td("Boxing",id="box"),html.Td(None, id="box_min_1"),html.Td(None, id="box_min_2"),html.Td(None, id="box_min_3"),html.Td(None, id="box_min_4"),html.Td(None, id="box_min_5")])
t5r4 = html.Tr([html.Td("Unboxing",id="unbox"),html.Td(None, id="unbox_min_1"),html.Td(None, id="unbox_min_2"),html.Td(None, id="unbox_min_3"),html.Td(None, id="unbox_min_4"),html.Td(None, id="unbox_min_5")])
t5r5 = html.Tr([html.Td("Onboarding",id="onboard"),html.Td(None, id="onboard_min_1"),html.Td(None, id="onboard_min_2"),html.Td(None, id="onboard_min_3"),html.Td(None, id="onboard_min_4"),html.Td(None, id="onboard_min_5")])
t5r6 = html.Tr([html.Td("Firmware Update",id="firm"),html.Td(None, id="firm_min_1"),html.Td(None, id="firm_min_2"),html.Td(None, id="firm_min_3"),html.Td(None, id="firm_min_4"),html.Td(None, id="firm_min_5")])
t5r7 = html.Tr([html.Td("Reboot Node",id="NReboot"),html.Td(None, id="NReboot_min_1"),html.Td(None, id="NReboot_min_2"),html.Td(None, id="NReboot_min_3"),html.Td(None, id="NReboot_min_4"),html.Td(None, id="NReboot_min_5")])
t5r8 = html.Tr([html.Td("Start Node",id="Nstart"),html.Td(None, id="Nstart_min_1"),html.Td(None, id="Nstart_min_2"),html.Td(None, id="Nstart_min_3"),html.Td(None, id="Nstart_min_4"),html.Td(None, id="Nstart_min_5")])
t5r9 = html.Tr([html.Td("Stop Node",id="Nstop"),html.Td(None, id="Nstop_min_1"),html.Td(None, id="Nstop_min_2"),html.Td(None, id="Nstop_min_3"),html.Td(None, id="Nstop_min_4"),html.Td(None, id="Nstop_min_5")])
t5r10 = html.Tr([html.Td("Node Failover",id="Nfail"),html.Td(None, id="Nfail_min_1"),html.Td(None, id="Nfail_min_2"),html.Td(None, id="Nfail_min_3"),html.Td(None, id="Nfail_min_4"),html.Td(None, id="Nfail_min_5")])
t5r15 = html.Tr([html.Td("Node Failback",id="Nfback"),html.Td(None, id="Nfback_min_1"),html.Td(None, id="Nfback_min_2"),html.Td(None, id="Nfback_min_3"),html.Td(None, id="Nfback_min_4"),html.Td(None, id="Nfback_min_5")])
t5r11 = html.Tr([html.Td("Stop All Services",id="stopA"),html.Td(None, id="stopA_min_1"),html.Td(None, id="stopA_min_2"),html.Td(None, id="stopA_min_3"),html.Td(None, id="stopA_min_4"),html.Td(None, id="stopA_min_5")])
t5r12 = html.Tr([html.Td("Start All Services",id="startA"),html.Td(None, id="startA_min_1"),html.Td(None, id="startA_min_2"),html.Td(None, id="startA_min_3"),html.Td(None, id="startA_min_4"),html.Td(None, id="startA_min_5")])
t5r13 = html.Tr([html.Td("Bucket Creation",id="bcre"),html.Td(None, id="bcre_min_1"),html.Td(None, id="bcre_min_2"),html.Td(None, id="bcre_min_3"),html.Td(None, id="bcre_min_4"),html.Td(None, id="bcre_min_5")])
t5r14 = html.Tr([html.Td("Bucket Deletion",id="bdel"),html.Td(None, id="bdel_min_1"),html.Td(None, id="bdel_min_2"),html.Td(None, id="bdel_min_3"),html.Td(None, id="bdel_min_4"),html.Td(None, id="bdel_min_5")])

### ====================================================================================
# Eng report page - Table 5 : S3 bench performance statistics
### ====================================================================================
eng_perf1_caption = [
    html.Caption(html.Tr([html.Th("Single Bucket Performance Statistics (Average) using S3Bench")])),
]
eng_write_throughput = html.Tr([html.Td("Write Throughput (MBps)", id="eWTH"),html.Td(None, id="e4WTH"),html.Td(None, id="e100WTH"),html.Td(None, id="e1WTH"),
                    html.Td(None, id="e5WTH"),html.Td(None, id="e36WTH"),html.Td(None, id="e64WTH"),html.Td(None, id="e128WTH"),html.Td(None, id="e256WTH")])
eng_read_throughput = html.Tr([html.Td("Read Throughput (MBps)", id="eRTH"),html.Td(None, id="e4RTH"),html.Td(None, id="e100RTH"),html.Td(None, id="e1RTH"),html.Td(None, id="e5RTH"),html.Td(None, id="e36RTH"),html.Td(None, id="e64RTH"),html.Td(None, id="e128RTH"),html.Td(None, id="e256RTH")])
eng_write_latency = html.Tr([html.Td("Write Latency (ms)", id="eWL"),html.Td(None, id="e4WL"),html.Td(None, id="e100WL"),html.Td(None, id="e1WL"),html.Td(None, id="e5WL"),html.Td(None, id="e36WL"),html.Td(None, id="e64WL"),html.Td(None, id="e128WL"),html.Td(None, id="e256WL")])
eng_read_latency = html.Tr([html.Td("Read Latency (ms)", id="eRL"),html.Td(None, id="e4RL"),html.Td(None, id="e100RL"),html.Td(None, id="e1RL"),html.Td(None, id="e5RL"),html.Td(None, id="e36RL"),html.Td(None, id="e64RL"),html.Td(None, id="e128RL"),html.Td(None, id="e256RL")])
eng_iops_write = html.Tr([html.Td("Write IOPS", id="WIOPS"),html.Td(None, id="e4WIOPS"),html.Td(None, id="e100WIOPS"),html.Td(None, id="e1WIOPS"),html.Td(None, id="e5WIOPS"),html.Td(None, id="e36WIOPS"),html.Td(None, id="e64WIOPS"),html.Td(None, id="e128WIOPS"),html.Td(None, id="e256WIOPS")])
eng_iops_read = html.Tr([html.Td("Read IOPS", id="RIOPS"),html.Td(None, id="e4RIOPS"),html.Td(None, id="e100RIOPS"),html.Td(None, id="e1RIOPS"),html.Td(None, id="e5RIOPS"),html.Td(None, id="e36RIOPS"),html.Td(None, id="e64RIOPS"),html.Td(None, id="e128RIOPS"),html.Td(None, id="e256RIOPS")])
eng_ttfb_write = html.Tr([html.Td("Write TTFB (ms)", id="WTTFB"),html.Td(None, id="e4WTTFB"),html.Td(None, id="e100WTTFB"),html.Td(None, id="e1WTTFB"),html.Td(None, id="e5WTTFB"),html.Td(None, id="e36WTTFB"),html.Td(None, id="e64WTTFB"),html.Td(None, id="e128WTTFB"),html.Td(None, id="e256WTTFB")])
eng_ttfb_read = html.Tr([html.Td("Read TTFB (ms)", id="RTTFB"),html.Td(None, id="e4RTTFB"),html.Td(None, id="e100RTTFB"),html.Td(None, id="e1RTTFB"),html.Td(None, id="e5RTTFB"),html.Td(None, id="e36RTTFB"),html.Td(None, id="e64RTTFB"),html.Td(None, id="e128RTTFB"),html.Td(None, id="e256RTTFB")])

eng_perf1_head = [
    html.Thead(html.Tr([html.Th("Statistics"),html.Th("4 KB"),html.Th("100 KB"),html.Th("1 MB"),html.Th("5 MB"),html.Th("36 MB"),html.Th("64 MB"),html.Th("128 MB"),html.Th("256 MB")]))
]

### ====================================================================================
# Eng report page - Table 6 : S3 bench performance metadata latencies
### ====================================================================================
eng_perf2_caption = [
    html.Caption(html.Tr([html.Th("Metadata Latencies (captured with 1KB object)")])),
]
t21 = html.Tr([html.Td("Add / Edit Object Tags", id="puttag"),html.Td(None, id="puttag_value")])
t22 = html.Tr([html.Td("Read Object Tags", id="gettag"),html.Td(None, id="gettag_value")])
t23 = html.Tr([html.Td("Read Object Metadata", id="headobj"),html.Td(None, id="headobj_value")])

eng_perf2_head = [
    html.Thead(html.Tr([html.Th("Operation Latency (ms)"),html.Th("Response Time")]))
]

### ====================================================================================
# Eng report page - Table 6 : HS & Cos bench performance statistics
### ====================================================================================
eng_perf3_caption = [
    html.Caption(html.Tr([html.Th("Multiple Buckets Performance Statistics (Average) using HSBench and COSBench")])),
]
t31 = html.Tr([html.Td(["Hsbench",html.Br(),"1 Bucket",html.Br(),"1000 Objects",html.Br(),"100 Sessions"], rowSpan=6, id = "hsbench_main_1"), html.Td("Write Throughput (MBps)", id="HS1WTH"),html.Td(None, id="e4HS1WTH"),html.Td(None, id="e100HS1WTH"),html.Td(None, id="e1HS1WTH"),html.Td(None, id="e5HS1WTH"),html.Td(None, id="e36HS1WTH"),html.Td(None, id="e64HS1WTH"),html.Td(None, id="e128HS1WTH"),html.Td(None, id="e256HS1WTH")])
t32 = html.Tr([html.Td("Read Throughput (MBps)", id="HS1RTH"),html.Td(None, id="e4HS1RTH"),html.Td(None, id="e100HS1RTH"),html.Td(None, id="e1HS1RTH"),html.Td(None, id="e5HS1RTH"),html.Td(None, id="e36HS1RTH"),html.Td(None, id="e64HS1RTH"),html.Td(None, id="e128HS1RTH"),html.Td(None, id="e256HS1RTH")])
t34 = html.Tr([html.Td("Read Latency (ms)", id="HS1RL"),html.Td(None, id="e4HS1RL"),html.Td(None, id="e100HS1RL"),html.Td(None, id="e1HS1RL"),html.Td(None, id="e5HS1RL"),html.Td(None, id="e36HS1RL"),html.Td(None, id="e64HS1RL"),html.Td(None, id="e128HS1RL"),html.Td(None, id="e256HS1RL")])
t33 = html.Tr([html.Td("write Latency (ms)", id="HS1WL"),html.Td(None, id="e4HS1WL"),html.Td(None, id="e100HS1WL"),html.Td(None, id="e1HS1WL"),html.Td(None, id="e5HS1WL"),html.Td(None, id="e36HS1WL"),html.Td(None, id="e64HS1WL"),html.Td(None, id="e128HS1WL"),html.Td(None, id="e256HS1WL")])
t35 = html.Tr([html.Td("Write IOPS", id="HS1WIOPS"),html.Td(None, id="e4HS1WIOPS"),html.Td(None, id="e100HS1WIOPS"),html.Td(None, id="e1HS1WIOPS"),html.Td(None, id="e5HS1WIOPS"),html.Td(None, id="e36HS1WIOPS"),html.Td(None, id="e64HS1WIOPS"),html.Td(None, id="e128HS1WIOPS"),html.Td(None, id="e256HS1WIOPS")])
t36 = html.Tr([html.Td("Read IOPS", id="HS1RIOPS"),html.Td(None, id="e4HS1RIOPS"),html.Td(None, id="e100HS1RIOPS"),html.Td(None, id="e1HS1RIOPS"),html.Td(None, id="e5HS1RIOPS"),html.Td(None, id="e36HS1RIOPS"),html.Td(None, id="e64HS1RIOPS"),html.Td(None, id="e128HS1RIOPS"),html.Td(None, id="e256HS1RIOPS")])

t37 = html.Tr([html.Td(["Hsbench",html.Br(),"10 Buckets",html.Br(),"100 Objects",html.Br(),"100 Sessions"], rowSpan=6, id = "hsbench_main_2"), html.Td("Write Throughput (MBps)", id="HS2WTH"),html.Td(None, id="e4HS2WTH"),html.Td(None, id="e100HS2WTH"),html.Td(None, id="e1HS2WTH"),html.Td(None, id="e5HS2WTH"),html.Td(None, id="e36HS2WTH"),html.Td(None, id="e64HS2WTH"),html.Td(None, id="e128HS2WTH"),html.Td(None, id="e256HS2WTH")])
t38 = html.Tr([html.Td("Read Throughput (MBps)", id="HS2RTH"),html.Td(None, id="e4HS2RTH"),html.Td(None, id="e100HS2RTH"),html.Td(None, id="e1HS2RTH"),html.Td(None, id="e5HS2RTH"),html.Td(None, id="e36HS2RTH"),html.Td(None, id="e64HS2RTH"),html.Td(None, id="e128HS2RTH"),html.Td(None, id="e256HS2RTH")])
t39 = html.Tr([html.Td("Read Latency (ms)", id="HS2RL"),html.Td(None, id="e4HS2RL"),html.Td(None, id="e100HS2RL"),html.Td(None, id="e1HS2RL"),html.Td(None, id="e5HS2RL"),html.Td(None, id="e36HS2RL"),html.Td(None, id="e64HS2RL"),html.Td(None, id="e128HS2RL"),html.Td(None, id="e256HS2RL")])
t310 = html.Tr([html.Td("write Latency (ms)", id="HS2WL"),html.Td(None, id="e4HS2WL"),html.Td(None, id="e100HS2WL"),html.Td(None, id="e1HS2WL"),html.Td(None, id="e5HS2WL"),html.Td(None, id="e36HS2WL"),html.Td(None, id="e64HS2WL"),html.Td(None, id="e128HS2WL"),html.Td(None, id="e256HS2WL")])
t311 = html.Tr([html.Td("Write IOPS", id="HS2WIOPS"),html.Td(None, id="e4HS2WIOPS"),html.Td(None, id="e100HS2WIOPS"),html.Td(None, id="e1HS2WIOPS"),html.Td(None, id="e5HS2WIOPS"),html.Td(None, id="e36HS2WIOPS"),html.Td(None, id="e64HS2WIOPS"),html.Td(None, id="e128HS2WIOPS"),html.Td(None, id="e256HS2WIOPS")])
t312 = html.Tr([html.Td("Read IOPS", id="HS2RIOPS"),html.Td(None, id="e4HS2RIOPS"),html.Td(None, id="e100HS2RIOPS"),html.Td(None, id="e1HS2RIOPS"),html.Td(None, id="e5HS2RIOPS"),html.Td(None, id="e36HS2RIOPS"),html.Td(None, id="e64HS2RIOPS"),html.Td(None, id="e128HS2RIOPS"),html.Td(None, id="e256HS2RIOPS")])

t313 = html.Tr([html.Td(["Hsbench",html.Br(),"50 Buckets",html.Br(),"100 Objects",html.Br(),"100 Sessions"], rowSpan=6, id = "hsbench_main_3"), html.Td("Write Throughput (MBps)", id="HS3WTH"),html.Td(None, id="e4HS3WTH"),html.Td(None, id="e100HS3WTH"),html.Td(None, id="e1HS3WTH"),html.Td(None, id="e5HS3WTH"),html.Td(None, id="e36HS3WTH"),html.Td(None, id="e64HS3WTH"),html.Td(None, id="e128HS3WTH"),html.Td(None, id="e256HS3WTH")])
t314 = html.Tr([html.Td("Read Throughput (MBps)", id="HS3RTH"),html.Td(None, id="e4HS3RTH"),html.Td(None, id="e100HS3RTH"),html.Td(None, id="e1HS3RTH"),html.Td(None, id="e5HS3RTH"),html.Td(None, id="e36HS3RTH"),html.Td(None, id="e64HS3RTH"),html.Td(None, id="e128HS3RTH"),html.Td(None, id="e256HS3RTH")])
t315= html.Tr([html.Td("Read Latency (ms)", id="HS3RL"),html.Td(None, id="e4HS3RL"),html.Td(None, id="e100HS3RL"),html.Td(None, id="e1HS3RL"),html.Td(None, id="e5HS3RL"),html.Td(None, id="e36HS3RL"),html.Td(None, id="e64HS3RL"),html.Td(None, id="e128HS3RL"),html.Td(None, id="e256HS3RL")])
t316 = html.Tr([html.Td("write Latency (ms)", id="HS3WL"),html.Td(None, id="e4HS3WL"),html.Td(None, id="e100HS3WL"),html.Td(None, id="e1HS3WL"),html.Td(None, id="e5HS3WL"),html.Td(None, id="e36HS3WL"),html.Td(None, id="e64HS3WL"),html.Td(None, id="e128HS3WL"),html.Td(None, id="e256HS3WL")])
t317 = html.Tr([html.Td("Write IOPS", id="HS3WIOPS"),html.Td(None, id="e4HS3WIOPS"),html.Td(None, id="e100HS3WIOPS"),html.Td(None, id="e1HS3WIOPS"),html.Td(None, id="e5HS3WIOPS"),html.Td(None, id="e36HS3WIOPS"),html.Td(None, id="e64HS3WIOPS"),html.Td(None, id="e128HS3WIOPS"),html.Td(None, id="e256HS3WIOPS")])
t318 = html.Tr([html.Td("Read IOPS", id="HS3RIOPS"),html.Td(None, id="e4HS3RIOPS"),html.Td(None, id="e100HS3RIOPS"),html.Td(None, id="e1HS3RIOPS"),html.Td(None, id="e5HS3RIOPS"),html.Td(None, id="e36HS3RIOPS"),html.Td(None, id="e64HS3RIOPS"),html.Td(None, id="e128HS3RIOPS"),html.Td(None, id="e256HS3RIOPS")])

t319 = html.Tr([html.Td(["Cosbench",html.Br(),"1 Bucket",html.Br(),"1000 Objects",html.Br(),"100 Sessions"], rowSpan=6, id = "cosbench_main_1"), html.Td("Write Throughput (MBps)", id="COS1WTH"),html.Td(None, id="e4COS1WTH"),html.Td(None, id="e100COS1WTH"),html.Td(None, id="e1COS1WTH"),html.Td(None, id="e5COS1WTH"),html.Td(None, id="e36COS1WTH"),html.Td(None, id="e64COS1WTH"),html.Td(None, id="e128COS1WTH"),html.Td(None, id="e256COS1WTH")])
t320 = html.Tr([html.Td("Read Throughput (MBps)", id="COS1RTH"),html.Td(None, id="e4COS1RTH"),html.Td(None, id="e100COS1RTH"),html.Td(None, id="e1COS1RTH"),html.Td(None, id="e5COS1RTH"),html.Td(None, id="e36COS1RTH"),html.Td(None, id="e64COS1RTH"),html.Td(None, id="e128COS1RTH"),html.Td(None, id="e256COS1RTH")])
t321 = html.Tr([html.Td("Read Latency (ms)", id="COS1RL"),html.Td(None, id="e4COS1RL"),html.Td(None, id="e100COS1RL"),html.Td(None, id="e1COS1RL"),html.Td(None, id="e5COS1RL"),html.Td(None, id="e36COS1RL"),html.Td(None, id="e64COS1RL"),html.Td(None, id="e128COS1RL"),html.Td(None, id="e256COS1RL")])
t322 = html.Tr([html.Td("Write Latency (ms)", id="COS1WL"),html.Td(None, id="e4COS1WL"),html.Td(None, id="e100COS1WL"),html.Td(None, id="e1COS1WL"),html.Td(None, id="e5COS1WL"),html.Td(None, id="e36COS1WL"),html.Td(None, id="e64COS1WL"),html.Td(None, id="e128COS1WL"),html.Td(None, id="e256COS1WL")])
t323 = html.Tr([html.Td("Write IOPS", id="COS1WIOPS"),html.Td(None, id="e4COS1WIOPS"),html.Td(None, id="e100COS1WIOPS"),html.Td(None, id="e1COS1WIOPS"),html.Td(None, id="e5COS1WIOPS"),html.Td(None, id="e36COS1WIOPS"),html.Td(None, id="e64COS1WIOPS"),html.Td(None, id="e128COS1WIOPS"),html.Td(None, id="e256COS1WIOPS")])
t324 = html.Tr([html.Td("Read IOPS", id="COS1RIOPS"),html.Td(None, id="e4COS1RIOPS"),html.Td(None, id="e100COS1RIOPS"),html.Td(None, id="e1COS1RIOPS"),html.Td(None, id="e5COS1RIOPS"),html.Td(None, id="e36COS1RIOPS"),html.Td(None, id="e64COS1RIOPS"),html.Td(None, id="e128COS1RIOPS"),html.Td(None, id="e256COS1RIOPS")])

t325 = html.Tr([html.Td(["Cosbench",html.Br(),"10 Buckets",html.Br(),"100 Objects",html.Br(),"100 Sessions"], rowSpan=6, id = "cosbench_main_2"), html.Td("Write Throughput (MBps)", id="COS2WTH"),html.Td(None, id="e4COS2WTH"),html.Td(None, id="e100COS2WTH"),html.Td(None, id="e1COS2WTH"),html.Td(None, id="e5COS2WTH"),html.Td(None, id="e36COS2WTH"),html.Td(None, id="e64COS2WTH"),html.Td(None, id="e128COS2WTH"),html.Td(None, id="e256COS2WTH")])
t326 = html.Tr([html.Td("Read Throughput (MBps)", id="COS2RTH"),html.Td(None, id="e4COS2RTH"),html.Td(None, id="e100COS2RTH"),html.Td(None, id="e1COS2RTH"),html.Td(None, id="e5COS2RTH"),html.Td(None, id="e36COS2RTH"),html.Td(None, id="e64COS2RTH"),html.Td(None, id="e128COS2RTH"),html.Td(None, id="e256COS2RTH")])
t327 = html.Tr([html.Td("Read Latency (ms)", id="COS2RL"),html.Td(None, id="e4COS2RL"),html.Td(None, id="e100COS2RL"),html.Td(None, id="e1COS2RL"),html.Td(None, id="e5COS2RL"),html.Td(None, id="e36COS2RL"),html.Td(None, id="e64COS2RL"),html.Td(None, id="e128COS2RL"),html.Td(None, id="e256COS2RL")])
t328 = html.Tr([html.Td("Write Latency (ms)", id="COS2WL"),html.Td(None, id="e4COS2WL"),html.Td(None, id="e100COS2WL"),html.Td(None, id="e1COS2WL"),html.Td(None, id="e5COS2WL"),html.Td(None, id="e36COS2WL"),html.Td(None, id="e64COS2WL"),html.Td(None, id="e128COS2WL"),html.Td(None, id="e256COS2WL")])
t329 = html.Tr([html.Td("Write IOPS", id="COS2WIOPS"),html.Td(None, id="e4COS2WIOPS"),html.Td(None, id="e100COS2WIOPS"),html.Td(None, id="e1COS2WIOPS"),html.Td(None, id="e5COS2WIOPS"),html.Td(None, id="e36COS2WIOPS"),html.Td(None, id="e64COS2WIOPS"),html.Td(None, id="e128COS2WIOPS"),html.Td(None, id="e256COS2WIOPS")])
t330 = html.Tr([html.Td("Read IOPS", id="COS2RIOPS"),html.Td(None, id="e4COS2RIOPS"),html.Td(None, id="e100COS2RIOPS"),html.Td(None, id="e1COS2RIOPS"),html.Td(None, id="e5COS2RIOPS"),html.Td(None, id="e36COS2RIOPS"),html.Td(None, id="e64COS2RIOPS"),html.Td(None, id="e128COS2RIOPS"),html.Td(None, id="e256COS2RIOPS")])

t331 = html.Tr([html.Td(["Cosbench",html.Br(),"50 Buckets",html.Br(),"100 Objects",html.Br(),"100 Sessions"], rowSpan=6, id = "cosbench_main_3"), html.Td("Write Throughput (MBps)", id="COS3WTH"),html.Td(None, id="e4COS3WTH"),html.Td(None, id="e100COS3WTH"),html.Td(None, id="e1COS3WTH"),html.Td(None, id="e5COS3WTH"),html.Td(None, id="e36COS3WTH"),html.Td(None, id="e64COS3WTH"),html.Td(None, id="e128COS3WTH"),html.Td(None, id="e256COS3WTH")])
t332 = html.Tr([html.Td("Read Throughput (MBps)", id="COS3RTH"),html.Td(None, id="e4COS3RTH"),html.Td(None, id="e100COS3RTH"),html.Td(None, id="e1COS3RTH"),html.Td(None, id="e5COS3RTH"),html.Td(None, id="e36COS3RTH"),html.Td(None, id="e64COS3RTH"),html.Td(None, id="e128COS3RTH"),html.Td(None, id="e256COS3RTH")])
t333= html.Tr([html.Td("Read Latency (ms)", id="COS3RL"),html.Td(None, id="e4COS3RL"),html.Td(None, id="e100COS3RL"),html.Td(None, id="e1COS3RL"),html.Td(None, id="e5COS3RL"),html.Td(None, id="e36COS3RL"),html.Td(None, id="e64COS3RL"),html.Td(None, id="e128COS3RL"),html.Td(None, id="e256COS3RL")])
t334 = html.Tr([html.Td("Write Latency (ms)", id="COS3WL"),html.Td(None, id="e4COS3WL"),html.Td(None, id="e100COS3WL"),html.Td(None, id="e1COS3WL"),html.Td(None, id="e5COS3WL"),html.Td(None, id="e36COS3WL"),html.Td(None, id="e64COS3WL"),html.Td(None, id="e128COS3WL"),html.Td(None, id="e256COS3WL")])
t335 = html.Tr([html.Td("Write IOPS", id="COS3WIOPS"),html.Td(None, id="e4COS3WIOPS"),html.Td(None, id="e100COS3WIOPS"),html.Td(None, id="e1COS3WIOPS"),html.Td(None, id="e5COS3WIOPS"),html.Td(None, id="e36COS3WIOPS"),html.Td(None, id="e64COS3WIOPS"),html.Td(None, id="e128COS3WIOPS"),html.Td(None, id="e256COS3WIOPS")])
t336 = html.Tr([html.Td("Read IOPS", id="COS3RIOPS"),html.Td(None, id="e4COS3RIOPS"),html.Td(None, id="e100COS3RIOPS"),html.Td(None, id="e1COS3RIOPS"),html.Td(None, id="e5COS3RIOPS"),html.Td(None, id="e36COS3RIOPS"),html.Td(None, id="e64COS3RIOPS"),html.Td(None, id="e128COS3RIOPS"),html.Td(None, id="e256COS3RIOPS")])

eng_perf3_head = [
    html.Thead(html.Tr([html.Th("Bench"),html.Th("Statistics"),html.Th("4 KB"),html.Th("100 KB"),html.Th("1 MB"),html.Th("5 MB"),html.Th("36 MB"),html.Th("64 MB"),html.Th("128 MB"),html.Th("256 MB")]))
]

### ====================================================================================
# Eng report page - Table 7 : HS bench bucket ops performance statistics
### ====================================================================================

bucketOps = [
    {'label': 'Average Latency', 'value':'AvgLat'},
    {'label': 'Minimum Latency', 'value':'MinLat'},
    {'label': 'Maximum Latency', 'value':'MaxLat'},
    {'label': 'IOPS', 'value':'Iops'},
    {'label': 'Throughput', 'value':'Mbps'},
    {'label': 'Operations', 'value':'Ops'},
    {'label': 'Execution Time', 'value':'Seconds'},
]
#### -------------------------------------------------------------------------------------------
bucketops_caption = [
    html.Caption(dbc.Row([html.Tr([html.Th("Bucket Operations for")]),
                dcc.Dropdown(
                    id = "Bucket_Ops_Dropdown",
                    options = bucketOps,
                    placeholder="Metrics",
                    value="AvgLat",
                    style = {'width': '300px', 'verticalAlign': 'middle',"margin-right": "15px"}, #,'align-items': 'center', 'justify-content': 'center'
                ),
            html.P(html.Em("(Select one of the Metrics)"),className="card-text",),
    
            ],justify="center", align="center"
            ),
        ),
]

b1 = html.Tr([html.Td(["1 Bucket",html.Br(),"1000 Objects",html.Br(),"100 Sessions"], rowSpan=9, id = "bops1"),html.Td("INIT BCLR", id="IBCLR"),html.Td(None, id="IBCLR4"),html.Td(None, id="IBCLR100"),html.Td(None, id="IBCLR1"),html.Td(None, id="IBCLR5"),html.Td(None, id="IBCLR36"),html.Td(None, id="IBCLR64"),html.Td(None, id="IBCLR128"),html.Td(None, id="IBCLR256")])
b2 = html.Tr([html.Td("INIT BDEL", id="IBDEL"),html.Td(None, id="IBDEL4"),html.Td(None, id="IBDEL100"),html.Td(None, id="IBDEL1"),html.Td(None, id="IBDEL5"),html.Td(None, id="IBDEL36"),html.Td(None, id="IBDEL64"),html.Td(None, id="IBDEL128"),html.Td(None, id="IBDEL256")])
b3 = html.Tr([html.Td("BINIT", id="BINIT"),html.Td(None, id="BINIT4"),html.Td(None, id="BINIT100"),html.Td(None, id="BINIT1"),html.Td(None, id="BINIT5"),html.Td(None, id="BINIT36"),html.Td(None, id="BINIT64"),html.Td(None, id="BINIT128"),html.Td(None, id="BINIT256")])
b4 = html.Tr([html.Td("PUT", id="PUT"),html.Td(None, id="PUT4"),html.Td(None, id="PUT100"),html.Td(None, id="PUT1"),html.Td(None, id="PUT5"),html.Td(None, id="PUT36"),html.Td(None, id="PUT64"),html.Td(None, id="PUT128"),html.Td(None, id="PUT256")])
b5 = html.Tr([html.Td("LIST", id="LIST"),html.Td(None, id="LIST4"),html.Td(None, id="LIST100"),html.Td(None, id="LIST1"),html.Td(None, id="LIST5"),html.Td(None, id="LIST36"),html.Td(None, id="LIST64"),html.Td(None, id="LIST128"),html.Td(None, id="LIST256")])
b6 = html.Tr([html.Td("GET", id="GET"),html.Td(None, id="GET4"),html.Td(None, id="GET100"),html.Td(None, id="GET1"),html.Td(None, id="GET5"),html.Td(None, id="GET36"),html.Td(None, id="GET64"),html.Td(None, id="GET128"),html.Td(None, id="GET256")])
b7 = html.Tr([html.Td("DEL", id="DEL"),html.Td(None, id="DEL4"),html.Td(None, id="DEL100"),html.Td(None, id="DEL1"),html.Td(None, id="DEL5"),html.Td(None, id="DEL36"),html.Td(None, id="DEL64"),html.Td(None, id="DEL128"),html.Td(None, id="DEL256")])
b8 = html.Tr([html.Td("BCLR", id="BCLR"),html.Td(None, id="BCLR4"),html.Td(None, id="BCLR100"),html.Td(None, id="BCLR1"),html.Td(None, id="BCLR5"),html.Td(None, id="BCLR36"),html.Td(None, id="BCLR64"),html.Td(None, id="BCLR128"),html.Td(None, id="BCLR256")])
b9 = html.Tr([html.Td("BDEL", id="BDEL"),html.Td(None, id="BDEL4"),html.Td(None, id="BDEL100"),html.Td(None, id="BDEL1"),html.Td(None, id="BDEL5"),html.Td(None, id="BDEL36"),html.Td(None, id="BDEL64"),html.Td(None, id="BDEL128"),html.Td(None, id="BDEL256")])

b10 = html.Tr([html.Td(["10 Buckets",html.Br(),"100 Objects",html.Br(),"100 Sessions"], rowSpan=9, id = "bops2"),html.Td("INIT BCLR", id="IBCLR1H"),html.Td(None, id="IBCLR41"),html.Td(None, id="IBCLR1001"),html.Td(None, id="IBCLR11"),html.Td(None, id="IBCLR51"),html.Td(None, id="IBCLR361"),html.Td(None, id="IBCLR641"),html.Td(None, id="IBCLR1281"),html.Td(None, id="IBCLR2561")])
b11 = html.Tr([html.Td("INIT BDEL", id="IBDEL1H"),html.Td(None, id="IBDEL41"),html.Td(None, id="IBDEL1001"),html.Td(None, id="IBDEL11"),html.Td(None, id="IBDEL51"),html.Td(None, id="IBDEL361"),html.Td(None, id="IBDEL641"),html.Td(None, id="IBDEL1281"),html.Td(None, id="IBDEL2561")])
b12 = html.Tr([html.Td("BINIT", id="BINIT1H"),html.Td(None, id="BINIT41"),html.Td(None, id="BINIT1001"),html.Td(None, id="BINIT11"),html.Td(None, id="BINIT51"),html.Td(None, id="BINIT361"),html.Td(None, id="BINIT641"),html.Td(None, id="BINIT1281"),html.Td(None, id="BINIT2561")])
b13 = html.Tr([html.Td("PUT", id="PUT1H"),html.Td(None, id="PUT41"),html.Td(None, id="PUT1001"),html.Td(None, id="PUT11"),html.Td(None, id="PUT51"),html.Td(None, id="PUT361"),html.Td(None, id="PUT641"),html.Td(None, id="PUT1281"),html.Td(None, id="PUT2561")])
b14 = html.Tr([html.Td("LIST", id="LIST1H"),html.Td(None, id="LIST41"),html.Td(None, id="LIST1001"),html.Td(None, id="LIST11"),html.Td(None, id="LIST51"),html.Td(None, id="LIST361"),html.Td(None, id="LIST641"),html.Td(None, id="LIST1281"),html.Td(None, id="LIST2561")])
b15 = html.Tr([html.Td("GET", id="GET1H"),html.Td(None, id="GET41"),html.Td(None, id="GET1001"),html.Td(None, id="GET11"),html.Td(None, id="GET51"),html.Td(None, id="GET361"),html.Td(None, id="GET641"),html.Td(None, id="GET1281"),html.Td(None, id="GET2561")])
b16 = html.Tr([html.Td("DEL", id="DEL1H"),html.Td(None, id="DEL41"),html.Td(None, id="DEL1001"),html.Td(None, id="DEL11"),html.Td(None, id="DEL51"),html.Td(None, id="DEL361"),html.Td(None, id="DEL641"),html.Td(None, id="DEL1281"),html.Td(None, id="DEL2561")])
b17 = html.Tr([html.Td("BCLR", id="BCLR1H"),html.Td(None, id="BCLR41"),html.Td(None, id="BCLR1001"),html.Td(None, id="BCLR11"),html.Td(None, id="BCLR51"),html.Td(None, id="BCLR361"),html.Td(None, id="BCLR641"),html.Td(None, id="BCLR1281"),html.Td(None, id="BCLR2561")])
b18 = html.Tr([html.Td("BDEL", id="BDEL1H"),html.Td(None, id="BDEL41"),html.Td(None, id="BDEL1001"),html.Td(None, id="BDEL11"),html.Td(None, id="BDEL51"),html.Td(None, id="BDEL361"),html.Td(None, id="BDEL641"),html.Td(None, id="BDEL1281"),html.Td(None, id="BDEL2561")])

b19 = html.Tr([html.Td(["50 Buckets",html.Br(),"100 Objects",html.Br(),"100 Sessions"], rowSpan=9, id = "bops3"),html.Td("INIT BCLR", id="IBCLR2"),html.Td(None, id="IBCLR42"),html.Td(None, id="IBCLR1002"),html.Td(None, id="IBCLR12"),html.Td(None, id="IBCLR52"),html.Td(None, id="IBCLR362"),html.Td(None, id="IBCLR642"),html.Td(None, id="IBCLR1282"),html.Td(None, id="IBCLR2562")])
b20 = html.Tr([html.Td("INIT BDEL", id="IBDEL2"),html.Td(None, id="IBDEL42"),html.Td(None, id="IBDEL1002"),html.Td(None, id="IBDEL12"),html.Td(None, id="IBDEL52"),html.Td(None, id="IBDEL362"),html.Td(None, id="IBDEL642"),html.Td(None, id="IBDEL1282"),html.Td(None, id="IBDEL2562")])
b21 = html.Tr([html.Td("BINIT", id="BINIT2"),html.Td(None, id="BINIT42"),html.Td(None, id="BINIT1002"),html.Td(None, id="BINIT12"),html.Td(None, id="BINIT52"),html.Td(None, id="BINIT362"),html.Td(None, id="BINIT642"),html.Td(None, id="BINIT1282"),html.Td(None, id="BINIT2562")])
b22 = html.Tr([html.Td("PUT", id="PUT2"),html.Td(None, id="PUT42"),html.Td(None, id="PUT1002"),html.Td(None, id="PUT12"),html.Td(None, id="PUT52"),html.Td(None, id="PUT362"),html.Td(None, id="PUT642"),html.Td(None, id="PUT1282"),html.Td(None, id="PUT2562")])
b23 = html.Tr([html.Td("LIST", id="LIST2"),html.Td(None, id="LIST42"),html.Td(None, id="LIST1002"),html.Td(None, id="LIST12"),html.Td(None, id="LIST52"),html.Td(None, id="LIST362"),html.Td(None, id="LIST642"),html.Td(None, id="LIST1282"),html.Td(None, id="LIST2562")])
b24 = html.Tr([html.Td("GET", id="GET2"),html.Td(None, id="GET42"),html.Td(None, id="GET1002"),html.Td(None, id="GET12"),html.Td(None, id="GET52"),html.Td(None, id="GET362"),html.Td(None, id="GET642"),html.Td(None, id="GET1282"),html.Td(None, id="GET2562")])
b25 = html.Tr([html.Td("DEL", id="DEL2"),html.Td(None, id="DEL42"),html.Td(None, id="DEL1002"),html.Td(None, id="DEL12"),html.Td(None, id="DEL52"),html.Td(None, id="DEL362"),html.Td(None, id="DEL642"),html.Td(None, id="DEL1282"),html.Td(None, id="DEL2562")])
b26 = html.Tr([html.Td("BCLR", id="BCLR2"),html.Td(None, id="BCLR42"),html.Td(None, id="BCLR1002"),html.Td(None, id="BCLR12"),html.Td(None, id="BCLR52"),html.Td(None, id="BCLR362"),html.Td(None, id="BCLR642"),html.Td(None, id="BCLR1282"),html.Td(None, id="BCLR2562")])
b27 = html.Tr([html.Td("BDEL", id="BDEL2"),html.Td(None, id="BDEL42"),html.Td(None, id="BDEL1002"),html.Td(None, id="BDEL12"),html.Td(None, id="BDEL52"),html.Td(None, id="BDEL362"),html.Td(None, id="BDEL642"),html.Td(None, id="BDEL1282"),html.Td(None, id="BDEL2562")])

bucketops_head = [
    html.Thead(html.Tr([html.Th("Buckets"),html.Th("Operations"),html.Th("4KB"),html.Th("100KB"),html.Th("1MB"),html.Th("5MB"),html.Th("36MB"),html.Th("64MB"),html.Th("128MB"),html.Th("256MB")]))
]

#### -------------------------------------------------------------------------------------------
tab1_content = dbc.Card(
    dbc.CardBody(
        [
            html.P(html.U("Engineers Report"), style={'text-align':'center','font-size':'30px','font-weight': 'bold'}),
            html.P(html.H5("Product: ", id = "product_heading_eng"),className="card-text",),
            html.P(html.H5("Build: ", id = "build_heading_eng"),className="card-text",),
            html.P(html.H5("Date: ", id = "date_heading_eng"),className="card-text"),
            
            dbc.Table(t1_caption + t1_head + [html.Tbody([t1r1,t1r2,t1r3,t1r4,t1r5,t1r6])],
            className = "caption-Top col-xs-6",
            hover=True,
            responsive=True,
            striped=True,
            style = {'textAlign': 'center'},
            id = "ET1",
            ),

            dbc.Table(t2_caption + t2_head + [html.Tbody([t2r1,t2r2,t2r3,t2r4,t2r5,t2r6])],
            className = "caption-Top col-xs-6",
            hover=True,
            responsive=True,
            striped=True,
            style = {'textAlign': 'center'},
            id = "ET2",
            ),

            dbc.Table(t3_caption + t3_head + [html.Tbody([t3r1,t3r2,t3r3,t3r4,t3r5,t3r6,t3r7,t3r8,t3r10,t3r11,t3r9])],
            className = "caption-Top col-xs-6",
            hover=True,
            responsive=True,
            striped=True,
            style = {'textAlign': 'center'},
            id = "ET3",
            ),

            dbc.Table(t5_caption + t5_head + [html.Tbody([t5r1,t5r2,t5r3,t5r4,t5r5,t5r6,t5r7,t5r8,t5r9,t5r11,t5r10,t5r15,t5r12,t5r13,t5r14])],
            className = "caption-Top col-xs-6",
            hover=True,
            responsive=True,
            striped=True,
            style = {'textAlign': 'center'},
            id = "ET7",
            ),

            dbc.Table(eng_perf1_caption + eng_perf1_head + [html.Tbody([eng_write_throughput, eng_read_throughput,
                eng_write_latency, eng_read_latency, eng_iops_write, eng_iops_read, eng_ttfb_write, eng_ttfb_read])],
            className = "caption-Top col-xs-6",
            hover=True,
            responsive=True,
            striped=True,
            style = {'textAlign': 'center'},
            id = "ET4",
            ),

            dbc.Table(eng_perf2_caption + eng_perf2_head + [html.Tbody([t21, t22, t23])],
            className = "caption-Top col-xs-6",
            hover=True,
            responsive=True,
            striped=True,
            style = {'textAlign': 'center'},
            id = "ET5",
            ),

            dbc.Table(eng_perf3_caption + eng_perf3_head + [html.Tbody([t31,t32,t33,t34,t35,t36,t37,t38,t39,t310,t311,t312,t313,t314,t315,
                t316,t317,t318,t319,t320,t321,t322,t323,t324,t325,t326,t327,t328,t329,t330,t331,t332,t333,t334,t335,t336])],
            className = "table-1",
            hover=True,
            responsive=True,
            striped=True,
            style = {'textAlign': 'center'},
            id = "ET6",
            ),

            dbc.Table(bucketops_caption + bucketops_head + [html.Tbody([b1,b2,b3,b4,b5,b6,b7,b9,b8,b10,b11,b12,b13,b14,b15,b16,b18,b17,\
                    b19,b20,b21,b22,b23,b24,b25,b27,b26])],
            className = "caption-Top col-xs-6",
            hover=True,
            responsive=True,
            striped=True,
            style = {'textAlign': 'center'},
            id = "B1",
            ),
            html.Th("Detailed Reported Bugs", id= 'detailed_report_header'),

            dbc.Row([dbc.Col(html.Div(id='build_report_div', className='text-center',style={'margin-top': 10, 'margin-bottom': 20}))])
        ]
    ),
    className="flex-sm-fill nav-link active",
)
#### Eng report defination ends ================================================================

### ============================================================================================
# Exe report page - Table 1 : Reported Bugs
### ============================================================================================
xt1_caption = [
    html.Caption(html.Tr([html.Th("Reported Bugs")])),
]
xt1r1 = html.Tr([html.Td("Total"),html.Td(None, id="exe_total_test"),html.Td(None, id="exe_total_product")], id="exe_total")
xt1r2 = html.Tr([html.Td("Blocker"),html.Td(None, id="exe_blocker_test"),html.Td(None, id="exe_blocker_product")],id="exe_blocker")
xt1r3 = html.Tr([html.Td("Critical"),html.Td(None, id="exe_critical_test"),html.Td(None, id="exe_critical_product")],id="exe_critical")
xt1r4 = html.Tr([html.Td("Major"),html.Td(None, id="exe_major_test"),html.Td(None, id="exe_major_product")],id="exe_major")
xt1r5 = html.Tr([html.Td("Minor"),html.Td(None, id="exe_minor_test"),html.Td(None, id="exe_minor_product")],id="exe_minor")
xt1r6 = html.Tr([html.Td("Trivial"),html.Td(None, id="exe_trivial_test"),html.Td(None, id="exe_trivial_product")], id="exe_trivial")
xt1_head = [
    html.Thead(html.Tr([html.Th("Priority"),html.Th("Test Infra Issues"),html.Th("CORTX SW Issues")]))
]

### ============================================================================================
# Exe report page - Table 2 : Overall QA report
#### ===========================================================================================
xt2_caption = [
    html.Caption(html.Tr([html.Th("Overall QA Report")])),
]
xt2r1 = html.Tr([html.Td("Total"),html.Td(None, id = "exe_qa_total_current"),html.Td(None, id="exe_qa_total_previous")], id="exe_qa_total")
xt2r2 = html.Tr([html.Td("Pass"),html.Td(None, id="exe_qa_pass_current"),html.Td(None, id="exe_qa_pass_previous")],id="exe_qa_pass")
xt2r3 = html.Tr([html.Td("Fail"),html.Td(None, id="exe_qa_fail_current"),html.Td(None, id="exe_qa_fail_previous")],id="exe_qa_fail")
xt2r4 = html.Tr([html.Td("Aborted"),html.Td(None, id="exe_qa_aborted_current"),html.Td(None, id="exe_qa_aborted_previous")],id="exe_qa_aborted")
xt2r5 = html.Tr([html.Td("Blocked"),html.Td(None, id="exe_qa_blocked_current"),html.Td(None, id="exe_qa_blocked_previous")],id="exe_qa_blocked")
xt2r6 = html.Tr([html.Td("To Do"),html.Td(None, id="exe_qa_todo_current"),html.Td(None, id="exe_qa_todo_previous")],id="exe_qa_todo")
xt2_head = [
    html.Thead(html.Tr([html.Th("Category"),html.Th("Current",id="qa_current_exe"),html.Th("Previous", id="qa_previous_exe")]))
]

### ====================================================================================
# Exe report page - Table 3 : Feature breakdown summary
### ====================================================================================
xt3_caption = [
    html.Caption(html.Tr([html.Th("Feature Breakdown Summary")])),
]
xt3_head = [
   
    html.Thead(html.Tr([html.Th("Feature"),html.Th("Total"),html.Th("Passed"), html.Th("Failed"),html.Th("% Passed"), html.Th("% Failed")]))
]
xt3r1 = html.Tr([html.Td("User Operations",id="User_operations"),html.Td(None, id="user_op_total"),html.Td(None, id="user_op_pass"),html.Td(None, id="user_op_fail"),html.Td(None, id="user_op_ppass"),html.Td(None, id="user_op_pfail")])
xt3r2 = html.Tr([html.Td("Scalability",id="Scalability"),html.Td(None, id="scale_total"),html.Td(None, id="scale_pass"),html.Td(None, id="scale_fail"),html.Td(None, id="scale_ppass"),html.Td(None, id="scale_pfail")])
xt3r3 = html.Tr([html.Td("Availability",id="Availability"),html.Td(None, id="avail_total"),html.Td(None, id="avail_pass"),html.Td(None, id="avail_fail"),html.Td(None, id="avail_ppass"),html.Td(None, id="avail_pfail")])
xt3r4 = html.Tr([html.Td("Longevity",id="Longevity"),html.Td(None, id="long_total"),html.Td(None, id="long_pass"),html.Td(None, id="long_fail"),html.Td(None, id="long_ppass"),html.Td(None, id="long_pfail")])
#xt3r5 = html.Tr([html.Td("Performance",id="Performance"),html.Td(None, id="perf_total"),html.Td(None, id="perf_pass"),html.Td(None, id="perf_fail"),html.Td(None, id="perf_ppass"),html.Td(None, id="perf_pfail")])
xt3r6 = html.Tr([html.Td("Use Cases",id="Use_cases"),html.Td(None, id="ucases_total"),html.Td(None, id="ucases_pass"),html.Td(None, id="ucases_fail"),html.Td(None, id="ucases_ppass"),html.Td(None, id="ucases_pfail")])
xt3r7 = html.Tr([html.Td("Orphans",id='Orphans'),html.Td(None, id='orphans_total'),html.Td(None, id="orphans_pass"),html.Td(None, id="orphans_fail"),html.Td(None, id="orphans_ppass"),html.Td(None, id="orphans_pfail")])
xt3r8 = html.Tr([html.Td("Total",id="xTotal"),html.Td(None, id="xtotal_total"),html.Td(None, id="xtotal_pass"),html.Td(None, id="xtotal_fail"),html.Td(None, id="xtotal_ppass"),html.Td(None, id="xtotal_pfail")])

### ====================================================================================
# Exe report page - Table 4 : Code maturity
### ====================================================================================

xt4_caption = [
    html.Caption(html.Tr([html.Th("Code Maturity")])),
]

xt4_head = [
   
    html.Thead(html.Tr([html.Th("Category"),html.Th("current", id="code_maturity_build_current"),html.Th("Prev Release", id ="CM2"),html.Th("Prev Release", id= "CM3"),html.Th("Prev Release", id = "CM4")]))
]

xt4r1 = html.Tr([html.Td("Total", id="exe_total4"),html.Td(None, id="total_r1"),html.Td(None, id="total_r2"),html.Td(None, id="total_r3"),html.Td(None, id="total_r4")], id="total_row")
xt4r2 = html.Tr([html.Td("Pass", id="exe_pass"),html.Td(None, id="pass_r1"),html.Td(None, id="pass_r2"),html.Td(None, id="pass_r3"),html.Td(None, id="pass_r4")], id = "pass_row")
xt4r3 = html.Tr([html.Td("Fail", id="exe_fail"),html.Td(None, id="fail_r1"),html.Td(None, id="fail_r2"),html.Td(None, id="fail_r3"),html.Td(None, id="fail_r4")], id= "fail_row")
xt4r4 = html.Tr([html.Td("Aborted", id="exe_aborted"),html.Td(None, id="abort_r1"),html.Td(None, id="abort_r2"),html.Td(None, id="abort_r3"),html.Td(None, id="abort_r4")], id = "abort_row")
xt4r5 = html.Tr([html.Td("Blocked", id="exe_blocked"),html.Td(None, id="blocked_r1"),html.Td(None, id="blocked_r2"),html.Td(None, id="blocked_r3"),html.Td(None, id="blocked_r4")], id = "blocked_row")

### ===========================================================================================
# Exe report page - Table 5 : Performance S3 bench staistics
### ===========================================================================================
exe_perf_caption = [
    html.Caption(html.Tr([html.Th("Single Bucket Performance Statistics (Average) using S3Bench - in a Nutshell")])),
]
write_throughput = html.Tr([html.Td("Write Throughput (MBps)", id="WTH"),html.Td(None, id="WTH4"),html.Td(None, id="WTH256")])
read_throughput = html.Tr([html.Td("Read Throughput (MBps)", id="RTH"),html.Td(None, id="RTH4"),html.Td(None, id="RTH256")])
write_latency = html.Tr([html.Td("Write Latency (ms)", id="WL"),html.Td(None, id="WL4"),html.Td(None, id="WL256")])
read_latency = html.Tr([html.Td("Read Latency (ms)", id="RL"),html.Td(None, id="RL4"),html.Td(None, id="RL256")])

exe_perf_head = [
    html.Thead(html.Tr([html.Th("Statistics"),html.Th("4 KB Object"),html.Th("256 MB Object")]))
]
#### -------------------------------------------------------------------------------------------
tab2_content = dbc.Card(
    dbc.CardBody(
        [
            html.P(html.U("Executive Report"), style={'text-align':'center','font-size':'30px','font-weight': 'bold'}),
            html.P(html.H5("Product: ", id = "product_heading_exe"),className="card-text",),
            html.P(html.H5("Build: ", id = "build_heading_exe"),className="card-text",),
            html.P(html.H5("Date: ", id = "date_heading_exe"),className="card-text",),
            
            dbc.Table(xt1_caption + xt1_head + [html.Tbody([xt1r1,xt1r2,xt1r3,xt1r4,xt1r5,xt1r6])],
            className = "caption-Top col-xs-6",
            hover=True,
            responsive=True,
            striped=True,
            style = {'textAlign': 'center'},
            id = "XT1",
            ),

            dbc.Table(xt2_caption + xt2_head + [html.Tbody([xt2r1,xt2r2,xt2r3,xt2r4,xt2r5,xt2r6])],
            className = "caption-Top col-xs-6",
            hover=True,
            responsive=True,
            striped=True,
            style = {'textAlign': 'center'},
            id = "XT2",
            ),

            dbc.Table(xt3_caption + xt3_head + [html.Tbody([xt3r1,xt3r2,xt3r3,xt3r4,xt3r6,xt3r7,xt3r8])], # ,xt3r5
            className = "caption-Top col-xs-6",
            hover=True,
            responsive=True,
            striped=True,
            style = {'textAlign': 'center'},
            id = "XT3",
            ),

            dbc.Table(xt4_caption + xt4_head + [html.Tbody([xt4r1,xt4r2,xt4r3,xt4r4,xt4r5])],
            className = "caption-Top col-xs-6 table-1",
            hover=True,
            responsive=True,
            striped=True,
            style = {'textAlign': 'center'},
            id = "XT4",
            ),

            dbc.Table(exe_perf_caption + exe_perf_head + [html.Tbody([write_throughput, read_throughput, write_latency, read_latency])],
            className = "caption-Top col-xs-6",
            hover=True,
            responsive=True,
            striped=True,
            style = {'textAlign': 'center'},
            id = "XT5",
            ),

        ]
    ),
    className="flex-sm-fill nav-link",
)
#### Exe report defination ends ================================================================

#### TAB3: Input for Test Executionwise defects table ==========================================
testPlan_inputs = dbc.Row(
    dbc.Col(dbc.InputGroup([
        dbc.Input(id="test_plan_input",
                  placeholder="Enter , seperated test execution IDs", debounce=True),
        dbc.InputGroupAddon(
            dbc.Button("Get defects!", id="test_plan_submit_button", color="success"),
            addon_type="postpend",
        )], style={'margin': 10}),
        width=5),
    justify="center"
)
#### -------------------------------------------------------------------------------------------
tab3_content = dbc.Card(
    dbc.CardBody(
        [
            testPlan_inputs,
            html.Th("Detailed Test Planwise Reported Bugs", id= 'detailed_report_tab3'),


            dcc.Loading((dbc.Row([dbc.Col(html.Div(id='TP_wise_defects', className='text-center',
                                 style={'margin': 20, 'margin-top': 10, 'margin-bottom': 20}))]))),
        ]
    ),
    className="flex-sm-fill nav-link",
)
#### Defects chart report defination ends ======================================================
#### TAB4 : Performance statistics =============================================================
versions = [
        {'label' : 'Cortx-1.0-Beta', 'value' : 'beta'},
        {'label' : 'Release', 'value' : 'release'},
        {'label' : 'Cortx-1.0', 'value' : 'cortx1'},
        {'label' : 'Custom', 'value' : 'custom'},
        {'label' : 'Main', 'value' : 'main', 'disabled': True}
]
#### -------------------------------------------------------------------------------------------
operations = [
    {'label': 'Both', 'value':'Both'},
    {'label': 'Read', 'value':'read'},
    {'label': 'Write', 'value':'write'},    
]
benchmarks = [
    {'label': 'S3Bench', 'value':'S3bench'},
    {'label': 'COSBench', 'value':'Cosbench'},
    {'label': 'HSBench', 'value':'Hsbench'},
]
config_list = [
        {'label' : '1 Bucket, 1000 Objects, 100 Sessions', 'value' : 'option1'},
        {'label' : '10 Buckets, 100 Objects, 100 Sessions', 'value' : 'option2'},
        {'label' : '50 Buckets, 100 Objects, 100 Sessions', 'value' : 'option3'}
]

Xfilter = [
    {'label': 'Object Size', 'value':'Object Size'},
    {'label': 'Build', 'value':'build'},
]
tab4_content = dbc.Card(
    dbc.CardBody(
        [ 
        html.Th("Graphical representation of S3bench Performance data", id= 'perf_graphs_heading',style={'text-align':'center'}),
        html.Div([dbc.Row(
            [
                dcc.Dropdown(
                    id = "Version_Dropdown",
                    options = versions,
                    placeholder="Build Version",
                ),

                dcc.Dropdown(
                    id = "Filter_Dropdown",
                    options = Xfilter,
                    placeholder="Filter by",
                ),

                dcc.Dropdown(
                    id = 'Build1_Dropdown',
                    placeholder="first choice",
                ),
            
                dcc.Dropdown(
                    id = 'Build2_Dropdown',
                    placeholder="Compare with",
                ),
                dcc.Dropdown(
                    id = "Benchmark_Dropdown",
                    options = benchmarks,
                    placeholder="Benchmark",
                    value = 'S3bench'
                ),
                dcc.Dropdown(
                    id = 'configs_Dropdown',
                    options = config_list,
                    placeholder="Choose configurations",
                    style={'display':'none'}
                    ),
                dcc.Dropdown(
                    id = "Operations_Dropdown",
                    options = operations,
                    placeholder="Operation",
                    value = 'Both'
                ),
                dbc.Button("Get!", id="get_graph_button", color="success",style={'height': '35px'}),
            ],
            justify='center',style={'padding':'10px'}),
            dbc.Row(
              [
                dcc.Graph(id='plot_Throughput'),
                dcc.Graph(id='plot_Latency'),
                dcc.Graph(id='plot_IOPS'),
                dcc.Graph(id='plot_TTFB'),
                dcc.Graph(id='plot'),
              ],
            justify='center',style={'padding':'10px'}),
            dbc.Row(
              [
                html.P('Statistics are displayed only for the builds on which Performance test suite has ran.',className="card-text",style={'margin-top':'10px'})
            ],
            justify='center',style={'padding':'10px'})
        ])
        ]
    ))
#### Performance report defination ends ==============================================================

tabs = dbc.Tabs(
    [
        dbc.Tab(tab2_content, label="Executive Report", style={
                'margin-left': 20, 'margin-right': 20}, label_style={'font-size':'20px'}),
        dbc.Tab(tab1_content, label="Engineers Report", style={
                'margin-left': 20, 'margin-right': 20}, label_style={'font-size':'20px'}),
        dbc.Tab(tab3_content, label='Defect List for Test Execution Plans', style={
        'margin-left': 20, 'margin-right': 20}, label_style={'font-size':'18px'}),
       dbc.Tab(tab4_content, label='Performance', style={
        'margin-left': 20, 'margin-right': 20}, label_style={'font-size':'18px'}),
        
    ],
    className="nav nav nav-pills nav-fill nav-pills flex-column flex-sm-row",
    id = "tabs",
)

#### ==============================================================================================
# Build number input field on top

build_report_header = dbc.Jumbotron(html.H4(html.Em("... looking for build number!")),
                        id="build_report_header",
                        style={'padding': '1em',
                                'background': 'transparent','text-align':'center'})

#### ==============================================================================================
# App configarations
#### ==============================================================================================
version_main = [
        {'label' : 'Cortx-1.0-Beta', 'value' : 'beta'},
        {'label' : 'Release', 'value' : 'release'},
        {'label' : 'Cortx-1.0', 'value' : 'cortx1'},
        {'label' : 'Custom', 'value' : 'custom'},
        {'label' : 'Main', 'value' : 'main', 'disabled': True}
]

input_options = dbc.Row(
    [
        dcc.Dropdown(
            id = "version_main_dropdown",
            options = version_main,
            placeholder="select version",
            style = {'width': '200px', 'verticalAlign': 'middle',"margin-right": "15px"},
        ),

        dcc.Dropdown(
            id = 'table_build_input',
            placeholder="select 1st build",
            style = {'width': '200px', 'verticalAlign': 'middle',"margin-right": "15px"},
        ),
        dbc.Button("Get!", id="table_submit_button", color="success",style={'height': '35px'}),
    ],
    justify='center')

app.layout = html.Div([
    navbar,
    input_options,
    build_report_header,
    tabs,
    
    dcc.Location(id='url', refresh=False),
    toast,
    html.Link(
        rel='stylesheet',
        href='/static/topography.css'
    )]) 

#### App configuration ends =======================================================================

### ===============================================================================================
# Supplimentary functions 
def roundoff(x, base=1):
    if x < 1:
        return round(x, 2)
    if x <26:
        return (int(x))
    return (base * round(x/base))
#### ----------------------------------------------------------------------------------------------
def get_previous_build(current_build, version):
	if version == 'release' and current_build.startswith("release"):
		current_build = current_build[8::]
	found = False
	cursor = mapi.find({'info' : 'build sequence'})
	current_index = 999999
	for doc in cursor:
		for i in range(0, len(doc[version])):
			if doc[version][i] == current_build:
				current_index = i
				found = True
				break

	if found and current_index > 0: 
		prev = doc[version][current_index - 1]
		if version == 'beta':
			return prev
		try:
			int(prev)
			if current_index < 7:
				return 'release_'+prev
			return prev
		except:
			return prev
	else:
		return None
#### ----------------------------------------------------------------------------------------------
def get_input(table_type, ctx, clicks, input_value, enter_input, pathname):
    found_current = False
    current_build = ''
    previous_build = ''
    prop_id = ''
    version = ''
    if not ctx.triggered:
        print('No input yet')
    
    else:
        prop_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if prop_id == 'table_submit_button':
        found_current = True
        current_build = input_value
    elif prop_id == 'table_build_input':
        if enter_input:            
            found_current = True
            current_build = enter_input
            
        else:
            return [None, None, None]
    elif prop_id == 'url' and pathname.startswith('/report/'):
        print('pathname starts with /report/')
        build_search = re.search(r'^\/report\/(.+)', pathname)
        if build_search:
            print('search complete')
            build_number = build_search.group(1).strip()
            print('build number is', build_number)
            found_current = True
            current_build = build_number
        else:
            return [None, None, None]
    else:
        return [None, None, None]
    print("Attempt for build {}".format(current_build))
    if table_type == 'cft':
        item = mapi.find({'info' : 'build sequence'})
        for doc in item :
            if current_build not in doc['beta'] and current_build not in doc['release'] and current_build not in doc['cortx1']:
                return [None, None, None]
            elif current_build in doc['beta']:
                version = 'beta'
            elif current_build in doc['release']:
                version = 'release'
        if found_current:
            previous_build = get_previous_build(current_build, version)
            try:
                int(current_build)
                if doc['release'].index(current_build) < 7:
                    current_build = 'release_' + current_build
                    previous_build = 'release_' + previous_build
            except Exception as exe:
                print(exe)

    if table_type == 'perf':
        item = perfDb.results.find({'Title' : 'Main Chain'})
        for doc in item:
            if current_build not in doc['beta'] and current_build not in doc['release'] and current_build not in doc['cortx1'] and current_build not in doc['custom']:
                return [None, None, None]
        if found_current:
            previous_build = None    

    return [current_build, previous_build, version]
#### ----------------------------------------------------------------------------------------------
def get_JIRA_details(auth_jira, number):
    issue = auth_jira.issue(number)
    issuePriority = str(issue.fields.priority)
    status =str(issue.fields.status)
    return issuePriority, status
#### ----------------------------------------------------------------------------------------------
def getDefectListFromTe(te):
    jiraURL = "https://jts.seagate.com/"
    options = {'server': jiraURL}
    auth_jira = JIRA(options, basic_auth=(username, password))
    TEID = te.upper()
    issue=auth_jira.issue(TEID)
    co = issue.fields.labels
    te_label = []
    for i in range(len(co)):
        te_label.append(str(co[i]))
    jiraLink = 'https://jts.seagate.com/rest/raven/1.0/api/testexec/' + str(TEID) + '/test?detailed=true'
    response = requests.get(jiraLink, auth=(username, password))
    test_execution_data = response.json()
    defects_list = {}
    finalDefectL = []
    for value in test_execution_data:
        try:		
            numDefectLinked = len(value['defects'])
            for defectNum in range(numDefectLinked):
                defects_list = {}
                defects_list['defects_item'] = value['defects'][defectNum]['key']
                defects_list['defects_summary'] = value['defects'][defectNum]['summary']
                Dpriority, status = get_JIRA_details(auth_jira, value['defects'][defectNum]['key'])
                defects_list['defect_priority'] = Dpriority
                defects_list['status'] = status
                defects_list['TE_ID'] = TEID
                defects_list['Test_ID'] = value['key']
                defects_list['TestPlan_ID'] = TEID
                defects_list['testExecutionLabels'] = te_label
                finalDefectL.append(defects_list)
        except Exception as exe:
            print(exe)
    return finalDefectL
#### ----------------------------------------------------------------------------------------------
def getDefectList(finalTeList):
    finalDefectList = []
    with concurrent.futures.ProcessPoolExecutor() as executor:
        defectList = {executor.submit(getDefectListFromTe, teJira): teJira for teJira in finalTeList}
        for future in concurrent.futures.as_completed(defectList):
            try:
                data = future.result()
                finalDefectList.extend(data)
            except Exception as exc:
                print(exc)

    return finalDefectList
#### ----------------------------------------------------------------------------------------------
def get_percent(outof, value):
    if not (outof):
        return "NA"
    return roundoff(value * 100 / outof, 2)

#### App callbacks begins =========================================================================
@app.callback(
    [dash.dependencies.Output('table_build_input', 'options')],
    [dash.dependencies.Input('version_main_dropdown', 'value')],
)
def fetch_build_for_dropdown(value):
    if not value:
        raise PreventUpdate
    if value == 'beta':
        version = 'beta'
    elif value == 'release':
        version = 'release'

    elif value== 'cortx1':
        cursor = mapi.find({'info' : 'build sequence'})
        builds = cursor[0][value]
        list1 = builds
        result = [ele for ele in reversed(list1)]
        another = [
                {'label' : build, 'value' : build} for build in result
        ]
        return [another]

    elif value== 'custom':
        cursor = mapi.find({'info' : 'build sequence'})
        builds = cursor[0][value]
        list1 = builds
        result = [ele for ele in reversed(list1)]
        another = [
                {'label' : build, 'value' : build} for build in result
        ]
        return [another]

    if version:
        cursor = mapi.find({'info' : 'build sequence'})
        builds = cursor[0][version]
        list1 = builds
        list2 = dd.get_chain(version)

        in_first = set(list1)
        in_second = set(list2)
        in_second_but_not_in_first = in_second - in_first
        result = list1 + list(in_second_but_not_in_first)   
        result = [ele for ele in reversed(result)]
        another = [
                {'label' : build, 'value' : build} for build in result
        ]
        return [another]
         
    return None

### ===============================================================================================
# Tab 4 : Performance
### ===============================================================================================

@app.callback(
    [dash.dependencies.Output('Build1_Dropdown', 'options'),
    dash.dependencies.Output('Build2_Dropdown', 'options'),],
    [dash.dependencies.Input('Filter_Dropdown', 'value'),
    dash.dependencies.Input('Version_Dropdown', 'value'),],
)
def versionCallback(Xfilter, value):
    if not Xfilter:
        raise PreventUpdate
    if Xfilter == 'build':
        if not value:
            raise PreventUpdate
 
        if value == 'beta':
            beta_chain = [ele for ele in reversed(dd.get_chain('beta'))]
            build_options_beta = [
                {'label' : build, 'value' : build} for build in beta_chain
            ]
            return [build_options_beta, build_options_beta]
            
        elif value == 'release':
            release_chain = [ele for ele in reversed(dd.get_chain('release'))]
            build_options_release = [
                {'label' : build, 'value' : build} for build in release_chain
            ]            
            return [build_options_release, build_options_release]
        
        elif value == 'custom':
           custom_chain = [ele for ele in reversed(dd.get_chain('custom'))]
           build_options_custom = [
            {'label' : build, 'value' : build} for build in custom_chain
           ]
           return [build_options_custom, build_options_custom]
           
        else:
            cortx1_chain = [ele for ele in reversed(dd.get_chain('cortx1'))]        
            build_options_cortx1 = [
                {'label' : build, 'value' : build} for build in cortx1_chain
            ]
            return [build_options_cortx1, build_options_cortx1]
            
    else:
        Objsize_list = get_x_axis('Object Size')
        Objsize_options = [
             {'label' : Objsize, 'value' : Objsize} for Objsize in Objsize_list
        ]
        return [Objsize_options, Objsize_options]

    return [None, None]
#### ----------------------------------------------------------------------------------------------
@app.callback(
    [dash.dependencies.Output('configs_Dropdown', 'style'),
    dash.dependencies.Output('plot_TTFB', 'style'),
    dash.dependencies.Output('perf_graphs_heading', 'children'),
    dash.dependencies.Output('Build1_Dropdown', 'placeholder'),
    dash.dependencies.Output('Build2_Dropdown', 'style'),],
    [dash.dependencies.Input('Benchmark_Dropdown', 'value'),
    dash.dependencies.Input('Filter_Dropdown', 'value')]
)
def update_configs(bench, label):
    if bench != 'S3bench':
        graph_state = {'display': 'none'}
        configs_state = {'display': 'block'}
    else:
        configs_state = {'display': 'none'}
        graph_state = {'display': 'block'}
    heading_String = html.Th("Graphical representation of {} Performance data".format(bench), style={'text-align':'center'})
    
    if label == None:
        placeholder = 'Choose prev filter'
    else:
        placeholder = "Select " + label

    if label == 'build':
        dropdown_state = {'display': 'block'}
    else:
        dropdown_state = {'display': 'none'}

    return [configs_state,graph_state,heading_String, placeholder,dropdown_state]

@app.callback(
    dash.dependencies.Output('plot', 'figure'),
    [dash.dependencies.Input('Filter_Dropdown', 'value'),
    dash.dependencies.Input('Version_Dropdown', 'value'),
    dash.dependencies.Input('Build1_Dropdown', 'value'),
    dash.dependencies.Input('Build2_Dropdown', 'value'),
    dash.dependencies.Input('Benchmark_Dropdown', 'value'),
    dash.dependencies.Input('configs_Dropdown', 'value'),
    dash.dependencies.Input('Operations_Dropdown', 'value')],
)
def update_all(xfilter, version, build1, build2, bench, configs, operation):
    if not build1:
        raise PreventUpdate
    if not operation:
        operation = 'Both'

    if (bench != 'S3bench') and not configs:
        raise PreventUpdate
    
    if bench == 'S3bench':
        configs = None
        operation = operation.capitalize()

    from support import get_all_traces
    return get_all_traces(xfilter, version, build1, build2, bench, configs, operation)
#### ----------------------------------------------------------------------------------------------
@app.callback(
    dash.dependencies.Output('plot_Throughput', 'figure'),
    [dash.dependencies.Input('Filter_Dropdown', 'value'),
    dash.dependencies.Input('Version_Dropdown', 'value'),
    dash.dependencies.Input('Build1_Dropdown', 'value'),
    dash.dependencies.Input('Build2_Dropdown', 'value'),
    dash.dependencies.Input('Benchmark_Dropdown', 'value'),
    dash.dependencies.Input('configs_Dropdown', 'value'),
    dash.dependencies.Input('Operations_Dropdown', 'value')],
)
def update_throughput(xfilter, version, build1, build2, bench, configs, operation):
    print("Attempt for build {} {}".format(build1, build2))
    param = 'Throughput'
    if not build1:
        raise PreventUpdate
    if not operation:
        operation = 'Both'
    if (bench != 'S3bench') and not configs:
        raise PreventUpdate
    if xfilter == 'build': 
        titleText = 'Object Sizes' 
    else:
        titleText = 'Builds'
 
    operation_read = 'read'
    operation_write = 'write'
    if bench == 'S3bench':
        operation_read = 'Read'
        operation_write = 'Write'
        configs = None
        operation = operation.capitalize()

    fig = go.Figure()
    data_read_B1 = []    
    data_write_B1 = []
    data_read_B2 = []
    data_write_B2 = []
    
    if operation != 'Both':
        if xfilter == 'build':
            x_axis, data_B1 = get_IOsizewise_data(build1,bench,configs,operation,param)
            x_axis, data_B2 = get_IOsizewise_data(build2,bench,configs,operation,param)
        else:
            x_axis, data_B1 = get_buildwise_data(version,build1,bench,configs,operation,param)
            x_axis, data_B2 = get_buildwise_data(version,build2,bench,configs,operation,param)

        trace1 = go.Scatter(
            name = '{} {} - {}'.format(operation, param, build1),
            x = x_axis,
            y= data_B1,
            hovertemplate = '<br>%{y} MBps<br>'+
                            '<b>{} - {}</b><extra></extra>'.format(operation, build1),
        )

        fig.add_trace(trace1)
        if build2 != None:
            trace2 = go.Scatter(
            name = '{} {} - {}'.format(operation, param, build2),
            x = x_axis,
            y= data_B2,
            hovertemplate = '<br>%{y} MBps<br>'+
                            '<b>{} - {}</b><extra></extra>'.format(operation, build2),
            )
            fig.add_trace(trace2)

    else:
        if xfilter == 'build':
            x_axis, data_read_B1 = get_IOsizewise_data(build1,bench,configs,operation_read,param)    
            x_axis, data_write_B1 = get_IOsizewise_data(build1,bench,configs,operation_write,param)
            x_axis, data_read_B2 = get_IOsizewise_data(build2,bench,configs,operation_read,param)
            x_axis, data_write_B2 = get_IOsizewise_data(build2,bench,configs,operation_write,param)

        else:
            x_axis, data_read_B1 = get_buildwise_data(version,build1,bench,configs,operation_read,param)    
            x_axis, data_write_B1 = get_buildwise_data(version,build1,bench,configs,operation_write,param)
            x_axis, data_read_B2 = get_buildwise_data(version,build2,bench,configs,operation_read,param)
            x_axis, data_write_B2 = get_buildwise_data(version,build2,bench,configs,operation_write,param)

        trace1 = go.Scatter(
            name = 'Read {} - {}'.format(param, build1),
            x = x_axis,
            y= data_read_B1,
            hovertemplate = '<br>%{y} MBps<br>'+
                            '<b>Read - {}</b><extra></extra>'.format(build1),
        )
        trace2 = go.Scatter(
            name = 'Write {} - {}'.format(param, build1),
            x = x_axis,
            y= data_write_B1,
            hovertemplate = '<br>%{y} MBps<br>'+
                            '<b>Write - {}</b><extra></extra>'.format(build1),
        )

        if build2 != None:
            trace3 = go.Scatter(
                name = 'Read {} - {}'.format(param, build2),
                x = x_axis,
                y=  data_read_B2,
                hovertemplate = '<br>%{y} MBps<br>'+
                                '<b>Read - {}</b><extra></extra>'.format(build2),      
            )
            trace4 = go.Scatter(
                name = 'Write {} - {}'.format(param, build2),
                x = x_axis,
                y= data_write_B2,
                hovertemplate = '<br>%{y} MBps<br>'+
                                '<b>Write - {}</b><extra></extra>'.format(build2),
            )
            fig.add_trace(trace3)
            fig.add_trace(trace4)

        fig.add_trace(trace1)
        fig.add_trace(trace2)
        
    fig.update_layout(
        autosize=True,
        showlegend = True,
        title = '{}'.format(param),
        legend_title= 'Glossary',
        width=1200,
        height=600,
        yaxis=dict(            
            title_text="Data (MBps)",
            titlefont=dict(size=16)),
        xaxis=dict(
            title_text=titleText,
            titlefont=dict(size=16)
        ),        
    )
    return fig
#### ----------------------------------------------------------------------------------------------
@app.callback(
    dash.dependencies.Output('plot_Latency', 'figure'),
    [dash.dependencies.Input('Filter_Dropdown', 'value'),
    dash.dependencies.Input('Version_Dropdown', 'value'),
    dash.dependencies.Input('Build1_Dropdown', 'value'),
    dash.dependencies.Input('Build2_Dropdown', 'value'),
    dash.dependencies.Input('Benchmark_Dropdown', 'value'),
    dash.dependencies.Input('configs_Dropdown', 'value'),
    dash.dependencies.Input('Operations_Dropdown', 'value')],
)
def update_latency(xfilter, version, build1, build2, bench, configs, operation):
    param = 'Latency'
    if not build1:
        raise PreventUpdate
    if not operation:
        operation = 'Both'
    if (bench != 'S3bench') and not configs:
        raise PreventUpdate
    if xfilter == 'build': 
        titleText = 'Object Sizes' 
    else:
        titleText = 'Builds'

    operation_read = 'read'
    operation_write = 'write'
    if bench == 'S3bench':
        operation_read = 'Read'
        operation_write = 'Write'
        configs = None
        operation = operation.capitalize()

    fig = go.Figure()    
    data_read_B1 = []    
    data_write_B1 = []
    data_read_B2 = []
    data_write_B2 = []

    if operation != 'Both':
        if xfilter == 'build':
            if bench != 'Hsbench':
                x_axis, data_B1 = get_IOsizewise_data(build1,bench,configs,operation,param,'Avg')
                x_axis, data_B2 = get_IOsizewise_data(build2,bench,configs,operation,param,'Avg')
            else:
                x_axis, data_B1 = get_IOsizewise_data(build1,bench,configs,operation,param)
                x_axis, data_B2 = get_IOsizewise_data(build2,bench,configs,operation,param)
        else:
            if bench != 'Hsbench':
                x_axis, data_B1 = get_buildwise_data(version,build1,bench,configs,operation,param,'Avg')
                x_axis, data_B2 = get_buildwise_data(version,build2,bench,configs,operation,param,'Avg')
            else:
                x_axis, data_B1 = get_buildwise_data(version,build1,bench,configs,operation,param)
                x_axis, data_B2 = get_buildwise_data(version,build2,bench,configs,operation,param)        

        trace1 = go.Scatter(
            name = '{} {} - {}'.format(operation, param, build1),
            x = x_axis,
            y= data_B1,
            hovertemplate = '<br>%{y} ms<br>'+
                            '<b>{} - {}</b><extra></extra>'.format(operation, build1),
        )

        fig.add_trace(trace1)

        if build2 != None:
            trace2 = go.Scatter(
            name = '{} {} - {}'.format(operation, param, build2),
            x = x_axis,
            y= data_B2,
            hovertemplate = '<br>%{y} ms<br>'+
                            '<b>{} - {}</b><extra></extra>'.format(operation, build2),
            )
            fig.add_trace(trace2)

    else:
        if xfilter == 'build':
            if bench != 'Hsbench':
                x_axis, data_read_B1 = get_IOsizewise_data(build1,bench,configs,operation_read,param,'Avg')    
                x_axis, data_write_B1 = get_IOsizewise_data(build1,bench,configs,operation_write,param,'Avg')
                x_axis, data_read_B2 = get_IOsizewise_data(build2,bench,configs,operation_read,param,'Avg')
                x_axis, data_write_B2 = get_IOsizewise_data(build2,bench,configs,operation_write,param,'Avg')
            else:
                x_axis, data_read_B1 = get_IOsizewise_data(build1,bench,configs,operation_read,param)    
                x_axis, data_write_B1 = get_IOsizewise_data(build1,bench,configs,operation_write,param)
                x_axis, data_read_B2 = get_IOsizewise_data(build2,bench,configs,operation_read,param)
                x_axis, data_write_B2 = get_IOsizewise_data(build2,bench,configs,operation_write,param)
        else:
            if bench != 'Hsbench':
                x_axis, data_read_B1 = get_buildwise_data(version,build1,bench,configs,operation_read,param,'Avg')    
                x_axis, data_write_B1 = get_buildwise_data(version,build1,bench,configs,operation_write,param,'Avg')
                x_axis, data_read_B2 = get_buildwise_data(version,build2,bench,configs,operation_read,param,'Avg')
                x_axis, data_write_B2 = get_buildwise_data(version,build2,bench,configs,operation_write,param,'Avg')
            else:
                x_axis, data_read_B1 = get_buildwise_data(version,build1,bench,configs,operation_read,param)    
                x_axis, data_write_B1 = get_buildwise_data(version,build1,bench,configs,operation_write,param)
                x_axis, data_read_B2 = get_buildwise_data(version,build2,bench,configs,operation_read,param)
                x_axis, data_write_B2 = get_buildwise_data(version,build2,bench,configs,operation_write,param)   

        trace1 = go.Scatter(
            name = 'Read {} - {}'.format(param, build1),
            x = x_axis,
            y= data_read_B1,
            hovertemplate = '<br>%{y} ms<br>'+
                            '<b>Read - {}</b><extra></extra>'.format(build1),
        )

        trace2 = go.Scatter(
            name = 'Write {} - {}'.format(param, build1),
            x = x_axis,
            y= data_write_B1,
            hovertemplate = '<br>%{y} ms<br>'+
                            '<b>Write - {}</b><extra></extra>'.format(build1),      
        )
        fig.add_trace(trace1)
        fig.add_trace(trace2)

        if build2 != None:
            trace3 = go.Scatter(
                name = 'Read {} - {}'.format(param, build2),
                x = x_axis,
                y=  data_read_B2,
                hovertemplate = '<br>%{y} ms<br>'+
                                '<b>Read - {}</b><extra></extra>'.format(build2),
            )

            trace4 = go.Scatter(
                name = 'Write {} - {}'.format(param, build2),
                x = x_axis,
                y= data_write_B2,
                hovertemplate = '<br>%{y} ms<br>'+
                                '<b>Write - {}</b><extra></extra>'.format(build2),
            )
            fig.add_trace(trace3)
            fig.add_trace(trace4)

        
        
    fig.update_layout(
        autosize=True,
        showlegend = True,
        title = '{}'.format(param),
        legend_title= 'Glossary',
        width=1200,
        height=600,
        yaxis=dict(            
            title_text="Data (ms)",
            titlefont=dict(size=16)),
        xaxis=dict(
            title_text=titleText,
            titlefont=dict(size=16)
        )
    )
    return fig
#### ----------------------------------------------------------------------------------------------
@app.callback(
    dash.dependencies.Output('plot_IOPS', 'figure'),
    [dash.dependencies.Input('Filter_Dropdown', 'value'),
    dash.dependencies.Input('Version_Dropdown', 'value'),
    dash.dependencies.Input('Build1_Dropdown', 'value'),
    dash.dependencies.Input('Build2_Dropdown', 'value'),
    dash.dependencies.Input('Benchmark_Dropdown', 'value'),
    dash.dependencies.Input('configs_Dropdown', 'value'),
    dash.dependencies.Input('Operations_Dropdown', 'value')],
)
def update_IOPS(xfilter, version, build1, build2, bench, configs, operation):
    param = 'IOPS'
    if not build1:
        raise PreventUpdate
    if not operation:
        operation = 'Both'
    if (bench != 'S3bench') and not configs:
        raise PreventUpdate
    if xfilter == 'build': 
        titleText = 'Object Sizes' 
    else:
        titleText = 'Builds'

    operation_read = 'read'
    operation_write = 'write'
    if bench == 'S3bench':
        operation_read = 'Read'
        operation_write = 'Write'
        configs = None
        operation = operation.capitalize()

    fig = go.Figure()    
    data_read_B1 = []    
    data_write_B1 = []
    data_read_B2 = []
    data_write_B2 = []

    if operation != 'Both':

        if xfilter == 'build':
            x_axis, data_B1 = get_IOsizewise_data(build1,bench,configs,operation,param)
            x_axis, data_B2 = get_IOsizewise_data(build2,bench,configs,operation,param)
        else:
            x_axis, data_B1 = get_buildwise_data(version,build1,bench,configs,operation,param)
            x_axis, data_B2 = get_buildwise_data(version,build2,bench,configs,operation,param)  

        trace1 = go.Scatter(
            name = '{} {} - {}'.format(operation, param, build1),
            x = x_axis,
            y= data_B1,
            hovertemplate = '<br>%{y}<br>'+
                            '<b>{} - {}</b><extra></extra>'.format(operation, build1),
        )
        
        fig.add_trace(trace1)

        if build2 != None:
            trace2 = go.Scatter(
            name = '{} {} - {}'.format(operation, param, build2),
            x = x_axis,
            y= data_B2,
            hovertemplate = '<br>%{y}<br>'+
                            '<b>{} - {}</b><extra></extra>'.format(operation, build2),
            )
            fig.add_trace(trace2)

    else:
        if xfilter == 'build':
            x_axis, data_read_B1 = get_IOsizewise_data(build1,bench,configs,operation_read,param)    
            x_axis, data_write_B1 = get_IOsizewise_data(build1,bench,configs,operation_write,param)
            x_axis, data_read_B2 = get_IOsizewise_data(build2,bench,configs,operation_read,param)
            x_axis, data_write_B2 = get_IOsizewise_data(build2,bench,configs,operation_write,param)
        else:
            x_axis, data_read_B1 = get_buildwise_data(version,build1,bench,configs,operation_read,param)    
            x_axis, data_write_B1 = get_buildwise_data(version,build1,bench,configs,operation_write,param)
            x_axis, data_read_B2 = get_buildwise_data(version,build2,bench,configs,operation_read,param)
            x_axis, data_write_B2 = get_buildwise_data(version,build2,bench,configs,operation_write,param)
  
        trace1 = go.Scatter(
            name = 'Read {} - {}'.format(param, build1),
            x = x_axis,
            y= data_read_B1,
            hovertemplate = '<br>%{y}<br>'+
                            '<b>Read - {}</b><extra></extra>'.format(build1),
        )
        trace2 = go.Scatter(
            name = 'Write {} - {}'.format(param, build1),
            x = x_axis,
            y= data_write_B1,
            hovertemplate = '<br>%{y}<br>'+
                            '<b>Write - {}</b><extra></extra>'.format(build1),
            
        )
        fig.add_trace(trace1)
        fig.add_trace(trace2)

        if build2 != None:
            trace3 = go.Scatter(
                name = 'Read {} - {}'.format(param, build2),
                x = x_axis,
                y=  data_read_B2,
                hovertemplate = '<br>%{y}<br>'+
                                '<b>Read - {}</b><extra></extra>'.format(build2),
                
            )
            trace4 = go.Scatter(
                name = 'Write {} - {}'.format(param, build2),
                x = x_axis,
                y= data_write_B2,
                hovertemplate = '<br>%{y}<br>'+
                                '<b>Write - {}</b><extra></extra>'.format(build2),
            )
            fig.add_trace(trace3)
            fig.add_trace(trace4)

    fig.update_layout(
        autosize=True,
        showlegend = True,
        title = 'Requests Per Second ({})'.format(param),
        legend_title= 'Glossary',
        width=1200,
        height=600,
        yaxis=dict(            
            title_text="Data",
            titlefont=dict(size=16)),
        xaxis=dict(
            title_text=titleText,
            titlefont=dict(size=16)
        )
    )
    return fig
#### ----------------------------------------------------------------------------------------------
@app.callback(
    dash.dependencies.Output('plot_TTFB', 'figure'),
    [dash.dependencies.Input('Filter_Dropdown', 'value'),
    dash.dependencies.Input('Version_Dropdown', 'value'),
    dash.dependencies.Input('Build1_Dropdown', 'value'),
    dash.dependencies.Input('Build2_Dropdown', 'value'),
    dash.dependencies.Input('Benchmark_Dropdown', 'value'),
    dash.dependencies.Input('configs_Dropdown', 'value'),
    dash.dependencies.Input('Operations_Dropdown', 'value')],
)
def update_TTFB(xfilter, version, build1, build2, bench, configs, operation):
    param = 'TTFB'
    if not build1:
        raise PreventUpdate
    if not operation:
        operation = 'Both'
    if not bench:
        bench = 'S3bench'
    if xfilter == 'build': 
        titleText = 'Object Sizes' 
    else:
        titleText = 'Builds'

    fig = go.Figure()    
    if bench != 'S3bench':
        return fig

    operation_read = 'read'
    operation_write = 'write'
    if bench == 'S3bench':
        operation_read = 'Read'
        operation_write = 'Write'
        configs = None
        operation = operation.capitalize()

    if operation != 'Both':
        
        if xfilter == 'build':
            x_axis, data_B1 = get_IOsizewise_data(build1,bench,configs,operation,param,'Avg')
            x_axis, data_B2 = get_IOsizewise_data(build2,bench,configs,operation,param,'Avg')
        else:
            x_axis, data_B1 = get_buildwise_data(version,build1,bench,configs,operation,param,'Avg')
            x_axis, data_B2 = get_buildwise_data(version,build2,bench,configs,operation,param,'Avg')

        trace1 = go.Scatter(
            name = '{} {} - {}'.format(operation, param, build1),
            x = x_axis,
            y= data_B1,
            hovertemplate = '<br>%{y} ms<br>'+
                            '<b>{} - {}</b><extra></extra>'.format(operation, build1),
        )
        fig.add_trace(trace1)

        if build2 != None:
            trace2 = go.Scatter(
                name = '{} {} - {}'.format(operation, param, build2),
                x = x_axis,
                y= data_B2,
                hovertemplate = '<br>%{y} ms<br>'+
                                '<b>{} - {}</b><extra></extra>'.format(operation, build2),
            )
            fig.add_trace(trace2)

    else:
        if xfilter == 'build':
            x_axis, data_read_B1 = get_IOsizewise_data(build1,bench,configs,operation_read,param,'Avg')    
            x_axis, data_write_B1 = get_IOsizewise_data(build1,bench,configs,operation_write,param,'Avg')
            x_axis, data_read_B2 = get_IOsizewise_data(build2,bench,configs,operation_read,param,'Avg')
            x_axis, data_write_B2 = get_IOsizewise_data(build2,bench,configs,operation_write,param,'Avg')
        else:
            x_axis, data_read_B1 = get_buildwise_data(version,build1,bench,configs,operation_read,param,'Avg')    
            x_axis, data_write_B1 = get_buildwise_data(version,build1,bench,configs,operation_write,param,'Avg')
            x_axis, data_read_B2 = get_buildwise_data(version,build2,bench,configs,operation_read,param,'Avg')
            x_axis, data_write_B2 = get_buildwise_data(version,build2,bench,configs,operation_write,param,'Avg')
        
        trace1 = go.Scatter(
            name = 'Read {} - {}'.format(param, build1),
            x = x_axis,
            y= data_read_B1,
            hoverinfo='skip',
            hovertemplate = '<br>%{y} ms<br>'+
                            '<b>Read - {}</b><extra></extra>'.format(build1),    
        )
        trace2 = go.Scatter(
            name = 'Write {} - {}'.format(param, build1),
            x = x_axis,
            y= data_write_B1,
            hoverinfo='skip',
            hovertemplate = '<br>%{y} ms<br>'+
                            '<b>Write - {}</b><extra></extra>'.format(build1),   
        )
        fig.add_trace(trace1)
        fig.add_trace(trace2)

        if build2 != None:
            trace3 = go.Scatter(
                name = 'Read {} - {}'.format(param, build2),
                x = x_axis,
                y=  data_read_B2,
                hoverinfo='skip',
                hovertemplate = '<br>%{y} ms<br>'+
                                '<b>Read - {}</b><extra></extra>'.format(build2),
            )
            trace4 = go.Scatter(
                name = 'Write {} - {}'.format(param, build2),
                x = x_axis,
                y= data_write_B2,
                hoverinfo='skip',
                hovertemplate = '<br>%{y} ms<br>'+
                                '<b>Write - {}</b><extra></extra>'.format(build2),
            )
            fig.add_trace(trace3)
            fig.add_trace(trace4)

    fig.update_layout(
        autosize=True,
        showlegend = True,
        title = 'Time To First Byte ({})'.format(param),
        legend_title= 'Glossary',
        width=1200,
        height=600,
        yaxis=dict(            
            title_text="Data (ms)",
            titlefont=dict(size=16)),
        xaxis=dict(
            title_text=titleText,
            titlefont=dict(size=16)
        )
    )
    return fig

### ===============================================================================================
# Tab 3 : Defects chart
### ===============================================================================================
@app.callback([
    Output('TP_wise_defects', 'children')],
    [Input('test_plan_submit_button', 'n_clicks'),
    Input('test_plan_input', 'value')],)
def update_tab3(clicks, input_value):
    ctx = dash.callback_context
    prop_id = ''
    found = False
    if not ctx.triggered:
        print('No input yet')
    
    else:
        prop_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if prop_id == 'test_plan_submit_button':
        found = True
        testPlanList = input_value.lower()
        print("Attempt for TE IDs {}".format(testPlanList))
    defectList = None   
    
    try:
        if found:
            tpList = testPlanList.split(",")
            finalTpList = []
            for tp in tpList:
                finalTpList.append(tp.strip())
            defectList = getDefectList(finalTpList)
            df = pd.DataFrame(defectList)
            df = df.drop_duplicates(subset=['defects_item'])

            df.drop(columns=['TE_ID'],inplace=True)
            detailed_report = dash_table.DataTable(
    
                id="detailed_defects_table",
                columns = [{'name':'Test Exec.','id':'TestPlan_ID'},{'name':'Component','id':'testExecutionLabels'},{'name':'Test ID','id':'Test_ID'},{'name':'Priority','id':'defect_priority'},
                        {'name':'JIRA ID','id':'defects_item'},{'name':'Status','id':'status'}, {'name':'Description','id':'defects_summary'}],
                data=df.to_dict('records'),
                sort_action="native",
                page_size=15,
                style_cell={'padding': '5px', 'fontSize': 16,'background-color' : '#E0E0E0',
                            'font-family': 'sans-serif','text-align':'center'},
                style_data = {'whitespace':'normal'},
                style_header={
                    'backgroundColor': '#7F8C8D',
                    'fontWeight': 'bold',
                    'textAlign': 'center'
                },
                style_data_conditional=[
                {
                    'if': {'column_id': 'defects_summary'},
                    'backgroundColor': '#FFFFFF',
                    'text-align':'left'
                },
                {
                'if': {
                        'column_id': 'defect_priority',
                        'filter_query': '{{defect_priority}} = {}'.format("Blocker"),
                    },
                        'color' : '#ff6262',
                },
                {
                'if': {
                        'column_id': 'defect_priority',
                        'filter_query': '{{defect_priority}} = {}'.format("Critical"),                        
                    },
                        'color'  :'#DC7633',
                },
                {
                'if': {
                        'column_id': 'defect_priority',
                        'filter_query': '{{defect_priority}} = {}'.format("Major"),                        
                    },
                        'color' : '#504de4',
                },
                {
                'if': {
                        'column_id': 'defect_priority',
                        'filter_query': '{{defect_priority}} = {}'.format("Minor"),
                    },
                        'color' : '#343a40',
                },
                {
                'if': {
                        'column_id': 'defect_priority',
                        'filter_query': '{{defect_priority}} = {}'.format("Trivial"),                        
                    },
                        'color' : '#3cba3c',
                },   
                ],
            )
            return [detailed_report]
    except:
        return [None]
    return [None]

### ===============================================================================================
# Tab 1 : Executive report
### ===============================================================================================
# Exe report page - Table 3 : Feature breakdown summary
@app.callback([
    Output('user_op_total', 'children'),Output('user_op_pass', 'children'),Output('user_op_fail', 'children'),Output('user_op_ppass', 'children'),Output('user_op_pfail', 'children'),
    Output('scale_total', 'children'),Output('scale_pass', 'children'),Output('scale_fail', 'children'),Output('scale_ppass', 'children'),Output('scale_pfail', 'children'),
    Output('avail_total', 'children'),Output('avail_pass', 'children'),Output('avail_fail', 'children'),Output('avail_ppass', 'children'),Output('avail_pfail', 'children'),
    Output('long_total', 'children'),Output('long_pass', 'children'),Output('long_fail', 'children'),Output('long_ppass', 'children'),Output('long_pfail', 'children'),
    Output('ucases_total', 'children'),Output('ucases_pass', 'children'),Output('ucases_fail', 'children'),Output('ucases_ppass', 'children'),Output('ucases_pfail', 'children'),
    Output('orphans_total', 'children'),Output('orphans_pass', 'children'),Output('orphans_fail', 'children'),Output('orphans_ppass', 'children'),Output('orphans_pfail', 'children'),
    Output('xtotal_total', 'children'),Output('xtotal_pass', 'children'),Output('xtotal_fail', 'children'),Output('xtotal_ppass', 'children'),Output('xtotal_pfail', 'children')],  #47 T3
    [Input('table_submit_button', 'n_clicks'),
    dash.dependencies.Input('url', 'pathname'),
    Input('table_build_input', 'value')],
    [State('table_build_input', 'value')],)
def update_exe_table_3(clicks, pathname, input_value, enter_input):
    build, _, _ = get_input('cft',dash.callback_context, clicks, input_value, enter_input, pathname)
    if build:
        try:
            uop_count_p = mapi.count_documents({'build': build,'deleted':False, 'feature': 'User operations', 'testResult':'PASS'})
        except:
            uop_count_p = "-"
        try:
            uop_count_f = mapi.count_documents({'build': build,'deleted':False, 'feature': 'User operations', 'testResult':'FAIL'})
        except:
            uop_count_f = "-"
        try:
            scale_count_p = mapi.count_documents({'build': build,'deleted':False, 'feature': 'Scalability', 'testResult':'PASS'})
        except:
            scale_count_p = "-"
        try:
            scale_count_f = mapi.count_documents({'build': build,'deleted':False, 'feature': 'Scalability', 'testResult':'FAIL'})
        except:
            scale_count_f = "-"
        try:
            avail_count_p = mapi.count_documents({'build': build,'deleted':False, 'feature': 'Availability', 'testResult':'PASS'})
        except:
            avail_count_p = "-"
        try:
            avail_count_f = mapi.count_documents({'build': build,'deleted':False, 'feature': 'Availability', 'testResult':'FAIL'})
        except:
            avail_count_f = "-"
        try:
            long_count_p = mapi.count_documents({'build': build,'deleted':False, 'feature': 'Longevity', 'testResult':'PASS'})
        except:
            long_count_p = "-"
        try:
            long_count_f = mapi.count_documents({'build': build,'deleted':False, 'feature': 'Longevity', 'testResult':'FAIL'})
        except:
            long_count_f = "-"
        try:
            uc_count_p = mapi.count_documents({'build': build,'deleted':False, 'feature': 'Usecases', 'testResult':'PASS'})
        except:
            uc_count_p = "-"
        try:
            uc_count_f = mapi.count_documents({'build': build,'deleted':False, 'feature': 'Usecases', 'testResult':'FAIL'})
        except:
            uc_count_f = "-"
        try:
            pass_count = mapi.count_documents({'build': build,'deleted':False, 'testResult':'PASS'})
        except:
            pass_count = "-"
        try:
            fail_count = mapi.count_documents({'build': build,'deleted':False, 'testResult':'FAIL'})
        except:
            fail_count = "-"
        try:
            op_total = uop_count_p + uop_count_f
        except:
            op_total = "-"
        try:
            s_total = scale_count_p + scale_count_f
        except:
            s_total = "-"
        try:
            a_total = avail_count_p + avail_count_f
        except:
            a_total = "-"
        try:
            l_total = long_count_p + long_count_f
        except:
            l_total = "-"
        try:
            u_total = uc_count_p + uc_count_f
        except:
            u_total = "-"
        try:
            total = pass_count + fail_count
        except:      
            total = "-"
        try:
            orph_count_p = pass_count - uop_count_p - scale_count_p - avail_count_p - long_count_p - uc_count_p
        except:
            orph_count_p = "-"
        try:
            orph_count_f = fail_count - uop_count_f - scale_count_f - avail_count_f - long_count_f - uc_count_f
        except:
            orph_count_f = "-"
        try:
            orph_total = orph_count_p + orph_count_f
        except:
            orph_total = "-"

        return [op_total,uop_count_p, uop_count_f,get_percent(op_total, uop_count_p),get_percent(op_total, uop_count_f),\
            s_total,scale_count_p,scale_count_f,get_percent(s_total, scale_count_p),get_percent(s_total, scale_count_f),\
            a_total,avail_count_p,avail_count_f,get_percent(a_total, avail_count_p),get_percent(a_total, avail_count_f),\
            l_total,long_count_p,long_count_f,get_percent(l_total, long_count_p),get_percent(l_total, long_count_f),\
            # p_total,perf_count_p,perf_count_f,get_percent(p_total, perf_count_p),get_percent(p_total, perf_count_f),\
            u_total,uc_count_p,uc_count_f,get_percent(u_total, uc_count_p),get_percent(u_total, uc_count_f),\
            orph_total,orph_count_p,orph_count_f,get_percent(orph_total, orph_count_p),get_percent(orph_total, orph_count_f),\
            total,pass_count,fail_count,get_percent(total,pass_count),get_percent(total,fail_count)]

    else:
        return [None] * 35
#### ----------------------------------------------------------------------------------------------
# Exe report page - Table 4 : Code maturity
@app.callback([
    Output('total_r1', 'children'),Output('pass_r1', 'children'),Output('fail_r1', 'children'),Output('abort_r1', 'children'),Output('blocked_r1', 'children'),
    Output('total_r2', 'children'),Output('pass_r2', 'children'),Output('fail_r2', 'children'),Output('abort_r2', 'children'),Output('blocked_r2', 'children'),
    Output('total_r3', 'children'),Output('pass_r3', 'children'),Output('fail_r3', 'children'),Output('abort_r3', 'children'),Output('blocked_r3', 'children'),
    Output('total_r4', 'children'),Output('pass_r4', 'children'),Output('fail_r4', 'children'),Output('abort_r4', 'children'),Output('blocked_r4', 'children'), #40 T4
    Output('CM2','children'),Output('CM3','children'),Output('CM4','children'),
    ],
    [Input('table_submit_button', 'n_clicks'),
    dash.dependencies.Input('url', 'pathname'),
    Input('table_build_input', 'value')],
    [State('table_build_input', 'value')],
    )
def update_exe_table_4(clicks, pathname, input_value, enter_input):
    build, pre_build, version = get_input('cft',dash.callback_context, clicks, input_value, enter_input, pathname)
  
    data = []
    pre_name = 'Prev Build'
    pre_pre_name = 'Prev Build'
    pre_pre_pre_name = 'Prev Build'
    try:
        if build:
            try:
                R1_pass = mapi.count_documents({'build': build,'deleted':False,'testResult':'PASS'})
            except:
                R1_pass = "-"
            try:
                R1_fail = mapi.count_documents({'build': build,'deleted':False,'testResult':'FAIL'})
            except:
                R1_fail = "-"
            try:
                R1_abort = mapi.count_documents({'build': build,'deleted':False,'testResult':'ABORTED'})
            except:
                R1_abort = "-"
            try:
                R1_blocked = mapi.count_documents({'build': build,'deleted':False,'testResult':'BLOCKED'})
            except:
                R1_blocked = "-"
            try:
                R1_total = R1_pass + R1_fail + R1_abort + R1_blocked
            except:
                R1_total = "-"
            
            data.extend([R1_total,R1_pass,R1_fail,R1_abort,R1_blocked])
        else:
            data.extend(["-", "-", "-", "-", "-"])
    except:
        data.extend(["-", "-", "-", "-", "-"])
    try:
        if pre_build:
            pre_name = pre_build
            
            try:
                R2_pass = mapi.count_documents({'build': pre_build,'deleted':False,'testResult':'PASS'})
            except:
                R2_pass = "-"
            try:
                R2_fail = mapi.count_documents({'build': pre_build,'deleted':False,'testResult':'FAIL'})
            except:
                R2_fail = "-"
            try:
                R2_abort = mapi.count_documents({'build': pre_build,'deleted':False,'testResult':'ABORTED'})
            except:
                R2_abort = "-"
            try:
                R2_blocked = mapi.count_documents({'build': pre_build,'deleted':False,'testResult':'BLOCKED'})
            except:
                R2_blocked = "-"
            try:
                R2_total = R2_pass + R2_fail + R2_abort + R2_blocked
            except:
                R2_total = "-"
        
            data.extend([R2_total,R2_pass,R2_fail,R2_abort,R2_blocked])
        else:
            data.extend(["-", "-", "-", "-", "-"])
    except:
        data.extend(["-", "-", "-", "-", "-"])
    try:
        pre_pre_build = get_previous_build(pre_build, version)
        pre_pre_name = pre_pre_build
        if pre_pre_build:
            try:
                R3_pass = mapi.count_documents({'build': pre_pre_build,'deleted':False,'testResult':'PASS'})
            except:
                R3_pass = "-"
            try:
                R3_fail = mapi.count_documents({'build': pre_pre_build,'deleted':False,'testResult':'FAIL'})
            except:
                R3_fail = "-"
            try:
                R3_abort = mapi.count_documents({'build': pre_pre_build,'deleted':False,'testResult':'ABORTED'})
            except:
                R3_abort = "-"
            try:
                R3_blocked = mapi.count_documents({'build': pre_pre_build,'deleted':False,'testResult':'BLOCKED'})
            except:
                R3_blocked = "-"
            try:
                R3_total = R3_pass + R3_fail + R3_abort + R3_blocked
            except:
                R3_total = "-"

            data.extend([R3_total,R3_pass,R3_fail,R3_abort,R3_blocked])
        else:
            data.extend(["-", "-", "-", "-", "-"])
    except:
        data.extend(["-", "-", "-", "-", "-"])

    try:
        pre_pre_pre_build = get_previous_build(pre_pre_build, version)
        pre_pre_pre_name = pre_pre_pre_build
        if pre_pre_pre_build:
            try:
                R4_pass = mapi.count_documents({'build': pre_pre_pre_build,'deleted':False,'testResult':'PASS'})
            except:
                R4_pass = "-"
            try:
                R4_fail = mapi.count_documents({'build': pre_pre_pre_build,'deleted':False,'testResult':'FAIL'})
            except:
                R4_fail = "-"
            try:
                R4_abort = mapi.count_documents({'build': pre_pre_pre_build,'deleted':False,'testResult':'ABORTED'})
            except:
                R4_abort = "-"
            try:
                R4_blocked = mapi.count_documents({'build': pre_pre_pre_build,'deleted':False,'testResult':'BLOCKED'})
            except:
                R4_blocked = "-"
            try:
                R4_total = R4_pass + R4_fail + R4_abort + R4_blocked
            except:
                R4_total = "-"

            data.extend([R4_total,R4_pass,R4_fail,R4_abort,R4_blocked])
        else:
            data.extend(["-", "-", "-", "-", "-"])
    except:
        data.extend(["-", "-", "-", "-", "-"])
    
    if not pre_name:
        pre_name = 'Prev Build'
    if not pre_pre_name:
        pre_pre_name = 'Prev Build'
    if not pre_pre_pre_name:
        pre_pre_pre_name = 'Prev Build'

    data.extend([pre_name.capitalize(), pre_pre_name.capitalize(), pre_pre_pre_name.capitalize()])
    return data
#### ----------------------------------------------------------------------------------------------
# rest of the table
@app.callback([
    Output('component_build_current','children'),Output('code_maturity_build_current','children'),Output('product_heading_eng','children'),
    Output('product_heading_exe','children'),Output('build_heading_eng','children'),Output('build_heading_exe','children'),Output('date_heading_eng','children'),
    Output('date_heading_exe','children'),Output('component_previous','children'),Output('build_report_header','children'),Output('qa_current_eng','children'),
    Output('qa_previous_eng','children'),Output('qa_current_exe','children'),Output('qa_previous_exe','children'),],
    [Input('table_submit_button', 'n_clicks'),dash.dependencies.Input('url', 'pathname'),Input('table_build_input', 'value')],[State('table_build_input', 'value')],
)
def update_rest(clicks, pathname, input_value, enter_input):
    build, pre_build, _ = get_input('cft',dash.callback_context, clicks, input_value, enter_input, pathname)
    if not build:
        build, _ , _ = get_input('perf',dash.callback_context, clicks, input_value, enter_input, pathname)
    pre_name = ''
    build_name = ''
    if not build:
        build_name = "Current Build"

    else:
        build_name = build.capitalize()
    if not pre_build:
        pre_name = "Previous Build"
    else:
        pre_name = pre_build.capitalize()
    if build:
        try:
            date = mapi.find({'build':build,'deleted':False}).sort([("dateOfExecution" , 1)]).limit(1)
            date1 = date[0]['dateOfExecution'].split("T")[0] + date[0]['dateOfExecution'][19::]
            date_field = html.H5("Date: {}".format(date1))
        except:
            date_field = html.H5("Date: -")

        return [build.capitalize(), build.capitalize(),html.H5("Product: Lyve Drive Rack"),html.H5("Product: Lyve Drive Rack"),html.H5("Build: {}".format(build.capitalize())), \
            html.H5("Build: {}".format(build.capitalize())),date_field,date_field,pre_name.capitalize(),html.H4(html.Em("Report for Build {}".format(build.capitalize()))),build_name,pre_name,build_name,pre_name] 
    
    heading = html.H4(html.Em("... looking for build number!"))
    return ["Current Build","Current Build",html.H5("Product: "),html.H5("Product: "),html.H5("Build: "),html.H5("Build: "),\
            html.H5("Date: "),html.H5("Date: "),pre_name,heading,build_name,pre_name,build_name,pre_name] 
    
### ===============================================================================================
# Tab 2 : Engineers report
### ===============================================================================================
# Eng & Exe report page - Table 1 : Reported bugs
@app.callback([
    Output('eng_blocker_test', 'children'),Output('eng_critical_test', 'children'),
    Output('eng_minor_test', 'children'),Output('eng_major_test', 'children'),Output('eng_trivial_test', 'children'),
    Output('eng_blocker_product', 'children'),Output('eng_critical_product', 'children'),
    Output('eng_major_product', 'children'),Output('eng_minor_product', 'children'),Output('eng_trivial_product', 'children'),
    Output('eng_total_test', 'children'),Output('eng_total_product', 'children'),
    
    Output('exe_blocker_test', 'children'),Output('exe_critical_test', 'children'),
    Output('exe_minor_test', 'children'),Output('exe_major_test', 'children'),Output('exe_trivial_test', 'children'),
    Output('exe_blocker_product', 'children'),Output('exe_critical_product', 'children'),
    Output('exe_major_product', 'children'),Output('exe_minor_product', 'children'),Output('exe_trivial_product', 'children'),
    Output('exe_total_test', 'children'),Output('exe_total_product', 'children'),], #12 T1
    [Input('table_submit_button', 'n_clicks'),
    dash.dependencies.Input('url', 'pathname'),
    Input('table_build_input', 'value')],
    [State('table_build_input', 'value')])
def update_eng_table_1(clicks, pathname, input_value, enter_input):
    
    build, _, _ = get_input('cft',dash.callback_context, clicks, input_value, enter_input, pathname)
    
    if build:
        try: 
            test_blocker_count = len(mapi.find_distinct("defectID",{'build':build,'deleted':False, "testLabels" : 'Automation', 'defectPriority' : 'Blocker'})) +\
                                len(mapi.find_distinct("defectID",{'build':build,'deleted':False, "testLabels" : 'CFT', 'defectPriority' : 'Blocker'}))
            
        except:
            test_blocker_count = "-"
        try:
            test_critical_count = len(mapi.find_distinct("defectID",{'build':build,'deleted':False, "testLabels" : 'Automation', 'defectPriority' : 'Critical'}))+\
                                len(mapi.find_distinct("defectID",{'build':build,'deleted':False, "testLabels" : 'CFT', 'defectPriority' : 'Critical'}))
        except:
            test_critical_count = "-"
        try:
            test_major_count = len(mapi.find_distinct("defectID",{'build':build,'deleted':False, "testLabels" : 'Automation', 'defectPriority' : 'Major'}))+\
                                len(mapi.find_distinct("defectID",{'build':build,'deleted':False, "testLabels" : 'CFT', 'defectPriority' : 'Major'}))
        except:
            test_major_count = "-"
        try:
            test_minor_count = len(mapi.find_distinct("defectID",{'build':build,'deleted':False, "testLabels" : 'Automation', 'defectPriority' : 'Minor'}))+\
                                len(mapi.find_distinct("defectID",{'build':build,'deleted':False, "testLabels" : 'CFT', 'defectPriority' : 'Minor'}))
        except:
            test_minor_count = "-"
        try:
            test_trivial_count = len(mapi.find_distinct("defectID",{'build':build,'deleted':False, "testLabels" : 'Automation', 'defectPriority' : 'Trivial'}))+\
                                len(mapi.find_distinct("defectID",{'build':build,'deleted':False, "testLabels" : 'CFT', 'defectPriority' : 'Trivial'}))
        except:
            test_trivial_count = "-"
        try:
            product_blocker_count = len(mapi.find_distinct("defectID",{'build':build,'deleted':False, 'defectPriority' : 'Blocker','testResult':'FAIL'}))
        except:
            product_blocker_count = "-"
        try:
            product_critical_count = len(mapi.find_distinct("defectID",{'build':build,'deleted':False, 'defectPriority' : 'Critical','testResult':'FAIL'}))
        except:
            product_critical_count = "-"
        try:
            product_major_count = len(mapi.find_distinct("defectID",{'build':build,'deleted':False, 'defectPriority' : 'Major','testResult':'FAIL'}))
        except:
            product_major_count = "-"
        try:
            product_minor_count = len(mapi.find_distinct("defectID",{'build':build,'deleted':False, 'defectPriority' : 'Minor','testResult':'FAIL'}))
        except:
            product_minor_count = "-"
        try:
            product_trivial_count = len(mapi.find_distinct("defectID",{'build':build,'deleted':False, 'defectPriority' : 'Trivial','testResult':'FAIL'}))
        except:
            product_trivial_count = "-"
        
        try:
            product_total = 0
            cursor = mapi.find({'build':build,'deleted':False,'testResult':'FAIL'})
            product_defect_IDs = []
            for doc in cursor:
                if 'defectID' in doc.keys():
                    if doc['defectID'] not in product_defect_IDs:
                        product_total +=1
                        product_defect_IDs.append(doc['defectID'])
        except:
            product_total = "-"
        try:
            test_total = test_blocker_count + test_critical_count + test_major_count + test_minor_count + test_trivial_count
        except:
            test_total = '-'    

        return [test_blocker_count,test_critical_count,test_major_count,test_minor_count,test_trivial_count,product_blocker_count,\
            product_critical_count,product_major_count,product_minor_count,product_trivial_count,test_total,product_total,\
            test_blocker_count,test_critical_count,test_major_count,test_minor_count,test_trivial_count,product_blocker_count,\
            product_critical_count,product_major_count,product_minor_count,product_trivial_count,test_total,product_total]
    else:
        return [None] * 24
#### ----------------------------------------------------------------------------------------------
# Eng & Exe report page - Table 2 : Overall QA report
@app.callback([
    # combine exe too
    Output('eng_qa_pass_current', 'children'),Output('eng_qa_fail_current', 'children'),Output('eng_qa_aborted_current', 'children'),
    Output('eng_qa_blocked_current', 'children'),Output('eng_qa_todo_current', 'children'),Output('eng_qa_pass_previous', 'children'),
    Output('eng_qa_fail_previous', 'children'),Output('eng_qa_aborted_previous', 'children'),Output('eng_qa_blocked_previous', 'children'),
    Output('eng_qa_todo_previous', 'children'),Output('eng_qa_total_current', 'children'),Output('eng_qa_total_previous', 'children'),
    
    Output('exe_qa_pass_current', 'children'),Output('exe_qa_fail_current', 'children'),Output('exe_qa_aborted_current', 'children'),
    Output('exe_qa_blocked_current', 'children'),Output('exe_qa_todo_current', 'children'),Output('exe_qa_pass_previous', 'children'),
    Output('exe_qa_fail_previous', 'children'),Output('exe_qa_aborted_previous', 'children'),Output('exe_qa_blocked_previous', 'children'),
    Output('exe_qa_todo_previous', 'children'),Output('exe_qa_total_current', 'children'),Output('exe_qa_total_previous', 'children'), ], #22 T2
    [Input('table_submit_button', 'n_clicks'),
    dash.dependencies.Input('url', 'pathname'),
    Input('table_build_input', 'value')],
    [State('table_build_input', 'value')],)
def update_eng_table_2(clicks, pathname, input_value, enter_input):

    build, pre_build, _ = get_input('cft',dash.callback_context, clicks, input_value, enter_input, pathname)
    if build:
        try:
            current_pass = mapi.count_documents({'build':build,'deleted':False, "testResult" : 'PASS'}) 
        except:
            current_pass = '-' 
        try:
            current_fail = mapi.count_documents({'build':build,'deleted':False, "testResult" : 'FAIL'})
        except:
            current_fail = '-' 
        try:
            current_aborted = mapi.count_documents({'build':build,'deleted':False, "testResult" : 'ABORTED'}) 
        except:
            current_aborted = '-' 
        try: 
            current_blocked = mapi.count_documents({'build':build,'deleted':False, "testResult" : 'BLOCKED'}) 
        except:
            current_blocked = '-' 
        try:
            current_todo = mapi.count_documents({'build':build,'deleted':False, "testResult" : 'TODO'}) 
        except:
            current_todo = '-' 
        try:
            current_total = mapi.count_documents({'build': build,'deleted':False})
        except:
            current_total = '-' 
        if pre_build:
            try:
                previous_pass = mapi.count_documents({'build':pre_build,'deleted':False, "testResult" : 'PASS'}) 
            except:
                previous_pass = '-' 
            try:
                previous_fail = mapi.count_documents({'build':pre_build,'deleted':False, "testResult" : 'FAIL'})
            except:
                previous_fail = '-' 
            try:
                previous_aborted = mapi.count_documents({'build':pre_build,'deleted':False, "testResult" : 'ABORTED'}) 
            except:
                previous_aborted = '-' 
            try:
                previous_blocked = mapi.count_documents({'build':pre_build,'deleted':False, "testResult" : 'BLOCKED'}) 
            except:
                previous_blocked = '-' 
            try:
                previous_todo = mapi.count_documents({'build':pre_build,'deleted':False, "testResult" : 'TODO'}) 
            except:
                previous_todo = '-' 
            try:
                previous_total = mapi.count_documents({'build': pre_build,'deleted':False})
            except:
                previous_total = '-' 
        else:
            previous_pass = '-'
            previous_fail = '-'
            previous_aborted = '-' 
            previous_blocked = '-' 
            previous_todo = '-' 
            previous_total = '-' 

        return [current_pass,current_fail,current_aborted,current_blocked,current_todo,previous_pass,previous_fail,\
            previous_aborted,previous_blocked,previous_todo,current_total,previous_total,\
            current_pass,current_fail,current_aborted,current_blocked,current_todo,previous_pass,previous_fail,\
            previous_aborted,previous_blocked,previous_todo,current_total,previous_total]
    else:
        return [None] * 24   
#### ----------------------------------------------------------------------------------------------
# Eng report page - Table 3 : Component Level Summary
@app.callback([
    Output('S3_1_pass', 'children'), Output('S3_1_fail', 'children'),Output('provision_1_pass', 'children'), Output('provision_1_fail', 'children'),Output('csm_1_pass', 'children'), 
    Output('csm_1_fail', 'children'), Output('sspl_1_pass', 'children'), Output('sspl_1_fail', 'children'), Output('motr_1_pass', 'children'), Output('motr_1_fail', 'children'),
    Output('ha_1_pass', 'children'), Output('ha_1_fail', 'children'), Output('loc_1_pass', 'children'), Output('loc_1_fail', 'children'),Output('cos_1_pass', 'children'), 
    Output('cos_1_fail', 'children'), Output('dr_1_pass', 'children'), Output('dr_1_fail', 'children'), Output('nr_1_pass', 'children'), Output('nr_1_fail', 'children'),Output('total_1_pass', 'children'), Output('total_1_fail', 'children'),
    
    Output('S3_2_pass', 'children'), Output('S3_2_fail', 'children'),Output('provision_2_pass', 'children'), Output('provision_2_fail', 'children'),
    Output('csm_2_pass', 'children'), Output('csm_2_fail', 'children'),Output('sspl_2_pass', 'children'), Output('sspl_2_fail', 'children'),
    Output('motr_2_pass', 'children'), Output('motr_2_fail', 'children'),Output('ha_2_pass', 'children'), Output('ha_2_fail', 'children'),
    Output('loc_2_pass', 'children'), Output('loc_2_fail', 'children'),Output('cos_2_pass', 'children'), Output('cos_2_fail', 'children'),
    Output('dr_2_pass', 'children'), Output('dr_2_fail', 'children'), Output('nr_2_pass', 'children'), Output('nr_2_fail', 'children'),
    Output('total_2_pass', 'children'), Output('total_2_fail', 'children'), #44 T3
    ],
    [Input('table_submit_button', 'n_clicks'),
    dash.dependencies.Input('url', 'pathname'),
    Input('table_build_input', 'value')],
    [State('table_build_input', 'value')],
    )
def update_eng_table_3(clicks, pathname, input_value, enter_input):
    build, pre_build, _ = get_input('cft',dash.callback_context, clicks, input_value, enter_input, pathname)
    S3_count_pass = 0
    S3_count_fail=0
    pro_count_pass=0
    pro_count_fail=0
    csm_count_pass=0
    csm_count_fail=0
    ras_count_pass=0
    ras_count_fail=0
    motr_count_pass=0
    motr_count_fail=0
    HA_count_pass=0
    HA_count_fail=0
    loc_count_pass=0
    loc_count_fail=0
    cos_count_pass=0
    cos_count_fail=0
    current_total_pass=0
    current_total_fail=0
    pre_S3_count_pass = 0
    pre_S3_count_fail=0
    pre_pro_count_pass=0
    pre_pro_count_fail=0
    pre_csm_count_pass=0
    pre_csm_count_fail=0
    pre_ras_count_pass=0
    pre_ras_count_fail=0
    pre_motr_count_pass=0
    pre_motr_count_fail=0
    pre_HA_count_pass=0
    pre_HA_count_fail=0
    pre_loc_count_pass=0
    pre_loc_count_fail=0
    pre_cos_count_pass=0
    pre_cos_count_fail=0
    pre_current_total_pass=0
    pre_current_total_fail=0
    data_recovery_pass = 0
    data_recovery_fail = 0
    node_recovery_pass = 0
    node_recovery_fail = 0
    pre_data_recovery_pass = 0
    pre_data_recovery_fail = 0
    pre_node_recovery_pass = 0
    pre_node_recovery_fail = 0	
    if build:
        try:
            cursor = mapi.find({'build':build,'deleted':False})
        except:
            return ['-'] * 44

        for doc in cursor:  
            try:                
                match = any(re.search('S3', label) for label in doc['testExecutionLabels'])
                if match:
                    if doc['testResult'] == 'PASS':
                        S3_count_pass+=1
                    elif doc['testResult'] == 'FAIL':
                        S3_count_fail+=1
                    continue
            except:
                S3_count_pass = "-"
                S3_count_fail = "-"
                
            try:
                match = any(re.search('Provision', label) for label in doc['testExecutionLabels'])
                if match:
                    if doc['testResult'] == 'PASS':
                        pro_count_pass+=1
                    elif doc['testResult'] == 'FAIL':
                        pro_count_fail+=1
                    continue
            except:
                pro_count_pass = "-"
                pro_count_fail = "-"
            try: 
                match = any(re.search('CSM', label) for label in doc['testExecutionLabels'])
                if match:
                    if doc['testResult'] == 'PASS':
                        csm_count_pass+=1
                    elif doc['testResult'] == 'FAIL':
                        csm_count_fail+=1
                    continue
            except:
                csm_count_pass = "-"
                csm_count_fail = "-"
            try: 
                match = any(re.search('RAS', label) for label in doc['testExecutionLabels'])
                if match:
                    if doc['testResult'] == 'PASS':
                        ras_count_pass+=1
                    elif doc['testResult'] == 'FAIL':
                        ras_count_fail+=1
                    continue
            except:
                ras_count_pass = "-"
                ras_count_fail = "-"
            try:
                match = any(re.search('motr', label) for label in doc['testExecutionLabels'])
                if match:
                    if doc['testResult'] == 'PASS':
                        motr_count_pass+=1
                    elif doc['testResult'] == 'FAIL':
                        motr_count_fail+=1
                    continue
            except:
                motr_count_pass = "-"
                motr_count_fail = "-"
            try:  
                match = any(re.search('HA', label) for label in doc['testExecutionLabels'])
                if match:
                    if doc['testResult'] == 'PASS':
                        HA_count_pass+=1
                    elif doc['testResult'] == 'FAIL':
                        HA_count_fail+=1
                    continue
            except:
                HA_count_pass = "-"
                HA_count_fail = "-"
            try: 
                match = any(re.search('locust', label.lower()) for label in doc['testExecutionLabels'])
                if match:
                    if doc['testResult'] == 'PASS':
                        loc_count_pass+=1
                    elif doc['testResult'] == 'FAIL':
                        loc_count_fail+=1
                    continue
            except:
                loc_count_pass = "-"
                loc_count_fail = "-"
            try: 
                match = any(re.search('cos', label.lower()) for label in doc['testExecutionLabels'])
                if match:
                    if doc['testResult'] == 'PASS':
                        cos_count_pass+=1
                    elif doc['testResult'] == 'FAIL':
                        cos_count_fail+=1
                    continue
            except:
                cos_count_pass = "-"
                cos_count_fail = "-"
            try: 
                match = any(re.search('data_recovery', label.lower()) for label in doc['testExecutionLabels'])
                if match:
                    if doc['testResult'] == 'PASS':
                        data_recovery_pass+=1
                    elif doc['testResult'] == 'FAIL':
                        data_recovery_fail+=1
                    continue
            except:
                data_recovery_pass = "-"
                data_recovery_fail = "-"
            try: 
                match = any(re.search('node_recovery', label.lower()) for label in doc['testExecutionLabels'])
                if match:
                    if doc['testResult'] == 'PASS':
                        node_recovery_pass+=1
                    elif doc['testResult'] == 'FAIL':
                        node_recovery_fail+=1
                    continue
            except:
                node_recovery_pass = "-"
                node_recovery_fail = "-"
        try:
            current_total_pass = mapi.count_documents({'build':build,'deleted':False,"testResult" : 'PASS'})
            current_total_fail = mapi.count_documents({'build':build,'deleted':False,"testResult" : 'FAIL'})
        except:
            current_total_pass = "-"
            current_total_fail = "-"
        
        if pre_build:
            cursorp = mapi.find({'build':pre_build,'deleted':False,})
            for doc in cursorp:  
                try:                
                    match = any(re.search('S3', label) for label in doc['testExecutionLabels'])
                    if match:
                        if doc['testResult'] == 'PASS':
                            pre_S3_count_pass+=1
                        elif doc['testResult'] == 'FAIL':
                            pre_S3_count_fail+=1
                        continue
                except:
                    pre_S3_count_pass = "-"
                    pre_S3_count_fail = "-"
                try:
                    match = any(re.search('Provision', label) for label in doc['testExecutionLabels'])
                    if match:
                        if doc['testResult'] == 'PASS':
                            pre_pro_count_pass+=1
                        elif doc['testResult'] == 'FAIL':
                            pre_pro_count_fail+=1
                        continue
                except:
                    pre_pro_count_pass = "-"
                    pre_pro_count_fail = "-"
                try: 
                    match = any(re.search('CSM', label) for label in doc['testExecutionLabels'])
                    if match:
                        if doc['testResult'] == 'PASS':
                            pre_csm_count_pass+=1
                        elif doc['testResult'] == 'FAIL':
                            pre_csm_count_fail+=1
                        continue
                except:
                    pre_csm_count_pass = "-"
                    pre_csm_count_fail = "-"
                try: 
                    match = any(re.search('RAS', label) for label in doc['testExecutionLabels'])
                    if match:
                        if doc['testResult'] == 'PASS':
                            pre_ras_count_pass+=1
                        elif doc['testResult'] == 'FAIL':
                            pre_ras_count_fail+=1
                        continue
                except:
                    pre_ras_count_pass = "-"
                    pre_ras_count_fail = "-"
                try: 
                    match = any(re.search('motr', label) for label in doc['testExecutionLabels'])
                    if match:
                        if doc['testResult'] == 'PASS':
                            pre_motr_count_pass+=1
                        elif doc['testResult'] == 'FAIL':
                            pre_motr_count_fail+=1
                        continue
                except:
                    pre_motr_count_pass = "-"
                    pre_motr_count_fail = "-"
                try:  
                    match = any(re.search('HA', label) for label in doc['testExecutionLabels'])
                    if match:
                        if doc['testResult'] == 'PASS':
                            pre_HA_count_pass+=1
                        elif doc['testResult'] == 'FAIL':
                            pre_HA_count_fail+=1
                        continue
                except:
                    pre_HA_count_pass = "-"
                    pre_HA_count_fail = "-"
                try:
                    match = any(re.search('locust', label.lower()) for label in doc['testExecutionLabels'])
                    if match:
                        if doc['testResult'] == 'PASS':
                            pre_loc_count_pass+=1
                        elif doc['testResult'] == 'FAIL':
                            pre_loc_count_fail+=1
                        continue
                except:
                    pre_loc_count_pass = "-"
                    pre_loc_count_fail = "-"
                try: 
                    match = any(re.search('cos', label.lower()) for label in doc['testExecutionLabels'])
                    if match:
                        if doc['testResult'] == 'PASS':
                            pre_cos_count_pass+=1
                        elif doc['testResult'] == 'FAIL':
                            pre_cos_count_fail+=1
                        continue
                except:
                    pre_cos_count_pass = "-"
                    pre_cos_count_fail = "-"
                try: 
                    match = any(re.search('data_recovery', label.lower()) for label in doc['testExecutionLabels'])
                    if match:
                        if doc['testResult'] == 'PASS':
                            pre_data_recovery_pass+=1
                        elif doc['testResult'] == 'FAIL':
                            pre_data_recovery_fail+=1
                        continue
                except:
                    pre_data_recovery_pass = "-"
                    pre_data_recovery_fail = "-"
                try: 
                    match = any(re.search('node_recovery', label.lower()) for label in doc['testExecutionLabels'])
                    if match:
                        if doc['testResult'] == 'PASS':
                            pre_node_recovery_pass+=1
                        elif doc['testResult'] == 'FAIL':
                            pre_node_recovery_fail+=1
                        continue
                except:
                    pre_node_recovery_pass = "-"
                    pre_node_recovery_fail = "-"
            try:
                pre_current_total_pass = mapi.count_documents({'build':pre_build,'deleted':False,"testResult" : 'PASS'})
                pre_current_total_fail = mapi.count_documents({'build':pre_build,'deleted':False,"testResult" : 'FAIL'})
            except:
                pre_current_total_pass = "-"
                pre_current_total_fail = "-"
            
        return [S3_count_pass,S3_count_fail,pro_count_pass,pro_count_fail,csm_count_pass,csm_count_fail,ras_count_pass,ras_count_fail,\
            motr_count_pass,motr_count_fail,HA_count_pass,HA_count_fail,loc_count_pass,loc_count_fail,cos_count_pass,cos_count_fail,data_recovery_pass,\
            data_recovery_fail,node_recovery_pass,node_recovery_fail,current_total_pass,current_total_fail,pre_S3_count_pass,pre_S3_count_fail,\
            pre_pro_count_pass,pre_pro_count_fail,pre_csm_count_pass,pre_csm_count_fail,pre_ras_count_pass,pre_ras_count_fail,pre_motr_count_pass,\
            pre_motr_count_fail,pre_HA_count_pass,pre_HA_count_fail,pre_loc_count_pass,pre_loc_count_fail,pre_cos_count_pass,pre_cos_count_fail,\
            pre_data_recovery_pass,pre_data_recovery_fail,pre_node_recovery_pass,pre_node_recovery_fail,pre_current_total_pass,pre_current_total_fail]
    
    return [None] * 44
#### ----------------------------------------------------------------------------------------------
# Eng report page - Table 5 : Timing Table
@app.callback([
    Output('update_min_1','children'),Output('deploy_min_1','children'),Output('box_min_1','children'),
    Output('unbox_min_1','children'),Output('onboard_min_1','children'),Output('firm_min_1','children'),Output('NReboot_min_1','children'),
    Output('Nstart_min_1','children'),Output('Nstop_min_1','children'),Output('Nfail_min_1','children'),Output('Nfback_min_1','children'),Output('stopA_min_1','children'),
    Output('startA_min_1','children'),Output('bcre_min_1','children'),Output('bdel_min_1','children'),Output('update_min_2','children'), 
    Output('deploy_min_2','children'),Output('box_min_2','children'),Output('unbox_min_2','children'),
    Output('onboard_min_2','children'),Output('firm_min_2','children'),Output('NReboot_min_2','children'),Output('Nstart_min_2','children'),
    Output('Nstop_min_2','children'),Output('Nfail_min_2','children'),Output('Nfback_min_2','children'),Output('stopA_min_2','children'),
    Output('startA_min_2','children'),Output('bcre_min_2','children'),Output('bdel_min_2','children'),Output('update_min_3','children'),
    Output('deploy_min_3','children'),Output('box_min_3','children'),Output('unbox_min_3','children'),
    Output('onboard_min_3','children'),Output('firm_min_3','children'),Output('NReboot_min_3','children'),Output('Nstart_min_3','children'),
    Output('Nstop_min_3','children'),Output('Nfail_min_3','children'),Output('Nfback_min_3','children'),Output('stopA_min_3','children'),
    Output('startA_min_3','children'),Output('bcre_min_3','children'),Output('bdel_min_3','children'),
    Output('update_min_4','children'),Output('deploy_min_4','children'),Output('box_min_4','children'),Output('unbox_min_4','children'),
    Output('onboard_min_4','children'),Output('firm_min_4','children'),Output('NReboot_min_4','children'),Output('Nstart_min_4','children'),
    Output('Nstop_min_4','children'),Output('Nfail_min_4','children'),Output('Nfback_min_4','children'),Output('stopA_min_4','children'),
    Output('startA_min_4','children'),Output('bcre_min_4','children'),Output('bdel_min_4','children'),
    Output('update_min_5','children'),Output('deploy_min_5','children'),Output('box_min_5','children'),Output('unbox_min_5','children'),
    Output('onboard_min_5','children'),Output('firm_min_5','children'),Output('NReboot_min_5','children'),Output('Nstart_min_5','children'),
    Output('Nstop_min_5','children'),Output('Nfail_min_5','children'),Output('Nfback_min_5','children'),Output('stopA_min_5','children'),
    Output('startA_min_5','children'),Output('bcre_min_5','children'),Output('bdel_min_5','children'),Output('timing_build_current','children'),
    Output('timing_build_prev_2','children'),Output('timing_build_prev_3','children'),Output('timing_build_prev_4','children'),Output('timing_build_prev_5','children'),
    ],
    [Input('table_submit_button', 'n_clicks'),
    dash.dependencies.Input('url', 'pathname'),
    Input('table_build_input', 'value')],
    [State('table_build_input', 'value')],
    )
def update_timing_table(clicks, pathname, input_value, enter_input):
    build, pre_build, version = get_input('cft',dash.callback_context, clicks, input_value, enter_input, pathname)
    data = []
    build_name = "Current Build"
    pre_build_name = "Prev Build"
    pre_pre_build_name = "Prev Build"
    pre_pre_pre_build_name = "Prev Build"
    pre_pre_pre_pre_build_name = "Prev Build"

    try:
        if build:
            build_name = build.capitalize()
            try:
                cursor = timingAPIs.find_distinct('updateTime',{'build':build})
                if cursor[-1] == 'NA':
                    cursor.pop()
                cursor = sorted(cursor)
                try:
                    update_avg_1 = sum(cursor)/len(cursor)
                except:
                    update_avg_1 = 'NA'
            except:
                update_avg_1 = '-'
            try:
                cursor = timingAPIs.find_distinct('deploymentTime',{'build':build})
                if cursor[-1] == 'NA':
                    cursor.pop()
                cursor = sorted(cursor)
                try:
                    deploy_avg_1 = sum(cursor)/len(cursor)
                except:
                    deploy_avg_1 = 'NA'
            except:
                deploy_avg_1 = '-'
            try:
                cursor = timingAPIs.find_distinct('boxingTime',{'build':build})
                if cursor[-1] == 'NA':
                    cursor.pop()
                cursor = sorted(cursor)
                try:
                    box_avg_1 = sum(cursor)/len(cursor)
                except:
                    box_avg_1 = 'NA'
            except:
                box_avg_1 = '-'
            try:
                cursor = timingAPIs.find_distinct('unboxingTime',{'build':build})
                if cursor[-1] == 'NA':
                    cursor.pop()
                cursor = sorted(cursor)
                try:
                    unbox_avg_1 = sum(cursor)/len(cursor)
                except:
                    unbox_avg_1 = 'NA'
            except:
                unbox_avg_1 = '-'
            try:
                cursor = timingAPIs.find_distinct('onboardingTime',{'build':build})
                if cursor[-1] == 'NA':
                    cursor.pop()
                cursor = sorted(cursor)
                try:
                    onboard_avg_1 = sum(cursor)/len(cursor)
                except:
                    onboard_avg_1 = 'NA'
            except:
                onboard_avg_1 = '-'
            try:
                cursor = timingAPIs.find_distinct('firmwareUpdateTime',{'build':build})
                if cursor[-1] == 'NA':
                    cursor.pop()
                cursor = sorted(cursor)
                try:
                    firm_avg_1 = sum(cursor)/len(cursor)
                except:
                    firm_avg_1 = 'NA'
            except:
                firm_avg_1 = '-'
            try:
                cursor = timingAPIs.find_distinct('nodeRebootTime',{'build':build})
                if cursor[-1] == 'NA':
                    cursor.pop()
                cursor = sorted(cursor)
                try:
                    reboot_avg_1 = sum(cursor)/len(cursor)
                except:
                    reboot_avg_1 = 'NA'
            except:
                reboot_avg_1 = '-'
            try:
                cursor = timingAPIs.find_distinct('nodeStarTime',{'build':build})
                if cursor[-1] == 'NA':
                    cursor.pop()
                cursor = sorted(cursor)
                try:
                    nstart_avg_1 = sum(cursor)/len(cursor)
                except:
                    nstart_avg_1 = 'NA'
            except:
                nstart_avg_1 = '-'
            try:
                cursor = timingAPIs.find_distinct('nodeStopTime',{'build':build})
                if cursor[-1] == 'NA':
                    cursor.pop()
                cursor = sorted(cursor)
                try:
                    nstop_avg_1 = sum(cursor)/len(cursor)
                except:
                    nstop_avg_1 = 'NA'
            except:
                nstop_avg_1 = '-'
            try:
                cursor = timingAPIs.find_distinct('nodeFailoverTime',{'build':build})
                if cursor[-1] == 'NA':
                    cursor.pop()
                cursor = sorted(cursor)
                try:
                    fail_avg_1 = sum(cursor)/len(cursor)
                except:
                    fail_avg_1 = 'NA'
            except:
                fail_avg_1 = '-'
            try:
                cursor = timingAPIs.find_distinct('nodeFailbackTime',{'build':build})
                if cursor[-1] == 'NA':
                    cursor.pop()
                cursor = sorted(cursor)
                try:
                    fb_avg_1 = sum(cursor)/len(cursor)
                except:
                    fb_avg_1 = 'NA'
            except:
                fb_avg_1 = '-'
            try:
                cursor = timingAPIs.find_distinct('allServiceStopTime',{'build':build})
                if cursor[-1] == 'NA':
                    cursor.pop()
                cursor = sorted(cursor)
                try:
                    allstop_avg_1 = sum(cursor)/len(cursor)
                except:
                    allstop_avg_1 = 'NA'
            except:
                allstop_avg_1 = '-'
            try:
                cursor = timingAPIs.find_distinct('allServiceStartTime',{'build':build})
                if cursor[-1] == 'NA':
                    cursor.pop()
                cursor = sorted(cursor)
                try:
                    allstart_avg_1 = sum(cursor)/len(cursor)
                except:
                    allstart_avg_1 = 'NA'
            except:

                allstart_avg_1 = '-'
            try:
                cursor = timingAPIs.find_distinct('bucketCreationTime',{'build':build})
                if cursor[-1] == 'NA':
                    cursor.pop()
                cursor = sorted(cursor)
                try:
                    bcrea_avg_1 = sum(cursor)/len(cursor)
                except:
                    bcrea_avg_1 = 'NA'
            except:
                bcrea_avg_1 = '-'
            try:
                cursor = timingAPIs.find_distinct('bucketDeletionTime',{'build':build})
                if cursor[-1] == 'NA':
                    cursor.pop()
                cursor = sorted(cursor)
                try:
                    bdel_avg_1 = sum(cursor)/len(cursor)
                except:
                    bdel_avg_1 = 'NA'
            except:
                bdel_avg_1 = '-'
            
            data.extend([update_avg_1,deploy_avg_1,box_avg_1,unbox_avg_1,onboard_avg_1,firm_avg_1,\
                reboot_avg_1,nstart_avg_1,nstop_avg_1,fail_avg_1,fb_avg_1,allstop_avg_1,allstart_avg_1,bcrea_avg_1,bdel_avg_1])
        else:
            data.extend(["-"]*15)
    except:
        data.extend(["-"]*15)
    try:
        if pre_build:
            pre_build_name = pre_build.capitalize()
            try:
                cursor = timingAPIs.find_distinct('updateTime',{'build':pre_build})
                if cursor[-1] == 'NA':
                    cursor.pop()
                cursor = sorted(cursor)
                try:
                    update_avg_2 = sum(cursor)/len(cursor)
                except:
                    update_avg_2 = 'NA'
            except:
                update_avg_2 = '-'
            try:
                cursor = timingAPIs.find_distinct('deploymentTime',{'build':pre_build})
                if cursor[-1] == 'NA':
                    cursor.pop()
                cursor = sorted(cursor)
                try:
                    deploy_avg_2 = sum(cursor)/len(cursor)
                except:
                    deploy_avg_2 = 'NA'
            except:
                deploy_avg_2 = '-'
            try:
                cursor = timingAPIs.find_distinct('boxingTime',{'build':pre_build})
                if cursor[-1] == 'NA':
                    cursor.pop()
                cursor = sorted(cursor)
                try:
                    box_avg_2 = sum(cursor)/len(cursor)
                except:
                    box_avg_2 = 'NA'
            except:
                box_avg_2 = '-'
            try:
                cursor = timingAPIs.find_distinct('unboxingTime',{'build':pre_build})
                if cursor[-1] == 'NA':
                    cursor.pop()
                cursor = sorted(cursor)
                try:
                    unbox_avg_2 = sum(cursor)/len(cursor)
                except:
                    unbox_avg_2 = 'NA'
            except:
                unbox_avg_2 = '-'
            try:
                cursor = timingAPIs.find_distinct('onboardingTime',{'build':pre_build})
                if cursor[-1] == 'NA':
                    cursor.pop()
                cursor = sorted(cursor)
                try:
                    onboard_avg_2 = sum(cursor)/len(cursor)
                except:
                    onboard_avg_2 = 'NA'
            except:
                onboard_avg_2 = '-'
            try:
                cursor = timingAPIs.find_distinct('firmwareUpdateTime',{'build':pre_build})
                if cursor[-1] == 'NA':
                    cursor.pop()
                cursor = sorted(cursor)
                try:
                    firm_avg_2 = sum(cursor)/len(cursor)
                except:
                    firm_avg_2 = 'NA'
            except:
                firm_avg_2 = '-'
            try:
                cursor = timingAPIs.find_distinct('nodeRebootTime',{'build':pre_build})
                if cursor[-1] == 'NA':
                    cursor.pop()
                cursor = sorted(cursor)
                try:
                    reboot_avg_2 = sum(cursor)/len(cursor)
                except:
                    reboot_avg_2 = 'NA'
            except:
                reboot_avg_2 = '-'
            try:
                cursor = timingAPIs.find_distinct('nodeStarTime',{'build':pre_build})
                if cursor[-1] == 'NA':
                    cursor.pop()
                cursor = sorted(cursor)
                try:
                    nstart_avg_2 = sum(cursor)/len(cursor)
                except:
                    nstart_avg_2 = 'NA'
            except:
                nstart_avg_2 = '-'
            try:
                cursor = timingAPIs.find_distinct('nodeStopTime',{'build':pre_build})
                if cursor[-1] == 'NA':
                    cursor.pop()
                cursor = sorted(cursor)
                try:
                    nstop_avg_2 = sum(cursor)/len(cursor)
                except:
                    nstop_avg_2 = 'NA'
            except:
                nstop_avg_2 = '-'
            try:
                cursor = timingAPIs.find_distinct('nodeFailoverTime',{'build':pre_build})
                if cursor[-1] == 'NA':
                    cursor.pop()
                cursor = sorted(cursor)
                try:
                    fail_avg_2 = sum(cursor)/len(cursor)
                except:
                    fail_avg_2 = 'NA'
            except:
                fail_avg_2 = '-'
            try:
                cursor = timingAPIs.find_distinct('nodeFailbackTime',{'build':pre_build})
                if cursor[-1] == 'NA':
                    cursor.pop()
                cursor = sorted(cursor)
                try:
                    fb_avg_2 = sum(cursor)/len(cursor)
                except:
                    fb_avg_2 = 'NA'
            except:
                fb_avg_2 = '-'
            try:
                cursor = timingAPIs.find_distinct('allServiceStopTime',{'build':pre_build})
                if cursor[-1] == 'NA':
                    cursor.pop()
                cursor = sorted(cursor)
                try:
                    allstop_avg_2 = sum(cursor)/len(cursor)
                except:
                    allstop_avg_2 = 'NA'
            except:
                allstop_avg_2 = '-'
            try:
                cursor = timingAPIs.find_distinct('allServiceStartTime',{'build':pre_build})
                if cursor[-1] == 'NA':
                    cursor.pop()
                cursor = sorted(cursor)
                try:
                    allstart_avg_2 = sum(cursor)/len(cursor)
                except:
                    allstart_avg_2 = 'NA'
            except:
                allstart_avg_2 = '-'
            try:
                cursor = timingAPIs.find_distinct('bucketCreationTime',{'build':pre_build})
                if cursor[-1] == 'NA':
                    cursor.pop()
                cursor = sorted(cursor)
                try:
                    bcrea_avg_2 = sum(cursor)/len(cursor)
                except:
                    bcrea_avg_2 = 'NA'
            except:
                bcrea_avg_2 = '-'
            try:
                cursor = timingAPIs.find_distinct('bucketDeletionTime',{'build':pre_build})
                if cursor[-1] == 'NA':
                    cursor.pop()
                cursor = sorted(cursor)
                try:
                    bdel_avg_2 = sum(cursor)/len(cursor)
                except:
                    bdel_avg_2 = 'NA'
            except:
                bdel_avg_2 = '-'
            
            data.extend([update_avg_2,deploy_avg_2,box_avg_2,unbox_avg_2,onboard_avg_2,firm_avg_2,\
                reboot_avg_2,nstart_avg_2,nstop_avg_2,fail_avg_2,fb_avg_2,allstop_avg_2,allstart_avg_2,bcrea_avg_2,bdel_avg_2])
        else:
            data.extend(["-"]*15)
    except:
        data.extend(["-"]*15)
    try:
        pre_pre_build = get_previous_build(pre_build, version)
        if pre_pre_build:
            pre_pre_build_name = pre_pre_build.capitalize()
            try:
                cursor = timingAPIs.find_distinct('updateTime',{'build':pre_pre_build})
                if cursor[-1] == 'NA':
                    cursor.pop()
                cursor = sorted(cursor)
                try:
                    update_avg_3 = sum(cursor)/len(cursor)
                except:
                    update_avg_3 = 'NA'
            except:
                update_avg_3 = '-'
            try:
                cursor = timingAPIs.find_distinct('deploymentTime',{'build':pre_pre_build})
                if cursor[-1] == 'NA':
                    cursor.pop()
                cursor = sorted(cursor)
                try:
                    deploy_avg_3 = sum(cursor)/len(cursor)
                except:
                    deploy_avg_3 = 'NA'
            except:
                deploy_avg_3 = '-'
            try:
                cursor = timingAPIs.find_distinct('boxingTime',{'build':pre_pre_build})
                if cursor[-1] == 'NA':
                    cursor.pop()
                cursor = sorted(cursor)
                try:
                    box_avg_3 = sum(cursor)/len(cursor)
                except:
                    box_avg_3 = 'NA'
            except:
                box_avg_3 = '-'
            try:
                cursor = timingAPIs.find_distinct('unboxingTime',{'build':pre_pre_build})
                if cursor[-1] == 'NA':
                    cursor.pop()
                cursor = sorted(cursor)
                try:
                    unbox_avg_3 = sum(cursor)/len(cursor)
                except:
                    unbox_avg_3 = 'NA'
            except:
                unbox_avg_3 = '-'
            try:
                cursor = timingAPIs.find_distinct('onboardingTime',{'build':pre_pre_build})
                if cursor[-1] == 'NA':
                    cursor.pop()
                cursor = sorted(cursor)
                try:
                    onboard_avg_3 = sum(cursor)/len(cursor)
                except:
                    onboard_avg_3 = 'NA'
            except:
                onboard_avg_3 = '-'
            try:
                cursor = timingAPIs.find_distinct('firmwareUpdateTime',{'build':pre_pre_build})
                if cursor[-1] == 'NA':
                    cursor.pop()
                cursor = sorted(cursor)
                try:
                    firm_avg_3 = sum(cursor)/len(cursor)
                except:
                    firm_avg_3 = 'NA'
            except:
                firm_avg_3 = '-'
            try:
                cursor = timingAPIs.find_distinct('nodeRebootTime',{'build':pre_pre_build})
                if cursor[-1] == 'NA':
                    cursor.pop()
                cursor = sorted(cursor)
                try:
                    reboot_avg_3 = sum(cursor)/len(cursor)
                except:
                    reboot_avg_3 = 'NA'
            except:
                reboot_avg_3 = '-'
            try:
                cursor = timingAPIs.find_distinct('nodeStarTime',{'build':pre_pre_build})
                if cursor[-1] == 'NA':
                    cursor.pop()
                cursor = sorted(cursor)
                try:
                    nstart_avg_3 = sum(cursor)/len(cursor)
                except:
                    nstart_avg_3 = 'NA'
            except:
                nstart_avg_3 = '-'
            try:
                cursor = timingAPIs.find_distinct('nodeStopTime',{'build':pre_pre_build})
                if cursor[-1] == 'NA':
                    cursor.pop()
                cursor = sorted(cursor)
                try:
                    nstop_avg_3 = sum(cursor)/len(cursor)
                except:
                    nstop_avg_3 = 'NA'
            except:
                nstop_avg_3 = '-'
            try:
                cursor = timingAPIs.find_distinct('nodeFailoverTime',{'build':pre_pre_build})
                if cursor[-1] == 'NA':
                    cursor.pop()
                cursor = sorted(cursor)
                try:
                    fail_avg_3 = sum(cursor)/len(cursor)
                except:
                    fail_avg_3 = 'NA'
            except:
                fail_avg_3 = '-'
            try:
                cursor = timingAPIs.find_distinct('nodeFailbackTime',{'build':pre_pre_build})
                if cursor[-1] == 'NA':
                    cursor.pop()
                cursor = sorted(cursor)
                try:
                    fb_avg_3 = sum(cursor)/len(cursor)
                except:
                    fb_avg_3 = 'NA'
            except:
                fb_avg_3 = '-'
            try:
                cursor = timingAPIs.find_distinct('allServiceStopTime',{'build':pre_pre_build})
                if cursor[-1] == 'NA':
                    cursor.pop()
                cursor = sorted(cursor)
                try:
                    allstop_avg_3 = sum(cursor)/len(cursor)
                except:
                    allstop_avg_3 = 'NA'
            except:
                allstop_avg_3 = '-'
            try:
                cursor = timingAPIs.find_distinct('allServiceStartTime',{'build':pre_pre_build})
                if cursor[-1] == 'NA':
                    cursor.pop()
                cursor = sorted(cursor)
                try:
                    allstart_avg_3 = sum(cursor)/len(cursor)
                except:
                    allstart_avg_3 = 'NA'
            except:
                allstart_avg_3 = '-'
            try:
                cursor = timingAPIs.find_distinct('bucketCreationTime',{'build':pre_pre_build})
                if cursor[-1] == 'NA':
                    cursor.pop()
                cursor = sorted(cursor)
                try:
                    bcrea_avg_3 = sum(cursor)/len(cursor)
                except:
                    bcrea_avg_3 = 'NA'
            except:
                bcrea_avg_3 = '-'
            try:
                cursor = timingAPIs.find_distinct('bucketDeletionTime',{'build':pre_pre_build})
                if cursor[-1] == 'NA':
                    cursor.pop()
                cursor = sorted(cursor)
                try:
                    bdel_avg_3 = sum(cursor)/len(cursor)
                except:
                    bdel_avg_3 = 'NA'
            except:
                bdel_avg_3 = '-'
            data.extend([update_avg_3,deploy_avg_3,box_avg_3,unbox_avg_3,onboard_avg_3,firm_avg_3,\
                reboot_avg_3,nstart_avg_3,nstop_avg_3,fail_avg_3,fb_avg_3,allstop_avg_3,allstart_avg_3,bcrea_avg_3,bdel_avg_3])
        else:
            data.extend(["-"]*15)
    except:
        data.extend(["-"]*15)
    try:
        pre_pre_pre_build = get_previous_build(pre_pre_build, version)
        if pre_pre_pre_build:
            pre_pre_pre_build_name = pre_pre_pre_build.capitalize()
            try:
                cursor = timingAPIs.find_distinct('updateTime',{'build':pre_pre_pre_build})
                if cursor[-1] == 'NA':
                    cursor.pop()
                cursor = sorted(cursor)
                try:
                    update_avg_4 = sum(cursor)/len(cursor)
                except:
                    update_avg_4 = 'NA'
            except:
                update_avg_4 = '-'
            try:
                cursor = timingAPIs.find_distinct('deploymentTime',{'build':pre_pre_pre_build})
                if cursor[-1] == 'NA':
                    cursor.pop()
                cursor = sorted(cursor)
                try:
                    deploy_avg_4 = sum(cursor)/len(cursor)
                except:
                    deploy_avg_4 = 'NA'
            except:
                deploy_avg_4 = '-'
            try:
                cursor = timingAPIs.find_distinct('boxingTime',{'build':pre_pre_pre_build})
                if cursor[-1] == 'NA':
                    cursor.pop()
                cursor = sorted(cursor)
                try:
                    box_avg_4 = sum(cursor)/len(cursor)
                except:
                    box_avg_4 = 'NA'
            except:
                box_avg_4 = '-'
            try:
                cursor = timingAPIs.find_distinct('unboxingTime',{'build':pre_pre_pre_build})
                if cursor[-1] == 'NA':
                    cursor.pop()
                cursor = sorted(cursor)
                try:
                    unbox_avg_4 = sum(cursor)/len(cursor)
                except:
                    unbox_avg_4 = 'NA'
            except:
                unbox_avg_4 = '-'
            try:
                cursor = timingAPIs.find_distinct('onboardingTime',{'build':pre_pre_pre_build})
                if cursor[-1] == 'NA':
                    cursor.pop()
                cursor = sorted(cursor)
                try:
                    onboard_avg_4 = sum(cursor)/len(cursor)
                except:
                    onboard_avg_4 = 'NA'
            except:
                onboard_avg_4 = '-'
            try:
                cursor = timingAPIs.find_distinct('firmwareUpdateTime',{'build':pre_pre_pre_build})
                if cursor[-1] == 'NA':
                    cursor.pop()
                cursor = sorted(cursor)
                try:
                    firm_avg_4 = sum(cursor)/len(cursor)
                except:
                    firm_avg_4 = 'NA'
            except:
                firm_avg_4 = '-'
            try:
                cursor = timingAPIs.find_distinct('nodeRebootTime',{'build':pre_pre_pre_build})
                if cursor[-1] == 'NA':
                    cursor.pop()
                cursor = sorted(cursor)
                try:
                    reboot_avg_4 = sum(cursor)/len(cursor)
                except:
                    reboot_avg_4 = 'NA'
            except:
                reboot_avg_4 = '-'
            try:
                cursor = timingAPIs.find_distinct('nodeStarTime',{'build':pre_pre_pre_build})
                if cursor[-1] == 'NA':
                    cursor.pop()
                cursor = sorted(cursor)
                try:
                    nstart_avg_4 = sum(cursor)/len(cursor)
                except:
                    nstart_avg_4 = 'NA'
            except:
                nstart_avg_4 = '-'
            try:
                cursor = timingAPIs.find_distinct('nodeStopTime',{'build':pre_pre_pre_build})
                if cursor[-1] == 'NA':
                    cursor.pop()
                cursor = sorted(cursor)
                try:
                    nstop_avg_4 = sum(cursor)/len(cursor)
                except:
                    nstop_avg_4 = 'NA'
            except:
                nstop_avg_4 = '-'
            try:
                cursor = timingAPIs.find_distinct('nodeFailoverTime',{'build':pre_pre_pre_build})
                if cursor[-1] == 'NA':
                    cursor.pop()
                cursor = sorted(cursor)
                try:
                    fail_avg_4 = sum(cursor)/len(cursor)
                except:
                    fail_avg_4 = 'NA'
            except:
                fail_avg_4 = '-'
            try:
                cursor = timingAPIs.find_distinct('nodeFailbackTime',{'build':pre_pre_pre_build})
                if cursor[-1] == 'NA':
                    cursor.pop()
                cursor = sorted(cursor)
                try:
                    fb_avg_4 = sum(cursor)/len(cursor)
                except:
                    fb_avg_4 = 'NA'
            except:
                fb_avg_4 = '-'
            try:
                cursor = timingAPIs.find_distinct('allServiceStopTime',{'build':pre_pre_pre_build})
                if cursor[-1] == 'NA':
                    cursor.pop()
                cursor = sorted(cursor)
                try:
                    allstop_avg_4 = sum(cursor)/len(cursor)
                except:
                    allstop_avg_4 = 'NA'
            except:
                allstop_avg_4 = '-'
            try:
                cursor = timingAPIs.find_distinct('allServiceStartTime',{'build':pre_pre_pre_build})
                if cursor[-1] == 'NA':
                    cursor.pop()
                cursor = sorted(cursor)
                try:
                    allstart_avg_4 = sum(cursor)/len(cursor)
                except:
                    allstart_avg_4 = 'NA'
            except:
                allstart_avg_4 = '-'
            try:
                cursor = timingAPIs.find_distinct('bucketCreationTime',{'build':pre_pre_pre_build})
                if cursor[-1] == 'NA':
                    cursor.pop()
                cursor = sorted(cursor)
                try:
                    bcrea_avg_4 = sum(cursor)/len(cursor)
                except:
                    bcrea_avg_4 = 'NA'
            except:
                bcrea_avg_4 = '-'
            try:
                cursor = timingAPIs.find_distinct('bucketDeletionTime',{'build':pre_pre_pre_build})
                if cursor[-1] == 'NA':
                    cursor.pop()
                cursor = sorted(cursor)
                try:
                    bdel_avg_4 = sum(cursor)/len(cursor)
                except:
                    bdel_avg_4 = 'NA'
            except:
                bdel_avg_4 = '-'
            
            data.extend([update_avg_4,deploy_avg_4,box_avg_4,unbox_avg_4,onboard_avg_4,firm_avg_4,\
                reboot_avg_4,nstart_avg_4,nstop_avg_4,fail_avg_4,fb_avg_4,allstop_avg_4,allstart_avg_4,bcrea_avg_4,bdel_avg_4])
        else:
            data.extend(["-"]*15)
    except:
        data.extend(["-"]*15)
    try:
        pre_pre_pre_pre_build = get_previous_build(pre_pre_pre_build, version)
        if pre_pre_pre_pre_build:
            pre_pre_pre_pre_build_name = pre_pre_pre_pre_build.capitalize()
            try:
                cursor = timingAPIs.find_distinct('updateTime',{'build':pre_pre_pre_pre_build})
                if cursor[-1] == 'NA':
                    cursor.pop()
                cursor = sorted(cursor)
                try:
                    update_avg_5 = sum(cursor)/len(cursor)
                except:
                    update_avg_5 = 'NA'
            except:
                update_avg_5 = '-'
            try:
                cursor = timingAPIs.find_distinct('deploymentTime',{'build':pre_pre_pre_pre_build})
                if cursor[-1] == 'NA':
                    cursor.pop()
                cursor = sorted(cursor)
                try:
                    deploy_avg_5 = sum(cursor)/len(cursor)
                except:
                    deploy_avg_5 = 'NA'
            except:
                deploy_avg_5 = '-'
            try:
                cursor = timingAPIs.find_distinct('boxingTime',{'build':pre_pre_pre_pre_build})
                if cursor[-1] == 'NA':
                    cursor.pop()
                cursor = sorted(cursor)
                try:
                    box_avg_5 = sum(cursor)/len(cursor)
                except:
                    box_avg_5 = 'NA'
            except:
                box_avg_5 = '-'
            try:
                cursor = timingAPIs.find_distinct('unboxingTime',{'build':pre_pre_pre_pre_build})
                if cursor[-1] == 'NA':
                    cursor.pop()
                cursor = sorted(cursor)
                try:
                    unbox_avg_5 = sum(cursor)/len(cursor)
                except:
                    unbox_avg_5 = 'NA'
            except:
                unbox_avg_5 = '-'
            try:
                cursor = timingAPIs.find_distinct('onboardingTime',{'build':pre_pre_pre_pre_build})
                if cursor[-1] == 'NA':
                    cursor.pop()
                cursor = sorted(cursor)
                try:
                    onboard_avg_5 = sum(cursor)/len(cursor)
                except:
                    onboard_avg_5 = 'NA'
            except:
                onboard_avg_5 = '-'
            try:
                cursor = timingAPIs.find_distinct('firmwareUpdateTime',{'build':pre_pre_pre_pre_build})
                if cursor[-1] == 'NA':
                    cursor.pop()
                cursor = sorted(cursor)
                try:
                    firm_avg_5 = sum(cursor)/len(cursor)
                except:
                    firm_avg_5 = 'NA'
            except:
                firm_avg_5 = '-'
            try:
                cursor = timingAPIs.find_distinct('nodeRebootTime',{'build':pre_pre_pre_pre_build})
                if cursor[-1] == 'NA':
                    cursor.pop()
                cursor = sorted(cursor)
                try:
                    reboot_avg_5 = sum(cursor)/len(cursor)
                except:
                    reboot_avg_5 = 'NA'
            except:
                reboot_avg_5 = '-'
            try:
                cursor = timingAPIs.find_distinct('nodeStarTime',{'build':pre_pre_pre_pre_build})
                if cursor[-1] == 'NA':
                    cursor.pop()
                cursor = sorted(cursor)
                try:
                    nstart_avg_5 = sum(cursor)/len(cursor)
                except:
                    nstart_avg_5 = 'NA'
            except:
                nstart_avg_5 = '-'
            try:
                cursor = timingAPIs.find_distinct('nodeStopTime',{'build':pre_pre_pre_pre_build})
                if cursor[-1] == 'NA':
                    cursor.pop()
                cursor = sorted(cursor)
                try:
                    nstop_avg_5 = sum(cursor)/len(cursor)
                except:
                    nstop_avg_5 = 'NA'
            except:
                nstop_avg_5 = '-'
            try:
                cursor = timingAPIs.find_distinct('nodeFailoverTime',{'build':pre_pre_pre_pre_build})
                if cursor[-1] == 'NA':
                    cursor.pop()
                cursor = sorted(cursor)
                try:
                    fail_avg_5 = sum(cursor)/len(cursor)
                except:
                    fail_avg_5 = 'NA'
            except:
                fail_avg_5 = '-'
            try:
                cursor = timingAPIs.find_distinct('nodeFailbackTime',{'build':pre_pre_pre_pre_build})
                if cursor[-1] == 'NA':
                    cursor.pop()
                cursor = sorted(cursor)
                try:
                    fb_avg_5 = sum(cursor)/len(cursor)
                except:
                    fb_avg_5 = 'NA'
            except:
                fb_avg_5 = '-'
            try:
                cursor = timingAPIs.find_distinct('allServiceStopTime',{'build':pre_pre_pre_pre_build})
                if cursor[-1] == 'NA':
                    cursor.pop()
                cursor = sorted(cursor)
                try:
                    allstop_avg_5 = sum(cursor)/len(cursor)
                except:
                    allstop_avg_5 = 'NA'
            except:
                allstop_avg_5 = '-'
            try:
                cursor = timingAPIs.find_distinct('allServiceStartTime',{'build':pre_pre_pre_pre_build})
                if cursor[-1] == 'NA':
                    cursor.pop()
                cursor = sorted(cursor)
                try:
                    allstart_avg_5 = sum(cursor)/len(cursor)
                except:
                    allstart_avg_5 = 'NA'
            except:
                allstart_avg_5 = '-'
            try:
                cursor = timingAPIs.find_distinct('bucketCreationTime',{'build':pre_pre_pre_pre_build})
                if cursor[-1] == 'NA':
                    cursor.pop()
                cursor = sorted(cursor)
                try:
                    bcrea_avg_5 = sum(cursor)/len(cursor)
                except:
                    bcrea_avg_5 = 'NA'
            except:
                bcrea_avg_5 = '-'
            try:
                cursor = timingAPIs.find_distinct('bucketDeletionTime',{'build':pre_pre_pre_pre_build})
                if cursor[-1] == 'NA':
                    cursor.pop()
                cursor = sorted(cursor)
                try:
                    bdel_avg_5 = sum(cursor)/len(cursor)
                except:
                    bdel_avg_5 = 'NA'
            except:
                bdel_avg_5 = '-'
            data.extend([update_avg_5,deploy_avg_5,box_avg_5,unbox_avg_5,onboard_avg_5,firm_avg_5,\
                reboot_avg_5,nstart_avg_5,nstop_avg_5,fail_avg_5,fb_avg_5,allstop_avg_5,allstart_avg_5,bcrea_avg_5,bdel_avg_5])
        else:
            data.extend(["-"]*15)
    except:
        data.extend(["-"]*15)
    
    data.extend([build_name,pre_build_name, pre_pre_build_name, pre_pre_pre_build_name, pre_pre_pre_pre_build_name])
    return data
#### ----------------------------------------------------------------------------------------------
# Eng report page - Table 4 : Detailed report
@app.callback(Output('build_report_div','children'),
    [Input('table_submit_button', 'n_clicks'),
    dash.dependencies.Input('url', 'pathname'),
    Input('table_build_input', 'value')],
    [State('table_build_input', 'value')],
)
def update_eng_table_4(clicks, pathname, input_value, enter_input):
    build, _, _ = get_input('cft', dash.callback_context, clicks, input_value, enter_input, pathname)
    if clicks:
        jiraURL = "https://jts.seagate.com/"
        options = {'server': jiraURL}
        auth_jira = JIRA(options, basic_auth=(username, password))

    while build:
        try:
            defectsList = mapi.find_distinct("defectID",{'build':build})
            if len(defectsList) == 0:
                return ["No Bugs."]
            data = []
            for defect in defectsList:
                result = mapi.find({'build':build,'defectID':defect})
                issue = auth_jira.issue(defect)
                entryy = result[0]
                entryy['status']=str(issue.fields.status)
                data.append(entryy)

            df = pd.DataFrame(list(data))
            df.drop(columns=['_id','testPlanID','build','testExecution','testLabels','feature','testResult','dateOfExecution','defectLabels',],inplace=True)
            detailed_report = dash_table.DataTable(
    
                id="detailed_report_table",
                columns = [{'name':'Component','id':'testExecutionLabels'},{'name':'Test ID','id':'testID'},{'name':'Priority','id':'defectPriority'},
                        {'name':'JIRA ID','id':'defectID'},{'name':'Status','id':'status'}, {'name':'Description','id':'defectSummary'}],
                data=df.to_dict('records'),
                sort_action="native",
                page_size=15,
                style_cell={'padding':'5px','fontSize': 18,'background-color' : '#E0E0E0',
                            'font-family': 'sans-serif','text-align':'center'},
                style_data = {'whitespace':'normal','height': 'auto','lineHeight': '15px'},
                style_header={
                    'backgroundColor': '#7F8C8D',
                    'fontWeight': 'bold',
                    'textAlign': 'center'
                },
                style_table={'overflowX': 'auto'},
                style_data_conditional=[{
                    'if': {'column_id': 'defectSummary'},
                    'backgroundColor': '#FFFFFF',
                    'text-align':'left'
                },
                {'if': {
                        'column_id': 'defectPriority',
                        'filter_query': '{{defectPriority}} = {}'.format("Blocker"),
                    },
                        'color' : '#ff6262',},
                {'if': {
                        'column_id': 'defectPriority',
                        'filter_query': '{{defectPriority}} = {}'.format("Critical"),                        
                    },
                        'color'  :'#DC7633',},
                {'if': {
                        'column_id': 'defectPriority',
                        'filter_query': '{{defectPriority}} = {}'.format("Major"),                        
                    },
                        'color' : '#504de4',},
                {'if': {
                        'column_id': 'defectPriority',
                        'filter_query': '{{defectPriority}} = {}'.format("Minor"),
                    },
                        'color' : '#343a40',},
                {'if': {
                        'column_id': 'defectPriority',
                        'filter_query': '{{defectPriority}} = {}'.format("Trivial"),                        
                    },
                        'color' : '#3cba3c',},     
            ],)
            return [detailed_report]
        except:
            return [None]
    return [None]
#### ----------------------------------------------------------------------------------------------
# Eng report page - Table 6 : S3 bench statistics table
@app.callback([
    Output('WTH4','children'),Output('WTH256','children'), Output('RTH4','children'),Output('RTH256','children'),
    Output('WL4','children'),Output('WL256','children'),Output('RL4','children'),Output('RL256','children'),
    Output('e4WTH','children'),Output('e100WTH','children'),Output('e1WTH','children'),Output('e5WTH','children'),
    Output('e36WTH','children'),Output('e64WTH','children'),Output('e128WTH','children'),Output('e256WTH','children'),
    Output('e4RTH','children'),Output('e100RTH','children'),Output('e1RTH','children'),Output('e5RTH','children'),
    Output('e36RTH','children'),Output('e64RTH','children'),Output('e128RTH','children'),Output('e256RTH','children'),
    Output('e4WL','children'),Output('e100WL','children'),Output('e1WL','children'),Output('e5WL','children'),
    Output('e36WL','children'),Output('e64WL','children'),Output('e128WL','children'),Output('e256WL','children'),
    Output('e4RL','children'),Output('e100RL','children'),Output('e1RL','children'),Output('e5RL','children'),
    Output('e36RL','children'),Output('e64RL','children'),Output('e128RL','children'),Output('e256RL','children'),
    Output('e4WIOPS','children'),Output('e100WIOPS','children'),Output('e1WIOPS','children'),Output('e5WIOPS','children'),
    Output('e36WIOPS','children'),Output('e64WIOPS','children'),Output('e128WIOPS','children'),Output('e256WIOPS','children'),
    Output('e4RIOPS','children'),Output('e100RIOPS','children'),Output('e1RIOPS','children'),Output('e5RIOPS','children'),
    Output('e36RIOPS','children'),Output('e64RIOPS','children'),Output('e128RIOPS','children'),Output('e256RIOPS','children'),
    Output('e4WTTFB','children'),Output('e100WTTFB','children'),Output('e1WTTFB','children'),Output('e5WTTFB','children'),
    Output('e36WTTFB','children'),Output('e64WTTFB','children'),Output('e128WTTFB','children'),Output('e256WTTFB','children'),
    Output('e4RTTFB','children'),Output('e100RTTFB','children'),Output('e1RTTFB','children'),Output('e5RTTFB','children'),
    Output('e36RTTFB','children'),Output('e64RTTFB','children'),Output('e128RTTFB','children'),Output('e256RTTFB','children'),
    ],
    [Input('table_submit_button', 'n_clicks'),
    dash.dependencies.Input('url', 'pathname'),
    Input('table_build_input', 'value')],
    [State('table_build_input', 'value')],
)
def update_perf1(clicks, pathname, input_value, enter_input):
    build, _, _ = get_input('perf',dash.callback_context, clicks, input_value, enter_input, pathname)
   
    if build:     
        try:
            write_data_4 = perfDb.results.find({'Build':build,'Name': 'S3bench','Object_Size': '4Kb', 'Operation': 'Write'})
            WTH4 = roundoff(write_data_4[0]['Throughput'])
            WLAT4 = roundoff(write_data_4[0]['Latency']['Avg']*1000)
            WIOPS4 = roundoff(write_data_4[0]['IOPS'])
            WTTFB4 = roundoff(write_data_4[0]['TTFB']['Avg']*1000)
        except:
            WTH4 = "-"
            WLAT4 = "-"
            WIOPS4 = "-"
            WTTFB4 = "-"
        try:
            read_data_4 = perfDb.results.find({'Build':build,'Name': 'S3bench','Object_Size': '4Kb', 'Operation': 'Read'})
            RTH4 = roundoff(read_data_4[0]['Throughput'])
            RLAT4 = roundoff(read_data_4[0]['Latency']['Avg']*1000)
            RIOPS4 = roundoff(read_data_4[0]['IOPS'])
            RTTFB4 = roundoff(read_data_4[0]['TTFB']['Avg']*1000)
        except:
            RTH4 = "-"
            RLAT4 = "-"
            RIOPS4 = "-"
            RTTFB4 = "-"
        try:
            write_data_100 = perfDb.results.find({'Build':build,'Name': 'S3bench','Object_Size': '100Kb', 'Operation': 'Write'})
            WTH100 = roundoff(write_data_100[0]['Throughput'])
            WLAT100 = roundoff(write_data_100[0]['Latency']['Avg']*1000)
            WIOPS100 = roundoff(write_data_100[0]['IOPS'])
            WTTFB100 = roundoff(write_data_100[0]['TTFB']['Avg']*1000)
        except:
            WTH100 = "-"
            WLAT100 = "-"
            WIOPS100 = "-"
            WTTFB100 = "-"
        try:
            read_data_100 = perfDb.results.find({'Build':build,'Name': 'S3bench','Object_Size': '100Kb', 'Operation': 'Read'})
            RTH100 = roundoff(read_data_100[0]['Throughput'])
            RLAT100 = roundoff(read_data_100[0]['Latency']['Avg']*1000)
            RIOPS100 = roundoff(read_data_100[0]['IOPS'])
            RTTFB100 = roundoff(read_data_100[0]['TTFB']['Avg']*1000)
        except:
            RTH100 = "-"
            RLAT100 = "-"
            RIOPS100 = "-"
            RTTFB100 = "-"
        try:
            write_data_1 = perfDb.results.find({'Build':build,'Name': 'S3bench','Object_Size': '1Mb', 'Operation': 'Write'})
            WTH1 = roundoff(write_data_1[0]['Throughput'])
            WLAT1 = roundoff(write_data_1[0]['Latency']['Avg']*1000)
            WIOPS1 = roundoff(write_data_1[0]['IOPS'])
            WTTFB1 = roundoff(write_data_1[0]['TTFB']['Avg']*1000)
        except:
            WTH1 = "-"
            WLAT1 = "-"
            WIOPS1 = "-"
            WTTFB1 = "-"
        try:
            read_data_1 = perfDb.results.find({'Build':build,'Name': 'S3bench','Object_Size': '1Mb', 'Operation': 'Read'})
            RTH1 = roundoff(read_data_1[0]['Throughput'])
            RLAT1 = roundoff(read_data_1[0]['Latency']['Avg']*1000)
            RIOPS1 = roundoff(read_data_1[0]['IOPS'])
            RTTFB1 = roundoff(read_data_1[0]['TTFB']['Avg']*1000)
        except:
            RTH1 = "-"
            RLAT1 = "-"
            RIOPS1 = "-"
            RTTFB1 = "-"
        try:
            write_data_5 = perfDb.results.find({'Build':build,'Name': 'S3bench','Object_Size': '5Mb', 'Operation': 'Write'})
            WTH5 = roundoff(write_data_5[0]['Throughput'])
            WLAT5 = roundoff(write_data_5[0]['Latency']['Avg']*1000)
            WIOPS5 = roundoff(write_data_5[0]['IOPS'])
            WTTFB5 = roundoff(write_data_5[0]['TTFB']['Avg']*1000)
        except:
            WTH5 = "-"
            WLAT5 = "-"
            WIOPS5 = "-"
            WTTFB5 = "-"
        try:
            read_data_5 = perfDb.results.find({'Build':build,'Name': 'S3bench','Object_Size': '5Mb', 'Operation': 'Read'})
            RTH5 = roundoff(read_data_5[0]['Throughput'])
            RLAT5 = roundoff(read_data_5[0]['Latency']['Avg']*1000)
            RIOPS5 = roundoff(read_data_5[0]['IOPS'])
            RTTFB5 = roundoff(read_data_5[0]['TTFB']['Avg']*1000)
        except:
            RTH5 = "-"
            RLAT5 = "-"
            RIOPS5 = "-"
            RTTFB5 = "-"
        try:
            write_data_36 = perfDb.results.find({'Build':build,'Name': 'S3bench','Object_Size': '36Mb', 'Operation': 'Write'})
            WTH36 = roundoff(write_data_36[0]['Throughput'])
            WLAT36 = roundoff(write_data_36[0]['Latency']['Avg']*1000)
            WIOPS36 = roundoff(write_data_36[0]['IOPS'])
            WTTFB36 = roundoff(write_data_36[0]['TTFB']['Avg']*1000)
        except:
            WTH36 = "-"
            WLAT36 = "-"
            WIOPS36 = "-"
            WTTFB36 = "-"
        try:
            read_data_36 = perfDb.results.find({'Build':build,'Name': 'S3bench','Object_Size': '36Mb', 'Operation': 'Read'})
            RTH36 = roundoff(read_data_36[0]['Throughput'])
            RLAT36 = roundoff(read_data_36[0]['Latency']['Avg']*1000)
            RIOPS36 = roundoff(read_data_36[0]['IOPS'])
            RTTFB36 = roundoff(read_data_36[0]['TTFB']['Avg']*1000)
        except:
            RTH36 = "-"
            RLAT36 = "-"
            RIOPS36 = "-"
            RTTFB36 = "-"
        try:
            write_data_64 = perfDb.results.find({'Build':build,'Name': 'S3bench','Object_Size': '64Mb', 'Operation': 'Write'})
            WTH64 = roundoff(write_data_64[0]['Throughput'])
            WLAT64 = roundoff(write_data_64[0]['Latency']['Avg']*1000)
            WIOPS64 = roundoff(write_data_64[0]['IOPS'])
            WTTFB64 = roundoff(write_data_64[0]['TTFB']['Avg']*1000)
        except:
            WTH64 = "-"
            WLAT64 = "-"
            WIOPS64 = "-"
            WTTFB64 = "-"
        try:
            read_data_64 = perfDb.results.find({'Build':build,'Name': 'S3bench','Object_Size': '64Mb', 'Operation': 'Read'})
            RTH64 = roundoff(read_data_64[0]['Throughput'])
            RLAT64 = roundoff(read_data_64[0]['Latency']['Avg']*1000)
            RIOPS64 = roundoff(read_data_64[0]['IOPS'])
            RTTFB64 = roundoff(read_data_64[0]['TTFB']['Avg']*1000)
        except:
            RTH64 = "-"
            RLAT64 = "-"
            RIOPS64 = "-"
            RTTFB64 = "-"
        try:
            write_data_128 = perfDb.results.find({'Build':build,'Name': 'S3bench','Object_Size': '128Mb', 'Operation': 'Write'})
            WTH128 = roundoff(write_data_128[0]['Throughput'])
            WLAT128 = roundoff(write_data_128[0]['Latency']['Avg']*1000)
            WIOPS128 = roundoff(write_data_128[0]['IOPS'])
            WTTFB128 = roundoff(write_data_128[0]['TTFB']['Avg']*1000)
        except:
            WTH128 = "-"
            WLAT128 = "-"
            WIOPS128 = "-"
            WTTFB128 = "-"
        try:
            read_data_128 = perfDb.results.find({'Build':build,'Name': 'S3bench','Object_Size': '128Mb', 'Operation': 'Read'})
            RTH128 = roundoff(read_data_128[0]['Throughput'])
            RLAT128 = roundoff(read_data_128[0]['Latency']['Avg']*1000)
            RIOPS128 = roundoff(read_data_128[0]['IOPS'])
            RTTFB128 = roundoff(read_data_128[0]['TTFB']['Avg']*1000)
        except:
            RTH128 = "-"
            RLAT128 = "-"
            RIOPS128 = "-"
            RTTFB128 = "-"
        try:
            write_data_256 = perfDb.results.find({'Build':build,'Name': 'S3bench','Object_Size': '256Mb', 'Operation': 'Write'})
            WTH256 = roundoff(write_data_256[0]['Throughput'])
            WLAT256 = roundoff(write_data_256[0]['Latency']['Avg']*1000)
            WIOPS256 = roundoff(write_data_256[0]['IOPS'])
            WTTFB256 = roundoff(write_data_256[0]['TTFB']['Avg']*1000)
        except:
            WTH256 = "-"
            WLAT256 = "-"
            WIOPS256 = "-"
            WTTFB256 = "-"
        try:
            read_data_256 = perfDb.results.find({'Build':build,'Name': 'S3bench','Object_Size': '256Mb', 'Operation': 'Read'})
            RTH256 = roundoff(read_data_256[0]['Throughput'])
            RLAT256 = roundoff(read_data_256[0]['Latency']['Avg']*1000)
            RIOPS256 = roundoff(read_data_256[0]['IOPS'])
            RTTFB256 = roundoff(read_data_256[0]['TTFB']['Avg']*1000)
        except:
            RTH256 = "-"
            RLAT256 = "-"
            RIOPS256 = "-"
            RTTFB256 = "-"

        return [WTH4,WTH256,RTH4,RTH256,WLAT4,WLAT256,RLAT4,RLAT256,WTH4,WTH100,WTH1,WTH5,WTH36,WTH64,WTH128,WTH256,RTH4,RTH100,RTH1,\
            RTH5,RTH36,RTH64,RTH128,RTH256,WLAT4,WLAT100,WLAT1,WLAT5,WLAT36,WLAT64,WLAT128,WLAT256,RLAT4,RLAT100,RLAT1,RLAT5,RLAT36,RLAT64,RLAT128,\
            RLAT256,WIOPS4,WIOPS100,WIOPS1,WIOPS5,WIOPS36,WIOPS64,WIOPS128,WIOPS256,RIOPS4,RIOPS100,RIOPS1,RIOPS5,RIOPS36,RIOPS64,RIOPS128,\
            RIOPS256,WTTFB4,WTTFB100,WTTFB1,WTTFB5,WTTFB36,WTTFB64,WTTFB128,WTTFB256,RTTFB4,RTTFB100,RTTFB1,RTTFB5,RTTFB36,RTTFB64,RTTFB128,RTTFB256]

    return [None] * 72 
#### ----------------------------------------------------------------------------------------------
# Eng report page - Table 7 : S3bench latencies table
@app.callback([Output('puttag_value','children'),Output('gettag_value','children'),
    Output('headobj_value','children'),],
    [Input('table_submit_button', 'n_clicks'),
    dash.dependencies.Input('url', 'pathname'),
    Input('table_build_input', 'value')],
    [State('table_build_input', 'value')],
)
def update_perf2(clicks, pathname, input_value, enter_input):
    build, _, _ = get_input('perf',dash.callback_context, clicks, input_value, enter_input, pathname)
    if build:
        try:
            data = perfDb.results.find({'Name':'S3bench','Build':build,'Object_Size': '1Kb', 'Operation': 'PutObjTag'})
            pv = data[0]['Latency']['Avg']*1000
        except:
            pv = "-"
        try:
            g = perfDb.results.find({'Name':'S3bench','Build':build,'Object_Size': '1Kb', 'Operation': 'GetObjTag'})
            gv = g[0]['Latency']['Avg']*1000
        except:
            gv = "-"
        try:
            h = perfDb.results.find({'Build':build,'Name':'S3bench','Object_Size': '1Kb', 'Operation': 'HeadObj'})
            hv = h[0]['Latency']['Avg']*1000
        except:
            hv = "-"

        return [pv,gv,hv]
    
    return [None] * 3
#### ----------------------------------------------------------------------------------------------
# Eng report page - Table 8 :Hsbench 1
@app.callback([Output('e4HS1WTH','children'),Output('e100HS1WTH','children'),Output('e1HS1WTH','children'),Output('e5HS1WTH','children'),Output('e36HS1WTH','children'),Output('e64HS1WTH','children'),Output('e128HS1WTH','children'),Output('e256HS1WTH','children'),
    Output('e4HS1RTH','children'),Output('e100HS1RTH','children'),Output('e1HS1RTH','children'),Output('e5HS1RTH','children'),Output('e36HS1RTH','children'),Output('e64HS1RTH','children'),Output('e128HS1RTH','children'),Output('e256HS1RTH','children'),
    Output('e4HS1WL','children'),Output('e100HS1WL','children'),Output('e1HS1WL','children'),Output('e5HS1WL','children'),Output('e36HS1WL','children'),Output('e64HS1WL','children'),Output('e128HS1WL','children'),Output('e256HS1WL','children'),
    Output('e4HS1RL','children'),Output('e100HS1RL','children'),Output('e1HS1RL','children'),Output('e5HS1RL','children'),Output('e36HS1RL','children'),Output('e64HS1RL','children'),Output('e128HS1RL','children'),Output('e256HS1RL','children'),
    Output('e4HS1WIOPS','children'),Output('e100HS1WIOPS','children'),Output('e1HS1WIOPS','children'),Output('e5HS1WIOPS','children'),Output('e36HS1WIOPS','children'),Output('e64HS1WIOPS','children'),Output('e128HS1WIOPS','children'),Output('e256HS1WIOPS','children'),
    Output('e4HS1RIOPS','children'),Output('e100HS1RIOPS','children'),Output('e1HS1RIOPS','children'),Output('e5HS1RIOPS','children'),Output('e36HS1RIOPS','children'),Output('e64HS1RIOPS','children'),Output('e128HS1RIOPS','children'),Output('e256HS1RIOPS','children'),
    ],
    [Input('table_submit_button', 'n_clicks'),
    dash.dependencies.Input('url', 'pathname'),
    Input('table_build_input', 'value')],
    [State('table_build_input', 'value')],
)
def update_hsbench1(clicks, pathname, input_value, enter_input):
    build, _, _ = get_input('perf',dash.callback_context, clicks, input_value, enter_input, pathname)
    if build:
        try:
            HS1 = perfDb.results.find({'Build':build,'Name': 'Hsbench','Operation':'write','Object_Size':'4Kb','Buckets':1,'Objects':1000,'Sessions':100}) 
            WTH41 = roundoff(HS1[0]['Throughput'])
            WL41 = roundoff(HS1[0]['Latency'])
            WIOPS41 = roundoff(HS1[0]['IOPS'])
        except:
            WTH41 = "-"
            WL41 = '-'
            WIOPS41 = '-'
        try:
            HS1 = perfDb.results.find({'Build':build,'Name': 'Hsbench','Operation':'read','Object_Size':'4Kb','Buckets':1,'Objects':1000,'Sessions':100}) 
            RTH41 = roundoff(HS1[0]['Throughput'])
            RL41 = roundoff(HS1[0]['Latency'])
            RIOPS41 = roundoff(HS1[0]['IOPS'])  
        except:
            RTH41 = "-"
            RL41 = '-'
            RIOPS41 = '-'
        try:
            HS1 = perfDb.results.find({'Build':build,'Name': 'Hsbench','Operation':'write','Object_Size':'100Kb','Buckets':1,'Objects':1000,'Sessions':100}) 
            WTH1001 = roundoff(HS1[0]['Throughput'])
            WL1001 = roundoff(HS1[0]['Latency'])
            WIOPS1001 = roundoff(HS1[0]['IOPS']) 
        except:
            WTH1001 = "-"
            WL1001 = '-'
            WIOPS1001 = '-'
        try:
            HS1 = perfDb.results.find({'Build':build,'Name': 'Hsbench','Operation':'read','Object_Size':'100Kb','Buckets':1,'Objects':1000,'Sessions':100}) 
            RTH1001 = roundoff(HS1[0]['Throughput'])
            RL1001 = roundoff(HS1[0]['Latency'])
            RIOPS1001 = roundoff(HS1[0]['IOPS'])  
        except:
            RTH1001 = "-"
            RL1001 = '-'
            RIOPS1001 = '-'
        try:
            HS1 = perfDb.results.find({'Build':build,'Name': 'Hsbench','Operation':'write','Object_Size':'1Mb','Buckets':1,'Objects':1000,'Sessions':100}) 
            WTH11 = roundoff(HS1[0]['Throughput'])
            WL11 = roundoff(HS1[0]['Latency'])
            WIOPS11 = roundoff(HS1[0]['IOPS'])  
        except:
            WTH11 = "-"
            WL11 = '-'
            WIOPS11 = '-'
        try:
            HS1 = perfDb.results.find({'Build':build,'Name': 'Hsbench','Operation':'read','Object_Size':'1Mb','Buckets':1,'Objects':1000,'Sessions':100}) 
            RTH11 = roundoff(HS1[0]['Throughput'])
            RL11 = roundoff(HS1[0]['Latency'])
            RIOPS11 = roundoff(HS1[0]['IOPS'])   
        except:
            RTH11 = "-"
            RL11 = '-'
            RIOPS11 = '-'
        try:
            HS1 = perfDb.results.find({'Build':build,'Name': 'Hsbench','Operation':'write','Object_Size':'5Mb','Buckets':1,'Objects':1000,'Sessions':100}) 
            WTH51 = roundoff(HS1[0]['Throughput'])
            WL51 = roundoff(HS1[0]['Latency'])
            WIOPS51 =roundoff(HS1[0]['IOPS'])   
        except:
            WTH51 = "-"
            WL51 = '-'
            WIOPS51 = '-'
        try:
            HS1 = perfDb.results.find({'Build':build,'Name': 'Hsbench','Operation':'read','Object_Size':'5Mb','Buckets':1,'Objects':1000,'Sessions':100}) 
            RTH51 = roundoff(HS1[0]['Throughput'])
            RL51 = roundoff(HS1[0]['Latency'])
            RIOPS51 =roundoff( HS1[0]['IOPS'])   
        except:
            RTH51 = "-"
            RL51 = '-'
            RIOPS51 = '-'
        try:
            HS1 = perfDb.results.find({'Build':build,'Name': 'Hsbench','Operation':'write','Object_Size':'36Mb','Buckets':1,'Objects':1000,'Sessions':100}) 
            WTH361 =roundoff( HS1[0]['Throughput'])
            WL361 = roundoff(HS1[0]['Latency'])
            WIOPS361 = roundoff(HS1[0]['IOPS']) 
        except:
            WTH361 = "-"
            WL361 = '-'
            WIOPS361 = '-'
        try:
            HS1 = perfDb.results.find({'Build':build,'Name': 'Hsbench','Operation':'read','Object_Size':'36Mb','Buckets':1,'Objects':1000,'Sessions':100}) 
            RTH361 = roundoff(HS1[0]['Throughput'])
            RL361 =roundoff( HS1[0]['Latency'])
            RIOPS361 = roundoff(HS1[0]['IOPS'])   
        except:
            RTH361 = "-"
            RL361 = '-'
            RIOPS361 = '-'
        try:
            HS1 = perfDb.results.find({'Build':build,'Name': 'Hsbench','Operation':'write','Object_Size':'64Mb','Buckets':1,'Objects':1000,'Sessions':100}) 
            WTH641 = roundoff(HS1[0]['Throughput'])
            WL641 = roundoff(HS1[0]['Latency'])
            WIOPS641 = roundoff(HS1[0]['IOPS'])   
        except:
            WTH641 = "-"
            WL641 = '-'
            WIOPS641 = '-'
        try:
            HS1 = perfDb.results.find({'Build':build,'Name': 'Hsbench','Operation':'read','Object_Size':'64Mb','Buckets':1,'Objects':1000,'Sessions':100}) 
            RTH641 = roundoff(HS1[0]['Throughput'])
            RL641 = roundoff(HS1[0]['Latency'])
            RIOPS641 = roundoff(HS1[0]['IOPS'])   
        except:
            RTH641 = "-"
            RL641 = '-'
            RIOPS641 = '-'
        try:
            HS1 = perfDb.results.find({'Build':build,'Name': 'Hsbench','Operation':'write','Object_Size':'128Mb','Buckets':1,'Objects':1000,'Sessions':100}) 
            WTH1281 = roundoff(HS1[0]['Throughput'])
            WL1281 = roundoff(HS1[0]['Latency'])
            WIOPS1281 = roundoff(HS1[0]['IOPS'])   
        except:
            WTH1281 = "-"
            WL1281 = '-'
            WIOPS1281 = '-'
        try:
            HS1 = perfDb.results.find({'Build':build,'Name': 'Hsbench','Operation':'read','Object_Size':'128Mb','Buckets':1,'Objects':1000,'Sessions':100}) 
            RTH1281 = roundoff(HS1[0]['Throughput'])
            RL1281 = roundoff(HS1[0]['Latency'])
            RIOPS1281 = roundoff(HS1[0]['IOPS'])   
        except:
            RTH1281 = "-"
            RL1281 = '-'
            RIOPS1281 = '-'
        try:
            HS1 = perfDb.results.find({'Build':build,'Name': 'Hsbench','Operation':'write','Object_Size':'256Mb','Buckets':1,'Objects':1000,'Sessions':100}) 
            WTH2561 = roundoff(HS1[0]['Throughput'])
            WL2561 = roundoff(HS1[0]['Latency'])
            WIOPS2561 = roundoff(HS1[0]['IOPS'])   
        except:
            WTH2561 = "-"
            WL2561 = '-'
            WIOPS2561 = '-'
        try:
            HS1 = perfDb.results.find({'Build':build,'Name': 'Hsbench','Operation':'read','Object_Size':'256Mb','Buckets':1,'Objects':1000,'Sessions':100}) 
            RTH2561 = roundoff(HS1[0]['Throughput'])
            RL2561 = roundoff(HS1[0]['Latency'])
            RIOPS2561 = roundoff(HS1[0]['IOPS'])   
        except:
            RTH2561 = "-"
            RL2561 = '-'
            RIOPS2561 = '-'
        return [WTH41,WTH1001,WTH11,WTH51,WTH361,WTH641,WTH1281,WTH2561,RTH41,RTH1001,RTH11,RTH51,RTH361,RTH641,RTH1281,RTH2561,\
            WL41,WL1001,WL11,WL51,WL361,WL641,WL1281,WL2561,RL41,RL1001,RL11,RL51,RL361,RL641,RL1281,RL2561,WIOPS41,WIOPS1001,WIOPS11,\
                WIOPS51,WIOPS361,WIOPS641,WIOPS1281,WIOPS2561,RIOPS41,RIOPS1001,RIOPS11,RIOPS51,RIOPS361,RIOPS641,RIOPS1281,RIOPS2561]
    
    return [None] * 48
#### ----------------------------------------------------------------------------------------------
# Eng report page - Table 9 :Hsbench 2
@app.callback([Output('e4HS2WTH','children'),Output('e100HS2WTH','children'),Output('e1HS2WTH','children'),Output('e5HS2WTH','children'),Output('e36HS2WTH','children'),Output('e64HS2WTH','children'),Output('e128HS2WTH','children'),Output('e256HS2WTH','children'),
    Output('e4HS2RTH','children'),Output('e100HS2RTH','children'),Output('e1HS2RTH','children'),Output('e5HS2RTH','children'),Output('e36HS2RTH','children'),Output('e64HS2RTH','children'),Output('e128HS2RTH','children'),Output('e256HS2RTH','children'),
    Output('e4HS2WL','children'),Output('e100HS2WL','children'),Output('e1HS2WL','children'),Output('e5HS2WL','children'),Output('e36HS2WL','children'),Output('e64HS2WL','children'),Output('e128HS2WL','children'),Output('e256HS2WL','children'),
    Output('e4HS2RL','children'),Output('e100HS2RL','children'),Output('e1HS2RL','children'),Output('e5HS2RL','children'),Output('e36HS2RL','children'),Output('e64HS2RL','children'),Output('e128HS2RL','children'),Output('e256HS2RL','children'),
    Output('e4HS2WIOPS','children'),Output('e100HS2WIOPS','children'),Output('e1HS2WIOPS','children'),Output('e5HS2WIOPS','children'),Output('e36HS2WIOPS','children'),Output('e64HS2WIOPS','children'),Output('e128HS2WIOPS','children'),Output('e256HS2WIOPS','children'),
    Output('e4HS2RIOPS','children'),Output('e100HS2RIOPS','children'),Output('e1HS2RIOPS','children'),Output('e5HS2RIOPS','children'),Output('e36HS2RIOPS','children'),Output('e64HS2RIOPS','children'),Output('e128HS2RIOPS','children'),Output('e256HS2RIOPS','children'),
    ],
    [Input('table_submit_button', 'n_clicks'),
    dash.dependencies.Input('url', 'pathname'),
    Input('table_build_input', 'value')],
    [State('table_build_input', 'value')],
)
def update_hsbench2(clicks, pathname, input_value, enter_input):
    build, _, _ = get_input('perf',dash.callback_context, clicks, input_value, enter_input, pathname)
    if build:

        try:
            HS2 = perfDb.results.find({'Build':build,'Name': 'Hsbench','Operation':'write','Object_Size':'4Kb','Buckets':10,'Objects':1000,'Sessions':100}) 
            WTH41 = roundoff(HS2[0]['Throughput'])
            WL41 = roundoff(HS2[0]['Latency'])
            WIOPS41 = roundoff(HS2[0]['IOPS'])
        except:
            WTH41 = "-"
            WL41 = '-'
            WIOPS41 = '-'
        try:
            HS2 = perfDb.results.find({'Build':build,'Name': 'Hsbench','Operation':'read','Object_Size':'4Kb','Buckets':10,'Objects':1000,'Sessions':100}) 
            RTH41 = roundoff(HS2[0]['Throughput'])
            RL41 = roundoff(HS2[0]['Latency'])
            RIOPS41 = roundoff(HS2[0]['IOPS'])  
        except:
            RTH41 = "-"
            RL41 = '-'
            RIOPS41 = '-'
        try:
            HS2 = perfDb.results.find({'Build':build,'Name': 'Hsbench','Operation':'write','Object_Size':'100Kb','Buckets':10,'Objects':1000,'Sessions':100}) 
            WTH1001 = roundoff(HS2[0]['Throughput'])
            WL1001 = roundoff(HS2[0]['Latency'])
            WIOPS1001 = roundoff(HS2[0]['IOPS']) 
        except:
            WTH1001 = "-"
            WL1001 = '-'
            WIOPS1001 = '-'
        try:
            HS2 = perfDb.results.find({'Build':build,'Name': 'Hsbench','Operation':'read','Object_Size':'100Kb','Buckets':10,'Objects':1000,'Sessions':100}) 
            RTH1001 = roundoff(HS2[0]['Throughput'])
            RL1001 = roundoff(HS2[0]['Latency'])
            RIOPS1001 = roundoff(HS2[0]['IOPS'])  
        except:
            RTH1001 = "-"
            RL1001 = '-'
            RIOPS1001 = '-'
        try:
            HS2 = perfDb.results.find({'Build':build,'Name': 'Hsbench','Operation':'write','Object_Size':'1Mb','Buckets':10,'Objects':1000,'Sessions':100}) 
            WTH11 = roundoff(HS2[0]['Throughput'])
            WL11 = roundoff(HS2[0]['Latency'])
            WIOPS11 = roundoff(HS2[0]['IOPS'])  
        except:
            WTH11 = "-"
            WL11 = '-'
            WIOPS11 = '-'
        try:
            HS2 = perfDb.results.find({'Build':build,'Name': 'Hsbench','Operation':'read','Object_Size':'1Mb','Buckets':10,'Objects':1000,'Sessions':100}) 
            RTH11 = roundoff(HS2[0]['Throughput'])
            RL11 = roundoff(HS2[0]['Latency'])
            RIOPS11 = roundoff(HS2[0]['IOPS'])   
        except:
            RTH11 = "-"
            RL11 = '-'
            RIOPS11 = '-'
        try:
            HS2 = perfDb.results.find({'Build':build,'Name': 'Hsbench','Operation':'write','Object_Size':'5Mb','Buckets':10,'Objects':1000,'Sessions':100}) 
            WTH51 = roundoff(HS2[0]['Throughput'])
            WL51 = roundoff(HS2[0]['Latency'])
            WIOPS51 =roundoff(HS2[0]['IOPS'])   
        except:
            WTH51 = "-"
            WL51 = '-'
            WIOPS51 = '-'
        try:
            HS2 = perfDb.results.find({'Build':build,'Name': 'Hsbench','Operation':'read','Object_Size':'5Mb','Buckets':10,'Objects':1000,'Sessions':100}) 
            RTH51 = roundoff(HS2[0]['Throughput'])
            RL51 = roundoff(HS2[0]['Latency'])
            RIOPS51 =roundoff( HS2[0]['IOPS'])   
        except:
            RTH51 = "-"
            RL51 = '-'
            RIOPS51 = '-'
        try:
            HS2 = perfDb.results.find({'Build':build,'Name': 'Hsbench','Operation':'write','Object_Size':'36Mb','Buckets':10,'Objects':1000,'Sessions':100}) 
            WTH361 =roundoff( HS2[0]['Throughput'])
            WL361 = roundoff(HS2[0]['Latency'])
            WIOPS361 = roundoff(HS2[0]['IOPS']) 
        except:
            WTH361 = "-"
            WL361 = '-'
            WIOPS361 = '-'
        try:
            HS2 = perfDb.results.find({'Build':build,'Name': 'Hsbench','Operation':'read','Object_Size':'36Mb','Buckets':10,'Objects':1000,'Sessions':100}) 
            RTH361 = roundoff(HS2[0]['Throughput'])
            RL361 =roundoff( HS2[0]['Latency'])
            RIOPS361 = roundoff(HS2[0]['IOPS'])   
        except:
            RTH361 = "-"
            RL361 = '-'
            RIOPS361 = '-'
        try:
            HS2 = perfDb.results.find({'Build':build,'Name': 'Hsbench','Operation':'write','Object_Size':'64Mb','Buckets':10,'Objects':1000,'Sessions':100}) 
            WTH641 = roundoff(HS2[0]['Throughput'])
            WL641 = roundoff(HS2[0]['Latency'])
            WIOPS641 = roundoff(HS2[0]['IOPS'])   
        except:
            WTH641 = "-"
            WL641 = '-'
            WIOPS641 = '-'
        try:
            HS2 = perfDb.results.find({'Build':build,'Name': 'Hsbench','Operation':'read','Object_Size':'64Mb','Buckets':10,'Objects':1000,'Sessions':100}) 
            RTH641 = roundoff(HS2[0]['Throughput'])
            RL641 = roundoff(HS2[0]['Latency'])
            RIOPS641 = roundoff(HS2[0]['IOPS'])   
        except:
            RTH641 = "-"
            RL641 = '-'
            RIOPS641 = '-'
        try:
            HS2 = perfDb.results.find({'Build':build,'Name': 'Hsbench','Operation':'write','Object_Size':'128Mb','Buckets':10,'Objects':1000,'Sessions':100}) 
            WTH1281 = roundoff(HS2[0]['Throughput'])
            WL1281 = roundoff(HS2[0]['Latency'])
            WIOPS1281 = roundoff(HS2[0]['IOPS'])   
        except:
            WTH1281 = "-"
            WL1281 = '-'
            WIOPS1281 = '-'
        try:
            HS2 = perfDb.results.find({'Build':build,'Name': 'Hsbench','Operation':'read','Object_Size':'128Mb','Buckets':10,'Objects':1000,'Sessions':100}) 
            RTH1281 = roundoff(HS2[0]['Throughput'])
            RL1281 = roundoff(HS2[0]['Latency'])
            RIOPS1281 = roundoff(HS2[0]['IOPS'])   
        except:
            RTH1281 = "-"
            RL1281 = '-'
            RIOPS1281 = '-'
        try:
            HS2 = perfDb.results.find({'Build':build,'Name': 'Hsbench','Operation':'write','Object_Size':'256Mb','Buckets':10,'Objects':1000,'Sessions':100}) 
            WTH2561 = roundoff(HS2[0]['Throughput'])
            WL2561 = roundoff(HS2[0]['Latency'])
            WIOPS2561 = roundoff(HS2[0]['IOPS'])   
        except:
            WTH2561 = "-"
            WL2561 = '-'
            WIOPS2561 = '-'
        try:
            HS2 = perfDb.results.find({'Build':build,'Name': 'Hsbench','Operation':'read','Object_Size':'256Mb','Buckets':10,'Objects':1000,'Sessions':100}) 
            RTH2561 = roundoff(HS2[0]['Throughput'])
            RL2561 = roundoff(HS2[0]['Latency'])
            RIOPS2561 = roundoff(HS2[0]['IOPS'])   
        except:
            RTH2561 = "-"
            RL2561 = '-'
            RIOPS2561 = '-'
        return [WTH41,WTH1001,WTH11,WTH51,WTH361,WTH641,WTH1281,WTH2561,RTH41,RTH1001,RTH11,RTH51,RTH361,RTH641,RTH1281,RTH2561,\
            WL41,WL1001,WL11,WL51,WL361,WL641,WL1281,WL2561,RL41,RL1001,RL11,RL51,RL361,RL641,RL1281,RL2561,WIOPS41,WIOPS1001,WIOPS11,\
                WIOPS51,WIOPS361,WIOPS641,WIOPS1281,WIOPS2561,RIOPS41,RIOPS1001,RIOPS11,RIOPS51,RIOPS361,RIOPS641,RIOPS1281,RIOPS2561]
    
    return [None] * 48
#### ----------------------------------------------------------------------------------------------
# Eng report page - Table 10 :Hsbench 3
@app.callback([Output('e4HS3WTH','children'),Output('e100HS3WTH','children'),Output('e1HS3WTH','children'),Output('e5HS3WTH','children'),Output('e36HS3WTH','children'),Output('e64HS3WTH','children'),Output('e128HS3WTH','children'),Output('e256HS3WTH','children'),
    Output('e4HS3RTH','children'),Output('e100HS3RTH','children'),Output('e1HS3RTH','children'),Output('e5HS3RTH','children'),Output('e36HS3RTH','children'),Output('e64HS3RTH','children'),Output('e128HS3RTH','children'),Output('e256HS3RTH','children'),
    Output('e4HS3WL','children'),Output('e100HS3WL','children'),Output('e1HS3WL','children'),Output('e5HS3WL','children'),Output('e36HS3WL','children'),Output('e64HS3WL','children'),Output('e128HS3WL','children'),Output('e256HS3WL','children'),
    Output('e4HS3RL','children'),Output('e100HS3RL','children'),Output('e1HS3RL','children'),Output('e5HS3RL','children'),Output('e36HS3RL','children'),Output('e64HS3RL','children'),Output('e128HS3RL','children'),Output('e256HS3RL','children'),
    Output('e4HS3WIOPS','children'),Output('e100HS3WIOPS','children'),Output('e1HS3WIOPS','children'),Output('e5HS3WIOPS','children'),Output('e36HS3WIOPS','children'),Output('e64HS3WIOPS','children'),Output('e128HS3WIOPS','children'),Output('e256HS3WIOPS','children'),
    Output('e4HS3RIOPS','children'),Output('e100HS3RIOPS','children'),Output('e1HS3RIOPS','children'),Output('e5HS3RIOPS','children'),Output('e36HS3RIOPS','children'),Output('e64HS3RIOPS','children'),Output('e128HS3RIOPS','children'),Output('e256HS3RIOPS','children'),
    ],
    [Input('table_submit_button', 'n_clicks'),
    dash.dependencies.Input('url', 'pathname'),
    Input('table_build_input', 'value')],
    [State('table_build_input', 'value')],
)
def update_hsbench3(clicks, pathname, input_value, enter_input):
    build, _, _ = get_input('perf',dash.callback_context, clicks, input_value, enter_input, pathname)
    if build:
        try:
            HS3 = perfDb.results.find({'Build':build,'Name': 'Hsbench','Operation':'write','Object_Size':'4Kb','Buckets':50,'Objects':5000,'Sessions':100}) 
            WTH41 = roundoff(HS3[0]['Throughput'])
            WL41 = roundoff(HS3[0]['Latency'])
            WIOPS41 = roundoff(HS3[0]['IOPS'])
        except:
            WTH41 = "-"
            WL41 = '-'
            WIOPS41 = '-'
        try:
            HS3 = perfDb.results.find({'Build':build,'Name': 'Hsbench','Operation':'read','Object_Size':'4Kb','Buckets':50,'Objects':5000,'Sessions':100}) 
            RTH41 = roundoff(HS3[0]['Throughput'])
            RL41 = roundoff(HS3[0]['Latency'])
            RIOPS41 = roundoff(HS3[0]['IOPS'])  
        except:
            RTH41 = "-"
            RL41 = '-'
            RIOPS41 = '-'
        try:
            HS3 = perfDb.results.find({'Build':build,'Name': 'Hsbench','Operation':'write','Object_Size':'100Kb','Buckets':50,'Objects':5000,'Sessions':100}) 
            WTH1001 = roundoff(HS3[0]['Throughput'])
            WL1001 = roundoff(HS3[0]['Latency'])
            WIOPS1001 = roundoff(HS3[0]['IOPS']) 
        except:
            WTH1001 = "-"
            WL1001 = '-'
            WIOPS1001 = '-'
        try:
            HS3 = perfDb.results.find({'Build':build,'Name': 'Hsbench','Operation':'read','Object_Size':'100Kb','Buckets':50,'Objects':5000,'Sessions':100}) 
            RTH1001 = roundoff(HS3[0]['Throughput'])
            RL1001 = roundoff(HS3[0]['Latency'])
            RIOPS1001 = roundoff(HS3[0]['IOPS'])  
        except:
            RTH1001 = "-"
            RL1001 = '-'
            RIOPS1001 = '-'
        try:
            HS3 = perfDb.results.find({'Build':build,'Name': 'Hsbench','Operation':'write','Object_Size':'1Mb','Buckets':50,'Objects':5000,'Sessions':100}) 
            WTH11 = roundoff(HS3[0]['Throughput'])
            WL11 = roundoff(HS3[0]['Latency'])
            WIOPS11 = roundoff(HS3[0]['IOPS'])  
        except:
            WTH11 = "-"
            WL11 = '-'
            WIOPS11 = '-'
        try:
            HS3 = perfDb.results.find({'Build':build,'Name': 'Hsbench','Operation':'read','Object_Size':'1Mb','Buckets':50,'Objects':5000,'Sessions':100}) 
            RTH11 = roundoff(HS3[0]['Throughput'])
            RL11 = roundoff(HS3[0]['Latency'])
            RIOPS11 = roundoff(HS3[0]['IOPS'])   
        except:
            RTH11 = "-"
            RL11 = '-'
            RIOPS11 = '-'
        try:
            HS3 = perfDb.results.find({'Build':build,'Name': 'Hsbench','Operation':'write','Object_Size':'5Mb','Buckets':50,'Objects':5000,'Sessions':100}) 
            WTH51 = roundoff(HS3[0]['Throughput'])
            WL51 = roundoff(HS3[0]['Latency'])
            WIOPS51 =roundoff(HS3[0]['IOPS'])   
        except:
            WTH51 = "-"
            WL51 = '-'
            WIOPS51 = '-'
        try:
            HS3 = perfDb.results.find({'Build':build,'Name': 'Hsbench','Operation':'read','Object_Size':'5Mb','Buckets':50,'Objects':5000,'Sessions':100}) 
            RTH51 = roundoff(HS3[0]['Throughput'])
            RL51 = roundoff(HS3[0]['Latency'])
            RIOPS51 =roundoff( HS3[0]['IOPS'])   
        except:
            RTH51 = "-"
            RL51 = '-'
            RIOPS51 = '-'
        try:
            HS3 = perfDb.results.find({'Build':build,'Name': 'Hsbench','Operation':'write','Object_Size':'36Mb','Buckets':50,'Objects':5000,'Sessions':100}) 
            WTH361 =roundoff( HS3[0]['Throughput'])
            WL361 = roundoff(HS3[0]['Latency'])
            WIOPS361 = roundoff(HS3[0]['IOPS']) 
        except:
            WTH361 = "-"
            WL361 = '-'
            WIOPS361 = '-'
        try:
            HS3 = perfDb.results.find({'Build':build,'Name': 'Hsbench','Operation':'read','Object_Size':'36Mb','Buckets':50,'Objects':5000,'Sessions':100}) 
            RTH361 = roundoff(HS3[0]['Throughput'])
            RL361 =roundoff( HS3[0]['Latency'])
            RIOPS361 = roundoff(HS3[0]['IOPS'])   
        except:
            RTH361 = "-"
            RL361 = '-'
            RIOPS361 = '-'
        try:
            HS3 = perfDb.results.find({'Build':build,'Name': 'Hsbench','Operation':'write','Object_Size':'64Mb','Buckets':50,'Objects':5000,'Sessions':100}) 
            WTH641 = roundoff(HS3[0]['Throughput'])
            WL641 = roundoff(HS3[0]['Latency'])
            WIOPS641 = roundoff(HS3[0]['IOPS'])   
        except:
            WTH641 = "-"
            WL641 = '-'
            WIOPS641 = '-'
        try:
            HS3 = perfDb.results.find({'Build':build,'Name': 'Hsbench','Operation':'read','Object_Size':'64Mb','Buckets':50,'Objects':5000,'Sessions':100}) 
            RTH641 = roundoff(HS3[0]['Throughput'])
            RL641 = roundoff(HS3[0]['Latency'])
            RIOPS641 = roundoff(HS3[0]['IOPS'])   
        except:
            RTH641 = "-"
            RL641 = '-'
            RIOPS641 = '-'
        try:
            HS3 = perfDb.results.find({'Build':build,'Name': 'Hsbench','Operation':'write','Object_Size':'128Mb','Buckets':50,'Objects':5000,'Sessions':100}) 
            WTH1281 = roundoff(HS3[0]['Throughput'])
            WL1281 = roundoff(HS3[0]['Latency'])
            WIOPS1281 = roundoff(HS3[0]['IOPS'])   
        except:
            WTH1281 = "-"
            WL1281 = '-'
            WIOPS1281 = '-'
        try:
            HS3 = perfDb.results.find({'Build':build,'Name': 'Hsbench','Operation':'read','Object_Size':'128Mb','Buckets':50,'Objects':5000,'Sessions':100}) 
            RTH1281 = roundoff(HS3[0]['Throughput'])
            RL1281 = roundoff(HS3[0]['Latency'])
            RIOPS1281 = roundoff(HS3[0]['IOPS'])   
        except:
            RTH1281 = "-"
            RL1281 = '-'
            RIOPS1281 = '-'
        try:
            HS3 = perfDb.results.find({'Build':build,'Name': 'Hsbench','Operation':'write','Object_Size':'256Mb','Buckets':50,'Objects':5000,'Sessions':100}) 
            WTH2561 = roundoff(HS3[0]['Throughput'])
            WL2561 = roundoff(HS3[0]['Latency'])
            WIOPS2561 = roundoff(HS3[0]['IOPS'])   
        except:
            WTH2561 = "-"
            WL2561 = '-'
            WIOPS2561 = '-'
        try:
            HS3 = perfDb.results.find({'Build':build,'Name': 'Hsbench','Operation':'read','Object_Size':'256Mb','Buckets':50,'Objects':5000,'Sessions':100}) 
            RTH2561 = roundoff(HS3[0]['Throughput'])
            RL2561 = roundoff(HS3[0]['Latency'])
            RIOPS2561 = roundoff(HS3[0]['IOPS'])   
        except:
            RTH2561 = "-"
            RL2561 = '-'
            RIOPS2561 = '-'
        return [WTH41,WTH1001,WTH11,WTH51,WTH361,WTH641,WTH1281,WTH2561,RTH41,RTH1001,RTH11,RTH51,RTH361,RTH641,RTH1281,RTH2561,\
            WL41,WL1001,WL11,WL51,WL361,WL641,WL1281,WL2561,RL41,RL1001,RL11,RL51,RL361,RL641,RL1281,RL2561,WIOPS41,WIOPS1001,WIOPS11,\
                WIOPS51,WIOPS361,WIOPS641,WIOPS1281,WIOPS2561,RIOPS41,RIOPS1001,RIOPS11,RIOPS51,RIOPS361,RIOPS641,RIOPS1281,RIOPS2561]
    
    return [None] * 48
#### ----------------------------------------------------------------------------------------------
# Eng report page - Table 11 :Cosbench 1
@app.callback([Output('e4COS1WTH','children'),Output('e100COS1WTH','children'),Output('e1COS1WTH','children'),Output('e5COS1WTH','children'),Output('e36COS1WTH','children'),Output('e64COS1WTH','children'),Output('e128COS1WTH','children'),Output('e256COS1WTH','children'),
    Output('e4COS1RTH','children'),Output('e100COS1RTH','children'),Output('e1COS1RTH','children'),Output('e5COS1RTH','children'),Output('e36COS1RTH','children'),Output('e64COS1RTH','children'),Output('e128COS1RTH','children'),Output('e256COS1RTH','children'),
    Output('e4COS1WL','children'),Output('e100COS1WL','children'),Output('e1COS1WL','children'),Output('e5COS1WL','children'),Output('e36COS1WL','children'),Output('e64COS1WL','children'),Output('e128COS1WL','children'),Output('e256COS1WL','children'),
    Output('e4COS1RL','children'),Output('e100COS1RL','children'),Output('e1COS1RL','children'),Output('e5COS1RL','children'),Output('e36COS1RL','children'),Output('e64COS1RL','children'),Output('e128COS1RL','children'),Output('e256COS1RL','children'),
    Output('e4COS1WIOPS','children'),Output('e100COS1WIOPS','children'),Output('e1COS1WIOPS','children'),Output('e5COS1WIOPS','children'),Output('e36COS1WIOPS','children'),Output('e64COS1WIOPS','children'),Output('e128COS1WIOPS','children'),Output('e256COS1WIOPS','children'),
    Output('e4COS1RIOPS','children'),Output('e100COS1RIOPS','children'),Output('e1COS1RIOPS','children'),Output('e5COS1RIOPS','children'),Output('e36COS1RIOPS','children'),Output('e64COS1RIOPS','children'),Output('e128COS1RIOPS','children'),Output('e256COS1RIOPS','children'),
    ],
    [Input('table_submit_button', 'n_clicks'),
    dash.dependencies.Input('url', 'pathname'),
    Input('table_build_input', 'value')],
    [State('table_build_input', 'value')],
)
def update_cosbench1(clicks, pathname, input_value, enter_input):
    build, _, _ = get_input('perf',dash.callback_context, clicks, input_value, enter_input, pathname)
    if build:
        try:
            COS1 = perfDb.results.find({'Build':build,'Name': 'Cosbench','Operation':'write','Object_Size':'4 KB','Buckets':1,'Objects':1000,'Sessions':100}) 
            WTH41 = roundoff(COS1[0]['Throughput'])
            WL41 = roundoff(COS1[0]['Latency']['Avg'])
            WIOPS41 = roundoff(COS1[0]['IOPS'])
        except:
            WTH41 = "-"
            WL41 = '-'
            WIOPS41 = '-'
        try:
            COS1 = perfDb.results.find({'Build':build,'Name': 'Cosbench','Operation':'read','Object_Size':'4 KB','Buckets':1,'Objects':1000,'Sessions':100}) 
            RTH41 = roundoff(COS1[0]['Throughput'])
            RL41 = roundoff(COS1[0]['Latency']['Avg'])
            RIOPS41 = roundoff(COS1[0]['IOPS'])  
        except:
            RTH41 = "-"
            RL41 = '-'
            RIOPS41 = '-'
        try:
            COS1 = perfDb.results.find({'Build':build,'Name': 'Cosbench','Operation':'write','Object_Size':'100 KB','Buckets':1,'Objects':1000,'Sessions':100}) 
            WTH1001 = roundoff(COS1[0]['Throughput'])
            WL1001 = roundoff(COS1[0]['Latency']['Avg'])
            WIOPS1001 = roundoff(COS1[0]['IOPS']) 
        except:
            WTH1001 = "-"
            WL1001 = '-'
            WIOPS1001 = '-'
        try:
            COS1 = perfDb.results.find({'Build':build,'Name': 'Cosbench','Operation':'read','Object_Size':'100 KB','Buckets':1,'Objects':1000,'Sessions':100}) 
            RTH1001 = roundoff(COS1[0]['Throughput'])
            RL1001 = roundoff(COS1[0]['Latency']['Avg'])
            RIOPS1001 = roundoff(COS1[0]['IOPS'])  
        except:
            RTH1001 = "-"
            RL1001 = '-'
            RIOPS1001 = '-'
        try:
            COS1 = perfDb.results.find({'Build':build,'Name': 'Cosbench','Operation':'write','Object_Size':'1 MB','Buckets':1,'Objects':1000,'Sessions':100}) 
            WTH11 = roundoff(COS1[0]['Throughput'])
            WL11 = roundoff(COS1[0]['Latency']['Avg'])
            WIOPS11 = roundoff(COS1[0]['IOPS'])  
        except:
            WTH11 = "-"
            WL11 = '-'
            WIOPS11 = '-'
        try:
            COS1 = perfDb.results.find({'Build':build,'Name': 'Cosbench','Operation':'read','Object_Size':'1 MB','Buckets':1,'Objects':1000,'Sessions':100}) 
            RTH11 = roundoff(COS1[0]['Throughput'])
            RL11 = roundoff(COS1[0]['Latency']['Avg'])
            RIOPS11 = roundoff(COS1[0]['IOPS'])   
        except:
            RTH11 = "-"
            RL11 = '-'
            RIOPS11 = '-'
        try:
            COS1 = perfDb.results.find({'Build':build,'Name': 'Cosbench','Operation':'write','Object_Size':'5 MB','Buckets':1,'Objects':1000,'Sessions':100}) 
            WTH51 = roundoff(COS1[0]['Throughput'])
            WL51 = roundoff(COS1[0]['Latency']['Avg'])
            WIOPS51 =roundoff(COS1[0]['IOPS'])   
        except:
            WTH51 = "-"
            WL51 = '-'
            WIOPS51 = '-'
        try:
            COS1 = perfDb.results.find({'Build':build,'Name': 'Cosbench','Operation':'read','Object_Size':'5 MB','Buckets':1,'Objects':1000,'Sessions':100}) 
            RTH51 = roundoff(COS1[0]['Throughput'])
            RL51 = roundoff(COS1[0]['Latency']['Avg'])
            RIOPS51 =roundoff( COS1[0]['IOPS'])   
        except:
            RTH51 = "-"
            RL51 = '-'
            RIOPS51 = '-'
        try:
            COS1 = perfDb.results.find({'Build':build,'Name': 'Cosbench','Operation':'write','Object_Size':'36 MB','Buckets':1,'Objects':1000,'Sessions':100}) 
            WTH361 =roundoff( COS1[0]['Throughput'])
            WL361 = roundoff(COS1[0]['Latency']['Avg'])
            WIOPS361 = roundoff(COS1[0]['IOPS']) 
        except:
            WTH361 = "-"
            WL361 = '-'
            WIOPS361 = '-'
        try:
            COS1 = perfDb.results.find({'Build':build,'Name': 'Cosbench','Operation':'read','Object_Size':'36 MB','Buckets':1,'Objects':1000,'Sessions':100}) 
            RTH361 = roundoff(COS1[0]['Throughput'])
            RL361 =roundoff( COS1[0]['Latency']['Avg'])
            RIOPS361 = roundoff(COS1[0]['IOPS'])   
        except:
            RTH361 = "-"
            RL361 = '-'
            RIOPS361 = '-'
        try:
            COS1 = perfDb.results.find({'Build':build,'Name': 'Cosbench','Operation':'write','Object_Size':'64 MB','Buckets':1,'Objects':1000,'Sessions':100}) 
            WTH641 = roundoff(COS1[0]['Throughput'])
            WL641 = roundoff(COS1[0]['Latency']['Avg'])
            WIOPS641 = roundoff(COS1[0]['IOPS'])   
        except:
            WTH641 = "-"
            WL641 = '-'
            WIOPS641 = '-'
        try:
            COS1 = perfDb.results.find({'Build':build,'Name': 'Cosbench','Operation':'read','Object_Size':'64 MB','Buckets':1,'Objects':1000,'Sessions':100}) 
            RTH641 = roundoff(COS1[0]['Throughput'])
            RL641 = roundoff(COS1[0]['Latency']['Avg'])
            RIOPS641 = roundoff(COS1[0]['IOPS'])   
        except:
            RTH641 = "-"
            RL641 = '-'
            RIOPS641 = '-'
        try:
            COS1 = perfDb.results.find({'Build':build,'Name': 'Cosbench','Operation':'write','Object_Size':'128 MB','Buckets':1,'Objects':1000,'Sessions':100}) 
            WTH1281 = roundoff(COS1[0]['Throughput'])
            WL1281 = roundoff(COS1[0]['Latency']['Avg'])
            WIOPS1281 = roundoff(COS1[0]['IOPS'])   
        except:
            WTH1281 = "-"
            WL1281 = '-'
            WIOPS1281 = '-'
        try:
            COS1 = perfDb.results.find({'Build':build,'Name': 'Cosbench','Operation':'read','Object_Size':'128 MB','Buckets':1,'Objects':1000,'Sessions':100}) 
            RTH1281 = roundoff(COS1[0]['Throughput'])
            RL1281 = roundoff(COS1[0]['Latency']['Avg'])
            RIOPS1281 = roundoff(COS1[0]['IOPS'])   
        except:
            RTH1281 = "-"
            RL1281 = '-'
            RIOPS1281 = '-'
        try:
            COS1 = perfDb.results.find({'Build':build,'Name': 'Cosbench','Operation':'write','Object_Size':'256 MB','Buckets':1,'Objects':1000,'Sessions':100}) 
            WTH2561 = roundoff(COS1[0]['Throughput'])
            WL2561 = roundoff(COS1[0]['Latency']['Avg'])
            WIOPS2561 = roundoff(COS1[0]['IOPS'])   
        except:
            WTH2561 = "-"
            WL2561 = '-'
            WIOPS2561 = '-'
        try:
            COS1 = perfDb.results.find({'Build':build,'Name': 'Cosbench','Operation':'read','Object_Size':'256 MB','Buckets':1,'Objects':1000,'Sessions':100}) 
            RTH2561 = roundoff(COS1[0]['Throughput'])
            RL2561 = roundoff(COS1[0]['Latency']['Avg'])
            RIOPS2561 = roundoff(COS1[0]['IOPS'])   
        except:
            RTH2561 = "-"
            RL2561 = '-'
            RIOPS2561 = '-'
        return [WTH41,WTH1001,WTH11,WTH51,WTH361,WTH641,WTH1281,WTH2561,RTH41,RTH1001,RTH11,RTH51,RTH361,RTH641,RTH1281,RTH2561,\
            WL41,WL1001,WL11,WL51,WL361,WL641,WL1281,WL2561,RL41,RL1001,RL11,RL51,RL361,RL641,RL1281,RL2561,WIOPS41,WIOPS1001,WIOPS11,\
                WIOPS51,WIOPS361,WIOPS641,WIOPS1281,WIOPS2561,RIOPS41,RIOPS1001,RIOPS11,RIOPS51,RIOPS361,RIOPS641,RIOPS1281,RIOPS2561]
    
    return [None] * 48
#### ----------------------------------------------------------------------------------------------
# Eng report page - Table 12 :Cosbench 2
@app.callback([Output('e4COS2WTH','children'),Output('e100COS2WTH','children'),Output('e1COS2WTH','children'),Output('e5COS2WTH','children'),Output('e36COS2WTH','children'),Output('e64COS2WTH','children'),Output('e128COS2WTH','children'),Output('e256COS2WTH','children'),
    Output('e4COS2RTH','children'),Output('e100COS2RTH','children'),Output('e1COS2RTH','children'),Output('e5COS2RTH','children'),Output('e36COS2RTH','children'),Output('e64COS2RTH','children'),Output('e128COS2RTH','children'),Output('e256COS2RTH','children'),
    Output('e4COS2WL','children'),Output('e100COS2WL','children'),Output('e1COS2WL','children'),Output('e5COS2WL','children'),Output('e36COS2WL','children'),Output('e64COS2WL','children'),Output('e128COS2WL','children'),Output('e256COS2WL','children'),
    Output('e4COS2RL','children'),Output('e100COS2RL','children'),Output('e1COS2RL','children'),Output('e5COS2RL','children'),Output('e36COS2RL','children'),Output('e64COS2RL','children'),Output('e128COS2RL','children'),Output('e256COS2RL','children'),
    Output('e4COS2WIOPS','children'),Output('e100COS2WIOPS','children'),Output('e1COS2WIOPS','children'),Output('e5COS2WIOPS','children'),Output('e36COS2WIOPS','children'),Output('e64COS2WIOPS','children'),Output('e128COS2WIOPS','children'),Output('e256COS2WIOPS','children'),
    Output('e4COS2RIOPS','children'),Output('e100COS2RIOPS','children'),Output('e1COS2RIOPS','children'),Output('e5COS2RIOPS','children'),Output('e36COS2RIOPS','children'),Output('e64COS2RIOPS','children'),Output('e128COS2RIOPS','children'),Output('e256COS2RIOPS','children'),
    ],
    [Input('table_submit_button', 'n_clicks'),
    dash.dependencies.Input('url', 'pathname'),
    Input('table_build_input', 'value')],
    [State('table_build_input', 'value')],
)
def update_cosbench2(clicks, pathname, input_value, enter_input):
    build, _, _ = get_input('perf',dash.callback_context, clicks, input_value, enter_input, pathname)
    if build:

        try:
            COS2 = perfDb.results.find({'Build':build,'Name': 'Cosbench','Operation':'write','Object_Size':'4 KB','Buckets':10,'Objects':100,'Sessions':100}) 
            WTH41 = roundoff(COS2[0]['Throughput'])
            WL41 = roundoff(COS2[0]['Latency']['Avg'])
            WIOPS41 = roundoff(COS2[0]['IOPS'])
        except:
            WTH41 = "-"
            WL41 = '-'
            WIOPS41 = '-'
        try:
            COS2 = perfDb.results.find({'Build':build,'Name': 'Cosbench','Operation':'read','Object_Size':'4 KB','Buckets':10,'Objects':100,'Sessions':100}) 
            RTH41 = roundoff(COS2[0]['Throughput'])
            RL41 = roundoff(COS2[0]['Latency']['Avg'])
            RIOPS41 = roundoff(COS2[0]['IOPS'])  
        except:
            RTH41 = "-"
            RL41 = '-'
            RIOPS41 = '-'
        try:
            COS2 = perfDb.results.find({'Build':build,'Name': 'Cosbench','Operation':'write','Object_Size':'100 KB','Buckets':10,'Objects':100,'Sessions':100}) 
            WTH1001 = roundoff(COS2[0]['Throughput'])
            WL1001 = roundoff(COS2[0]['Latency']['Avg'])
            WIOPS1001 = roundoff(COS2[0]['IOPS']) 
        except:
            WTH1001 = "-"
            WL1001 = '-'
            WIOPS1001 = '-'
        try:
            COS2 = perfDb.results.find({'Build':build,'Name': 'Cosbench','Operation':'read','Object_Size':'100 KB','Buckets':10,'Objects':100,'Sessions':100}) 
            RTH1001 = roundoff(COS2[0]['Throughput'])
            RL1001 = roundoff(COS2[0]['Latency']['Avg'])
            RIOPS1001 = roundoff(COS2[0]['IOPS'])  
        except:
            RTH1001 = "-"
            RL1001 = '-'
            RIOPS1001 = '-'
        try:
            COS2 = perfDb.results.find({'Build':build,'Name': 'Cosbench','Operation':'write','Object_Size':'1 MB','Buckets':10,'Objects':100,'Sessions':100}) 
            WTH11 = roundoff(COS2[0]['Throughput'])
            WL11 = roundoff(COS2[0]['Latency']['Avg'])
            WIOPS11 = roundoff(COS2[0]['IOPS'])  
        except:
            WTH11 = "-"
            WL11 = '-'
            WIOPS11 = '-'
        try:
            COS2 = perfDb.results.find({'Build':build,'Name': 'Cosbench','Operation':'read','Object_Size':'1 MB','Buckets':10,'Objects':100,'Sessions':100}) 
            RTH11 = roundoff(COS2[0]['Throughput'])
            RL11 = roundoff(COS2[0]['Latency']['Avg'])
            RIOPS11 = roundoff(COS2[0]['IOPS'])   
        except:
            RTH11 = "-"
            RL11 = '-'
            RIOPS11 = '-'
        try:
            COS2 = perfDb.results.find({'Build':build,'Name': 'Cosbench','Operation':'write','Object_Size':'5 MB','Buckets':10,'Objects':100,'Sessions':100}) 
            WTH51 = roundoff(COS2[0]['Throughput'])
            WL51 = roundoff(COS2[0]['Latency']['Avg'])
            WIOPS51 =roundoff(COS2[0]['IOPS'])   
        except:
            WTH51 = "-"
            WL51 = '-'
            WIOPS51 = '-'
        try:
            COS2 = perfDb.results.find({'Build':build,'Name': 'Cosbench','Operation':'read','Object_Size':'5 MB','Buckets':10,'Objects':100,'Sessions':100}) 
            RTH51 = roundoff(COS2[0]['Throughput'])
            RL51 = roundoff(COS2[0]['Latency']['Avg'])
            RIOPS51 =roundoff( COS2[0]['IOPS'])   
        except:
            RTH51 = "-"
            RL51 = '-'
            RIOPS51 = '-'
        try:
            COS2 = perfDb.results.find({'Build':build,'Name': 'Cosbench','Operation':'write','Object_Size':'36 MB','Buckets':10,'Objects':100,'Sessions':100}) 
            WTH361 =roundoff( COS2[0]['Throughput'])
            WL361 = roundoff(COS2[0]['Latency']['Avg'])
            WIOPS361 = roundoff(COS2[0]['IOPS']) 
        except:
            WTH361 = "-"
            WL361 = '-'
            WIOPS361 = '-'
        try:
            COS2 = perfDb.results.find({'Build':build,'Name': 'Cosbench','Operation':'read','Object_Size':'36 MB','Buckets':10,'Objects':100,'Sessions':100}) 
            RTH361 = roundoff(COS2[0]['Throughput'])
            RL361 =roundoff( COS2[0]['Latency']['Avg'])
            RIOPS361 = roundoff(COS2[0]['IOPS'])   
        except:
            RTH361 = "-"
            RL361 = '-'
            RIOPS361 = '-'
        try:
            COS2 = perfDb.results.find({'Build':build,'Name': 'Cosbench','Operation':'write','Object_Size':'64 MB','Buckets':10,'Objects':100,'Sessions':100}) 
            WTH641 = roundoff(COS2[0]['Throughput'])
            WL641 = roundoff(COS2[0]['Latency']['Avg'])
            WIOPS641 = roundoff(COS2[0]['IOPS'])   
        except:
            WTH641 = "-"
            WL641 = '-'
            WIOPS641 = '-'
        try:
            COS2 = perfDb.results.find({'Build':build,'Name': 'Cosbench','Operation':'read','Object_Size':'64 MB','Buckets':10,'Objects':100,'Sessions':100}) 
            RTH641 = roundoff(COS2[0]['Throughput'])
            RL641 = roundoff(COS2[0]['Latency']['Avg'])
            RIOPS641 = roundoff(COS2[0]['IOPS'])   
        except:
            RTH641 = "-"
            RL641 = '-'
            RIOPS641 = '-'
        try:
            COS2 = perfDb.results.find({'Build':build,'Name': 'Cosbench','Operation':'write','Object_Size':'128 MB','Buckets':10,'Objects':100,'Sessions':100}) 
            WTH1281 = roundoff(COS2[0]['Throughput'])
            WL1281 = roundoff(COS2[0]['Latency']['Avg'])
            WIOPS1281 = roundoff(COS2[0]['IOPS'])   
        except:
            WTH1281 = "-"
            WL1281 = '-'
            WIOPS1281 = '-'
        try:
            COS2 = perfDb.results.find({'Build':build,'Name': 'Cosbench','Operation':'read','Object_Size':'128 MB','Buckets':10,'Objects':100,'Sessions':100}) 
            RTH1281 = roundoff(COS2[0]['Throughput'])
            RL1281 = roundoff(COS2[0]['Latency']['Avg'])
            RIOPS1281 = roundoff(COS2[0]['IOPS'])   
        except:
            RTH1281 = "-"
            RL1281 = '-'
            RIOPS1281 = '-'
        try:
            COS2 = perfDb.results.find({'Build':build,'Name': 'Cosbench','Operation':'write','Object_Size':'256 MB','Buckets':10,'Objects':100,'Sessions':100}) 
            WTH2561 = roundoff(COS2[0]['Throughput'])
            WL2561 = roundoff(COS2[0]['Latency']['Avg'])
            WIOPS2561 = roundoff(COS2[0]['IOPS'])   
        except:
            WTH2561 = "-"
            WL2561 = '-'
            WIOPS2561 = '-'
        try:
            COS2 = perfDb.results.find({'Build':build,'Name': 'Cosbench','Operation':'read','Object_Size':'256 MB','Buckets':10,'Objects':100,'Sessions':100}) 
            RTH2561 = roundoff(COS2[0]['Throughput'])
            RL2561 = roundoff(COS2[0]['Latency']['Avg'])
            RIOPS2561 = roundoff(COS2[0]['IOPS'])   
        except:
            RTH2561 = "-"
            RL2561 = '-'
            RIOPS2561 = '-'
        return [WTH41,WTH1001,WTH11,WTH51,WTH361,WTH641,WTH1281,WTH2561,RTH41,RTH1001,RTH11,RTH51,RTH361,RTH641,RTH1281,RTH2561,\
            WL41,WL1001,WL11,WL51,WL361,WL641,WL1281,WL2561,RL41,RL1001,RL11,RL51,RL361,RL641,RL1281,RL2561,WIOPS41,WIOPS1001,WIOPS11,\
                WIOPS51,WIOPS361,WIOPS641,WIOPS1281,WIOPS2561,RIOPS41,RIOPS1001,RIOPS11,RIOPS51,RIOPS361,RIOPS641,RIOPS1281,RIOPS2561]
    
    return [None] * 48
#### ----------------------------------------------------------------------------------------------
# Eng report page - Table 13 :Cosbench 3
@app.callback([Output('e4COS3WTH','children'),Output('e100COS3WTH','children'),Output('e1COS3WTH','children'),Output('e5COS3WTH','children'),Output('e36COS3WTH','children'),Output('e64COS3WTH','children'),Output('e128COS3WTH','children'),Output('e256COS3WTH','children'),
    Output('e4COS3RTH','children'),Output('e100COS3RTH','children'),Output('e1COS3RTH','children'),Output('e5COS3RTH','children'),Output('e36COS3RTH','children'),Output('e64COS3RTH','children'),Output('e128COS3RTH','children'),Output('e256COS3RTH','children'),
    Output('e4COS3WL','children'),Output('e100COS3WL','children'),Output('e1COS3WL','children'),Output('e5COS3WL','children'),Output('e36COS3WL','children'),Output('e64COS3WL','children'),Output('e128COS3WL','children'),Output('e256COS3WL','children'),
    Output('e4COS3RL','children'),Output('e100COS3RL','children'),Output('e1COS3RL','children'),Output('e5COS3RL','children'),Output('e36COS3RL','children'),Output('e64COS3RL','children'),Output('e128COS3RL','children'),Output('e256COS3RL','children'),
    Output('e4COS3WIOPS','children'),Output('e100COS3WIOPS','children'),Output('e1COS3WIOPS','children'),Output('e5COS3WIOPS','children'),Output('e36COS3WIOPS','children'),Output('e64COS3WIOPS','children'),Output('e128COS3WIOPS','children'),Output('e256COS3WIOPS','children'),
    Output('e4COS3RIOPS','children'),Output('e100COS3RIOPS','children'),Output('e1COS3RIOPS','children'),Output('e5COS3RIOPS','children'),Output('e36COS3RIOPS','children'),Output('e64COS3RIOPS','children'),Output('e128COS3RIOPS','children'),Output('e256COS3RIOPS','children'),
    ],
    [Input('table_submit_button', 'n_clicks'),
    dash.dependencies.Input('url', 'pathname'),
    Input('table_build_input', 'value')],
    [State('table_build_input', 'value')],
)
def update_cosbench3(clicks, pathname, input_value, enter_input):
    build, _, _ = get_input('perf',dash.callback_context, clicks, input_value, enter_input, pathname)
    if build:
        try:
            COS3 = perfDb.results.find({'Build':build,'Name': 'Cosbench','Operation':'write','Object_Size':'4 KB','Buckets':50,'Objects':100,'Sessions':100}) 
            WTH41 = roundoff(COS3[0]['Throughput'])
            WL41 = roundoff(COS3[0]['Latency']['Avg'])
            WIOPS41 = roundoff(COS3[0]['IOPS'])
        except:
            WTH41 = "-"
            WL41 = '-'
            WIOPS41 = '-'
        try:
            COS3 = perfDb.results.find({'Build':build,'Name': 'Cosbench','Operation':'read','Object_Size':'4 KB','Buckets':50,'Objects':100,'Sessions':100}) 
            RTH41 = roundoff(COS3[0]['Throughput'])
            RL41 = roundoff(COS3[0]['Latency']['Avg'])
            RIOPS41 = roundoff(COS3[0]['IOPS'])  
        except:
            RTH41 = "-"
            RL41 = '-'
            RIOPS41 = '-'
        try:
            COS3 = perfDb.results.find({'Build':build,'Name': 'Cosbench','Operation':'write','Object_Size':'100 KB','Buckets':50,'Objects':100,'Sessions':100}) 
            WTH1001 = roundoff(COS3[0]['Throughput'])
            WL1001 = roundoff(COS3[0]['Latency']['Avg'])
            WIOPS1001 = roundoff(COS3[0]['IOPS']) 
        except:
            WTH1001 = "-"
            WL1001 = '-'
            WIOPS1001 = '-'
        try:
            COS3 = perfDb.results.find({'Build':build,'Name': 'Cosbench','Operation':'read','Object_Size':'100 KB','Buckets':50,'Objects':100,'Sessions':100}) 
            RTH1001 = roundoff(COS3[0]['Throughput'])
            RL1001 = roundoff(COS3[0]['Latency']['Avg'])
            RIOPS1001 = roundoff(COS3[0]['IOPS'])  
        except:
            RTH1001 = "-"
            RL1001 = '-'
            RIOPS1001 = '-'
        try:
            COS3 = perfDb.results.find({'Build':build,'Name': 'Cosbench','Operation':'write','Object_Size':'1 MB','Buckets':50,'Objects':100,'Sessions':100}) 
            WTH11 = roundoff(COS3[0]['Throughput'])
            WL11 = roundoff(COS3[0]['Latency']['Avg'])
            WIOPS11 = roundoff(COS3[0]['IOPS'])  
        except:
            WTH11 = "-"
            WL11 = '-'
            WIOPS11 = '-'
        try:
            COS3 = perfDb.results.find({'Build':build,'Name': 'Cosbench','Operation':'read','Object_Size':'1 MB','Buckets':50,'Objects':100,'Sessions':100}) 
            RTH11 = roundoff(COS3[0]['Throughput'])
            RL11 = roundoff(COS3[0]['Latency']['Avg'])
            RIOPS11 = roundoff(COS3[0]['IOPS'])   
        except:
            RTH11 = "-"
            RL11 = '-'
            RIOPS11 = '-'
        try:
            COS3 = perfDb.results.find({'Build':build,'Name': 'Cosbench','Operation':'write','Object_Size':'5 MB','Buckets':50,'Objects':100,'Sessions':100}) 
            WTH51 = roundoff(COS3[0]['Throughput'])
            WL51 = roundoff(COS3[0]['Latency']['Avg'])
            WIOPS51 =roundoff(COS3[0]['IOPS'])   
        except:
            WTH51 = "-"
            WL51 = '-'
            WIOPS51 = '-'
        try:
            COS3 = perfDb.results.find({'Build':build,'Name': 'Cosbench','Operation':'read','Object_Size':'5 MB','Buckets':50,'Objects':100,'Sessions':100}) 
            RTH51 = roundoff(COS3[0]['Throughput'])
            RL51 = roundoff(COS3[0]['Latency']['Avg'])
            RIOPS51 =roundoff( COS3[0]['IOPS'])   
        except:
            RTH51 = "-"
            RL51 = '-'
            RIOPS51 = '-'
        try:
            COS3 = perfDb.results.find({'Build':build,'Name': 'Cosbench','Operation':'write','Object_Size':'36 MB','Buckets':50,'Objects':100,'Sessions':100}) 
            WTH361 =roundoff( COS3[0]['Throughput'])
            WL361 = roundoff(COS3[0]['Latency']['Avg'])
            WIOPS361 = roundoff(COS3[0]['IOPS']) 
        except:
            WTH361 = "-"
            WL361 = '-'
            WIOPS361 = '-'
        try:
            COS3 = perfDb.results.find({'Build':build,'Name': 'Cosbench','Operation':'read','Object_Size':'36 MB','Buckets':50,'Objects':100,'Sessions':100}) 
            RTH361 = roundoff(COS3[0]['Throughput'])
            RL361 =roundoff( COS3[0]['Latency']['Avg'])
            RIOPS361 = roundoff(COS3[0]['IOPS'])   
        except:
            RTH361 = "-"
            RL361 = '-'
            RIOPS361 = '-'
        try:
            COS3 = perfDb.results.find({'Build':build,'Name': 'Cosbench','Operation':'write','Object_Size':'64 MB','Buckets':50,'Objects':100,'Sessions':100}) 
            WTH641 = roundoff(COS3[0]['Throughput'])
            WL641 = roundoff(COS3[0]['Latency']['Avg'])
            WIOPS641 = roundoff(COS3[0]['IOPS'])   
        except:
            WTH641 = "-"
            WL641 = '-'
            WIOPS641 = '-'
        try:
            COS3 = perfDb.results.find({'Build':build,'Name': 'Cosbench','Operation':'read','Object_Size':'64 MB','Buckets':50,'Objects':100,'Sessions':100}) 
            RTH641 = roundoff(COS3[0]['Throughput'])
            RL641 = roundoff(COS3[0]['Latency']['Avg'])
            RIOPS641 = roundoff(COS3[0]['IOPS'])   
        except:
            RTH641 = "-"
            RL641 = '-'
            RIOPS641 = '-'
        try:
            COS3 = perfDb.results.find({'Build':build,'Name': 'Cosbench','Operation':'write','Object_Size':'128 MB','Buckets':50,'Objects':100,'Sessions':100}) 
            WTH1281 = roundoff(COS3[0]['Throughput'])
            WL1281 = roundoff(COS3[0]['Latency']['Avg'])
            WIOPS1281 = roundoff(COS3[0]['IOPS'])   
        except:
            WTH1281 = "-"
            WL1281 = '-'
            WIOPS1281 = '-'
        try:
            COS3 = perfDb.results.find({'Build':build,'Name': 'Cosbench','Operation':'read','Object_Size':'128 MB','Buckets':50,'Objects':100,'Sessions':100}) 
            RTH1281 = roundoff(COS3[0]['Throughput'])
            RL1281 = roundoff(COS3[0]['Latency']['Avg'])
            RIOPS1281 = roundoff(COS3[0]['IOPS'])   
        except:
            RTH1281 = "-"
            RL1281 = '-'
            RIOPS1281 = '-'
        try:
            COS3 = perfDb.results.find({'Build':build,'Name': 'Cosbench','Operation':'write','Object_Size':'256 MB','Buckets':50,'Objects':100,'Sessions':100}) 
            WTH2561 = roundoff(COS3[0]['Throughput'])
            WL2561 = roundoff(COS3[0]['Latency']['Avg'])
            WIOPS2561 = roundoff(COS3[0]['IOPS'])   
        except:
            WTH2561 = "-"
            WL2561 = '-'
            WIOPS2561 = '-'
        try:
            COS3 = perfDb.results.find({'Build':build,'Name': 'Cosbench','Operation':'read','Object_Size':'256 MB','Buckets':50,'Objects':100,'Sessions':100}) 
            RTH2561 = roundoff(COS3[0]['Throughput'])
            RL2561 = roundoff(COS3[0]['Latency']['Avg'])
            RIOPS2561 = roundoff(COS3[0]['IOPS'])   
        except:
            RTH2561 = "-"
            RL2561 = '-'
            RIOPS2561 = '-'
        return [WTH41,WTH1001,WTH11,WTH51,WTH361,WTH641,WTH1281,WTH2561,RTH41,RTH1001,RTH11,RTH51,RTH361,RTH641,RTH1281,RTH2561,\
            WL41,WL1001,WL11,WL51,WL361,WL641,WL1281,WL2561,RL41,RL1001,RL11,RL51,RL361,RL641,RL1281,RL2561,WIOPS41,WIOPS1001,WIOPS11,\
                WIOPS51,WIOPS361,WIOPS641,WIOPS1281,WIOPS2561,RIOPS41,RIOPS1001,RIOPS11,RIOPS51,RIOPS361,RIOPS641,RIOPS1281,RIOPS2561]
    
    return [None] * 48
#### ----------------------------------------------------------------------------------------------
# Eng report page - Table 14 : Bucketops 1
@app.callback([  
    Output('IBCLR4', 'children'),Output('IBDEL4', 'children'),Output('BINIT4', 'children'),Output('PUT4', 'children'),Output('LIST4', 'children'),Output('GET4', 'children'),Output('DEL4', 'children'),Output('BCLR4', 'children'),Output('BDEL4', 'children'),
    Output('IBCLR100', 'children'),Output('IBDEL100', 'children'),Output('BINIT100', 'children'),Output('PUT100', 'children'),Output('LIST100', 'children'),Output('GET100', 'children'),Output('DEL100', 'children'),Output('BCLR100','children'),Output('BDEL100', 'children'),
    Output('IBCLR1', 'children'),Output('IBDEL1', 'children'),Output('BINIT1', 'children'),Output('PUT1', 'children'),Output('LIST1', 'children'),Output('GET1', 'children'),Output('DEL1', 'children'),Output('BCLR1', 'children'),Output('BDEL1', 'children'),
    Output('IBCLR5', 'children'),Output('IBDEL5', 'children'),Output('BINIT5', 'children'),Output('PUT5', 'children'),Output('LIST5', 'children'),Output('GET5', 'children'),Output('DEL5', 'children'),Output('BCLR5', 'children'),Output('BDEL5', 'children'),
    Output('IBCLR36', 'children'),Output('IBDEL36', 'children'),Output('BINIT36', 'children'),Output('PUT36', 'children'),Output('LIST36', 'children'),Output('GET36', 'children'),Output('DEL36', 'children'),Output('BCLR36', 'children'),Output('BDEL36', 'children'),
    Output('IBCLR64', 'children'),Output('IBDEL64', 'children'),Output('BINIT64', 'children'),Output('PUT64', 'children'),Output('LIST64', 'children'),Output('GET64', 'children'),Output('DEL64', 'children'),Output('BCLR64', 'children'),Output('BDEL64', 'children'),
    Output('IBCLR128', 'children'),Output('IBDEL128', 'children'),Output('BINIT128', 'children'),Output('PUT128', 'children'),Output('LIST128', 'children'),Output('GET128', 'children'),Output('DEL128', 'children'),Output('BCLR128', 'children'),Output('BDEL128', 'children'),
    Output('IBCLR256', 'children'),Output('IBDEL256', 'children'),Output('BINIT256', 'children'),Output('PUT256', 'children'),Output('LIST256', 'children'),Output('GET256', 'children'),Output('DEL256', 'children'),Output('BCLR256', 'children'),Output('BDEL256', 'children')],
    [Input('Bucket_Ops_Dropdown','value'),Input('table_submit_button', 'n_clicks'),dash.dependencies.Input('url', 'pathname'),Input('table_build_input', 'value')],[State('table_build_input', 'value')])
def update_bucketops1(parameter,clicks, pathname, input_value, enter_input):
    if not parameter:
        parameter = 'AvgLat'
    if parameter:
        Build = input_value
        try:
            cursor = perfDb.results.find({'Build':Build,'Name':'Hsbench','Object_Size':'4Kb','Buckets':1,'Objects':1000,'Sessions':100}) 
            doc = cursor[0]
            IBCLR4 = roundoff(doc['Bucket_Ops'][0][parameter])
            IBDEL4 = roundoff(doc['Bucket_Ops'][1][parameter])
            BINIT4 = roundoff(doc['Bucket_Ops'][2][parameter])
            PUT4 = roundoff(doc['Bucket_Ops'][3][parameter])
            LIST4 = roundoff(doc['Bucket_Ops'][4][parameter])
            GET4 = roundoff(doc['Bucket_Ops'][5][parameter])
            DEL4 = roundoff(doc['Bucket_Ops'][6][parameter])
            BCLR4 = roundoff(doc['Bucket_Ops'][7][parameter])
            BDEL4 = roundoff(doc['Bucket_Ops'][8][parameter])
        except:
            IBCLR4 = '-'
            IBDEL4 = '-'
            BINIT4 = '-'
            PUT4 = '-'
            LIST4 = '-'
            GET4 = '-'
            DEL4 = '-'
            BCLR4 = '-'
            BDEL4 ='-'
        try:
            cursor1 = perfDb.results.find({'Build':Build,'Name':'Hsbench','Object_Size':'100Kb','Buckets':1,'Objects':1000,'Sessions':100}) 
            doc = cursor1[0]
            IBCLR100 = roundoff(doc['Bucket_Ops'][0][parameter])
            IBDEL100 = roundoff(doc['Bucket_Ops'][1][parameter])
            BINIT100 = roundoff(doc['Bucket_Ops'][2][parameter])
            PUT100 = roundoff(doc['Bucket_Ops'][3][parameter])
            LIST100 = roundoff(doc['Bucket_Ops'][4][parameter])
            GET100 = roundoff(doc['Bucket_Ops'][5][parameter])
            DEL100 = roundoff(doc['Bucket_Ops'][6][parameter])
            BCLR100 = roundoff(doc['Bucket_Ops'][7][parameter])
            BDEL100 = roundoff(doc['Bucket_Ops'][8][parameter])
        except:
            IBCLR100 = '-'
            IBDEL100 = '-'
            BINIT100 = '-'
            PUT100 = '-'
            LIST100 = '-'
            GET100 = '-'
            DEL100 = '-'
            BCLR100 = '-'
            BDEL100 = '-'
        try:
            cursor2 = perfDb.results.find({'Build':Build,'Name':'Hsbench','Object_Size':'1Mb','Buckets':1,'Objects':1000,'Sessions':100}) 
            doc = cursor2[0]
            IBCLR1 = roundoff(doc['Bucket_Ops'][0][parameter])
            IBDEL1 = roundoff(doc['Bucket_Ops'][1][parameter])
            BINIT1 = roundoff(doc['Bucket_Ops'][2][parameter])
            PUT1 = roundoff(doc['Bucket_Ops'][3][parameter])
            LIST1 = roundoff(doc['Bucket_Ops'][4][parameter])
            GET1 = roundoff(doc['Bucket_Ops'][5][parameter])
            DEL1 = roundoff(doc['Bucket_Ops'][6][parameter])
            BCLR1 = roundoff(doc['Bucket_Ops'][7][parameter])
            BDEL1 = roundoff(doc['Bucket_Ops'][8][parameter])
        except:
            IBCLR1 = '-'
            IBDEL1 = '-'
            BINIT1 = '-'
            PUT1 = '-'
            LIST1 = '-'
            GET1 = '-'
            DEL1 = '-'
            BCLR1 = '-'
            BDEL1 = '-'
        try:
            cursor3 = perfDb.results.find({'Build':Build,'Name':'Hsbench','Object_Size':'5Mb','Buckets':1,'Objects':1000,'Sessions':100}) 
            doc = cursor3[0]
            IBCLR5 = roundoff(doc['Bucket_Ops'][0][parameter])
            IBDEL5 = roundoff(doc['Bucket_Ops'][1][parameter])
            BINIT5 = roundoff(doc['Bucket_Ops'][2][parameter])
            PUT5 = roundoff(doc['Bucket_Ops'][3][parameter])
            LIST5 = roundoff(doc['Bucket_Ops'][4][parameter])
            GET5 = roundoff(doc['Bucket_Ops'][5][parameter])
            DEL5 = roundoff(doc['Bucket_Ops'][6][parameter])
            BCLR5 = roundoff(doc['Bucket_Ops'][7][parameter])
            BDEL5 = roundoff(doc['Bucket_Ops'][8][parameter])
        except:
            IBCLR5 = '-'
            IBDEL5 = '-'
            BINIT5 = '-'
            PUT5 = '-'
            LIST5 = '-'
            GET5 = '-'
            DEL5 = '-'
            BCLR5 = '-'
            BDEL5 = '-'
        try:
            cursor5 = perfDb.results.find({'Build':Build,'Name':'Hsbench','Object_Size':'36Mb','Buckets':1,'Objects':1000,'Sessions':100}) 
            doc = cursor5[0]
            IBCLR36 = roundoff(doc['Bucket_Ops'][0][parameter])
            IBDEL36 = roundoff(doc['Bucket_Ops'][1][parameter])
            BINIT36 = roundoff(doc['Bucket_Ops'][2][parameter])
            PUT36 = roundoff(doc['Bucket_Ops'][3][parameter])
            LIST36 = roundoff(doc['Bucket_Ops'][4][parameter])
            GET36 = roundoff(doc['Bucket_Ops'][5][parameter])
            DEL36 = roundoff(doc['Bucket_Ops'][6][parameter])
            BCLR36 = roundoff(doc['Bucket_Ops'][7][parameter])
            BDEL36 = roundoff(doc['Bucket_Ops'][8][parameter])
        except:
            IBCLR36 = '-'
            IBDEL36 = '-'
            BINIT36 = '-'
            PUT36 = '-'
            LIST36 = '-'
            GET36 = '-'
            DEL36 = '-'
            BCLR36 = '-'
            BDEL36 = '-'
        try:
            cursor6 = perfDb.results.find({'Build':Build,'Name':'Hsbench','Object_Size':'64Mb','Buckets':1,'Objects':1000,'Sessions':100}) 
            doc = cursor6[0]
            IBCLR64 = roundoff(doc['Bucket_Ops'][0][parameter])
            IBDEL64 = roundoff(doc['Bucket_Ops'][1][parameter])
            BINIT64 = roundoff(doc['Bucket_Ops'][2][parameter])
            PUT64 = roundoff(doc['Bucket_Ops'][3][parameter])
            LIST64 = roundoff(doc['Bucket_Ops'][4][parameter])
            GET64 = roundoff(doc['Bucket_Ops'][5][parameter])
            DEL64 = roundoff(doc['Bucket_Ops'][6][parameter])
            BCLR64 = roundoff(doc['Bucket_Ops'][7][parameter])
            BDEL64 = roundoff(doc['Bucket_Ops'][8][parameter])   
        except:
            IBCLR64 = '-'
            IBDEL64 = '-'
            BINIT64 = '-'
            PUT64 = '-'
            LIST64 = '-'
            GET64 = '-'
            DEL64 = '-'
            BCLR64 = '-'
            BDEL64 = '-'
        try:
            cursor7 = perfDb.results.find({'Build':Build,'Name':'Hsbench','Object_Size':'128Mb','Buckets':1,'Objects':1000,'Sessions':100}) 
            doc = cursor7[0]
            IBCLR128 = roundoff(doc['Bucket_Ops'][0][parameter])
            IBDEL128 = roundoff(doc['Bucket_Ops'][1][parameter])
            BINIT128 = roundoff(doc['Bucket_Ops'][2][parameter])
            PUT128 = roundoff(doc['Bucket_Ops'][3][parameter])
            LIST128 = roundoff(doc['Bucket_Ops'][4][parameter])
            GET128 = roundoff(doc['Bucket_Ops'][5][parameter])
            DEL128 = roundoff(doc['Bucket_Ops'][6][parameter])
            BCLR128 = roundoff(doc['Bucket_Ops'][7][parameter])
            BDEL128 = roundoff(doc['Bucket_Ops'][8][parameter]) 
        except:
            IBCLR128 = '-'
            IBDEL128 = '-'
            BINIT128 = '-'
            PUT128 = '-'
            LIST128 = '-'
            GET128 = '-'
            DEL128 = '-'
            BCLR128 = '-'
            BDEL128 = '-'
        try:
            cursor8 = perfDb.results.find({'Build':Build,'Name':'Hsbench','Object_Size':'256Mb','Buckets':1,'Objects':1000,'Sessions':100}) 
            doc = cursor8[0]
            IBCLR256 = roundoff(doc['Bucket_Ops'][0][parameter])
            IBDEL256 = roundoff(doc['Bucket_Ops'][1][parameter])
            BINIT256 = roundoff(doc['Bucket_Ops'][2][parameter])
            PUT256 = roundoff(doc['Bucket_Ops'][3][parameter])
            LIST256 = roundoff(doc['Bucket_Ops'][4][parameter])
            GET256 = roundoff(doc['Bucket_Ops'][5][parameter])
            DEL256 = roundoff(doc['Bucket_Ops'][6][parameter])
            BCLR256 = roundoff(doc['Bucket_Ops'][7][parameter])
            BDEL256 = roundoff(doc['Bucket_Ops'][8][parameter])
        except:
            IBCLR256 = '-'
            IBDEL256 = '-'
            BINIT256 = '-'
            PUT256 = '-'
            LIST256 = '-'
            GET256 = '-'
            DEL256 = '-'
            BCLR256 = '-'
            BDEL256 = '-'
        
        return [IBCLR4,IBDEL4,BINIT4,PUT4,LIST4,GET4,DEL4,BCLR4,BDEL4,\
        IBCLR100,IBDEL100,BINIT100,PUT100,LIST100,GET100,DEL100,BCLR100,BDEL100,\
        IBCLR1,IBDEL1,BINIT1,PUT1,LIST1,GET1,DEL1,BCLR1,BDEL1,\
        IBCLR5,IBDEL5,BINIT5,PUT5,LIST5,GET5,DEL5,BCLR5,BDEL5,\
        IBCLR36,IBDEL36,BINIT36,PUT36,LIST36,GET36,DEL36,BCLR36,BDEL36,\
        IBCLR64,IBDEL64,BINIT64,PUT64,LIST64,GET64,DEL64,BCLR64,BDEL64,\
        IBCLR128,IBDEL128,BINIT128,PUT128,LIST128,GET128,DEL128,BCLR128,BDEL128,\
        IBCLR256,IBDEL256,BINIT256,PUT256,LIST256,GET256,DEL256,BCLR256,BDEL256,\
        ]
    return [None]*72
#### ----------------------------------------------------------------------------------------------
# Eng report page - Table 15 : Bucketops 2
@app.callback([  
    Output('IBCLR41', 'children'),Output('IBDEL41', 'children'),Output('BINIT41', 'children'),Output('PUT41', 'children'),Output('LIST41', 'children'),Output('GET41', 'children'),Output('DEL41', 'children'),Output('BCLR41', 'children'),Output('BDEL41', 'children'),
    Output('IBCLR1001', 'children'),Output('IBDEL1001', 'children'),Output('BINIT1001', 'children'),Output('PUT1001', 'children'),Output('LIST1001', 'children'),Output('GET1001', 'children'),Output('DEL1001', 'children'),Output('BCLR1001','children'),Output('BDEL1001', 'children'),
    Output('IBCLR11', 'children'),Output('IBDEL11', 'children'),Output('BINIT11', 'children'),Output('PUT11', 'children'),Output('LIST11', 'children'),Output('GET11', 'children'),Output('DEL11', 'children'),Output('BCLR11', 'children'),Output('BDEL11', 'children'),
    Output('IBCLR51', 'children'),Output('IBDEL51', 'children'),Output('BINIT51', 'children'),Output('PUT51', 'children'),Output('LIST51', 'children'),Output('GET51', 'children'),Output('DEL51', 'children'),Output('BCLR51', 'children'),Output('BDEL51', 'children'),
    Output('IBCLR361', 'children'),Output('IBDEL361', 'children'),Output('BINIT361', 'children'),Output('PUT361', 'children'),Output('LIST361', 'children'),Output('GET361', 'children'),Output('DEL361', 'children'),Output('BCLR361', 'children'),Output('BDEL361', 'children'),
    Output('IBCLR641', 'children'),Output('IBDEL641', 'children'),Output('BINIT641', 'children'),Output('PUT641', 'children'),Output('LIST641', 'children'),Output('GET641', 'children'),Output('DEL641', 'children'),Output('BCLR641', 'children'),Output('BDEL641', 'children'),
    Output('IBCLR1281', 'children'),Output('IBDEL1281', 'children'),Output('BINIT1281', 'children'),Output('PUT1281', 'children'),Output('LIST1281', 'children'),Output('GET1281', 'children'),Output('DEL1281', 'children'),Output('BCLR1281', 'children'),Output('BDEL1281', 'children'),
    Output('IBCLR2561', 'children'),Output('IBDEL2561', 'children'),Output('BINIT2561', 'children'),Output('PUT2561', 'children'),Output('LIST2561', 'children'),Output('GET2561', 'children'),Output('DEL2561', 'children'),Output('BCLR2561', 'children'),Output('BDEL2561', 'children')],
    [Input('Bucket_Ops_Dropdown','value'),Input('table_submit_button', 'n_clicks'),dash.dependencies.Input('url', 'pathname'),Input('table_build_input', 'value')],[State('table_build_input', 'value')])
def update_bucketops2(parameter,clicks, pathname, input_value, enter_input):    
    if not parameter:
        parameter = 'AvgLat'  
    if parameter:
        Build = input_value
        try:
            cursor = perfDb.results.find({'Build':Build,'Name':'Hsbench','Object_Size':'4Kb','Buckets':10,'Objects':1000,'Sessions':100}) 
            doc = cursor[0]
            IBCLR4 = roundoff(doc['Bucket_Ops'][0][parameter])
            IBDEL4 = roundoff(doc['Bucket_Ops'][1][parameter])
            BINIT4 = roundoff(doc['Bucket_Ops'][2][parameter])
            PUT4 = roundoff(doc['Bucket_Ops'][3][parameter])
            LIST4 = roundoff(doc['Bucket_Ops'][4][parameter])
            GET4 = roundoff(doc['Bucket_Ops'][5][parameter])
            DEL4 = roundoff(doc['Bucket_Ops'][6][parameter])
            BCLR4 = roundoff(doc['Bucket_Ops'][7][parameter])
            BDEL4 = roundoff(doc['Bucket_Ops'][8][parameter])
        except:
            IBCLR4 = '-'
            IBDEL4 = '-'
            BINIT4 = '-'
            PUT4 = '-'
            LIST4 = '-'
            GET4 = '-'
            DEL4 = '-'
            BCLR4 = '-'
            BDEL4 ='-'
        try:
            cursor1 = perfDb.results.find({'Build':Build,'Name':'Hsbench','Object_Size':'100Kb','Buckets':10,'Objects':1000,'Sessions':100}) 
            doc = cursor1[0]
            IBCLR100 = roundoff(doc['Bucket_Ops'][0][parameter])
            IBDEL100 = roundoff(doc['Bucket_Ops'][1][parameter])
            BINIT100 = roundoff(doc['Bucket_Ops'][2][parameter])
            PUT100 = roundoff(doc['Bucket_Ops'][3][parameter])
            LIST100 = roundoff(doc['Bucket_Ops'][4][parameter])
            GET100 = roundoff(doc['Bucket_Ops'][5][parameter])
            DEL100 = roundoff(doc['Bucket_Ops'][6][parameter])
            BCLR100 = roundoff(doc['Bucket_Ops'][7][parameter])
            BDEL100 = roundoff(doc['Bucket_Ops'][8][parameter])
        except:
            IBCLR100 = '-'
            IBDEL100 = '-'
            BINIT100 = '-'
            PUT100 = '-'
            LIST100 = '-'
            GET100 = '-'
            DEL100 = '-'
            BCLR100 = '-'
            BDEL100 = '-'
        try:
            cursor2 = perfDb.results.find({'Build':Build,'Name':'Hsbench','Object_Size':'1Mb','Buckets':10,'Objects':1000,'Sessions':100}) 
            doc = cursor2[0]
            IBCLR1 = roundoff(doc['Bucket_Ops'][0][parameter])
            IBDEL1 = roundoff(doc['Bucket_Ops'][1][parameter])
            BINIT1 = roundoff(doc['Bucket_Ops'][2][parameter])
            PUT1 = roundoff(doc['Bucket_Ops'][3][parameter])
            LIST1 = roundoff(doc['Bucket_Ops'][4][parameter])
            GET1 = roundoff(doc['Bucket_Ops'][5][parameter])
            DEL1 = roundoff(doc['Bucket_Ops'][6][parameter])
            BCLR1 = roundoff(doc['Bucket_Ops'][7][parameter])
            BDEL1 = roundoff(doc['Bucket_Ops'][8][parameter])
        except:
            IBCLR1 = '-'
            IBDEL1 = '-'
            BINIT1 = '-'
            PUT1 = '-'
            LIST1 = '-'
            GET1 = '-'
            DEL1 = '-'
            BCLR1 = '-'
            BDEL1 = '-'
        try:
            cursor3 = perfDb.results.find({'Build':Build,'Name':'Hsbench','Object_Size':'5Mb','Buckets':10,'Objects':1000,'Sessions':100}) 
            doc = cursor3[0]
            IBCLR5 = roundoff(doc['Bucket_Ops'][0][parameter])
            IBDEL5 = roundoff(doc['Bucket_Ops'][1][parameter])
            BINIT5 = roundoff(doc['Bucket_Ops'][2][parameter])
            PUT5 = roundoff(doc['Bucket_Ops'][3][parameter])
            LIST5 = roundoff(doc['Bucket_Ops'][4][parameter])
            GET5 = roundoff(doc['Bucket_Ops'][5][parameter])
            DEL5 = roundoff(doc['Bucket_Ops'][6][parameter])
            BCLR5 = roundoff(doc['Bucket_Ops'][7][parameter])
            BDEL5 = roundoff(doc['Bucket_Ops'][8][parameter])
        except:
            IBCLR5 = '-'
            IBDEL5 = '-'
            BINIT5 = '-'
            PUT5 = '-'
            LIST5 = '-'
            GET5 = '-'
            DEL5 = '-'
            BCLR5 = '-'
            BDEL5 = '-'
        try:
            cursor5 = perfDb.results.find({'Build':Build,'Name':'Hsbench','Object_Size':'36Mb','Buckets':10,'Objects':1000,'Sessions':100}) 
            doc = cursor5[0]
            IBCLR36 = roundoff(doc['Bucket_Ops'][0][parameter])
            IBDEL36 = roundoff(doc['Bucket_Ops'][1][parameter])
            BINIT36 = roundoff(doc['Bucket_Ops'][2][parameter])
            PUT36 = roundoff(doc['Bucket_Ops'][3][parameter])
            LIST36 = roundoff(doc['Bucket_Ops'][4][parameter])
            GET36 = roundoff(doc['Bucket_Ops'][5][parameter])
            DEL36 = roundoff(doc['Bucket_Ops'][6][parameter])
            BCLR36 = roundoff(doc['Bucket_Ops'][7][parameter])
            BDEL36 = roundoff(doc['Bucket_Ops'][8][parameter])
        except:
            IBCLR36 = '-'
            IBDEL36 = '-'
            BINIT36 = '-'
            PUT36 = '-'
            LIST36 = '-'
            GET36 = '-'
            DEL36 = '-'
            BCLR36 = '-'
            BDEL36 = '-'
        try:
            cursor6 = perfDb.results.find({'Build':Build,'Name':'Hsbench','Object_Size':'64Mb','Buckets':10,'Objects':1000,'Sessions':100}) 
            doc = cursor6[0]
            IBCLR64 = roundoff(doc['Bucket_Ops'][0][parameter])
            IBDEL64 = roundoff(doc['Bucket_Ops'][1][parameter])
            BINIT64 = roundoff(doc['Bucket_Ops'][2][parameter])
            PUT64 = roundoff(doc['Bucket_Ops'][3][parameter])
            LIST64 = roundoff(doc['Bucket_Ops'][4][parameter])
            GET64 = roundoff(doc['Bucket_Ops'][5][parameter])
            DEL64 = roundoff(doc['Bucket_Ops'][6][parameter])
            BCLR64 = roundoff(doc['Bucket_Ops'][7][parameter])
            BDEL64 = roundoff(doc['Bucket_Ops'][8][parameter])   
        except:
            IBCLR64 = '-'
            IBDEL64 = '-'
            BINIT64 = '-'
            PUT64 = '-'
            LIST64 = '-'
            GET64 = '-'
            DEL64 = '-'
            BCLR64 = '-'
            BDEL64 = '-'
        try:
            cursor7 = perfDb.results.find({'Build':Build,'Name':'Hsbench','Object_Size':'128Mb','Buckets':10,'Objects':1000,'Sessions':100}) 
            doc = cursor7[0]
            IBCLR128 = roundoff(doc['Bucket_Ops'][0][parameter])
            IBDEL128 = roundoff(doc['Bucket_Ops'][1][parameter])
            BINIT128 = roundoff(doc['Bucket_Ops'][2][parameter])
            PUT128 = roundoff(doc['Bucket_Ops'][3][parameter])
            LIST128 = roundoff(doc['Bucket_Ops'][4][parameter])
            GET128 = roundoff(doc['Bucket_Ops'][5][parameter])
            DEL128 = roundoff(doc['Bucket_Ops'][6][parameter])
            BCLR128 = roundoff(doc['Bucket_Ops'][7][parameter])
            BDEL128 = roundoff(doc['Bucket_Ops'][8][parameter]) 
        except:
            IBCLR128 = '-'
            IBDEL128 = '-'
            BINIT128 = '-'
            PUT128 = '-'
            LIST128 = '-'
            GET128 = '-'
            DEL128 = '-'
            BCLR128 = '-'
            BDEL128 = '-'
        try:
            cursor8 = perfDb.results.find({'Build':Build,'Name':'Hsbench','Object_Size':'256Mb','Buckets':10,'Objects':1000,'Sessions':100}) 
            doc = cursor8[0]
            IBCLR256 = roundoff(doc['Bucket_Ops'][0][parameter])
            IBDEL256 = roundoff(doc['Bucket_Ops'][1][parameter])
            BINIT256 = roundoff(doc['Bucket_Ops'][2][parameter])
            PUT256 = roundoff(doc['Bucket_Ops'][3][parameter])
            LIST256 = roundoff(doc['Bucket_Ops'][4][parameter])
            GET256 = roundoff(doc['Bucket_Ops'][5][parameter])
            DEL256 = roundoff(doc['Bucket_Ops'][6][parameter])
            BCLR256 = roundoff(doc['Bucket_Ops'][7][parameter])
            BDEL256 = roundoff(doc['Bucket_Ops'][8][parameter])
        except:
            IBCLR256 = '-'
            IBDEL256 = '-'
            BINIT256 = '-'
            PUT256 = '-'
            LIST256 = '-'
            GET256 = '-'
            DEL256 = '-'
            BCLR256 = '-'
            BDEL256 = '-'
        return [IBCLR4,IBDEL4,BINIT4,PUT4,LIST4,GET4,DEL4,BCLR4,BDEL4,\
        IBCLR100,IBDEL100,BINIT100,PUT100,LIST100,GET100,DEL100,BCLR100,BDEL100,\
        IBCLR1,IBDEL1,BINIT1,PUT1,LIST1,GET1,DEL1,BCLR1,BDEL1,\
        IBCLR5,IBDEL5,BINIT5,PUT5,LIST5,GET5,DEL5,BCLR5,BDEL5,\
        IBCLR36,IBDEL36,BINIT36,PUT36,LIST36,GET36,DEL36,BCLR36,BDEL36,\
        IBCLR64,IBDEL64,BINIT64,PUT64,LIST64,GET64,DEL64,BCLR64,BDEL64,\
        IBCLR128,IBDEL128,BINIT128,PUT128,LIST128,GET128,DEL128,BCLR128,BDEL128,\
        IBCLR256,IBDEL256,BINIT256,PUT256,LIST256,GET256,DEL256,BCLR256,BDEL256,\
        ]
    return [None]*72
#### ----------------------------------------------------------------------------------------------
# Eng report page - Table 16 : Bucketops 3
@app.callback([  
    Output('IBCLR42', 'children'),Output('IBDEL42', 'children'),Output('BINIT42', 'children'),Output('PUT42', 'children'),Output('LIST42', 'children'),Output('GET42', 'children'),Output('DEL42', 'children'),Output('BCLR42', 'children'),Output('BDEL42', 'children'),
    Output('IBCLR1002', 'children'),Output('IBDEL1002', 'children'),Output('BINIT1002', 'children'),Output('PUT1002', 'children'),Output('LIST1002', 'children'),Output('GET1002', 'children'),Output('DEL1002', 'children'),Output('BCLR1002','children'),Output('BDEL1002', 'children'),
    Output('IBCLR12', 'children'),Output('IBDEL12', 'children'),Output('BINIT12', 'children'),Output('PUT12', 'children'),Output('LIST12', 'children'),Output('GET12', 'children'),Output('DEL12', 'children'),Output('BCLR12', 'children'),Output('BDEL12', 'children'),
    Output('IBCLR52', 'children'),Output('IBDEL52', 'children'),Output('BINIT52', 'children'),Output('PUT52', 'children'),Output('LIST52', 'children'),Output('GET52', 'children'),Output('DEL52', 'children'),Output('BCLR52', 'children'),Output('BDEL52', 'children'),
    Output('IBCLR362', 'children'),Output('IBDEL362', 'children'),Output('BINIT362', 'children'),Output('PUT362', 'children'),Output('LIST362', 'children'),Output('GET362', 'children'),Output('DEL362', 'children'),Output('BCLR362', 'children'),Output('BDEL362', 'children'),
    Output('IBCLR642', 'children'),Output('IBDEL642', 'children'),Output('BINIT642', 'children'),Output('PUT642', 'children'),Output('LIST642', 'children'),Output('GET642', 'children'),Output('DEL642', 'children'),Output('BCLR642', 'children'),Output('BDEL642', 'children'),
    Output('IBCLR1282', 'children'),Output('IBDEL1282', 'children'),Output('BINIT1282', 'children'),Output('PUT1282', 'children'),Output('LIST1282', 'children'),Output('GET1282', 'children'),Output('DEL1282', 'children'),Output('BCLR1282', 'children'),Output('BDEL1282', 'children'),
    Output('IBCLR2562', 'children'),Output('IBDEL2562', 'children'),Output('BINIT2562', 'children'),Output('PUT2562', 'children'),Output('LIST2562', 'children'),Output('GET2562', 'children'),Output('DEL2562', 'children'),Output('BCLR2562', 'children'),Output('BDEL2562', 'children')],
    [Input('Bucket_Ops_Dropdown','value'),Input('table_submit_button', 'n_clicks'),dash.dependencies.Input('url', 'pathname'),Input('table_build_input', 'value')],[State('table_build_input', 'value')])
def update_bucketops3(parameter,clicks, pathname, input_value, enter_input):
    if not parameter:
        parameter = 'AvgLat'
    if parameter:
        Build = input_value
        try:
            cursor = perfDb.results.find({'Build':Build,'Name':'Hsbench','Object_Size':'4Kb','Buckets':50,'Objects':5000,'Sessions':100}) 
            doc = cursor[0]
            IBCLR4 = roundoff(doc['Bucket_Ops'][0][parameter])
            IBDEL4 = roundoff(doc['Bucket_Ops'][1][parameter])
            BINIT4 = roundoff(doc['Bucket_Ops'][2][parameter])
            PUT4 = roundoff(doc['Bucket_Ops'][3][parameter])
            LIST4 = roundoff(doc['Bucket_Ops'][4][parameter])
            GET4 = roundoff(doc['Bucket_Ops'][5][parameter])
            DEL4 = roundoff(doc['Bucket_Ops'][6][parameter])
            BCLR4 = roundoff(doc['Bucket_Ops'][7][parameter])
            BDEL4 = roundoff(doc['Bucket_Ops'][8][parameter])
        except:
            IBCLR4 = '-'
            IBDEL4 = '-'
            BINIT4 = '-'
            PUT4 = '-'
            LIST4 = '-'
            GET4 = '-'
            DEL4 = '-'
            BCLR4 = '-'
            BDEL4 ='-'
        try:
            cursor1 = perfDb.results.find({'Build':Build,'Name':'Hsbench','Object_Size':'100Kb','Buckets':50,'Objects':5000,'Sessions':100}) 
            doc = cursor1[0]
            IBCLR100 = roundoff(doc['Bucket_Ops'][0][parameter])
            IBDEL100 = roundoff(doc['Bucket_Ops'][1][parameter])
            BINIT100 = roundoff(doc['Bucket_Ops'][2][parameter])
            PUT100 = roundoff(doc['Bucket_Ops'][3][parameter])
            LIST100 = roundoff(doc['Bucket_Ops'][4][parameter])
            GET100 = roundoff(doc['Bucket_Ops'][5][parameter])
            DEL100 = roundoff(doc['Bucket_Ops'][6][parameter])
            BCLR100 = roundoff(doc['Bucket_Ops'][7][parameter])
            BDEL100 = roundoff(doc['Bucket_Ops'][8][parameter])
        except:
            IBCLR100 = '-'
            IBDEL100 = '-'
            BINIT100 = '-'
            PUT100 = '-'
            LIST100 = '-'
            GET100 = '-'
            DEL100 = '-'
            BCLR100 = '-'
            BDEL100 = '-'
        try:
            cursor2 = perfDb.results.find({'Build':Build,'Name':'Hsbench','Object_Size':'1Mb','Buckets':50,'Objects':5000,'Sessions':100}) 
            doc = cursor2[0]
            IBCLR1 = roundoff(doc['Bucket_Ops'][0][parameter])
            IBDEL1 = roundoff(doc['Bucket_Ops'][1][parameter])
            BINIT1 = roundoff(doc['Bucket_Ops'][2][parameter])
            PUT1 = roundoff(doc['Bucket_Ops'][3][parameter])
            LIST1 = roundoff(doc['Bucket_Ops'][4][parameter])
            GET1 = roundoff(doc['Bucket_Ops'][5][parameter])
            DEL1 = roundoff(doc['Bucket_Ops'][6][parameter])
            BCLR1 = roundoff(doc['Bucket_Ops'][7][parameter])
            BDEL1 = roundoff(doc['Bucket_Ops'][8][parameter])
        except:
            IBCLR1 = '-'
            IBDEL1 = '-'
            BINIT1 = '-'
            PUT1 = '-'
            LIST1 = '-'
            GET1 = '-'
            DEL1 = '-'
            BCLR1 = '-'
            BDEL1 = '-'
        try:
            cursor3 = perfDb.results.find({'Build':Build,'Name':'Hsbench','Object_Size':'5Mb','Buckets':50,'Objects':5000,'Sessions':100}) 
            doc = cursor3[0]
            IBCLR5 = roundoff(doc['Bucket_Ops'][0][parameter])
            IBDEL5 = roundoff(doc['Bucket_Ops'][1][parameter])
            BINIT5 = roundoff(doc['Bucket_Ops'][2][parameter])
            PUT5 = roundoff(doc['Bucket_Ops'][3][parameter])
            LIST5 = roundoff(doc['Bucket_Ops'][4][parameter])
            GET5 = roundoff(doc['Bucket_Ops'][5][parameter])
            DEL5 = roundoff(doc['Bucket_Ops'][6][parameter])
            BCLR5 = roundoff(doc['Bucket_Ops'][7][parameter])
            BDEL5 = roundoff(doc['Bucket_Ops'][8][parameter])
        except:
            IBCLR5 = '-'
            IBDEL5 = '-'
            BINIT5 = '-'
            PUT5 = '-'
            LIST5 = '-'
            GET5 = '-'
            DEL5 = '-'
            BCLR5 = '-'
            BDEL5 = '-'
        try:
            cursor5 = perfDb.results.find({'Build':Build,'Name':'Hsbench','Object_Size':'36Mb','Buckets':50,'Objects':5000,'Sessions':100}) 
            doc = cursor5[0]
            IBCLR36 = roundoff(doc['Bucket_Ops'][0][parameter])
            IBDEL36 = roundoff(doc['Bucket_Ops'][1][parameter])
            BINIT36 = roundoff(doc['Bucket_Ops'][2][parameter])
            PUT36 = roundoff(doc['Bucket_Ops'][3][parameter])
            LIST36 = roundoff(doc['Bucket_Ops'][4][parameter])
            GET36 = roundoff(doc['Bucket_Ops'][5][parameter])
            DEL36 = roundoff(doc['Bucket_Ops'][6][parameter])
            BCLR36 = roundoff(doc['Bucket_Ops'][7][parameter])
            BDEL36 = roundoff(doc['Bucket_Ops'][8][parameter])
        except:
            IBCLR36 = '-'
            IBDEL36 = '-'
            BINIT36 = '-'
            PUT36 = '-'
            LIST36 = '-'
            GET36 = '-'
            DEL36 = '-'
            BCLR36 = '-'
            BDEL36 = '-'
        try:
            cursor6 = perfDb.results.find({'Build':Build,'Name':'Hsbench','Object_Size':'64Mb','Buckets':50,'Objects':5000,'Sessions':100}) 
            doc = cursor6[0]
            IBCLR64 = roundoff(doc['Bucket_Ops'][0][parameter])
            IBDEL64 = roundoff(doc['Bucket_Ops'][1][parameter])
            BINIT64 = roundoff(doc['Bucket_Ops'][2][parameter])
            PUT64 = roundoff(doc['Bucket_Ops'][3][parameter])
            LIST64 = roundoff(doc['Bucket_Ops'][4][parameter])
            GET64 = roundoff(doc['Bucket_Ops'][5][parameter])
            DEL64 = roundoff(doc['Bucket_Ops'][6][parameter])
            BCLR64 = roundoff(doc['Bucket_Ops'][7][parameter])
            BDEL64 = roundoff(doc['Bucket_Ops'][8][parameter])   
        except:
            IBCLR64 = '-'
            IBDEL64 = '-'
            BINIT64 = '-'
            PUT64 = '-'
            LIST64 = '-'
            GET64 = '-'
            DEL64 = '-'
            BCLR64 = '-'
            BDEL64 = '-'
        try:
            cursor7 = perfDb.results.find({'Build':Build,'Name':'Hsbench','Object_Size':'128Mb','Buckets':50,'Objects':5000,'Sessions':100}) 
            doc = cursor7[0]
            IBCLR128 = roundoff(doc['Bucket_Ops'][0][parameter])
            IBDEL128 = roundoff(doc['Bucket_Ops'][1][parameter])
            BINIT128 = roundoff(doc['Bucket_Ops'][2][parameter])
            PUT128 = roundoff(doc['Bucket_Ops'][3][parameter])
            LIST128 = roundoff(doc['Bucket_Ops'][4][parameter])
            GET128 = roundoff(doc['Bucket_Ops'][5][parameter])
            DEL128 = roundoff(doc['Bucket_Ops'][6][parameter])
            BCLR128 = roundoff(doc['Bucket_Ops'][7][parameter])
            BDEL128 = roundoff(doc['Bucket_Ops'][8][parameter]) 
        except:
            IBCLR128 = '-'
            IBDEL128 = '-'
            BINIT128 = '-'
            PUT128 = '-'
            LIST128 = '-'
            GET128 = '-'
            DEL128 = '-'
            BCLR128 = '-'
            BDEL128 = '-'
        try:
            cursor8 = perfDb.results.find({'Build':Build,'Name':'Hsbench','Object_Size':'256Mb','Buckets':50,'Objects':5000,'Sessions':100}) 
            doc = cursor8[0]
            IBCLR256 = roundoff(doc['Bucket_Ops'][0][parameter])
            IBDEL256 = roundoff(doc['Bucket_Ops'][1][parameter])
            BINIT256 = roundoff(doc['Bucket_Ops'][2][parameter])
            PUT256 = roundoff(doc['Bucket_Ops'][3][parameter])
            LIST256 = roundoff(doc['Bucket_Ops'][4][parameter])
            GET256 = roundoff(doc['Bucket_Ops'][5][parameter])
            DEL256 = roundoff(doc['Bucket_Ops'][6][parameter])
            BCLR256 = roundoff(doc['Bucket_Ops'][7][parameter])
            BDEL256 = roundoff(doc['Bucket_Ops'][8][parameter])
        except:
            IBCLR256 = '-'
            IBDEL256 = '-'
            BINIT256 = '-'
            PUT256 = '-'
            LIST256 = '-'
            GET256 = '-'
            DEL256 = '-'
            BCLR256 = '-'
            BDEL256 = '-'
        return [IBCLR4,IBDEL4,BINIT4,PUT4,LIST4,GET4,DEL4,BCLR4,BDEL4,\
        IBCLR100,IBDEL100,BINIT100,PUT100,LIST100,GET100,DEL100,BCLR100,BDEL100,\
        IBCLR1,IBDEL1,BINIT1,PUT1,LIST1,GET1,DEL1,BCLR1,BDEL1,\
        IBCLR5,IBDEL5,BINIT5,PUT5,LIST5,GET5,DEL5,BCLR5,BDEL5,\
        IBCLR36,IBDEL36,BINIT36,PUT36,LIST36,GET36,DEL36,BCLR36,BDEL36,\
        IBCLR64,IBDEL64,BINIT64,PUT64,LIST64,GET64,DEL64,BCLR64,BDEL64,\
        IBCLR128,IBDEL128,BINIT128,PUT128,LIST128,GET128,DEL128,BCLR128,BDEL128,\
        IBCLR256,IBDEL256,BINIT256,PUT256,LIST256,GET256,DEL256,BCLR256,BDEL256,\
        ]
    return [None]*72

#### App Callbacks ends ===========================================================================
# run server 

if __name__ == '__main__':
    # run on port 5002
    app.run_server(host='0.0.0.0', port=5002, threaded=True, debug=False)

#### Application ends ==============================================================================
