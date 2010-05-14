'''
Created on Nov 2, 2009

@author: jecortez
'''
import models.MongoConnection as dbconn
import json, re, pymongo, web
from datetime import datetime
import dateutil.parser
from web import webapi


###
#Constants
###
#db keys
JOB_KEY = "job"
JOBSTATE_KEY = "jobstate"
EDGE_NODE = "condor.dag.edge"

#job states
JOB_SUBMITTED = "SUBMIT"
JOB_STARTED = "EXECUTE"
JOB_TERMINATED = "JOB_TERMINATED"
JOB_COMPLETED = "JOB_SUCCESS"
JOB_FAILED = "JOB_FAILURE"
JOB_KICKSTART_STARTED = "POST_SCRIPT_STARTED"
JOB_KICKSTART_TERMINATED = "POST_SCRIPT_TERMINATED"
JOB_KICKSTART_COMPLETED = "POST_SCRIPT_SUCCESS"
JOB_KICKSTART_FAILED = "POST_SCRIPT_FAILURE"

def _prepareJSON(data):
    """Set reponse headers and encode JSON"""
    webapi.header("content-type", "application/json")
    return json.dumps(data)

def _addTimeCeilingToQuery(query):
    """Add a snapshot string to the mongo query"""
    if "timeCeiling" in web.input():
        query["timestamp"] = {"$lt": float(web.input()["timeCeiling"])}
        print("snapshot as of "+web.input()["timeCeiling"])
    return query

def _getPageAndlimit(default_page=1, default_limit=-1):
    retval = {"page":default_page, "limit":default_limit}
    if "page" in web.input() and web.input()["page"] > 0:
        retval["page"] = int(web.input()["page"])
    if "limit" in web.input() and web.input()["limit"] > 0:
        retval["limit"] = int(web.input()["limit"])
    return retval

def _getWorkflowState(options, connection, id):
    """Find the latest job event in the workflow and use that as the workflow state"""
    #find Last job invocation
    workflowsEndQuery = {"event":JOBSTATE_KEY, "wf_uuid":id}
    workflowsEndEvent = connection.find(options["dbeventtable"], _addTimeCeilingToQuery(workflowsEndQuery), -1).sort("timestamp", pymongo.DESCENDING)
    
    if workflowsEndEvent and workflowsEndEvent.count() > 0:
        return workflowsEndEvent[0]["state"], float(workflowsEndEvent[0]["timestamp"])
    else:
        return None, -1

def _getWorkflow(options, connection, id):
    """Get workflow information"""
    query = {"wf_uuid":id}
    
    workflowsCount = connection.find(options["dbeventtable"], _addTimeCeilingToQuery(query), 1)
    if workflowsCount == None:
        return None
    
    #find first job invocation
    workflowsStartQuery = {"event":JOBSTATE_KEY, "state":JOB_SUBMITTED, "wf_uuid":id, }
    workflowStartEvent = connection.find(options["dbeventtable"], _addTimeCeilingToQuery(workflowsStartQuery), -1).sort("timestamp", pymongo.ASCENDING)
    workflowStart = float(workflowStartEvent[0]["timestamp"])
    
    workflowsEndEventState, workflowsEnd = _getWorkflowState(options, connection, id)
    
    submittedQuery = {"event":"jobstate", "state":JOB_SUBMITTED, "wf_uuid":id}
    workflowsSubmitted = connection.find(options["dbeventtable"], _addTimeCeilingToQuery(submittedQuery), -1, fields=["wf_uuid"]).count()
    
    runningQuery = {"event":"jobstate", "state":JOB_STARTED, "wf_uuid":id}
    workflowsRunning = connection.find(options["dbeventtable"], _addTimeCeilingToQuery(runningQuery), -1, fields=["wf_uuid"]).count()
    
    completedQuery = {"event":"jobstate", "state":JOB_COMPLETED, "wf_uuid":id}
    workflowsCompleted = connection.find(options["dbeventtable"], _addTimeCeilingToQuery(completedQuery), -1, fields=["wf_uuid"]).count()
    
    failedQuery = {"event":"jobstate", "state":JOB_FAILED, "wf_uuid":id}
    workflowsFailed = connection.find(options["dbeventtable"], _addTimeCeilingToQuery(failedQuery), -1, fields=["wf_uuid"]).count()
    
    #calculate current states
    workflowsSubmitted = workflowsSubmitted-workflowsRunning
    workflowsRunning = workflowsRunning-(workflowsCompleted+workflowsFailed)
    
    workflow = {"id":id, 
                "state":workflowsEndEventState,
                "lastEvent": workflowsEnd,
                "runtime": workflowsEnd - workflowStart,  
                "jobStatus": {"submitted":workflowsSubmitted, 
                              "running":workflowsRunning, 
                              "completed":workflowsCompleted, 
                              "failed":workflowsFailed},
                "submitted":workflowStart, 
                }
    
    return workflow
    

def getAllWorkflows(options):
    """Get all workflows and thier states"""
    connection = dbconn.MongoConnection(options=options)
    resultSet = connection.getUnique(options["dbeventtable"], "wf_uuid")
    
    dataLimits = _getPageAndlimit()
    page = dataLimits["page"]
    limit = dataLimits["limit"]
    if limit > 0:
        resultSet = resultSet[(page-1)*limit:limit*page]
    
    results = []
    for workflowID in resultSet:
        result = {"id":workflowID}
        result["state"], result["lastEvent"] = _getWorkflowState(options, connection, workflowID)
        if(result["state"]):
            results.append(result)
        
    return _prepareJSON(results)
    
def getWorkflow(options, id):
    """Get a specific workflow"""
    connection = dbconn.MongoConnection(options=options)

    workflow = _getWorkflow(options, connection, id)
    
    if workflow == None: raise web.NotFound("Workflow %s not found" % id)
    
    return _prepareJSON(workflow)

def _getJob(options, connection, workflow, id):
    """Get Job information"""
    query = {"wf_uuid": workflow["id"], "event":JOBSTATE_KEY, "name":id}
    jobs = connection.find(options["dbeventtable"], _addTimeCeilingToQuery(query), -1).sort("timestamp", pymongo.ASCENDING)
    
    if jobs.count() == 0:
        return None
    
    earliestJob = jobs[0]
    latestJob = jobs[jobs.count()-1]
    
    job = { "id":id,
            "state":latestJob["state"],
            "submitted": float(earliestJob["timestamp"]),
            "runtime":float(latestJob["timestamp"]) - float(earliestJob["timestamp"])
            }
    
    return job

def getJobs(options, workflowId):
    """Get all jobs for a specific workflow"""
    connection = dbconn.MongoConnection(options=options)
    
    workflow = _getWorkflow(options, connection, workflowId)
    
    if workflow == None: raise web.NotFound("Workflow %s not found" % workflowId)
    
    dataLimits = _getPageAndlimit(1, -1)
    
    query = {"wf_uuid":workflowId, "event":JOB_KEY}
    allJobs = connection.find(options["dbeventtable"], _addTimeCeilingToQuery(query),
                              size=dataLimits["limit"], page=dataLimits["page"], forceFindMany=True)
    
    jobs = []
    for job in allJobs:
        newJob = _getJob(options, connection, workflow, job["name"])
        if newJob:
            jobs.append(newJob)
    
    return _prepareJSON(jobs)

def getJob(options, workflowId, id):
    """Get a specific job"""
    connection = dbconn.MongoConnection(options=options)
    
    workflow = _getWorkflow(options, connection, workflowId)
    
    if workflow == None: raise web.NotFound("Workflow %s not found" % workflowId)
    
    job = _getJob(options, connection, workflow, id)
    
    if job == None: raise web.NotFound("Job %s not found" % id)
            
    return _prepareJSON(job)

def getChildJobs(options, workflow, jobId):
    """Get child Job ID's of a specific job"""
    connection = dbconn.MongoConnection(options=options)
    
    ataLimits = _getPageAndlimit(1, -1)
    
    childQuery = {"event":EDGE_NODE, "comp-child-id" : jobId}
    childJobs = connection.find(options["dbeventtable"], childQuery,
                              size=dataLimits["limit"], page=dataLimits["page"])
    
    children = [node["comp-child-id"] for node in childJobs]
    
    return _prepareJSON(children)
    
def getParentJobs(options, workflow, jobId):
    """Get parent ID's of a specific job"""
    connection = dbconn.MongoConnection(options=options)
    
    dataLimits = _getPageAndlimit(1, -1)
    
    parentQuery = {"event":EDGE_NODE, "comp-parent-id" : jobId}
    parentJobs = connection.find(options["dbeventtable"], parentQuery,
                              size=dataLimits["limit"], page=dataLimits["page"], forceFindMany=True)
    
    parents = [node["comp-parent-id"] for node in parentJobs]
    
    return _prepareJSON(parents)
        
def invokeAction(action, options):
    if action == "unique" or action == "all" or action == "":
        print "Unique jobs"
        return getAllWorkflows(options)
    
    splitAction = action.split("/")
    print splitAction
    if len(splitAction) > 1:
        if "jobs" in splitAction[-1]:
            print "All Jobs"
            return getJobs(options, splitAction[0])
        elif "parents" in splitAction[-1]:
            print "Workflow Root: "+splitAction[0]
            print "Parents: "+splitAction[1]
            return getParentJobs(options, splitAction[0], splitAction[1])
        elif "children" in splitAction[-1]:
            print "Workflow Root: "+splitAction[1]
            print "Children: "+splitAction[-1]
            return getChildJobs(options, splitAction[0], splitAction[1])
        else:
            print "Workflow Root: "+splitAction[0]
            print "Job: "+splitAction[1]
            return getJob(options, splitAction[0], splitAction[1])
    
    #is a workflow
    print "Workflow: "+action
    return getWorkflow(options, action)