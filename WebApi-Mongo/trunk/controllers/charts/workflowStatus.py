'''
Created on Nov 8, 2009

@author: jecortez
'''
import web, random
import models.MongoConnection as dbconn
from math import *
from datetime import *

TIMESTEPS = 25

def streamingDuration(options):
    return options["render"].streamingStatuses()

def streamingStatusData(options):
    connection = dbconn.MongoConnection(options["dbname"], options["dbhost"])
        
    nodes = []
    for entry in connection.findAll("workflowStatuses"):
        
        nodes.append(_makeChartNode(entry["comp-id"], entry["timestamps"], entry["derived"]))

    json = """{"Results":["""
    json += ','.join(nodes)
    json += "]}"
    return options['render_plain'].empty(json)

def prettyStamp(stamp):
    return stamp.strftime("%I:%M %p")

def _makeChartNode(tick):
    return """{"Time":"%(Time)s", "Unsubmitted":%(Unsubmitted)d, "Submitted":%(Submitted)d, "Running":%(Running)d, "Completed":%(Completed)d, "Failed":%(Failed)d}""" % tick

def statusWorkflowData(workflowID, options):
    connection = dbconn.MongoConnection(options["dbname"], options["dbhost"])
    
    workflow={"workflow":workflowID, "completed":"", "start":"", "end":"", "jobs":[]}
    print "starting workflow", workflow
    
    query = {"event":"pegasus.invocation", "workflow-id":workflowID}
    invocationEvents = connection.find("event", query, -1)
    if invocationEvents.count() > 0:
        #get all submit times
        for event in invocationEvents:
            submittedJobQuery = {"event":"pegasus.jobstate.submit", "comp-id":event["comp-id"]}
            submittedJob = connection.find("event", submittedJobQuery, 1)[0]
            
            start = datetime.fromtimestamp(event['timestamp'])
            duration = timedelta(seconds=float(event['duration']))
            workflowJob = {"job":submittedJob["comp-id"], 
                           "submitted":datetime.fromtimestamp(submittedJob['timestamp']),
                           "start": start,
                           "duration": duration,
                           "end": start+duration,
                           "success": ( True if int(event['status'])==0 else False )
                          }
            workflow["jobs"].append(workflowJob);
    else:
        print "NO invocation records!"
    
    #sort invocation events by time
    #workflow['completed'] = ( True if int(baseEvent['status'])==0 else False )
    workflow['start'] = min(workflow["jobs"],key = lambda a: a.get("start"))["start"]
    workflow['end'] = max(workflow["jobs"],key = lambda a: a.get("end"))["end"]
    workflow['duration'] = workflow['end']-workflow['start']
    
    #create graph data
    ticks = [] #[{Time:"12:00 PM", Unsubmitted:8, Submitted:0, Running:0, Completed:0, Failed:0, Held:0},...]
    
    #what is my timestep?
    timestep = workflow['duration']/TIMESTEPS
    
    currentStep = workflow['start']
    while currentStep <= workflow['end']:
        unsubmitted = len(workflow["jobs"])
        submitted = 0
        running = 0
        completed=0
        failed=0
        
        for job in workflow["jobs"]:
            if job['submitted'] <= currentStep:
                submitted+=1
            if job['start'] <= currentStep:
                running+=1
            if job["end"] <=currentStep:
                completed+=1
            if not job["success"]:
                failed+=1
        
        tick = {"Time":prettyStamp(currentStep), "Unsubmitted":unsubmitted, "Submitted":submitted,\
                "Running":running, "Completed":completed, "Failed":failed}
        ticks.append(_makeChartNode(tick))
        currentStep+=timestep
                                         
    json = """{"Results":["""
    json += ','.join(ticks)
    json += "]}"
    return options['render_plain'].empty(json)
    
def flexChart(workflowID, options):
    return options['render_plain'].jobChartFlex(workflowID)