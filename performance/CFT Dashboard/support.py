from pymongo import MongoClient
from jproperties import Properties
from multipledispatch import dispatch
import plotly.graph_objs as go 
import pandas as pd

def get_DB_details():
    data_config = Properties()
    with open('config.properties','rb') as config_file:
        data_config.load(config_file)
        client = MongoClient(data_config.get("DB_URL").data)  #connecting with mongodb database
        db=client[data_config.get("DB_DATABASE").data]  #database name=performance 
        collection=db[data_config.get("DB_COLLECTION").data]
    return collection

@dispatch(str,str,str)
def get_Data(build,operation,param):
    data = []
    col = get_DB_details()
    cursor = col.find({'Build':build,'Name': 'S3bench', 'Operation':operation,'Object_Size': '4Kb'})
    data.append(cursor[0][param])
    cursor = col.find({'Build':build,'Name': 'S3bench', 'Operation':operation,'Object_Size': '100Kb'})
    data.append(cursor[0][param])
    cursor = col.find({'Build':build,'Name': 'S3bench', 'Operation':operation,'Object_Size': '1Mb'})
    data.append(cursor[0][param])
    cursor = col.find({'Build':build,'Name': 'S3bench', 'Operation':operation,'Object_Size': '5Mb'})
    data.append(cursor[0][param])
    cursor = col.find({'Build':build,'Name': 'S3bench', 'Operation':operation,'Object_Size': '36Mb'})
    data.append(cursor[0][param])
    cursor = col.find({'Build':build,'Name': 'S3bench', 'Operation':operation,'Object_Size': '64Mb'})
    data.append(cursor[0][param])
    cursor = col.find({'Build':build,'Name': 'S3bench', 'Operation':operation,'Object_Size': '128Mb'})
    data.append(cursor[0][param])
    cursor = col.find({'Build':build,'Name': 'S3bench', 'Operation':operation,'Object_Size': '256Mb'})
    data.append(cursor[0][param])
    
    return data

@dispatch(str,str,str,str)
def get_Data(build,operation,param,subparam):
    data = []
    col = get_DB_details()
    cursor = col.find({'Build':build,'Name': 'S3bench', 'Operation':operation,'Object_Size': '4Kb'})
    data.append(cursor[0][param][subparam])
    cursor = col.find({'Build':build,'Name': 'S3bench', 'Operation':operation,'Object_Size': '100Kb'})
    data.append(cursor[0][param][subparam])
    cursor = col.find({'Build':build,'Name': 'S3bench', 'Operation':operation,'Object_Size': '1Mb'})
    data.append(cursor[0][param][subparam])
    cursor = col.find({'Build':build,'Name': 'S3bench', 'Operation':operation,'Object_Size': '5Mb'})
    data.append(cursor[0][param][subparam])
    cursor = col.find({'Build':build,'Name': 'S3bench', 'Operation':operation,'Object_Size': '36Mb'})
    data.append(cursor[0][param][subparam])
    cursor = col.find({'Build':build,'Name': 'S3bench', 'Operation':operation,'Object_Size': '64Mb'})
    data.append(cursor[0][param][subparam])
    cursor = col.find({'Build':build,'Name': 'S3bench', 'Operation':operation,'Object_Size': '128Mb'})
    data.append(cursor[0][param][subparam])
    cursor = col.find({'Build':build,'Name': 'S3bench', 'Operation':operation,'Object_Size': '256Mb'})
    data.append(cursor[0][param][subparam])
    
    return (pd.Series(data) * 1000).tolist()

def get_all_traces(build1, build2, objects, operation):
    fig = go.Figure()    
    if operation != 'Both':
        data_throughput_B1 = get_Data(build1,operation,'Throughput')
        data_latency_B1 = get_Data(build1,operation,'Latency','Avg')
        data_IOPS_B1 = get_Data(build1,operation,'IOPS')
        data_TTFB_B1 = get_Data(build1,operation,'TTFB','Avg')

        data_throughput_B2 = get_Data(build2,operation,'Throughput')
        data_latency_B2 = get_Data(build2,operation,'Latency','Avg')
        data_IOPS_B2 = get_Data(build2,operation,'IOPS')
        data_TTFB_B2 = get_Data(build2,operation,'TTFB','Avg')

        trace1 = go.Scatter(
            name = '{} Throughput - {}'.format(operation, build1),
            x = objects,
            y = data_throughput_B1,
            hovertemplate = '<br>%{y} MBps<br>'+
                            '<b>Throughput - {build1}</b><extra></extra>',
        )
        fig.add_trace(trace1)

        trace3 = go.Scatter(
            name = '{} Latency - {}'.format(operation, build1),
            x = objects,
            y = data_latency_B1,
            hovertemplate = '<br>%{y} ms<br>'+
                            '<b>Latency - {build1}</b><extra></extra>',
        )
        fig.add_trace(trace3)
        trace5 = go.Scatter(
            name = '{} IOPS - {}'.format(operation, build1),
            x = objects,
            y = data_IOPS_B1,
            hovertemplate = '<br>%{y}<br>'+
                            '<b>IOPS - {build1}</b><extra></extra>',
        )
        fig.add_trace(trace5)

        trace7 = go.Scatter(
            name = '{} TTFB - {}'.format(operation, build1),
            x = objects,
            y = data_TTFB_B1,
            hovertemplate = '<br>%{y} ms<br>'+
                                '<b>TTFB - {build1}</b><extra></extra>',     
        )
        fig.add_trace(trace7)

        trace9 = go.Scatter(
            name = '{} Throughput - {}'.format(operation, build2),
            x = objects,
            y = data_throughput_B2,
            hovertemplate = '<br>%{y} MBps<br>'+
                            '<b>Throughput - {build2}</b><extra></extra>',
        )
        fig.add_trace(trace9)

        trace11 = go.Scatter(
            name = '{} Latency - {}'.format(operation, build2),
            x = objects,
            y = data_latency_B2,
            hovertemplate = '<br>%{y} ms<br>'+
                            '<b>Latency - {build2}</b><extra></extra>',
        )
        fig.add_trace(trace11)
        trace13 = go.Scatter(
            name = '{} IOPS - {}'.format(operation, build2),
            x = objects,
            y = data_IOPS_B2,
            hovertemplate = '<br>%{y}<br>'+
                            '<b>IOPS - {build2}</b><extra></extra>',
        )
        fig.add_trace(trace13)

        trace15 = go.Scatter(
            name = '{} TTFB - {}'.format(operation, build2),
            x = objects,
            y = data_TTFB_B2,
        hovertemplate = '<br>%{y} ms<br>'+
                            '<b>TTFB - {build2}</b><extra></extra>',     
        )
        fig.add_trace(trace15)       

    else:

        data_read_throughput_B1 = get_Data(build1,'Read','Throughput')    
        data_write_throughput_B1 = get_Data(build1,'Write','Throughput')
        data_read_latency_B1 = get_Data(build1,'Read','Latency','Avg')
        data_write_latency_B1 = get_Data(build1,'Write','Latency','Avg')
        data_read_IOPS_B1 = get_Data(build1,'Read','IOPS')
        data_write_IOPS_B1 = get_Data(build1,'Write','IOPS')
        data_read_TTFB_B1 = get_Data(build1,'Read','TTFB','Avg')
        data_write_TTFB_B1 = get_Data(build1,'Write','TTFB','Avg')

        data_read_throughput_B2 = get_Data(build2,'Read','Throughput')    
        data_write_throughput_B2 = get_Data(build2,'Write','Throughput')
        data_read_latency_B2 = get_Data(build2,'Read','Latency','Avg')
        data_write_latency_B2 = get_Data(build2,'Write','Latency','Avg')
        data_read_IOPS_B2 = get_Data(build2,'Read','IOPS')
        data_write_IOPS_B2 = get_Data(build2,'Write','IOPS')
        data_read_TTFB_B2 = get_Data(build2,'Read','TTFB','Avg')
        data_write_TTFB_B2 = get_Data(build2,'Write','TTFB','Avg')

        trace1 = go.Scatter(
            name = 'Read Throughput - {}'.format(build1),
            x = objects,
            y = data_read_throughput_B1,
            hovertemplate = '<br>%{y} MBps<br>'+
                            '<b>R Throughput - {build1}</b><extra></extra>',
        )
        fig.add_trace(trace1)

        trace2 = go.Scatter(
            name = 'Write Throughput - {}'.format(build1),
            x = objects,
            y = data_write_throughput_B1,
            hovertemplate = '<br>%{y} MBps<br>'+
                            '<b>W Throughput - {build1}</b><extra></extra>',  
        )
        fig.add_trace(trace2)

        trace3 = go.Scatter(
            name = 'Read Latency - {}'.format(build1),
            x = objects,
            y = data_read_latency_B1,
            hovertemplate = '<br>%{y} ms<br>'+
                            '<b>R Latency - {build1}</b><extra></extra>',
        )
        fig.add_trace(trace3)

        trace4 = go.Scatter(
            name = 'Write Latency - {}'.format(build1),
            x = objects,
            y = data_write_latency_B1,
            hovertemplate = '<br>%{y} ms<br>'+
                            '<b>W Latency - {build1}</b><extra></extra>',
        )
        fig.add_trace(trace4)

        trace5 = go.Scatter(
            name = 'Read IOPS - {}'.format(build1),
            x = objects,
            y = data_read_IOPS_B1,
            hovertemplate = '<br>%{y}<br>'+
                            '<b>R IOPS - {build1}</b><extra></extra>',
        )
        fig.add_trace(trace5)

        trace6 = go.Scatter(
            name = 'Write IOPS - {}'.format(build1),
            x = objects,
            y = data_write_IOPS_B1,
            hovertemplate = '<br>%{y}<br>'+
                            '<b>W IOPS - {build1}</b><extra></extra>',
        )
        fig.add_trace(trace6)

        trace7 = go.Scatter(
            name = 'Read TTFB - {}'.format(build1),
            x = objects,
            y = data_read_TTFB_B1,
        hovertemplate = '<br>%{y} ms<br>'+
                            '<b>R TTFB - {build1}</b><extra></extra>',     
        )
        fig.add_trace(trace7)

        trace8 = go.Scatter(
            name = 'Write TTFB - {}'.format(build1),
            x = objects,
            y = data_write_TTFB_B1,
            hovertemplate = '<br>%{y} ms<br>'+
                            '<b>W TTFB - {build1}</b><extra></extra>',
        )
        fig.add_trace(trace8)

        trace9 = go.Scatter(
            name = 'Read Throughput - {}'.format(build2),
            x = objects,
            y = data_read_throughput_B2,
            hovertemplate = '<br>%{y} MBps<br>'+
                            '<b>R Throughput - {build2}</b><extra></extra>',
        )
        fig.add_trace(trace9)

        trace10 = go.Scatter(
            name = 'Write Throughput - {}'.format(build2),
            x = objects,
            y = data_write_throughput_B2,
            hovertemplate = '<br>%{y} MBps<br>'+
                            '<b>W Throughput - {build2}</b><extra></extra>',
        )
        fig.add_trace(trace10)

        trace11 = go.Scatter(
            name = 'Read Latency - {}'.format(build2),
            x = objects,
            y = data_read_latency_B2,
            hovertemplate = '<br>%{y} ms<br>'+
                            '<b>R Latency - {build2}</b><extra></extra>', 
        )
        fig.add_trace(trace11)

        trace12 = go.Scatter(
            name = 'Write Latency - {}'.format(build2),
            x = objects,
            y = data_write_latency_B2,
            hovertemplate = '<br>%{y} ms<br>'+
                            '<b>W Latency - {build2}</b><extra></extra>',
        )
        fig.add_trace(trace12)

        trace13 = go.Scatter(
            name = 'Read IOPS - {}'.format(build2),
            x = objects,
            y = data_read_IOPS_B2,
            hovertemplate = '<br>%{y}<br>'+
                            '<b>R IOPS - {build2}</b><extra></extra>',        
        )
        fig.add_trace(trace13)

        trace14 = go.Scatter(
            name = 'Write IOPS - {}'.format(build2),
            x = objects,
            y = data_write_IOPS_B2,
            hovertemplate = '<br>%{y}<br>'+
                            '<b>W IOPS - {build2}</b><extra></extra>',
        )
        fig.add_trace(trace14)

        trace15 = go.Scatter(
            name = 'Read TTFB - {}'.format(build2),
            x = objects,
            y = data_read_TTFB_B2,
            hovertemplate = '<br>%{y} ms<br>'+
                            '<b>R TTFB - {build2}</b><extra></extra>',
        )
        fig.add_trace(trace15)

        trace16 = go.Scatter(
            name = 'Write TTFB - {}'.format(build2),
            x = objects,
            y = data_write_TTFB_B2,
            hovertemplate = '<br>%{y} ms<br>'+
                            '<b>W TTFB - {build2}</b><extra></extra>',
        )
        fig.add_trace(trace16)

    fig.update_layout(
        autosize=True,
        showlegend = True,
        title = 'All Statistics Variance',
        legend_title= 'Glossary',
        width=1200,
        height=600,
        yaxis=dict(            
            title_text="Data",
            titlefont=dict(size=16)),
        xaxis=dict(
            title_text="Object Sizes",
            titlefont=dict(size=16)
        )
    )
    return fig