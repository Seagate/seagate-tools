'''
CFT webpage improvement Task for CORTX CFT Report
@ Seagate Pune
Modified on : 5 August 2020
             19 August 2020
             24 August 2020 with CSS
Created by : Sampada Petkar 
Version: 7
Updates:
- web page for report generations for eng and exe reports
- local csv file reads and updates on sending dummy build number
- updates both tables
- access through URL for build report data
- in sync with database
- all entries are fetched from database
- with CSS and coloured cells
- shows previous build, performance data and detailed report
'''
### ======================================================
import dash
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc
import dash_table
import flask
import re
import os
from dash.dependencies import Output, State, Input
import requests
import mongodbAPIs as mapi
from pymongo import MongoClient
import pandas as pd
### ======================================================
# global declarations

external_stylesheets = [dbc.themes.COSMO]

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.title = "CORTX Test Status"
server = app.server

perf_host = "mongodb://sampada:password@cftic1.pun.seagate.com:27017,cftic2.pun.seagate.com:27017,apollojenkins.pun.seagate.com:27017/test?authSource=performance_db&replicaSet=rs0&readPreference=primary&appname=MongoDB%20Compass%20Community&ssl=false"
client = MongoClient(perf_host)
perfDb = client['performance_db']

rHost = "mongodb://dataread:seagate%40123@cftic1.pun.seagate.com:27017,cftic2.pun.seagate.com:27017,apollojenkins.pun.seagate.com:27017/?authSource=cft_test_results&replicaSet=rs0"
cftClientRead = MongoClient(rHost)
cftdbRead = cftClientRead['cft_test_results'] 
### ======================================================

@server.route('/favicon.ico')
def favicon():
    return flask.send_from_directory(os.path.join(server.root_path, 'static'), 'favicon.ico')

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
# two buttons on top right
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

#=================================================
# Eng report page - Table 1 : Report bugs
#=================================================
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
    html.Thead(html.Tr([html.Th("Priority"),html.Th("Test"),html.Th("Product")]))
]

#=================================================
# Eng report page - Table 2 : Overall QA report
#=================================================
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

#=================================================
# Eng report page - Table 3 : Component Level Summary
#=================================================
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
t3r9 = html.Tr([html.Td("Total",id="Total"),html.Td(None, id="total_1_pass"),html.Td(None, id="total_1_fail"),html.Td(None, id="total_2_pass"),html.Td(None, id="total_2_fail")])

#=================================================
# Eng report page - Table 5 : Timing tables
#=================================================
# t5_caption = [
#     html.Caption(html.Tr([html.Th("Timing Summary (minutes)")])),
# ]
# t5_head = [
#     html.Thead(html.Tr([html.Th(" ", rowSpan=2),html.Th("Current Build",id='timing_build_current', colSpan=2),html.Th("Prev Build", colSpan=2,id= "timing_build_prev_2"),html.Th("Prev Build", colSpan=2,id= "timing_build_prev_3"),html.Th("Prev Build", colSpan=2,id= "timing_build_prev_4"),html.Th("Prev Build", colSpan=2,id= "timing_build_prev_5")])),
#     html.Thead(html.Tr([html.Th(" "),html.Th("Min"), html.Th("Max"),html.Th("Min"), html.Th("Max"),html.Th("Min"), html.Th("Max"),html.Th("Min"), html.Th("Max"),html.Th("Min"), html.Th("Max")]))
# ]
# t5r1 = html.Tr([html.Td("Update",id="update"),html.Td(None, id="update_min_1"),html.Td(None, id="update_max_1"),html.Td(None, id="update_min_2"),html.Td(None, id="update_max_2"),html.Td(None, id="update_min_3"),html.Td(None, id="update_max_3"),html.Td(None, id="update_min_4"),html.Td(None, id="update_max_4"),html.Td(None, id="update_min_5"),html.Td(None, id="update_max_5")])
# t5r2 = html.Tr([html.Td("Deployment",id="deploy"),html.Td(None, id="deploy_min_1"),html.Td(None, id="deploy_max_1"),html.Td(None, id="deploy_min_2"),html.Td(None, id="deploy_max_2"),html.Td(None, id="deploy_min_3"),html.Td(None, id="deploy_max_3"),html.Td(None, id="deploy_min_4"),html.Td(None, id="deploy_max_4"),html.Td(None, id="deploy_min_5"),html.Td(None, id="deploy_max_5")])
# t5r3 = html.Tr([html.Td("Boxing",id="box"),html.Td(None, id="box_min_1"),html.Td(None, id="box_max_1"),html.Td(None, id="box_min_2"),html.Td(None, id="box_max_2"),html.Td(None, id="box_min_3"),html.Td(None, id="box_max_3"),html.Td(None, id="box_min_4"),html.Td(None, id="box_max_4"),html.Td(None, id="box_min_5"),html.Td(None, id="box_max_5")])
# t5r4 = html.Tr([html.Td("Unboxing",id="unbox"),html.Td(None, id="unbox_min_1"),html.Td(None, id="unbox_max_1"),html.Td(None, id="unbox_min_2"),html.Td(None, id="unbox_max_2"),html.Td(None, id="unbox_min_3"),html.Td(None, id="unbox_max_3"),html.Td(None, id="unbox_min_4"),html.Td(None, id="unbox_max_4"),html.Td(None, id="unbox_min_5"),html.Td(None, id="unbox_max_5")])
# t5r5 = html.Tr([html.Td("Onboaring",id="onboard"),html.Td(None, id="onboard_min_1"),html.Td(None, id="onboard_max_1"),html.Td(None, id="onboard_min_2"),html.Td(None, id="onboard_max_2"),html.Td(None, id="onboard_min_3"),html.Td(None, id="onboard_max_3"),html.Td(None, id="onboard_min_4"),html.Td(None, id="onboard_max_4"),html.Td(None, id="onboard_min_5"),html.Td(None, id="onboard_max_5")])
# t5r6 = html.Tr([html.Td("Firmware Update",id="firm"),html.Td(None, id="firm_min_1"),html.Td(None, id="firm_max_1"),html.Td(None, id="firm_min_2"),html.Td(None, id="firm_max_2"),html.Td(None, id="firm_min_3"),html.Td(None, id="firm_max_3"),html.Td(None, id="firm_min_4"),html.Td(None, id="firm_max_4"),html.Td(None, id="firm_min_5"),html.Td(None, id="firm_max_5")])
# t5r7 = html.Tr([html.Td("Reboot Node",id="NReboot"),html.Td(None, id="NReboot_min_1"),html.Td(None, id="NReboot_max_1"),html.Td(None, id="NReboot_min_2"),html.Td(None, id="NReboot_max_2"),html.Td(None, id="NReboot_min_3"),html.Td(None, id="NReboot_max_3"),html.Td(None, id="NReboot_min_4"),html.Td(None, id="NReboot_max_4"),html.Td(None, id="NReboot_min_5"),html.Td(None, id="NReboot_max_5")])
# t5r8 = html.Tr([html.Td("Start Node",id="Nstart"),html.Td(None, id="Nstart_min_1"),html.Td(None, id="Nstart_max_1"),html.Td(None, id="Nstart_min_2"),html.Td(None, id="Nstart_max_2"),html.Td(None, id="Nstart_min_3"),html.Td(None, id="Nstart_max_3"),html.Td(None, id="Nstart_min_4"),html.Td(None, id="Nstart_max_4"),html.Td(None, id="Nstart_min_5"),html.Td(None, id="Nstart_max_5")])
# t5r9 = html.Tr([html.Td("Stop Node",id="Nstop"),html.Td(None, id="Nstop_min_1"),html.Td(None, id="Nstop_max_1"),html.Td(None, id="Nstop_min_2"),html.Td(None, id="Nstop_max_2"),html.Td(None, id="Nstop_min_3"),html.Td(None, id="Nstop_max_3"),html.Td(None, id="Nstop_min_4"),html.Td(None, id="Nstop_max_4"),html.Td(None, id="Nstop_min_5"),html.Td(None, id="Nstop_max_5")])
# t5r10 = html.Tr([html.Td("Node Failover",id="Nfail"),html.Td(None, id="Nfail_min_1"),html.Td(None, id="Nfail_max_1"),html.Td(None, id="Nfail_min_2"),html.Td(None, id="Nfail_max_2"),html.Td(None, id="Nfail_min_3"),html.Td(None, id="Nfail_max_3"),html.Td(None, id="Nfail_min_4"),html.Td(None, id="Nfail_max_4"),html.Td(None, id="Nfail_min_5"),html.Td(None, id="Nfail_max_5")])
# t5r11 = html.Tr([html.Td("Stop All Services",id="stopA"),html.Td(None, id="stopA_min_1"),html.Td(None, id="stopA_max_1"),html.Td(None, id="stopA_min_2"),html.Td(None, id="stopA_max_2"),html.Td(None, id="stopA_min_3"),html.Td(None, id="stopA_max_3"),html.Td(None, id="stopA_min_4"),html.Td(None, id="stopA_max_4"),html.Td(None, id="stopA_min_5"),html.Td(None, id="stopA_max_5")])
# t5r12 = html.Tr([html.Td("Start All Services",id="startA"),html.Td(None, id="startA_min_1"),html.Td(None, id="startA_max_1"),html.Td(None, id="startA_min_2"),html.Td(None, id="startA_max_2"),html.Td(None, id="startA_min_3"),html.Td(None, id="startA_max_3"),html.Td(None, id="startA_min_4"),html.Td(None, id="startA_max_4"),html.Td(None, id="startA_min_5"),html.Td(None, id="startA_max_5")])
# t5r13 = html.Tr([html.Td("Bucket Creation",id="bcre"),html.Td(None, id="bcre_min_1"),html.Td(None, id="bcre_max_1"),html.Td(None, id="bcre_min_2"),html.Td(None, id="bcre_max_2"),html.Td(None, id="bcre_min_3"),html.Td(None, id="bcre_max_3"),html.Td(None, id="bcre_min_4"),html.Td(None, id="bcre_max_4"),html.Td(None, id="bcre_min_5"),html.Td(None, id="bcre_max_5")])
# t5r14 = html.Tr([html.Td("Bucket Deletion",id="bdel"),html.Td(None, id="bdel_min_1"),html.Td(None, id="bdel_max_1"),html.Td(None, id="bdel_min_2"),html.Td(None, id="bdel_max_2"),html.Td(None, id="bdel_min_3"),html.Td(None, id="bdel_max_3"),html.Td(None, id="bdel_min_4"),html.Td(None, id="bdel_max_4"),html.Td(None, id="bdel_min_5"),html.Td(None, id="bdel_max_5")])

#=================================================
# perf Eng report page - Table 1 
#=================================================
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

#=================================================
# perf Eng report page - Table 2 
#=================================================
eng_perf2_caption = [
    html.Caption(html.Tr([html.Th("Metadata Latencies (captured with 1KB object)")])),
]
t21 = html.Tr([html.Td("Add / Edit Object Tags", id="puttag"),html.Td(None, id="puttag_value")])
t22 = html.Tr([html.Td("Read Object Tags", id="gettag"),html.Td(None, id="gettag_value")])
t23 = html.Tr([html.Td("Read Object Metadata", id="headobj"),html.Td(None, id="headobj_value")])

eng_perf2_head = [
    html.Thead(html.Tr([html.Th("Operation Latency (ms)"),html.Th("Response Time")]))
]

#=================================================
# perf Eng report page - Table 3 
#=================================================
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

### ======================================================


tab1_content = dbc.Card(
    dbc.CardBody(
        [
            html.P(html.U("Engineers Report"), style={'text-align':'center','font-size':'30px','font-weight': 'bold'}),
            html.P(html.H5("Product: ", id = "product_heading_eng"),className="card-text",),
            html.P(html.H5("Build: ", id = "build_heading_eng"),className="card-text",),
            html.P(html.H5("Date: ", id = "date_heading_eng"),className="card-text"),
            
            dbc.Table(t1_caption + t1_head + [html.Tbody([t1r1,t1r2,t1r3,t1r4,t1r5,t1r6])],
            className = "caption-Top col-xs-6",
            # dark=True,
            hover=True,
            responsive=True,
            striped=True,
            style = {'textAlign': 'center'},
            #bordered=True,
            id = "ET1",
            ),

            dbc.Table(t2_caption + t2_head + [html.Tbody([t2r1,t2r2,t2r3,t2r4,t2r5,t2r6])],
            className = "caption-Top col-xs-6",
            # dark=True,
            hover=True,
            responsive=True,
            striped=True,
            style = {'textAlign': 'center'},
            #bordered=True,
            id = "ET2",
            ),

            dbc.Table(t3_caption + t3_head + [html.Tbody([t3r1,t3r2,t3r3,t3r4,t3r5,t3r6,t3r7,t3r8,t3r9])],
            className = "caption-Top col-xs-6",
            hover=True,
            # dark=True,
            responsive=True,
            striped=True,
            style = {'textAlign': 'center'},
            #bordered=True,
            id = "ET3",
            ),

            # dbc.Table(t5_caption + t5_head + [html.Tbody([t5r1,t5r2,t5r3,t5r4,t5r5,t5r6,t5r7,t5r8,t5r9,t5r10,t5r11,t5r12,t5r13,t5r14])],
            # className = "caption-Top col-xs-6",
            # hover=True,
            # # dark=True,
            # responsive=True,
            # striped=True,
            # style = {'textAlign': 'center'},
            # #bordered=True,
            # id = "ET7",
            # ),

            dbc.Table(eng_perf1_caption + eng_perf1_head + [html.Tbody([eng_write_throughput, eng_read_throughput,
                eng_write_latency, eng_read_latency, eng_iops_write, eng_iops_read, eng_ttfb_write, eng_ttfb_read])],
            className = "caption-Top col-xs-6",
            # dark=True,
            hover=True,
            responsive=True,
            striped=True,
            style = {'textAlign': 'center'},
            #bordered=True,
            id = "ET4",
            ),

            dbc.Table(eng_perf2_caption + eng_perf2_head + [html.Tbody([t21, t22, t23])],
            className = "caption-Top col-xs-6",
            # dark=True,
            hover=True,
            responsive=True,
            striped=True,
            style = {'textAlign': 'center'},
            #bordered=True,
            id = "ET5",
            ),

            dbc.Table(eng_perf3_caption + eng_perf3_head + [html.Tbody([t31,t32,t33,t34,t35,t36,t37,t38,t39,t310,t311,t312,t313,t314,t315,
                t316,t317,t318,t319,t320,t321,t322,t323,t324,t325,t326,t327,t328,t329,t330,t331,t332,t333,t334,t335,t336])],
            className = "table-1",
            # dark=True,
            hover=True,
            responsive=True,
            striped=True,
            style = {'textAlign': 'center'},
            #bordered=True,
            id = "ET6",
            ),

            html.Th("Detailed Reported Bugs", id= 'detailed_report_header'),

            dbc.Row([dbc.Col(html.Div(id='build_report_div', className='text-center',
                                 style={'margin': 20, 'margin-top': 10, 'margin-bottom': 20}))])
        ]
    ),
    className="flex-sm-fill nav-link active",
)
##====================================================

#=================================================
# Exe report page - Table 1 : Reported Bugs
#=================================================
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
    html.Thead(html.Tr([html.Th("Priority"),html.Th("Test"),html.Th("Product")]))
]

#=================================================
# Exe report page - Table 2 : Overall QA report
#=================================================
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

#=================================================
# Exe report page - Table 3 : Feature breakdown summary
#=================================================
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

#=================================================
# Exe report page - Table 4 : Code maturity
#=================================================

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

#========================================================
# Perf Exe report page - Table 1 
#========================================================
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
### =====================================================
tab2_content = dbc.Card(
    dbc.CardBody(
        [
            html.P(html.U("Executive Report"), style={'text-align':'center','font-size':'30px','font-weight': 'bold'}),
            html.P(html.H5("Product: ", id = "product_heading_exe"),className="card-text",),
            html.P(html.H5("Build: ", id = "build_heading_exe"),className="card-text",),
            html.P(html.H5("Date: ", id = "date_heading_exe"),className="card-text",),
            
            dbc.Table(xt1_caption + xt1_head + [html.Tbody([xt1r1,xt1r2,xt1r3,xt1r4,xt1r5,xt1r6])],
            className = "caption-Top col-xs-6",
            # dark=True,
            hover=True,
            responsive=True,
            striped=True,
            style = {'textAlign': 'center'},
            #bordered=True,
            id = "XT1",
            ),

            dbc.Table(xt2_caption + xt2_head + [html.Tbody([xt2r1,xt2r2,xt2r3,xt2r4,xt2r5,xt2r6])],
            className = "caption-Top col-xs-6",
            # dark=True,
            hover=True,
            responsive=True,
            striped=True,
            style = {'textAlign': 'center'},
            #bordered=True,
            id = "XT2",
            ),

            dbc.Table(xt3_caption + xt3_head + [html.Tbody([xt3r1,xt3r2,xt3r3,xt3r4,xt3r6,xt3r7,xt3r8])], # ,xt3r5
            className = "caption-Top col-xs-6",
            hover=True,
            # dark=True,
            responsive=True,
            striped=True,
            style = {'textAlign': 'center'},
            #bordered=True,
            id = "XT3",
            ),

            dbc.Table(xt4_caption + xt4_head + [html.Tbody([xt4r1,xt4r2,xt4r3,xt4r4,xt4r5])],
            className = "caption-Top col-xs-6 table-1",
            hover=True,
            # dark=True,
            responsive=True,
            striped=True,
            style = {'textAlign': 'center'},
            #bordered=True,
            id = "XT4",
            ),

            dbc.Table(exe_perf_caption + exe_perf_head + [html.Tbody([write_throughput, read_throughput, write_latency, read_latency])],
            className = "caption-Top col-xs-6",
            # dark=True,
            hover=True,
            responsive=True,
            striped=True,
            style = {'textAlign': 'center'},
            #bordered=True,
            id = "XT5",
            ),

        ]
    ),
    className="flex-sm-fill nav-link",
)
### =====================================================

tabs = dbc.Tabs(
    [
        dbc.Tab(tab2_content, label="Executive Report", style={
                'margin-left': 20, 'margin-right': 20}, label_style={'font-size':'20px'}),
        dbc.Tab(tab1_content, label="Engineers Report", style={
                'margin-left': 20, 'margin-right': 20}, label_style={'font-size':'20px'}),
        
    ],
    className="nav nav nav-pills nav-fill nav-pills flex-column flex-sm-row",
    id = "tabs",
)

### =====================================================
# Build number input field on top

build_input_group = dbc.Row(
    dbc.Col(dbc.InputGroup([
        dbc.Input(id="table_build_input",
                  placeholder="Input build version", debounce=True),
        dbc.InputGroupAddon(
            dbc.Button("Get Build Report", id="table_submit_button", color="success"),
            addon_type="postpend",
        )], style={'margin': 10}),
        width=4),
    justify="center"
)

build_report_header = dbc.Jumbotron([html.H4(html.Em("... looking for build number!")),
                        html.P(html.H6("eg. for beta build enter 'cortx-1.0.0-33-rc12' and for release build enter '2715'."))
                        ],id="build_report_header",
                        style={'padding': '1em',
                                'background': 'transparent','text-align':'center'})

### =====================================================
# App configarations
### =====================================================

app.layout = html.Div([
    navbar,
    build_input_group,
    build_report_header,
    tabs,
    
    # represents the URL bar, doesn't render anything
    dcc.Location(id='url', refresh=False),
    toast,
    html.Link(
        rel='stylesheet',
        href='/static/topography.css'
    )]) 

### =====================================================
# call back for eng report aka first tab
def roundoff(x, base=25):
    if x <26:
        return (int(x))
    return (base * round(x/base))

def get_previous_build(current_build, version):
    cursor = mapi.find({'info' : 'build sequence'})
    current_index = 999999
    for doc in cursor:
        for i in range(0, len(doc[version])):
            if doc[version][i] == current_build:
                current_index = i
                break
    #print(doc[version][current_index - 1])
    if current_index > 0:  
        return doc[version][current_index - 1]
    else:
        return None

def get_input(ctx, clicks, input_value, enter_input, pathname):
    previous_exists = False
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
        current_build = input_value.lower()
    elif prop_id == 'table_build_input':
        if enter_input:            
            found_current = True
            current_build = enter_input.lower()
            
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
            current_build = build_number.lower()
        else:
            return [None, None, None]
    else:
        return [None, None, None]
    
    if current_build.lower().startswith("release"):
        version = 'release'
    else:
        try:
            _ = int(current_build)
            version = 'release'
        except:
            version = 'beta'
    #print(version)
    item = mapi.find({'info' : 'build sequence'})
    for doc in item:
        if current_build not in doc['beta'] and current_build not in doc['release']:
            return [None, None, None]
    if found_current:
        cursor1 = mapi.find({'info' : 'build sequence'})
        previous_exists = False
        current_index = 999999
        for doc in cursor1:            
            for i in range(0, len(doc[version])):
                if doc[version][i] == current_build:
                    current_index = i
                    break
            if current_index > 0:
                previous_exists = True
                #print(doc['beta'][current_index - 1])
            else:
                previous_exists = False
        if previous_exists:
            # current_build = doc['beta'][current_index])
            previous_build = doc[version][current_index - 1]
        else:
            previous_build = None

    if version == 'release' and not(current_build.startswith("release")):
        current_build = 'release_' + current_build
        previous_build = 'release_' + previous_build
    
    return [current_build, previous_build, version]
#=================================================
# Eng & Exe report page - Table 1 : Report bugs
#=================================================

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
    
    build, _, _ = get_input(dash.callback_context, clicks, input_value, enter_input, pathname)
    
    if build:
        try: 
            test_blocker_count = len(cftdbRead.results.distinct("defectID",{'build':build,'deleted':False, "testLabels" : 'EOS_TA', 'defectPriority' : 'Blocker','testResult':'FAIL'}))
        except:
            test_blocker_count = "-"
        try:
            test_critical_count = len(cftdbRead.results.distinct("defectID",{'build':build,'deleted':False, "testLabels" : 'EOS_TA', 'defectPriority' : 'Critical','testResult':'FAIL'}))
        except:
            test_critical_count = "-"
        try:
            test_major_count = len(cftdbRead.results.distinct("defectID",{'build':build,'deleted':False, "testLabels" : 'EOS_TA', 'defectPriority' : 'Major','testResult':'FAIL'}))
        except:
            test_major_count = "-"
        try:
            test_minor_count = len(cftdbRead.results.distinct("defectID",{'build':build,'deleted':False, "testLabels" : 'EOS_TA', 'defectPriority' : 'Minor','testResult':'FAIL'}))
        except:
            test_minor_count = "-"
        try:
            test_trivial_count = len(cftdbRead.results.distinct("defectID",{'build':build,'deleted':False, "testLabels" : 'EOS_TA', 'defectPriority' : 'Trivial','testResult':'FAIL'}))
        except:
            test_trivial_count = "-"
        try:
            product_blocker_count = len(cftdbRead.results.distinct("defectID",{'build':build,'deleted':False, 'defectPriority' : 'Blocker','testResult':'FAIL'}))
        except:
            product_blocker_count = "-"
        try:
            product_critical_count = len(cftdbRead.results.distinct("defectID",{'build':build,'deleted':False, 'defectPriority' : 'Critical','testResult':'FAIL'}))
        except:
            product_critical_count = "-"
        try:
            product_major_count = len(cftdbRead.results.distinct("defectID",{'build':build,'deleted':False, 'defectPriority' : 'Major','testResult':'FAIL'}))
        except:
            product_major_count = "-"
        try:
            product_minor_count = len(cftdbRead.results.distinct("defectID",{'build':build,'deleted':False, 'defectPriority' : 'Minor','testResult':'FAIL'}))
        except:
            product_minor_count = "-"
        try:
            product_trivial_count = len(cftdbRead.results.distinct("defectID",{'build':build,'deleted':False, 'defectPriority' : 'Trivial','testResult':'FAIL'}))
        except:
            product_trivial_count = "-"
        #test_total = mapi.count_documents({'build':build,'deleted':False, "testLabels" : 'EOS_TA'})
        
        try:
            product_total = 0
            cursor = mapi.find({'build':build,'deleted':False,'testResult':'FAIL'})
            product_defect_IDs = []
            for doc in cursor:
                if 'defectID' in doc.keys():
                    if doc['defectID'] not in product_defect_IDs:
                        product_total +=1
                        product_defect_IDs.append(doc['defectID'])
            
            cursor = mapi.find({'build':build,'deleted':False, "testLabels" : 'EOS_TA','testResult':'FAIL'})
            test_defect_IDs = []
        except:
            product_total = "-"
        try:
            test_total = 0
            for doc in cursor:
                if 'defectID' in doc.keys():
                    if doc['defectID'] not in test_defect_IDs:
                        test_total +=1
                        test_defect_IDs.append(doc['defectID'])  
        except:
            test_total = '-'    
        

        #print(product_blocker_count + product_critical_count + product_major_count + product_minor_count + product_trivial_count)
        return [test_blocker_count,test_critical_count,test_major_count,test_minor_count,test_trivial_count,product_blocker_count,\
            product_critical_count,product_major_count,product_minor_count,product_trivial_count,test_total,product_total,\
            test_blocker_count,test_critical_count,test_major_count,test_minor_count,test_trivial_count,product_blocker_count,\
            product_critical_count,product_major_count,product_minor_count,product_trivial_count,test_total,product_total]
    else:
        return [None] * 24

#=================================================
# Eng & Exe report page - Table 2 : Overall QA report
#=================================================
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

    build, pre_build, _ = get_input(dash.callback_context, clicks, input_value, enter_input, pathname)

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

#=================================================
# Eng report page - Table 3 : Component Level Summary
#=================================================
@app.callback([
    Output('S3_1_pass', 'children'), Output('S3_1_fail', 'children'),Output('provision_1_pass', 'children'), Output('provision_1_fail', 'children'),Output('csm_1_pass', 'children'), 
    Output('csm_1_fail', 'children'), Output('sspl_1_pass', 'children'), Output('sspl_1_fail', 'children'), Output('motr_1_pass', 'children'), Output('motr_1_fail', 'children'),
    Output('ha_1_pass', 'children'), Output('ha_1_fail', 'children'), Output('loc_1_pass', 'children'), Output('loc_1_fail', 'children'),Output('cos_1_pass', 'children'), 
    Output('cos_1_fail', 'children'), Output('total_1_pass', 'children'), Output('total_1_fail', 'children'),
    
    Output('S3_2_pass', 'children'), Output('S3_2_fail', 'children'),Output('provision_2_pass', 'children'), Output('provision_2_fail', 'children'),
    Output('csm_2_pass', 'children'), Output('csm_2_fail', 'children'),Output('sspl_2_pass', 'children'), Output('sspl_2_fail', 'children'),
    Output('motr_2_pass', 'children'), Output('motr_2_fail', 'children'),Output('ha_2_pass', 'children'), Output('ha_2_fail', 'children'),
    Output('loc_2_pass', 'children'), Output('loc_2_fail', 'children'),Output('cos_2_pass', 'children'), Output('cos_2_fail', 'children'),
    Output('total_2_pass', 'children'), Output('total_2_fail', 'children'), #36 T3
    ],
    [Input('table_submit_button', 'n_clicks'),
    dash.dependencies.Input('url', 'pathname'),
    Input('table_build_input', 'value')],
    [State('table_build_input', 'value')],
    )
def update_eng_table_3(clicks, pathname, input_value, enter_input):
    build, pre_build, _ = get_input(dash.callback_context, clicks, input_value, enter_input, pathname)

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
    if build:
        try:
            cursor = mapi.find({'build':build,'deleted':False})
        except:
            return ['-'] * 36

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
                        #print(doc['testID'])
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
                            #print(doc['testID'])
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
                pre_current_total_pass = mapi.count_documents({'build':pre_build,'deleted':False,"testResult" : 'PASS'})
                pre_current_total_fail = mapi.count_documents({'build':pre_build,'deleted':False,"testResult" : 'FAIL'})
            except:
                pre_current_total_pass = "-"
                pre_current_total_fail = "-"

        return [S3_count_pass,S3_count_fail,pro_count_pass,pro_count_fail,csm_count_pass,csm_count_fail,ras_count_pass,ras_count_fail,\
            motr_count_pass,motr_count_fail,HA_count_pass,HA_count_fail,loc_count_pass,loc_count_fail,cos_count_pass,cos_count_fail,current_total_pass,current_total_fail,\
            pre_S3_count_pass,pre_S3_count_fail,pre_pro_count_pass,pre_pro_count_fail,pre_csm_count_pass,pre_csm_count_fail,pre_ras_count_pass,pre_ras_count_fail,\
            pre_motr_count_pass,pre_motr_count_fail,pre_HA_count_pass,pre_HA_count_fail,pre_loc_count_pass,pre_loc_count_fail,pre_cos_count_pass,pre_cos_count_fail,pre_current_total_pass,pre_current_total_fail]
    
    return [None] * 36

#=================================================
# Eng report page - Table 4 : Detailed report
#=================================================
@app.callback([Output('build_report_div','children')],
    [Input('table_submit_button', 'n_clicks'),
        dash.dependencies.Input('url', 'pathname'),
        Input('table_build_input', 'value')],
        [State('table_build_input', 'value')],
)
def update_eng_table_4(clicks, pathname, input_value, enter_input):
    build, _, _ = get_input(dash.callback_context, clicks, input_value, enter_input, pathname)
    while build:
        try:
            defectsList = cftdbRead.results.distinct("defectID",{'build':build,'deleted':False,'testResult':'FAIL'})
            if len(defectsList) == 0:
                return ["No Bugs."]
            data = []
            for defect in defectsList:
                result = cftdbRead.results.find({'build':build,'deleted':False,'defectID':defect})
                data.append(result[0])

            df = pd.DataFrame(list(data))
            df.drop(columns=['_id','testPlanID','build','testExecution','testLabels','feature','testResult','dateOfExecution','defectLabels',],inplace=True)
            detailed_report = dash_table.DataTable(
    
                id="detailed_report_table",
                columns = [{'name':'Component','id':'testExecutionLabels'},{'name':'Test ID','id':'testID'},{'name':'Priority','id':'defectPriority'},
                        {'name':'JIRA ID','id':'defectID'}, {'name':'Description','id':'defectSummary'}],
                data=df.to_dict('records'),
                sort_action="native",
                page_size=15,
                style_cell={'padding': '5px', 'fontSize': 18,'background-color' : '#E0E0E0',
                            'font-family': 'sans-serif','text-align':'center'},
                style_header={
                    'backgroundColor': '#7F8C8D',
                    'fontWeight': 'bold',
                    'textAlign': 'center'
                },
                style_data_conditional=[
                # {
                #     'if': {'column_id': 'testID'},
                #     'backgroundColor': 'rgb(174, 214, 241)'#D1F2EB
                # },
                # {
                #     'if': {'column_id': 'defectPriority'},
                #     'backgroundColor': 'rgb(241, 148, 138)'#FAD7A0
                # },
                # {
                #     'if': {'column_id': 'defectID'},
                #     'backgroundColor': 'rgb(162, 217, 206)'#E6B0AA
                # },
                {
                    'if': {'column_id': 'defectSummary'},
                    'backgroundColor': '#FFFFFF',
                    'text-align':'left'
                },
                {
                'if': {
                        'column_id': 'defectPriority',
                        'filter_query': '{{defectPriority}} = {}'.format("Blocker"),
                    },
                        # 'backgroundColor': "#F1948A",
                        'color' : '#ff6262',
                },
                {
                'if': {
                        'column_id': 'defectPriority',
                        'filter_query': '{{defectPriority}} = {}'.format("Critical"),                        
                    },
                        # 'backgroundColor': "#D35400",
                        'color'  :'#DC7633',
                },
                {
                'if': {
                        'column_id': 'defectPriority',
                        'filter_query': '{{defectPriority}} = {}'.format("Major"),                        
                    },
                        #'backgroundColor': "#5DADE2",
                        'color' : '#504de4',
                },
                {
                'if': {
                        'column_id': 'defectPriority',
                        'filter_query': '{{defectPriority}} = {}'.format("Minor"),
                    },
                        # 'backgroundColor': "#CDED94",
                        'color' : '#343a40',
                },
                {
                'if': {
                        'column_id': 'defectPriority',
                        'filter_query': '{{defectPriority}} = {}'.format("Trivial"),                        
                    },
                        # 'backgroundColor': "#76D7C4",
                        'color' : '#3cba3c',
                },
                
            ],
            )
            return [detailed_report]
        except:
            return [None]
    return [None]
### =====================================================
# call back for exe report aka second tab
#=================================================
# Exe report page - Table 3 : Feature breakdown summary
#=================================================
def get_percent(outof, value):
    if not (outof):
        return "NA"
    return roundoff(value * 100 / outof, 2)

@app.callback([
    Output('user_op_total', 'children'),Output('user_op_pass', 'children'),Output('user_op_fail', 'children'),Output('user_op_ppass', 'children'),Output('user_op_pfail', 'children'),
    Output('scale_total', 'children'),Output('scale_pass', 'children'),Output('scale_fail', 'children'),Output('scale_ppass', 'children'),Output('scale_pfail', 'children'),
    Output('avail_total', 'children'),Output('avail_pass', 'children'),Output('avail_fail', 'children'),Output('avail_ppass', 'children'),Output('avail_pfail', 'children'),
    Output('long_total', 'children'),Output('long_pass', 'children'),Output('long_fail', 'children'),Output('long_ppass', 'children'),Output('long_pfail', 'children'),
    #Output('perf_total', 'children'),Output('perf_pass', 'children'),Output('perf_fail', 'children'),Output('perf_ppass', 'children'),Output('perf_pfail', 'children'),
    Output('ucases_total', 'children'),Output('ucases_pass', 'children'),Output('ucases_fail', 'children'),Output('ucases_ppass', 'children'),Output('ucases_pfail', 'children'),
    Output('orphans_total', 'children'),Output('orphans_pass', 'children'),Output('orphans_fail', 'children'),Output('orphans_ppass', 'children'),Output('orphans_pfail', 'children'),
    Output('xtotal_total', 'children'),Output('xtotal_pass', 'children'),Output('xtotal_fail', 'children'),Output('xtotal_ppass', 'children'),Output('xtotal_pfail', 'children')],  #47 T3
    [Input('table_submit_button', 'n_clicks'),
    dash.dependencies.Input('url', 'pathname'),
    Input('table_build_input', 'value')],
    [State('table_build_input', 'value')],)
def update_exe_table_3(clicks, pathname, input_value, enter_input):
    build, _, _ = get_input(dash.callback_context, clicks, input_value, enter_input, pathname)
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
        # try:
        #     perf_count_p = mapi.count_documents({'build': build,'deleted':False, 'feature': 'Performance', 'testResult':'PASS'})
        # except:
        #     perf_count_p = "-"
        # try:
        #     perf_count_f = mapi.count_documents({'build': build,'deleted':False, 'feature': 'Performance', 'testResult':'FAIL'})
        # except:
        #     perf_count_f = "-"
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
        # try:
        #     p_total = perf_count_p + perf_count_f
        # except:
        #     p_total = "-"
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
#=================================================
# Exe report page - Table 4 : Code maturity
#=================================================
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
    build, pre_build, version = get_input(dash.callback_context, clicks, input_value, enter_input, pathname)
  
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
            # data.extend([None]*15)
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
            # data.extend([None]*15)
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
    # except:
    #     return [None] * 20

#=================================================
# rest of the table
#=================================================
@app.callback([
    Output('component_build_current','children'),
    Output('code_maturity_build_current','children'),
    Output('product_heading_eng','children'),
    Output('product_heading_exe','children'),
    Output('build_heading_eng','children'),
    Output('build_heading_exe','children'),
    Output('date_heading_eng','children'),
    Output('date_heading_exe','children'),
    Output('component_previous','children'),
    Output('build_report_header','children'),
    Output('qa_current_eng','children'),
    Output('qa_previous_eng','children'),
    Output('qa_current_exe','children'),
    Output('qa_previous_exe','children'),

    ],
    [Input('table_submit_button', 'n_clicks'),
    dash.dependencies.Input('url', 'pathname'),
    Input('table_build_input', 'value')],
    [State('table_build_input', 'value')],
)
def update_rest(clicks, pathname, input_value, enter_input):
    build, pre_build, _ = get_input(dash.callback_context, clicks, input_value, enter_input, pathname)
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
        #print(build)
        try:
            date = cftdbRead.results.find({'build':build,'deleted':False}).sort([("dateOfExecution" , 1)]).limit(1)
            date1 = date[0]['dateOfExecution'].split("T")[0] + date[0]['dateOfExecution'][19::]
            date_field = html.H5("Date: {}".format(date1))
        except:
            date_field = html.H5("Date: -")

        return [build.capitalize(), build.capitalize(),html.H5("Product: Lyve Drive Rack"),html.H5("Product: Lyve Drive Rack"),html.H5("Build: {}".format(build.capitalize())), \
            html.H5("Build: {}".format(build.capitalize())),date_field,date_field,pre_name.capitalize(),html.H4(html.Em("Report for Build {}".format(build.capitalize()))),build_name,pre_name,build_name,pre_name] 
    
    heading = [html.H4(html.Em("... looking for build number!")), html.P(html.H6("eg. for beta build enter 'cortx-1.0.0-33-rc12' and for release build enter '2715'."))]
    return ["Current Build","Current Build",html.H5("Product: "),html.H5("Product: "),html.H5("Build: "),html.H5("Build: "),\
            html.H5("Date: "),html.H5("Date: "),pre_name,heading,build_name,pre_name,build_name,pre_name] 
    


#=================================================
# Perf call backs - eng table 1 and exe 
#=================================================
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
    build, _, _ = get_input(dash.callback_context, clicks, input_value, enter_input, pathname)
    #'Build':build,
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

#=================================================
# Perf call backs - eng table 2 
#=================================================
@app.callback([Output('puttag_value','children'),Output('gettag_value','children'),
    Output('headobj_value','children'),],
    [Input('table_submit_button', 'n_clicks'),
    dash.dependencies.Input('url', 'pathname'),
    Input('table_build_input', 'value')],
    [State('table_build_input', 'value')],
)
def update_perf2(clicks, pathname, input_value, enter_input):
    build, _, _ = get_input(dash.callback_context, clicks, input_value, enter_input, pathname)
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

#=================================================
# Perf call backs - eng table 3 Hsbench
#=================================================
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
    build, _, _ = get_input(dash.callback_context, clicks, input_value, enter_input, pathname)
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

#=================================================
# Perf call backs - eng table 4 Hsbench
#=================================================
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
    build, _, _ = get_input(dash.callback_context, clicks, input_value, enter_input, pathname)
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
#=================================================
# Perf call backs - eng table 5 Hsbench
#=================================================
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
    build, _, _ = get_input(dash.callback_context, clicks, input_value, enter_input, pathname)
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

#=================================================
# Perf call backs - eng table 6 Cosbench
#=================================================
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
    build, _, _ = get_input(dash.callback_context, clicks, input_value, enter_input, pathname)
    if build:
        try:
            COS1 = perfDb.results.find({'Build':build,'Name': 'Cosbench','Operation':'write','Object_Size':'4 KB','Buckets':1,'Objects':1000,'Sessions':100}) 
            WTH41 = roundoff(COS1[0]['Throughput']*4)
            WL41 = roundoff(COS1[0]['Latency']['Avg'])
            WIOPS41 = roundoff(COS1[0]['Throughput'])
        except:
            WTH41 = "-"
            WL41 = '-'
            WIOPS41 = '-'
        try:
            COS1 = perfDb.results.find({'Build':build,'Name': 'Cosbench','Operation':'read','Object_Size':'4 KB','Buckets':1,'Objects':1000,'Sessions':100}) 
            RTH41 = roundoff(COS1[0]['Throughput']*0.004)
            RL41 = roundoff(COS1[0]['Latency']['Avg'])
            RIOPS41 = roundoff(COS1[0]['Throughput'])  
        except:
            RTH41 = "-"
            RL41 = '-'
            RIOPS41 = '-'
        try:
            COS1 = perfDb.results.find({'Build':build,'Name': 'Cosbench','Operation':'write','Object_Size':'100 KB','Buckets':1,'Objects':1000,'Sessions':100}) 
            WTH1001 = roundoff(COS1[0]['Throughput']*0.1)
            WL1001 = roundoff(COS1[0]['Latency']['Avg'])
            WIOPS1001 = roundoff(COS1[0]['Throughput']) 
        except:
            WTH1001 = "-"
            WL1001 = '-'
            WIOPS1001 = '-'
        try:
            COS1 = perfDb.results.find({'Build':build,'Name': 'Cosbench','Operation':'read','Object_Size':'100 KB','Buckets':1,'Objects':1000,'Sessions':100}) 
            RTH1001 = roundoff(COS1[0]['Throughput']*0.1)
            RL1001 = roundoff(COS1[0]['Latency']['Avg'])
            RIOPS1001 = roundoff(COS1[0]['Throughput'])  
        except:
            RTH1001 = "-"
            RL1001 = '-'
            RIOPS1001 = '-'
        try:
            COS1 = perfDb.results.find({'Build':build,'Name': 'Cosbench','Operation':'write','Object_Size':'1 MB','Buckets':1,'Objects':1000,'Sessions':100}) 
            WTH11 = roundoff(COS1[0]['Throughput'])
            WL11 = roundoff(COS1[0]['Latency']['Avg'])
            WIOPS11 = roundoff(COS1[0]['Throughput'])  
        except:
            WTH11 = "-"
            WL11 = '-'
            WIOPS11 = '-'
        try:
            COS1 = perfDb.results.find({'Build':build,'Name': 'Cosbench','Operation':'read','Object_Size':'1 MB','Buckets':1,'Objects':1000,'Sessions':100}) 
            RTH11 = roundoff(COS1[0]['Throughput'])
            RL11 = roundoff(COS1[0]['Latency']['Avg'])
            RIOPS11 = roundoff(COS1[0]['Throughput'])   
        except:
            RTH11 = "-"
            RL11 = '-'
            RIOPS11 = '-'
        try:
            COS1 = perfDb.results.find({'Build':build,'Name': 'Cosbench','Operation':'write','Object_Size':'5 MB','Buckets':1,'Objects':1000,'Sessions':100}) 
            WTH51 = roundoff(COS1[0]['Throughput']*5)
            WL51 = roundoff(COS1[0]['Latency']['Avg'])
            WIOPS51 =roundoff(COS1[0]['Throughput'])   
        except:
            WTH51 = "-"
            WL51 = '-'
            WIOPS51 = '-'
        try:
            COS1 = perfDb.results.find({'Build':build,'Name': 'Cosbench','Operation':'read','Object_Size':'5 MB','Buckets':1,'Objects':1000,'Sessions':100}) 
            RTH51 = roundoff(COS1[0]['Throughput']*5)
            RL51 = roundoff(COS1[0]['Latency']['Avg'])
            RIOPS51 =roundoff( COS1[0]['Throughput'])   
        except:
            RTH51 = "-"
            RL51 = '-'
            RIOPS51 = '-'
        try:
            COS1 = perfDb.results.find({'Build':build,'Name': 'Cosbench','Operation':'write','Object_Size':'36 MB','Buckets':1,'Objects':1000,'Sessions':100}) 
            WTH361 =roundoff( COS1[0]['Throughput']*36)
            WL361 = roundoff(COS1[0]['Latency']['Avg'])
            WIOPS361 = roundoff(COS1[0]['Throughput']) 
        except:
            WTH361 = "-"
            WL361 = '-'
            WIOPS361 = '-'
        try:
            COS1 = perfDb.results.find({'Build':build,'Name': 'Cosbench','Operation':'read','Object_Size':'36 MB','Buckets':1,'Objects':1000,'Sessions':100}) 
            RTH361 = roundoff(COS1[0]['Throughput']*36)
            RL361 =roundoff( COS1[0]['Latency']['Avg'])
            RIOPS361 = roundoff(COS1[0]['Throughput'])   
        except:
            RTH361 = "-"
            RL361 = '-'
            RIOPS361 = '-'
        try:
            COS1 = perfDb.results.find({'Build':build,'Name': 'Cosbench','Operation':'write','Object_Size':'64 MB','Buckets':1,'Objects':1000,'Sessions':100}) 
            WTH641 = roundoff(COS1[0]['Throughput']*64)
            WL641 = roundoff(COS1[0]['Latency']['Avg'])
            WIOPS641 = roundoff(COS1[0]['Throughput'])   
        except:
            WTH641 = "-"
            WL641 = '-'
            WIOPS641 = '-'
        try:
            COS1 = perfDb.results.find({'Build':build,'Name': 'Cosbench','Operation':'read','Object_Size':'64 MB','Buckets':1,'Objects':1000,'Sessions':100}) 
            RTH641 = roundoff(COS1[0]['Throughput']*64)
            RL641 = roundoff(COS1[0]['Latency']['Avg'])
            RIOPS641 = roundoff(COS1[0]['Throughput'])   
        except:
            RTH641 = "-"
            RL641 = '-'
            RIOPS641 = '-'
        try:
            COS1 = perfDb.results.find({'Build':build,'Name': 'Cosbench','Operation':'write','Object_Size':'128 MB','Buckets':1,'Objects':1000,'Sessions':100}) 
            WTH1281 = roundoff(COS1[0]['Throughput']*128)
            WL1281 = roundoff(COS1[0]['Latency']['Avg'])
            WIOPS1281 = roundoff(COS1[0]['Throughput'])   
        except:
            WTH1281 = "-"
            WL1281 = '-'
            WIOPS1281 = '-'
        try:
            COS1 = perfDb.results.find({'Build':build,'Name': 'Cosbench','Operation':'read','Object_Size':'128 MB','Buckets':1,'Objects':1000,'Sessions':100}) 
            RTH1281 = roundoff(COS1[0]['Throughput']*128)
            RL1281 = roundoff(COS1[0]['Latency']['Avg'])
            RIOPS1281 = roundoff(COS1[0]['Throughput'])   
        except:
            RTH1281 = "-"
            RL1281 = '-'
            RIOPS1281 = '-'
        try:
            COS1 = perfDb.results.find({'Build':build,'Name': 'Cosbench','Operation':'write','Object_Size':'256 MB','Buckets':1,'Objects':1000,'Sessions':100}) 
            WTH2561 = roundoff(COS1[0]['Throughput']*256)
            WL2561 = roundoff(COS1[0]['Latency']['Avg'])
            WIOPS2561 = roundoff(COS1[0]['Throughput'])   
        except:
            WTH2561 = "-"
            WL2561 = '-'
            WIOPS2561 = '-'
        try:
            COS1 = perfDb.results.find({'Build':build,'Name': 'Cosbench','Operation':'read','Object_Size':'256 MB','Buckets':1,'Objects':1000,'Sessions':100}) 
            RTH2561 = roundoff(COS1[0]['Throughput']*256)
            RL2561 = roundoff(COS1[0]['Latency']['Avg'])
            RIOPS2561 = roundoff(COS1[0]['Throughput'])   
        except:
            RTH2561 = "-"
            RL2561 = '-'
            RIOPS2561 = '-'
        return [WTH41,WTH1001,WTH11,WTH51,WTH361,WTH641,WTH1281,WTH2561,RTH41,RTH1001,RTH11,RTH51,RTH361,RTH641,RTH1281,RTH2561,\
            WL41,WL1001,WL11,WL51,WL361,WL641,WL1281,WL2561,RL41,RL1001,RL11,RL51,RL361,RL641,RL1281,RL2561,WIOPS41,WIOPS1001,WIOPS11,\
                WIOPS51,WIOPS361,WIOPS641,WIOPS1281,WIOPS2561,RIOPS41,RIOPS1001,RIOPS11,RIOPS51,RIOPS361,RIOPS641,RIOPS1281,RIOPS2561]
    
    return [None] * 48

#=================================================
# Perf call backs - eng table 7 Cosbench
#=================================================
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
    build, _, _ = get_input(dash.callback_context, clicks, input_value, enter_input, pathname)
    if build:
        try:
            COS2 = perfDb.results.find({'Build':build,'Name': 'Cosbench','Operation':'write','Object_Size':'4 KB','Buckets':10,'Objects':100,'Sessions':100}) 
            WTH41 = roundoff(COS2[0]['Throughput']*0.004)
            WL41 = roundoff(COS2[0]['Latency']['Avg'])
            WIOPS41 = roundoff(COS2[0]['Throughput'])
        except:
            WTH41 = "-"
            WL41 = '-'
            WIOPS41 = '-'
        try:
            COS2 = perfDb.results.find({'Build':build,'Name': 'Cosbench','Operation':'read','Object_Size':'4 KB','Buckets':10,'Objects':100,'Sessions':100}) 
            RTH41 = roundoff(COS2[0]['Throughput']*0.004)
            RL41 = roundoff(COS2[0]['Latency']['Avg'])
            RIOPS41 = roundoff(COS2[0]['Throughput'])  
        except:
            RTH41 = "-"
            RL41 = '-'
            RIOPS41 = '-'
        try:
            COS2 = perfDb.results.find({'Build':build,'Name': 'Cosbench','Operation':'write','Object_Size':'100 KB','Buckets':10,'Objects':100,'Sessions':100}) 
            WTH1001 = roundoff(COS2[0]['Throughput']*0.1)
            WL1001 = roundoff(COS2[0]['Latency']['Avg'])
            WIOPS1001 = roundoff(COS2[0]['Throughput']) 
        except:
            WTH1001 = "-"
            WL1001 = '-'
            WIOPS1001 = '-'
        try:
            COS2 = perfDb.results.find({'Build':build,'Name': 'Cosbench','Operation':'read','Object_Size':'100 KB','Buckets':10,'Objects':100,'Sessions':100}) 
            RTH1001 = roundoff(COS2[0]['Throughput']*0.1)
            RL1001 = roundoff(COS2[0]['Latency']['Avg'])
            RIOPS1001 = roundoff(COS2[0]['Throughput'])  
        except:
            RTH1001 = "-"
            RL1001 = '-'
            RIOPS1001 = '-'
        try:
            COS2 = perfDb.results.find({'Build':build,'Name': 'Cosbench','Operation':'write','Object_Size':'1 MB','Buckets':10,'Objects':100,'Sessions':100}) 
            WTH11 = roundoff(COS2[0]['Throughput'])
            WL11 = roundoff(COS2[0]['Latency']['Avg'])
            WIOPS11 = roundoff(COS2[0]['Throughput'])  
        except:
            WTH11 = "-"
            WL11 = '-'
            WIOPS11 = '-'
        try:
            COS2 = perfDb.results.find({'Build':build,'Name': 'Cosbench','Operation':'read','Object_Size':'1 MB','Buckets':10,'Objects':100,'Sessions':100}) 
            RTH11 = roundoff(COS2[0]['Throughput'])
            RL11 = roundoff(COS2[0]['Latency']['Avg'])
            RIOPS11 = roundoff(COS2[0]['Throughput'])   
        except:
            RTH11 = "-"
            RL11 = '-'
            RIOPS11 = '-'
        try:
            COS2 = perfDb.results.find({'Build':build,'Name': 'Cosbench','Operation':'write','Object_Size':'5 MB','Buckets':10,'Objects':100,'Sessions':100}) 
            WTH51 = roundoff(COS2[0]['Throughput']*5)
            WL51 = roundoff(COS2[0]['Latency']['Avg'])
            WIOPS51 =roundoff(COS2[0]['Throughput'])   
        except:
            WTH51 = "-"
            WL51 = '-'
            WIOPS51 = '-'
        try:
            COS2 = perfDb.results.find({'Build':build,'Name': 'Cosbench','Operation':'read','Object_Size':'5 MB','Buckets':10,'Objects':100,'Sessions':100}) 
            RTH51 = roundoff(COS2[0]['Throughput']*5)
            RL51 = roundoff(COS2[0]['Latency']['Avg'])
            RIOPS51 =roundoff( COS2[0]['Throughput'])   
        except:
            RTH51 = "-"
            RL51 = '-'
            RIOPS51 = '-'
        try:
            COS2 = perfDb.results.find({'Build':build,'Name': 'Cosbench','Operation':'write','Object_Size':'36 MB','Buckets':10,'Objects':100,'Sessions':100}) 
            WTH361 =roundoff( COS2[0]['Throughput']*36)
            WL361 = roundoff(COS2[0]['Latency']['Avg'])
            WIOPS361 = roundoff(COS2[0]['Throughput']) 
        except:
            WTH361 = "-"
            WL361 = '-'
            WIOPS361 = '-'
        try:
            COS2 = perfDb.results.find({'Build':build,'Name': 'Cosbench','Operation':'read','Object_Size':'36 MB','Buckets':10,'Objects':100,'Sessions':100}) 
            RTH361 = roundoff(COS2[0]['Throughput']*36)
            RL361 =roundoff( COS2[0]['Latency']['Avg'])
            RIOPS361 = roundoff(COS2[0]['Throughput'])   
        except:
            RTH361 = "-"
            RL361 = '-'
            RIOPS361 = '-'
        try:
            COS2 = perfDb.results.find({'Build':build,'Name': 'Cosbench','Operation':'write','Object_Size':'64 MB','Buckets':10,'Objects':100,'Sessions':100}) 
            WTH641 = roundoff(COS2[0]['Throughput']*64)
            WL641 = roundoff(COS2[0]['Latency']['Avg'])
            WIOPS641 = roundoff(COS2[0]['Throughput'])   
        except:
            WTH641 = "-"
            WL641 = '-'
            WIOPS641 = '-'
        try:
            COS2 = perfDb.results.find({'Build':build,'Name': 'Cosbench','Operation':'read','Object_Size':'64 MB','Buckets':10,'Objects':100,'Sessions':100}) 
            RTH641 = roundoff(COS2[0]['Throughput']*64)
            RL641 = roundoff(COS2[0]['Latency']['Avg'])
            RIOPS641 = roundoff(COS2[0]['Throughput'])   
        except:
            RTH641 = "-"
            RL641 = '-'
            RIOPS641 = '-'
        try:
            COS2 = perfDb.results.find({'Build':build,'Name': 'Cosbench','Operation':'write','Object_Size':'128 MB','Buckets':10,'Objects':100,'Sessions':100}) 
            WTH1281 = roundoff(COS2[0]['Throughput']*128)
            WL1281 = roundoff(COS2[0]['Latency']['Avg'])
            WIOPS1281 = roundoff(COS2[0]['Throughput'])   
        except:
            WTH1281 = "-"
            WL1281 = '-'
            WIOPS1281 = '-'
        try:
            COS2 = perfDb.results.find({'Build':build,'Name': 'Cosbench','Operation':'read','Object_Size':'128 MB','Buckets':10,'Objects':100,'Sessions':100}) 
            RTH1281 = roundoff(COS2[0]['Throughput']*128)
            RL1281 = roundoff(COS2[0]['Latency']['Avg'])
            RIOPS1281 = roundoff(COS2[0]['Throughput'])   
        except:
            RTH1281 = "-"
            RL1281 = '-'
            RIOPS1281 = '-'
        try:
            COS2 = perfDb.results.find({'Build':build,'Name': 'Cosbench','Operation':'write','Object_Size':'256 MB','Buckets':10,'Objects':100,'Sessions':100}) 
            WTH2561 = roundoff(COS2[0]['Throughput']*256)
            WL2561 = roundoff(COS2[0]['Latency']['Avg'])
            WIOPS2561 = roundoff(COS2[0]['Throughput'])   
        except:
            WTH2561 = "-"
            WL2561 = '-'
            WIOPS2561 = '-'
        try:
            COS2 = perfDb.results.find({'Build':build,'Name': 'Cosbench','Operation':'read','Object_Size':'256 MB','Buckets':10,'Objects':100,'Sessions':100}) 
            RTH2561 = roundoff(COS2[0]['Throughput']*256)
            RL2561 = roundoff(COS2[0]['Latency']['Avg'])
            RIOPS2561 = roundoff(COS2[0]['Throughput'])   
        except:
            RTH2561 = "-"
            RL2561 = '-'
            RIOPS2561 = '-'
        return [WTH41,WTH1001,WTH11,WTH51,WTH361,WTH641,WTH1281,WTH2561,RTH41,RTH1001,RTH11,RTH51,RTH361,RTH641,RTH1281,RTH2561,\
            WL41,WL1001,WL11,WL51,WL361,WL641,WL1281,WL2561,RL41,RL1001,RL11,RL51,RL361,RL641,RL1281,RL2561,WIOPS41,WIOPS1001,WIOPS11,\
                WIOPS51,WIOPS361,WIOPS641,WIOPS1281,WIOPS2561,RIOPS41,RIOPS1001,RIOPS11,RIOPS51,RIOPS361,RIOPS641,RIOPS1281,RIOPS2561]
    
    return [None] * 48
#=================================================
# Perf call backs - eng table 8 Cosbench
#=================================================
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
    build, _, _ = get_input(dash.callback_context, clicks, input_value, enter_input, pathname)
    if build:
        try:
            COS3 = perfDb.results.find({'Build':build,'Name': 'Cosbench','Operation':'write','Object_Size':'4 KB','Buckets':50,'Objects':100,'Sessions':100}) 
            WTH41 = roundoff(COS3[0]['Throughput']*0.004)
            WL41 = roundoff(COS3[0]['Latency']['Avg'])
            WIOPS41 = roundoff(COS3[0]['Throughput'])
        except:
            WTH41 = "-"
            WL41 = '-'
            WIOPS41 = '-'
        try:
            COS3 = perfDb.results.find({'Build':build,'Name': 'Cosbench','Operation':'read','Object_Size':'4 KB','Buckets':50,'Objects':100,'Sessions':100}) 
            RTH41 = roundoff(COS3[0]['Throughput']*0.004)
            RL41 = roundoff(COS3[0]['Latency']['Avg'])
            RIOPS41 = roundoff(COS3[0]['Throughput'])  
        except:
            RTH41 = "-"
            RL41 = '-'
            RIOPS41 = '-'
        try:
            COS3 = perfDb.results.find({'Build':build,'Name': 'Cosbench','Operation':'write','Object_Size':'100 KB','Buckets':50,'Objects':100,'Sessions':100}) 
            WTH1001 = roundoff(COS3[0]['Throughput']*0.1)
            WL1001 = roundoff(COS3[0]['Latency']['Avg'])
            WIOPS1001 = roundoff(COS3[0]['Throughput']) 
        except:
            WTH1001 = "-"
            WL1001 = '-'
            WIOPS1001 = '-'
        try:
            COS3 = perfDb.results.find({'Build':build,'Name': 'Cosbench','Operation':'read','Object_Size':'100 KB','Buckets':50,'Objects':100,'Sessions':100}) 
            RTH1001 = roundoff(COS3[0]['Throughput']*0.1)
            RL1001 = roundoff(COS3[0]['Latency']['Avg'])
            RIOPS1001 = roundoff(COS3[0]['Throughput'])  
        except:
            RTH1001 = "-"
            RL1001 = '-'
            RIOPS1001 = '-'
        try:
            COS3 = perfDb.results.find({'Build':build,'Name': 'Cosbench','Operation':'write','Object_Size':'1 MB','Buckets':50,'Objects':100,'Sessions':100}) 
            WTH11 = roundoff(COS3[0]['Throughput'])
            WL11 = roundoff(COS3[0]['Latency']['Avg'])
            WIOPS11 = roundoff(COS3[0]['Throughput'])  
        except:
            WTH11 = "-"
            WL11 = '-'
            WIOPS11 = '-'
        try:
            COS3 = perfDb.results.find({'Build':build,'Name': 'Cosbench','Operation':'read','Object_Size':'1 MB','Buckets':50,'Objects':100,'Sessions':100}) 
            RTH11 = roundoff(COS3[0]['Throughput'])
            RL11 = roundoff(COS3[0]['Latency']['Avg'])
            RIOPS11 = roundoff(COS3[0]['Throughput'])   
        except:
            RTH11 = "-"
            RL11 = '-'
            RIOPS11 = '-'
        try:
            COS3 = perfDb.results.find({'Build':build,'Name': 'Cosbench','Operation':'write','Object_Size':'5 MB','Buckets':50,'Objects':100,'Sessions':100}) 
            WTH51 = roundoff(COS3[0]['Throughput']*5)
            WL51 = roundoff(COS3[0]['Latency']['Avg'])
            WIOPS51 =roundoff(COS3[0]['Throughput'])   
        except:
            WTH51 = "-"
            WL51 = '-'
            WIOPS51 = '-'
        try:
            COS3 = perfDb.results.find({'Build':build,'Name': 'Cosbench','Operation':'read','Object_Size':'5 MB','Buckets':50,'Objects':100,'Sessions':100}) 
            RTH51 = roundoff(COS3[0]['Throughput']*5)
            RL51 = roundoff(COS3[0]['Latency']['Avg'])
            RIOPS51 =roundoff( COS3[0]['Throughput'])   
        except:
            RTH51 = "-"
            RL51 = '-'
            RIOPS51 = '-'
        try:
            COS3 = perfDb.results.find({'Build':build,'Name': 'Cosbench','Operation':'write','Object_Size':'36 MB','Buckets':50,'Objects':100,'Sessions':100}) 
            WTH361 =roundoff( COS3[0]['Throughput']*36)
            WL361 = roundoff(COS3[0]['Latency']['Avg'])
            WIOPS361 = roundoff(COS3[0]['Throughput']) 
        except:
            WTH361 = "-"
            WL361 = '-'
            WIOPS361 = '-'
        try:
            COS3 = perfDb.results.find({'Build':build,'Name': 'Cosbench','Operation':'read','Object_Size':'36 MB','Buckets':50,'Objects':100,'Sessions':100}) 
            RTH361 = roundoff(COS3[0]['Throughput']*36)
            RL361 =roundoff( COS3[0]['Latency']['Avg'])
            RIOPS361 = roundoff(COS3[0]['Throughput'])   
        except:
            RTH361 = "-"
            RL361 = '-'
            RIOPS361 = '-'
        try:
            COS3 = perfDb.results.find({'Build':build,'Name': 'Cosbench','Operation':'write','Object_Size':'64 MB','Buckets':50,'Objects':100,'Sessions':100}) 
            WTH641 = roundoff(COS3[0]['Throughput']*64)
            WL641 = roundoff(COS3[0]['Latency']['Avg'])
            WIOPS641 = roundoff(COS3[0]['Throughput'])   
        except:
            WTH641 = "-"
            WL641 = '-'
            WIOPS641 = '-'
        try:
            COS3 = perfDb.results.find({'Build':build,'Name': 'Cosbench','Operation':'read','Object_Size':'64 MB','Buckets':50,'Objects':100,'Sessions':100}) 
            RTH641 = roundoff(COS3[0]['Throughput']*64)
            RL641 = roundoff(COS3[0]['Latency']['Avg'])
            RIOPS641 = roundoff(COS3[0]['Throughput'])   
        except:
            RTH641 = "-"
            RL641 = '-'
            RIOPS641 = '-'
        try:
            COS3 = perfDb.results.find({'Build':build,'Name': 'Cosbench','Operation':'write','Object_Size':'128 MB','Buckets':50,'Objects':100,'Sessions':100}) 
            WTH1281 = roundoff(COS3[0]['Throughput']*128)
            WL1281 = roundoff(COS3[0]['Latency']['Avg'])
            WIOPS1281 = roundoff(COS3[0]['Throughput'])   
        except:
            WTH1281 = "-"
            WL1281 = '-'
            WIOPS1281 = '-'
        try:
            COS3 = perfDb.results.find({'Build':build,'Name': 'Cosbench','Operation':'read','Object_Size':'128 MB','Buckets':50,'Objects':100,'Sessions':100}) 
            RTH1281 = roundoff(COS3[0]['Throughput']*128)
            RL1281 = roundoff(COS3[0]['Latency']['Avg'])
            RIOPS1281 = roundoff(COS3[0]['Throughput'])   
        except:
            RTH1281 = "-"
            RL1281 = '-'
            RIOPS1281 = '-'
        try:
            COS3 = perfDb.results.find({'Build':build,'Name': 'Cosbench','Operation':'write','Object_Size':'256 MB','Buckets':50,'Objects':100,'Sessions':100}) 
            WTH2561 = roundoff(COS3[0]['Throughput']*256)
            WL2561 = roundoff(COS3[0]['Latency']['Avg'])
            WIOPS2561 = roundoff(COS3[0]['Throughput'])   
        except:
            WTH2561 = "-"
            WL2561 = '-'
            WIOPS2561 = '-'
        try:
            COS3 = perfDb.results.find({'Build':build,'Name': 'Cosbench','Operation':'read','Object_Size':'256 MB','Buckets':50,'Objects':100,'Sessions':100}) 
            RTH2561 = roundoff(COS3[0]['Throughput']*256)
            RL2561 = roundoff(COS3[0]['Latency']['Avg'])
            RIOPS2561 = roundoff(COS3[0]['Throughput'])   
        except:
            RTH2561 = "-"
            RL2561 = '-'
            RIOPS2561 = '-'
        return [WTH41,WTH1001,WTH11,WTH51,WTH361,WTH641,WTH1281,WTH2561,RTH41,RTH1001,RTH11,RTH51,RTH361,RTH641,RTH1281,RTH2561,\
            WL41,WL1001,WL11,WL51,WL361,WL641,WL1281,WL2561,RL41,RL1001,RL11,RL51,RL361,RL641,RL1281,RL2561,WIOPS41,WIOPS1001,WIOPS11,\
                WIOPS51,WIOPS361,WIOPS641,WIOPS1281,WIOPS2561,RIOPS41,RIOPS1001,RIOPS11,RIOPS51,RIOPS361,RIOPS641,RIOPS1281,RIOPS2561]
    
    return [None] * 48

# app configuration ends
### =====================================================
# run server 


if __name__ == '__main__':
    # run localhost:5002
    app.run_server(host='0.0.0.0', port=5002, threaded=True, debug=False)
