## Support file

from pymongo import MongoClient
import plotly.graph_objs as go 
import pandas as pd

def get_DB_details():
   from db_details import makeconnection
   return makeconnection()

def get_x_axis(options,bench=None,version=None):
    if options == 'Object Size':
        objects = ['4KB','100KB','1MB','5MB','36MB','64MB','128MB','256MB']
        return objects
    else:
        col = get_DB_details()
        cursor = col.find({'Title': 'Main Chain'})
        builds = cursor[0][version]

        for build in builds:
            if col.count_documents({'Build':build}) == 0:
                builds.remove(build)
        
        return builds

def get_IO_size(IOsize,bench):
    if bench == 'Cosbench':
        return IOsize[:-2] + ' ' + IOsize[-2::].upper()
    else:
        return IOsize[:-2]+IOsize[-2::].lower().capitalize()

def get_non_configs_IOsize_data(build,bench,operation,param,subparam=None):
    IOsize_list = get_x_axis('Object Size',bench)

    data = []
    col = get_DB_details()

    if subparam==None:
        for IOsize in IOsize_list:
            try: 
                cursor = col.find({'Build':build,'Name': bench, 'Operation':operation,'Object_Size': get_IO_size(IOsize,bench)})
                data.append(cursor[0][param])
            except:
               data.append(None)

    else:
        for IOsize in IOsize_list:
            try:
                cursor = col.find({'Build':build,'Name': bench, 'Operation':operation,'Object_Size': get_IO_size(IOsize,bench)})
                data.append(cursor[0][param][subparam])
            except:
               data.append(None)

        data = (pd.Series(data) * 1000).tolist()

    return IOsize_list, data

def get_configs_IOsize_data(build,bench,operation,buckets,objects,sessions,param,subparam=None):
    data = []
    col = get_DB_details()
    IOsize_list = get_x_axis('Object Size',bench)

    if subparam==None:
        operation = operation.lower()
        for IOsize in IOsize_list:
            try:
                cursor = col.find({'Build':build,'Name': bench, 'Operation':operation,'Object_Size': get_IO_size(IOsize,bench),'Buckets':buckets,'Objects':objects,'Sessions':sessions})
                data.append(cursor[0][param])
            except:
               data.append(None)
    else:
        for IOsize in IOsize_list:
            try:
                cursor = col.find({'Build':build,'Name': bench, 'Operation':operation,'Object_Size': get_IO_size(IOsize,bench),'Buckets':buckets,'Objects':objects,'Sessions':sessions})
                data.append(cursor[0][param][subparam])
            except:
               data.append(None)

        data = (pd.Series(data) * 1000).tolist()

    return IOsize_list, data

def get_benchmark_configs(configs, bench):
    Sessions = 100
    Buckets = 1
    Objects = 1000
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

    return Buckets, Objects, Sessions

def get_IOsizewise_data(build,bench,configs,operation,param,subparam=None):
    Buckets, Objects, Sessions = get_benchmark_configs(configs, bench)

    if configs == None:
        return get_non_configs_IOsize_data(build,bench,operation,param,subparam)

    else:
        return get_configs_IOsize_data(build,bench,operation,Buckets,Objects,Sessions,param,subparam)

def get_non_config_builds_data(version,IOsize,bench,configs,operation,param,subparam):
    build_list = get_x_axis('builds',bench,version)
    data = []
    col = get_DB_details()

    if subparam==None:
        for build in build_list:
            try:
                cursor = col.find({'Build':build,'Name': bench, 'Operation':operation,'Object_Size': get_IO_size(IOsize,bench)})
                data.append(cursor[0][param])
            except:
                data.append(None)

        return build_list, data
    else:
        for build in build_list:
            try:
                cursor = col.find({'Build':build,'Name': bench, 'Operation':operation,'Object_Size': get_IO_size(IOsize,bench)})
                data.append(cursor[0][param][subparam])
            except:
                data.append(None)

        return build_list, (pd.Series(data) * 1000).tolist()

def get_config_builds_data(version,IOsize,bench,operation,buckets,objects,sessions,param,subparam=None):
    data = []
    col = get_DB_details()
    build_list = get_x_axis('builds',bench,version)

    if subparam==None:
        operation = operation.lower()
        for build in build_list:
            try:
                cursor = col.find({'Build':build,'Name': bench,'Operation':operation,'Object_Size': get_IO_size(IOsize,bench),'Buckets':buckets,'Objects':objects,'Sessions':sessions})
                data.append(cursor[0][param])
            except:
                data.append(None)
        return build_list, data

    else:
        operation = operation.lower()
        for build in build_list:
            try:
                cursor = col.find({'Build':build,'Name': bench,'Operation':operation,'Object_Size': get_IO_size(IOsize,bench),'Buckets':buckets,'Objects':objects,'Sessions':sessions})
                data.append(cursor[0][param][subparam])
            except:
                data.append(None)
        return build_list, data

def get_buildwise_data(version,IOsize,bench,configs,operation,param,subparam=None):
    if bench == 'S3bench':
        builds, datapoints = get_non_config_builds_data(version,IOsize,bench,configs,operation,param,subparam)
    
    else:
        Buckets, Objects, Sessions = get_benchmark_configs(configs, bench)
        builds, datapoints = get_config_builds_data(version,IOsize,bench,operation,Buckets,Objects,Sessions,param,subparam)
    
    return builds, datapoints

def get_all_traces(xfilter, version, build1, build2, bench, configs, operation):
    fig = go.Figure() 
    print("get all traces",configs,operation)   
    operation_read = 'read'
    operation_write = 'write'

    if bench == 'S3bench':
        operation_read = 'Read'
        operation_write = 'Write'

    if xfilter == 'build': 
        titleText = 'Object Sizes' 
    else:
        titleText = 'Builds'

    if operation != 'Both':

        if xfilter == 'build':            
            x_axis, data_throughput_B1 = get_IOsizewise_data(build1,bench,configs,operation,'Throughput')

            if bench != 'Hsbench':
                x_axis, data_latency_B1 = get_IOsizewise_data(build1,bench,configs,operation,'Latency','Avg')
            else:
                x_axis, data_latency_B1 = get_IOsizewise_data(build1,bench,configs,operation,'Latency')

            x_axis, data_IOPS_B1 = get_IOsizewise_data(build1,bench,configs,operation,'IOPS')
            if bench == 'S3bench':
                x_axis, data_TTFB_B1 = get_IOsizewise_data(build1,bench,configs,operation,'TTFB','Avg')

            x_axis, data_throughput_B2 = get_IOsizewise_data(build2,bench,configs,operation,'Throughput')

            if bench != 'Hsbench':
                x_axis, data_latency_B2 = get_IOsizewise_data(build2,bench,configs,operation,'Latency','Avg')
            else:
                data_latency_B2 = get_IOsizewise_data(build2,bench,configs,operation,'Latency')

            x_axis, data_IOPS_B2 = get_IOsizewise_data(build2,bench,configs,operation,'IOPS')
            if bench == 'S3bench':
                x_axis, data_TTFB_B2 = get_IOsizewise_data(build2,bench,configs,operation,'TTFB','Avg')
        
        else:          
            x_axis, data_throughput_B1 = get_buildwise_data(version,build1,bench,configs,operation,'Throughput')

            if bench != 'Hsbench':
                x_axis, data_latency_B1 = get_buildwise_data(version,build1,bench,configs,operation,'Latency','Avg')
            else:
                x_axis, data_latency_B1 = get_buildwise_data(version,build1,bench,configs,operation,'Latency')

            x_axis, data_IOPS_B1 = get_buildwise_data(version,build1,bench,configs,operation,'IOPS')
            if bench == 'S3bench':
                x_axis, data_TTFB_B1 = get_buildwise_data(version,build1,bench,configs,operation,'TTFB','Avg')

            x_axis, data_throughput_B2 = get_buildwise_data(version,build2,bench,configs,operation,'Throughput')

            if bench != 'Hsbench':
                x_axis, data_latency_B2 = get_buildwise_data(version,build2,bench,configs,operation,'Latency','Avg')
            else:
                data_latency_B2 = get_buildwise_data(version,build2,bench,configs,operation,'Latency')

            x_axis, data_IOPS_B2 = get_buildwise_data(version,build2,bench,configs,operation,'IOPS')
            if bench == 'S3bench':
                x_axis, data_TTFB_B2 = get_buildwise_data(version,build2,bench,configs,operation,'TTFB','Avg')

        trace1 = go.Scatter(
            name = '{} Throughput - {}'.format(operation, build1),
            x = x_axis,
            y = data_throughput_B1,
            hovertemplate = '<br>%{y} MBps<br>'+
                            '<b>Throughput - {}</b><extra></extra>'.format(build1),
        )
        fig.add_trace(trace1)

        trace3 = go.Scatter(
            name = '{} Latency - {}'.format(operation, build1),
            x = x_axis,
            y = data_latency_B1,
            hovertemplate = '<br>%{y} ms<br>'+
                            '<b>Latency - {}</b><extra></extra>'.format(build1),
        )
        fig.add_trace(trace3)
        trace5 = go.Scatter(
            name = '{} IOPS - {}'.format(operation, build1),
            x = x_axis,
            y = data_IOPS_B1,
            hovertemplate = '<br>%{y}<br>'+
                            '<b>IOPS - {}</b><extra></extra>'.format(build1),
        )
        fig.add_trace(trace5)

        if bench == 'S3bench':
            trace7 = go.Scatter(
                name = '{} TTFB - {}'.format(operation, build1),
                x = x_axis,
                y = data_TTFB_B1,
                hovertemplate = '<br>%{y} ms<br>'+
                                    '<b>TTFB - {}</b><extra></extra>'.format(build1),     
            )
            fig.add_trace(trace7)

        if build2 != None:
            trace9 = go.Scatter(
                name = '{} Throughput - {}'.format(operation, build2),
                x = x_axis,
                y = data_throughput_B2,
                hovertemplate = '<br>%{y} MBps<br>'+
                                '<b>Throughput - {}</b><extra></extra>'.format(build2),
            )
            fig.add_trace(trace9)

            trace11 = go.Scatter(
                name = '{} Latency - {}'.format(operation, build2),
                x = x_axis,
                y = data_latency_B2,
                hovertemplate = '<br>%{y} ms<br>'+
                                '<b>Latency - {}</b><extra></extra>'.format(build2),
            )
            fig.add_trace(trace11)
            trace13 = go.Scatter(
                name = '{} IOPS - {}'.format(operation, build2),
                x = x_axis,
                y = data_IOPS_B2,
                hovertemplate = '<br>%{y}<br>'+
                                '<b>IOPS - {}</b><extra></extra>'.format(build2),
            )
            fig.add_trace(trace13)

            if bench == 'S3bench':
                trace15 = go.Scatter(
                    name = '{} TTFB - {}'.format(operation, build2),
                    x = x_axis,
                    y = data_TTFB_B2,
                hovertemplate = '<br>%{y} ms<br>'+
                                    '<b>TTFB - {}</b><extra></extra>'.format(build2),     
                )
                fig.add_trace(trace15)       

    else:
        if xfilter == 'build':
            x_axis, data_read_throughput_B1 = get_IOsizewise_data(build1,bench,configs,operation_read,'Throughput')    
            x_axis, data_write_throughput_B1 = get_IOsizewise_data(build1,bench,configs,operation_write,'Throughput')
            if bench != 'Hsbench':
                x_axis, data_read_latency_B1 = get_IOsizewise_data(build1,bench,configs,operation_read,'Latency','Avg')
                x_axis, data_write_latency_B1 = get_IOsizewise_data(build1,bench,configs,operation_write,'Latency','Avg')
            else:
                x_axis, data_read_latency_B1 = get_IOsizewise_data(build1,bench,configs,operation_read,'Latency')
                x_axis, data_write_latency_B1 = get_IOsizewise_data(build1,bench,configs,operation_write,'Latency')

            x_axis, data_read_IOPS_B1 = get_IOsizewise_data(build1,bench,configs,operation_read,'IOPS')
            x_axis, data_write_IOPS_B1 = get_IOsizewise_data(build1,bench,configs,operation_write,'IOPS')
            if bench == 'S3bench':
                x_axis, data_read_TTFB_B1 = get_IOsizewise_data(build1,bench,configs,operation_read,'TTFB','Avg')
                x_axis, data_write_TTFB_B1 = get_IOsizewise_data(build1,bench,configs,operation_write,'TTFB','Avg')

            x_axis, data_read_throughput_B2 = get_IOsizewise_data(build2,bench,configs,operation_read,'Throughput')    
            x_axis, data_write_throughput_B2 = get_IOsizewise_data(build2,bench,configs,operation_write,'Throughput')
            if bench != 'Hsbench':
                x_axis, data_read_latency_B2 = get_IOsizewise_data(build2,bench,configs,operation_read,'Latency','Avg')
                x_axis, data_write_latency_B2 = get_IOsizewise_data(build2,bench,configs,operation_write,'Latency','Avg')
            else:
                x_axis, data_read_latency_B2 = get_IOsizewise_data(build2,bench,configs,operation_read,'Latency')
                x_axis, data_write_latency_B2 = get_IOsizewise_data(build2,bench,configs,operation_write,'Latency')

            x_axis, data_read_IOPS_B2 = get_IOsizewise_data(build2,bench,configs,operation_read,'IOPS')
            x_axis, data_write_IOPS_B2 = get_IOsizewise_data(build2,bench,configs,operation_write,'IOPS')
            if bench == 'S3bench':
                x_axis, data_read_TTFB_B2 = get_IOsizewise_data(build2,bench,configs,operation_read,'TTFB','Avg')
                x_axis, data_write_TTFB_B2 = get_IOsizewise_data(build2,bench,configs,operation_write,'TTFB','Avg')
        
        else:
            x_axis, data_read_throughput_B1 = get_buildwise_data(version,build1,bench,configs,operation_read,'Throughput')    
            x_axis, data_write_throughput_B1 = get_buildwise_data(version,build1,bench,configs,operation_write,'Throughput')
            if bench != 'Hsbench':
                x_axis, data_read_latency_B1 = get_buildwise_data(version,build1,bench,configs,operation_read,'Latency','Avg')
                x_axis, data_write_latency_B1 = get_buildwise_data(version,build1,bench,configs,operation_write,'Latency','Avg')
            else:
                x_axis, data_read_latency_B1 = get_buildwise_data(version,build1,bench,configs,operation_read,'Latency')
                x_axis, data_write_latency_B1 = get_buildwise_data(version,build1,bench,configs,operation_write,'Latency')

            x_axis, data_read_IOPS_B1 = get_buildwise_data(version,build1,bench,configs,operation_read,'IOPS')
            x_axis, data_write_IOPS_B1 = get_buildwise_data(version,build1,bench,configs,operation_write,'IOPS')
            if bench == 'S3bench':
                x_axis, data_read_TTFB_B1 = get_buildwise_data(version,build1,bench,configs,operation_read,'TTFB','Avg')
                x_axis, data_write_TTFB_B1 = get_buildwise_data(version,build1,bench,configs,operation_write,'TTFB','Avg')

            x_axis, data_read_throughput_B2 = get_buildwise_data(version,build2,bench,configs,operation_read,'Throughput')    
            x_axis, data_write_throughput_B2 = get_buildwise_data(version,build2,bench,configs,operation_write,'Throughput')
            if bench != 'Hsbench':
                x_axis, data_read_latency_B2 = get_buildwise_data(version,build2,bench,configs,operation_read,'Latency','Avg')
                x_axis, data_write_latency_B2 = get_buildwise_data(version,build2,bench,configs,operation_write,'Latency','Avg')
            else:
                x_axis, data_read_latency_B2 = get_buildwise_data(version,build2,bench,configs,operation_read,'Latency')
                x_axis, data_write_latency_B2 = get_buildwise_data(version,build2,bench,configs,operation_write,'Latency')

            x_axis, data_read_IOPS_B2 = get_buildwise_data(version,build2,bench,configs,operation_read,'IOPS')
            x_axis, data_write_IOPS_B2 = get_buildwise_data(version,build2,bench,configs,operation_write,'IOPS')
            if bench == 'S3bench':
                x_axis, data_read_TTFB_B2 = get_buildwise_data(version,build2,bench,configs,operation_read,'TTFB','Avg')
                x_axis, data_write_TTFB_B2 = get_buildwise_data(version,build2,bench,configs,operation_write,'TTFB','Avg')

        trace1 = go.Scatter(
            name = 'Read Throughput - {}'.format(build1),
            x = x_axis,
            y = data_read_throughput_B1,
            hovertemplate = '<br>%{y} MBps<br>'+
                            '<b>Read Throughput - {}</b><extra></extra>'.format(build1),
        )
        fig.add_trace(trace1)

        trace2 = go.Scatter(
            name = 'Write Throughput - {}'.format(build1),
            x = x_axis,
            y = data_write_throughput_B1,
            hovertemplate = '<br>%{y} MBps<br>'+
                            '<b>Write Throughput - {}</b><extra></extra>'.format(build1),  
        )
        fig.add_trace(trace2)

        trace3 = go.Scatter(
            name = 'Read Latency - {}'.format(build1),
            x = x_axis,
            y = data_read_latency_B1,
            hovertemplate = '<br>%{y} ms<br>'+
                            '<b>Read Latency - {}</b><extra></extra>'.format(build1),
        )
        fig.add_trace(trace3)

        trace4 = go.Scatter(
            name = 'Write Latency - {}'.format(build1),
            x = x_axis,
            y = data_write_latency_B1,
            hovertemplate = '<br>%{y} ms<br>'+
                            '<b>Write Latency - {}</b><extra></extra>'.format(build1),
        )
        fig.add_trace(trace4)

        trace5 = go.Scatter(
            name = 'Read IOPS - {}'.format(build1),
            x = x_axis,
            y = data_read_IOPS_B1,
            hovertemplate = '<br>%{y}<br>'+
                            '<b>Read IOPS - {}</b><extra></extra>'.format(build1),
        )
        fig.add_trace(trace5)

        trace6 = go.Scatter(
            name = 'Write IOPS - {}'.format(build1),
            x = x_axis,
            y = data_write_IOPS_B1,
            hovertemplate = '<br>%{y}<br>'+
                            '<b>Write IOPS - {}</b><extra></extra>'.format(build1),
        )
        fig.add_trace(trace6)

        if bench == 'S3bench':
            trace7 = go.Scatter(
                name = 'Read TTFB - {}'.format(build1),
                x = x_axis,
                y = data_read_TTFB_B1,
            hovertemplate = '<br>%{y} ms<br>'+
                                '<b>Read TTFB - {}</b><extra></extra>'.format(build1),     
            )
            fig.add_trace(trace7)

            trace8 = go.Scatter(
                name = 'Write TTFB - {}'.format(build1),
                x = x_axis,
                y = data_write_TTFB_B1,
                hovertemplate = '<br>%{y} ms<br>'+
                                '<b>Write TTFB - {}</b><extra></extra>'.format(build1),
            )
            fig.add_trace(trace8)

        if build2 != None:
            trace9 = go.Scatter(
                name = 'Read Throughput - {}'.format(build2),
                x = x_axis,
                y = data_read_throughput_B2,
                hovertemplate = '<br>%{y} MBps<br>'+
                                '<b>Read Throughput - {}</b><extra></extra>'.format(build2),
            )
            fig.add_trace(trace9)

            trace10 = go.Scatter(
                name = 'Write Throughput - {}'.format(build2),
                x = x_axis,
                y = data_write_throughput_B2,
                hovertemplate = '<br>%{y} MBps<br>'+
                                '<b>Write Throughput - {}</b><extra></extra>'.format(build2),
            )
            fig.add_trace(trace10)

            trace11 = go.Scatter(
                name = 'Read Latency - {}'.format(build2),
                x = x_axis,
                y = data_read_latency_B2,
                hovertemplate = '<br>%{y} ms<br>'+
                                '<b>Read Latency - {}</b><extra></extra>'.format(build2), 
            )
            fig.add_trace(trace11)

            trace12 = go.Scatter(
                name = 'Write Latency - {}'.format(build2),
                x = x_axis,
                y = data_write_latency_B2,
                hovertemplate = '<br>%{y} ms<br>'+
                                '<b>Write Latency - {}</b><extra></extra>'.format(build2),
            )
            fig.add_trace(trace12)

            trace13 = go.Scatter(
                name = 'Read IOPS - {}'.format(build2),
                x = x_axis,
                y = data_read_IOPS_B2,
                hovertemplate = '<br>%{y}<br>'+
                                '<b>Read IOPS - {}</b><extra></extra>'.format(build2),        
            )
            fig.add_trace(trace13)

            trace14 = go.Scatter(
                name = 'Write IOPS - {}'.format(build2),
                x = x_axis,
                y = data_write_IOPS_B2,
                hovertemplate = '<br>%{y}<br>'+
                                '<b>Write IOPS - {}</b><extra></extra>'.format(build2),
            )
            fig.add_trace(trace14)

            if bench == 'S3bench':
                trace15 = go.Scatter(
                    name = 'Read TTFB - {}'.format(build2),
                    x = x_axis,
                    y = data_read_TTFB_B2,
                    hovertemplate = '<br>%{y} ms<br>'+
                                    '<b>Read TTFB - {}</b><extra></extra>'.format(build2),
                )
                fig.add_trace(trace15)

                trace16 = go.Scatter(
                    name = 'Write TTFB - {}'.format(build2),
                    x = x_axis,
                    y = data_write_TTFB_B2,
                    hovertemplate = '<br>%{y} ms<br>'+
                                    '<b>Write TTFB - {}</b><extra></extra>'.format(build2),
                )
                fig.add_trace(trace16)

    fig.update_layout(
        autosize=True,
        showlegend = True,
        title = 'All in One',
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
