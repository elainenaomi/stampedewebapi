'''
Created on Nov 2, 2009

@author: jecortez
'''
import random, datetime, web
import models.MongoConnection as dbconn
import workflowDurations, workflowStatus
        
def invokeAction(action, options):
    print "invoking action: ", action
    splitAction = action.split("/")
    action = splitAction[0]
    
    if action == "yuiChart":
        return samples.yuiChart(options)
    elif action == "chartData":
        return samples.chartData(options)
    elif action == "matPlotLibChart":
        return samples.matPlotLibChart(options)
    elif action == "startFillDB":
        return workflowDurations.startFillDB(options)
    elif action == "streamingDuration":
        return workflowDurations.streamingDuration(options)
    elif action == "streamingDurationFlex":
        raise web.seeother("/static/charts/chartExample.html")
    elif action == "streamingDurationData":
        return workflowDurations.streamingDurationData(options)
    elif action == "staticDurationChart":
        return workflowDurations.staticDurationChart(options)
    elif action == "dag":
        return dag.dag(options)
    elif action == "status":
        if splitAction[1] == "data":
            return workflowStatus.streamingStatusData(options)
        if splitAction[1] == "chart":
            return workflowStatus.flexChart(splitAction[2], options)
        else:
            return workflowStatus.statusWorkflowData(splitAction[1], options)
