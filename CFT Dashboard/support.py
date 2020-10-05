from pymongo import MongoClient
from multipledispatch import dispatch
import plotly.graph_objs as go 
import pandas as pd

def get_DB_details():
   from db_details import makeconnection
   return makeconnection()

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
                            '<b>Throughput - {}</b><extra></extra>'.format(build1),
        )
        fig.add_trace(trace1)

        trace3 = go.Scatter(
            name = '{} Latency - {}'.format(operation, build1),
            x = objects,
            y = data_latency_B1,
            hovertemplate = '<br>%{y} ms<br>'+
                            '<b>Latency - {}</b><extra></extra>'.format(build1),
        )
        fig.add_trace(trace3)
        trace5 = go.Scatter(
            name = '{} IOPS - {}'.format(operation, build1),
            x = objects,
            y = data_IOPS_B1,
            hovertemplate = '<br>%{y}<br>'+
                            '<b>IOPS - {}</b><extra></extra>'.format(build1),
        )
        fig.add_trace(trace5)

        trace7 = go.Scatter(
            name = '{} TTFB - {}'.format(operation, build1),
            x = objects,
            y = data_TTFB_B1,
            hovertemplate = '<br>%{y} ms<br>'+
                                '<b>TTFB - {}</b><extra></extra>'.format(build1),     
        )
        fig.add_trace(trace7)

        trace9 = go.Scatter(
            name = '{} Throughput - {}'.format(operation, build2),
            x = objects,
            y = data_throughput_B2,
            hovertemplate = '<br>%{y} MBps<br>'+
                            '<b>Throughput - {}</b><extra></extra>'.format(build2),
        )
        fig.add_trace(trace9)

        trace11 = go.Scatter(
            name = '{} Latency - {}'.format(operation, build2),
            x = objects,
            y = data_latency_B2,
            hovertemplate = '<br>%{y} ms<br>'+
                            '<b>Latency - {}</b><extra></extra>'.format(build2),
        )
        fig.add_trace(trace11)
        trace13 = go.Scatter(
            name = '{} IOPS - {}'.format(operation, build2),
            x = objects,
            y = data_IOPS_B2,
            hovertemplate = '<br>%{y}<br>'+
                            '<b>IOPS - {}</b><extra></extra>'.format(build2),
        )
        fig.add_trace(trace13)

        trace15 = go.Scatter(
            name = '{} TTFB - {}'.format(operation, build2),
            x = objects,
            y = data_TTFB_B2,
        hovertemplate = '<br>%{y} ms<br>'+
                            '<b>TTFB - {}</b><extra></extra>'.format(build2),     
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
                            '<b>Read Throughput - {}</b><extra></extra>'.format(build1),
        )
        fig.add_trace(trace1)

        trace2 = go.Scatter(
            name = 'Write Throughput - {}'.format(build1),
            x = objects,
            y = data_write_throughput_B1,
            hovertemplate = '<br>%{y} MBps<br>'+
                            '<b>Write Throughput - {}</b><extra></extra>'.format(build1),  
        )
        fig.add_trace(trace2)

        trace3 = go.Scatter(
            name = 'Read Latency - {}'.format(build1),
            x = objects,
            y = data_read_latency_B1,
            hovertemplate = '<br>%{y} ms<br>'+
                            '<b>Read Latency - {}</b><extra></extra>'.format(build1),
        )
        fig.add_trace(trace3)

        trace4 = go.Scatter(
            name = 'Write Latency - {}'.format(build1),
            x = objects,
            y = data_write_latency_B1,
            hovertemplate = '<br>%{y} ms<br>'+
                            '<b>Write Latency - {}</b><extra></extra>'.format(build1),
        )
        fig.add_trace(trace4)

        trace5 = go.Scatter(
            name = 'Read IOPS - {}'.format(build1),
            x = objects,
            y = data_read_IOPS_B1,
            hovertemplate = '<br>%{y}<br>'+
                            '<b>Read IOPS - {}</b><extra></extra>'.format(build1),
        )
        fig.add_trace(trace5)

        trace6 = go.Scatter(
            name = 'Write IOPS - {}'.format(build1),
            x = objects,
            y = data_write_IOPS_B1,
            hovertemplate = '<br>%{y}<br>'+
                            '<b>Write IOPS - {}</b><extra></extra>'.format(build1),
        )
        fig.add_trace(trace6)

        trace7 = go.Scatter(
            name = 'Read TTFB - {}'.format(build1),
            x = objects,
            y = data_read_TTFB_B1,
        hovertemplate = '<br>%{y} ms<br>'+
                            '<b>Read TTFB - {}</b><extra></extra>'.format(build1),     
        )
        fig.add_trace(trace7)

        trace8 = go.Scatter(
            name = 'Write TTFB - {}'.format(build1),
            x = objects,
            y = data_write_TTFB_B1,
            hovertemplate = '<br>%{y} ms<br>'+
                            '<b>Write TTFB - {}</b><extra></extra>'.format(build1),
        )
        fig.add_trace(trace8)

        trace9 = go.Scatter(
            name = 'Read Throughput - {}'.format(build2),
            x = objects,
            y = data_read_throughput_B2,
            hovertemplate = '<br>%{y} MBps<br>'+
                            '<b>Read Throughput - {}</b><extra></extra>'.format(build2),
        )
        fig.add_trace(trace9)

        trace10 = go.Scatter(
            name = 'Write Throughput - {}'.format(build2),
            x = objects,
            y = data_write_throughput_B2,
            hovertemplate = '<br>%{y} MBps<br>'+
                            '<b>Write Throughput - {}</b><extra></extra>'.format(build2),
        )
        fig.add_trace(trace10)

        trace11 = go.Scatter(
            name = 'Read Latency - {}'.format(build2),
            x = objects,
            y = data_read_latency_B2,
            hovertemplate = '<br>%{y} ms<br>'+
                            '<b>Read Latency - {}</b><extra></extra>'.format(build2), 
        )
        fig.add_trace(trace11)

        trace12 = go.Scatter(
            name = 'Write Latency - {}'.format(build2),
            x = objects,
            y = data_write_latency_B2,
            hovertemplate = '<br>%{y} ms<br>'+
                            '<b>Write Latency - {}</b><extra></extra>'.format(build2),
        )
        fig.add_trace(trace12)

        trace13 = go.Scatter(
            name = 'Read IOPS - {}'.format(build2),
            x = objects,
            y = data_read_IOPS_B2,
            hovertemplate = '<br>%{y}<br>'+
                            '<b>Read IOPS - {}</b><extra></extra>'.format(build2),        
        )
        fig.add_trace(trace13)

        trace14 = go.Scatter(
            name = 'Write IOPS - {}'.format(build2),
            x = objects,
            y = data_write_IOPS_B2,
            hovertemplate = '<br>%{y}<br>'+
                            '<b>Write IOPS - {}</b><extra></extra>'.format(build2),
        )
        fig.add_trace(trace14)

        trace15 = go.Scatter(
            name = 'Read TTFB - {}'.format(build2),
            x = objects,
            y = data_read_TTFB_B2,
            hovertemplate = '<br>%{y} ms<br>'+
                            '<b>Read TTFB - {}</b><extra></extra>'.format(build2),
        )
        fig.add_trace(trace15)

        trace16 = go.Scatter(
            name = 'Write TTFB - {}'.format(build2),
            x = objects,
            y = data_write_TTFB_B2,
            hovertemplate = '<br>%{y} ms<br>'+
                            '<b>Write TTFB - {}</b><extra></extra>'.format(build2),
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