'''
Created on Nov 8, 2009

@author: jecortez
'''
import web, random
import models.MongoConnection as dbconn
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

def streamingDuration(options):
    return options["render"].streamingAverages()

def _pidSorter(xOrig,yOrig):
    x = int(str(xOrig).upper().split("PID")[1])
    y = int(str(yOrig).upper().split("PID")[1])
    if x>y:
        return 1
    elif x==y:
        return 0
    else: # x<y
        return -1

def startFillDB(options):
    connection = dbconn.MongoConnection(options["dbname"], options["dbhost"])
    connection.drop("workflowDurations")
    workflowIds = connection.getUnique("event", "workflow-id")
    workflowIds.sort(_pidSorter)
    for workflowId in workflowIds:
        connection.insert("workflowDurations", {"workflow-id":workflowId, "durations":{}})
    
    for workflowId in workflowIds:
        events = connection.find("event", {"workflow-id":workflowId}, -1)
        
        record = connection.find("workflowDurations", {"workflow-id":workflowId}, 1)[0]
        
        for event in events:
            compid = str(event["comp-id"]).split("_")[0]
            if(compid in record["durations"]):
                record["durations"][compid]+=float(event["duration"])
            else:
                record["durations"][compid]=float(event["duration"])
        
        connection.save("workflowDurations", record)
        print("Generated datastream: "+workflowId)
    
    raise web.seeother("/charts/streamingDuration")

def _makeChartNode(name, values):
    retval= """{"PID":"%(name)s",""" % {"name":name}
    events=[]
    for key, value in values.items():
        events.append(""""%(key)s":%(value)f""" % {"key": key, "value":value})
    retval+=",".join(events)
    retval+="}"
    return retval

def streamingDurationData(options):
    connection = dbconn.MongoConnection(options["dbname"], options["dbhost"])
        
    nodes = []
    for entry in connection.findAll("workflowDurations"):
        nodes.append(_makeChartNode(entry["workflow-id"], entry["durations"]))
        #if(len(nodes)>10):
        #    break;

    json = """{"Results":["""
    json += ','.join(nodes)
    json += "]}"
    return options['render_plain'].empty(json)

def staticDurationChart(options):
    connection = dbconn.MongoConnection(options["dbname"], options["dbhost"])
    
    wfldur = connection.findAll("workflowDurations")
    names = []
    durations = []
    for wfl in wfldur:
        names.append(str(wfl["workflow-id"]))
        durations.append(float(wfl["durations"]))
    
    fig=Figure()
    ax=fig.add_subplot(111)
    
    ax.bar(names, durations, 0.35)
    canvas=FigureCanvas(fig)
    filename = "static/chart-"+str(random.randint(0, 1000))+".png"
    canvas.print_png(filename)
    
    raise web.seeother("/"+filename)