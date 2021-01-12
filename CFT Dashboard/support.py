# Support file
from pymongo import MongoClient
# from multipledispatch import dispatch
import plotly.graph_objs as go 
import pandas as pd

def get_DB_details():
   from db_details import makeconnection
   return makeconnection()

# @dispatch(str,str,str)
# def get_Data(build,bench,operation,param):

def getObjectUnit(unit,bench):
    if bench == 'Cosbench':
        return ' ' + unit.upper()
    else:
        return unit

def get_non_configs_data(build,bench,operation,param,subparam=None):
    print("nc",build,bench,operation,param,subparam)
    if subparam==None:
        data = []
        col = get_DB_details()
        cursor = col.find({'Build':build,'Name': bench, 'Operation':operation,'Object_Size': '4'+getObjectUnit('Kb',bench)})
        data.append(cursor[0][param])
        cursor = col.find({'Build':build,'Name': bench, 'Operation':operation,'Object_Size': '100'+getObjectUnit('Kb',bench)})
        data.append(cursor[0][param])
        cursor = col.find({'Build':build,'Name': bench, 'Operation':operation,'Object_Size': '1'+getObjectUnit('Mb',bench)})
        data.append(cursor[0][param])
        cursor = col.find({'Build':build,'Name': bench, 'Operation':operation,'Object_Size': '5'+getObjectUnit('Mb',bench)})
        data.append(cursor[0][param])
        cursor = col.find({'Build':build,'Name': bench, 'Operation':operation,'Object_Size': '36'+getObjectUnit('Mb',bench)})
        data.append(cursor[0][param])
        cursor = col.find({'Build':build,'Name': bench, 'Operation':operation,'Object_Size': '64'+getObjectUnit('Mb',bench)})
        data.append(cursor[0][param])
        cursor = col.find({'Build':build,'Name': bench, 'Operation':operation,'Object_Size': '128'+getObjectUnit('Mb',bench)})
        data.append(cursor[0][param])
        cursor = col.find({'Build':build,'Name': bench, 'Operation':operation,'Object_Size': '256'+getObjectUnit('Mb',bench)})
        data.append(cursor[0][param])
        
        return data

    else:
        data = []
        col = get_DB_details()
        cursor = col.find({'Build':build,'Name': bench, 'Operation':operation,'Object_Size': '4'+getObjectUnit('Kb',bench)})
        data.append(cursor[0][param][subparam])
        cursor = col.find({'Build':build,'Name': bench, 'Operation':operation,'Object_Size': '100'+getObjectUnit('Kb',bench)})
        data.append(cursor[0][param][subparam])
        cursor = col.find({'Build':build,'Name': bench, 'Operation':operation,'Object_Size': '1'+getObjectUnit('Mb',bench)})
        data.append(cursor[0][param][subparam])
        cursor = col.find({'Build':build,'Name': bench, 'Operation':operation,'Object_Size': '5'+getObjectUnit('Mb',bench)})
        data.append(cursor[0][param][subparam])
        cursor = col.find({'Build':build,'Name': bench, 'Operation':operation,'Object_Size': '36'+getObjectUnit('Mb',bench)})
        data.append(cursor[0][param][subparam])
        cursor = col.find({'Build':build,'Name': bench, 'Operation':operation,'Object_Size': '64'+getObjectUnit('Mb',bench)})
        data.append(cursor[0][param][subparam])
        cursor = col.find({'Build':build,'Name': bench, 'Operation':operation,'Object_Size': '128'+getObjectUnit('Mb',bench)})
        data.append(cursor[0][param][subparam])
        cursor = col.find({'Build':build,'Name': bench, 'Operation':operation,'Object_Size': '256'+getObjectUnit('Mb',bench)})
        data.append(cursor[0][param][subparam])
        
        return (pd.Series(data) * 1000).tolist()

def get_configs_data(build,bench,operation,buckets,objects,sessions,param,subparam=None):
    print("c",build,bench,operation,buckets,objects,sessions,param,subparam)
    if subparam==None:
        data = []
        col = get_DB_details()
        operation = operation.lower()
        cursor = col.find({'Build':build,'Name': bench, 'Operation':operation,'Object_Size': '4'+getObjectUnit('Kb',bench),'Buckets':buckets,'Objects':objects,'Sessions':sessions})
        data.append(cursor[0][param])
        cursor = col.find({'Build':build,'Name': bench, 'Operation':operation,'Object_Size': '100'+getObjectUnit('Kb',bench),'Buckets':buckets,'Objects':objects,'Sessions':sessions})
        data.append(cursor[0][param])
        cursor = col.find({'Build':build,'Name': bench, 'Operation':operation,'Object_Size': '1'+getObjectUnit('Mb',bench),'Buckets':buckets,'Objects':objects,'Sessions':sessions})
        data.append(cursor[0][param])
        cursor = col.find({'Build':build,'Name': bench, 'Operation':operation,'Object_Size': '5'+getObjectUnit('Mb',bench),'Buckets':buckets,'Objects':objects,'Sessions':sessions})
        data.append(cursor[0][param])
        cursor = col.find({'Build':build,'Name': bench, 'Operation':operation,'Object_Size': '36'+getObjectUnit('Mb',bench),'Buckets':buckets,'Objects':objects,'Sessions':sessions})
        data.append(cursor[0][param])
        cursor = col.find({'Build':build,'Name': bench, 'Operation':operation,'Object_Size': '64'+getObjectUnit('Mb',bench),'Buckets':buckets,'Objects':objects,'Sessions':sessions})
        data.append(cursor[0][param])
        cursor = col.find({'Build':build,'Name': bench, 'Operation':operation,'Object_Size': '128'+getObjectUnit('Mb',bench),'Buckets':buckets,'Objects':objects,'Sessions':sessions})
        data.append(cursor[0][param])
        cursor = col.find({'Build':build,'Name': bench, 'Operation':operation,'Object_Size': '256'+getObjectUnit('Mb',bench),'Buckets':buckets,'Objects':objects,'Sessions':sessions})
        data.append(cursor[0][param])
        
        return data

    else:
        data = []
        col = get_DB_details()
        cursor = col.find({'Build':build,'Name': bench, 'Operation':operation,'Object_Size': '4'+getObjectUnit('Kb',bench),'Buckets':buckets,'Objects':objects,'Sessions':sessions})
        data.append(cursor[0][param][subparam])
        cursor = col.find({'Build':build,'Name': bench, 'Operation':operation,'Object_Size': '100'+getObjectUnit('Kb',bench),'Buckets':buckets,'Objects':objects,'Sessions':sessions})
        data.append(cursor[0][param][subparam])
        cursor = col.find({'Build':build,'Name': bench, 'Operation':operation,'Object_Size': '1'+getObjectUnit('Mb',bench),'Buckets':buckets,'Objects':objects,'Sessions':sessions})
        data.append(cursor[0][param][subparam])
        cursor = col.find({'Build':build,'Name': bench, 'Operation':operation,'Object_Size': '5'+getObjectUnit('Mb',bench),'Buckets':buckets,'Objects':objects,'Sessions':sessions})
        data.append(cursor[0][param][subparam])
        cursor = col.find({'Build':build,'Name': bench, 'Operation':operation,'Object_Size': '36'+getObjectUnit('Mb',bench),'Buckets':buckets,'Objects':objects,'Sessions':sessions})
        data.append(cursor[0][param][subparam])
        cursor = col.find({'Build':build,'Name': bench, 'Operation':operation,'Object_Size': '64'+getObjectUnit('Mb',bench),'Buckets':buckets,'Objects':objects,'Sessions':sessions})
        data.append(cursor[0][param][subparam])
        cursor = col.find({'Build':build,'Name': bench, 'Operation':operation,'Object_Size': '128'+getObjectUnit('Mb',bench),'Buckets':buckets,'Objects':objects,'Sessions':sessions})
        data.append(cursor[0][param][subparam])
        cursor = col.find({'Build':build,'Name': bench, 'Operation':operation,'Object_Size': '256'+getObjectUnit('Mb',bench),'Buckets':buckets,'Objects':objects,'Sessions':sessions})
        data.append(cursor[0][param][subparam])
        
        return (pd.Series(data) * 1000).tolist()

# @dispatch(str,str,str,str)
def get_Data(build,bench,configs,operation,param,subparam=None):
    Sessions = 100
    if bench == 'Cosbench':
        if configs == 'option1':
            Buckets = 1
            Objects = 1000
        elif configs == 'option2':
            Buckets = 10
            Objects = 100
        elif configs == 'option3':
            Buckets = 50
            Objects = 100
        else:
            Buckets = 1
            Objects = 1000
    elif bench == 'Hsbench':
        if configs == 'option1':
            Buckets = 1
            Objects = 1000
        elif configs == 'option2':
            Buckets = 10
            Objects = 1000
        elif configs == 'option3':
            Buckets = 50
            Objects = 5000
        else:
            Buckets = 1
            Objects = 1000

    if configs == None:
        return get_non_configs_data(build,bench,operation,param,subparam)

    else:
        return get_configs_data(build,bench,operation,Buckets,Objects,Sessions,param,subparam)
    

def get_all_traces(build1, build2, objects, bench, configs, operation):
    fig = go.Figure() 
    print("get all traces",configs,operation)   
    operation_read = 'read'
    operation_write = 'write'
    if bench == 'S3bench':
        operation_read = 'Read'
        operation_write = 'Write'

    if operation != 'Both':
        data_throughput_B1 = get_Data(build1,bench,configs,operation,'Throughput')

        if bench != 'Hsbench':
            data_latency_B1 = get_Data(build1,bench,configs,operation,'Latency','Avg')
        else:
            data_latency_B1 = get_Data(build1,bench,configs,operation,'Latency')

        data_IOPS_B1 = get_Data(build1,bench,configs,operation,'IOPS')
        if bench == 'S3bench':
            data_TTFB_B1 = get_Data(build1,bench,configs,operation,'TTFB','Avg')

        data_throughput_B2 = get_Data(build2,bench,configs,operation,'Throughput')

        if bench != 'Hsbench':
            data_latency_B2 = get_Data(build2,bench,configs,operation,'Latency','Avg')
        else:
            data_latency_B2 = get_Data(build2,bench,configs,operation,'Latency')

        data_IOPS_B2 = get_Data(build2,bench,configs,operation,'IOPS')
        if bench == 'S3bench':
            data_TTFB_B2 = get_Data(build2,bench,configs,operation,'TTFB','Avg')

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

        if bench == 'S3bench':
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

        if bench == 'S3bench':
            trace15 = go.Scatter(
                name = '{} TTFB - {}'.format(operation, build2),
                x = objects,
                y = data_TTFB_B2,
            hovertemplate = '<br>%{y} ms<br>'+
                                '<b>TTFB - {}</b><extra></extra>'.format(build2),     
            )
            fig.add_trace(trace15)       

    else:
        data_read_throughput_B1 = get_Data(build1,bench,configs,operation_read,'Throughput')    
        data_write_throughput_B1 = get_Data(build1,bench,configs,operation_write,'Throughput')
        if bench != 'Hsbench':
            data_read_latency_B1 = get_Data(build1,bench,configs,operation_read,'Latency','Avg')
            data_write_latency_B1 = get_Data(build1,bench,configs,operation_write,'Latency','Avg')
        else:
            data_read_latency_B1 = get_Data(build1,bench,configs,operation_read,'Latency')
            data_write_latency_B1 = get_Data(build1,bench,configs,operation_write,'Latency')

        data_read_IOPS_B1 = get_Data(build1,bench,configs,operation_read,'IOPS')
        data_write_IOPS_B1 = get_Data(build1,bench,configs,operation_write,'IOPS')
        if bench == 'S3bench':
            data_read_TTFB_B1 = get_Data(build1,bench,configs,operation_read,'TTFB','Avg')
            data_write_TTFB_B1 = get_Data(build1,bench,configs,operation_write,'TTFB','Avg')

        data_read_throughput_B2 = get_Data(build2,bench,configs,operation_read,'Throughput')    
        data_write_throughput_B2 = get_Data(build2,bench,configs,operation_write,'Throughput')
        if bench != 'Hsbench':
            data_read_latency_B2 = get_Data(build2,bench,configs,operation_read,'Latency','Avg')
            data_write_latency_B2 = get_Data(build2,bench,configs,operation_write,'Latency','Avg')
        else:
            data_read_latency_B2 = get_Data(build2,bench,configs,operation_read,'Latency')
            data_write_latency_B2 = get_Data(build2,bench,configs,operation_write,'Latency')

        data_read_IOPS_B2 = get_Data(build2,bench,configs,operation_read,'IOPS')
        data_write_IOPS_B2 = get_Data(build2,bench,configs,operation_write,'IOPS')
        if bench == 'S3bench':
            data_read_TTFB_B2 = get_Data(build2,bench,configs,operation_read,'TTFB','Avg')
            data_write_TTFB_B2 = get_Data(build2,bench,configs,operation_write,'TTFB','Avg')

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

        if bench == 'S3bench':
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

        if bench == 'S3bench':
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