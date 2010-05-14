'''
Created on Feb 1, 2010

@author: jecortez
'''
import models.MongoConnection as dbconn
import datetime, re
from time import mktime

#select count(id) from event 
#where time >= unix_timestamp('2007-11-30') and time < unix_timestamp('2007-12-01')
#and name = 'pegasus.invocation';
def jobsPerDay(options):
    connection = dbconn.MongoConnection("pegasus", "bass02")
    d=datetime.datetime(2009, 11, 12, 12)
    time=mktime(d.timetuple())+1e-6*d.microsecond
    
    query = {"timestamp": {"$lt": time}, "name":"pegasus.invocation"}
    count = connection.find("event", query, -1).count()
    
    return options['render_plain'].empty("count: "+str(count))

#select sum(value) from attr join event on e_id = id
#where time >= unix_timestamp('2007-11-30') and time < unix_timestamp('2007-12-01')
#and event.name = 'pegasus.invocation'  and attr.name = 'duration';
def runtime(options):
    connection = dbconn.MongoConnection("pegasus", "bass02")
    d=datetime.datetime(2009, 11, 12, 12)
    time=mktime(d.timetuple())+1e-6*d.microsecond
    
    query = {"timestamp": {"$lt": time}, "name":"pegasus.invocation"}
    
    result = connection._getCollection("event").group(None, query, { "csum": 0.0 }, "function(obj,prev) { prev.csum += parseFloat(obj.duration); }")
    return options['render_plain'].empty(result[0])

#select count(id), value from event join attr on e_id = id 
#where event.name = 'pegasus.invocation' and attr.name = 'host' 
#group by value;
def jobsOnHost(options):
    connection = dbconn.MongoConnection("pegasus", "bass02")
    
    query = {"name":"pegasus.invocation"}
    
    result = connection._getCollection("event").group(["host"], query, { "csum": 0 }, "function(obj,prev) { prev.csum += 1; }")
    return options['render_plain'].empty(result)

#select count(attr.e_id) from attr join ident on attr.e_id = ident.e_id
#where  attr.name = 'status' and ident.name='workflow' and ident.value
#LIKE 'CyberShake_WNGC%';
def totalJobs(options):
    connection = dbconn.MongoConnection("pegasus", "bass02")
    regex = re.compile("CyberShake.*") 
    query = {"comp-id":regex}
    result = connection.find("event", query, -1, fields=["status"])
    count = result.count()
    
    return options['render_plain'].empty("count: "+str(count))

#select count(attr.e_id) from attr join ident on attr.e_id = ident.e_id
#where  attr.name = 'status' and attr.value = '0' and
#ident.name='workflow' and ident.value LIKE 'CyberShake_WNGC%';
def totalJobsSucceeded(options):
    connection = dbconn.MongoConnection("pegasus", "bass02")
    regex = re.compile("CyberShake_.*") 
    query = {"comp-id":regex, "status":"0"}
    count = connection.find("event", query, -1, fields=["status"]).count()
    
    return options['render_plain'].empty("count: "+str(count))

#select attr.value, count(attr.e_id) from attr 
#join ident on attr.e_id = ident.e_id
#where  ident.name='workflow' and ident.value LIKE 'CyberShake_WNGC%'  and
#       attr.name='type' group by attr.value;
def breakdownOfJobs(options):
    connection = dbconn.MongoConnection("pegasus", "bass02")
    regex = re.compile("CyberShake_.*") 
    query = {"comp-id":regex}
    jFunction = "function(obj,prev) { prev.elems.push(obj); }"
    result = connection._getCollection("event").group(["type"], query, {"elems":[]}, jFunction)
    return options['render_plain'].empty(result)

#select sum(attr.value) from attr join ident on attr.e_id=ident.e_id
#where attr.name='duration' and ident.name='workflow' and ident.value
#LIKE 'CyberShake_WNGC%';
def totalRuntimeOfJobs(options):
    connection = dbconn.MongoConnection("pegasus", "bass02")
    regex = re.compile("CyberShake_.*")
    regex2 = re.compile(".*")
    query = {"comp-id":regex, "duration":regex2}
    
    result = connection._getCollection("event").group(None, query, { "csum": 0.0 }, "function(obj,prev) { prev.csum += parseFloat(obj.duration); }")
    return options['render_plain'].empty(result)

#select TRANSFORMATION, count(TRANSFORMATION) as number
# ,round(sum(attr.value),2) as sum_seconds,
# round(sum(attr.value)/(3600),2) as sum_hours, round(avg(attr.value),2)
# as avg_seconds from attr join (select attr.e_id as event_id,
# attr.value as TRANSFORMATION from  attr join ident on
# attr.e_id=ident.e_id  where attr.name='type' and
# ident.name='workflow' and ident.value LIKE 'CyberShake_USC%') ident
# on attr.e_id=event_id WHERE attr.name='duration' group by
# TRANSFORMATION;
def runtimeBreakdownByJobPerWorkflow(options):
    pass

#select TRANSFORMATION, count(TRANSFORMATION) as failures from attr
#join (select attr.e_id as event_id, attr.value as TRANSFORMATION from
#attr join ident on attr.e_id=ident.e_id  where attr.name='type' and
#ident.name='workflow' and ident.value LIKE 'CyberShake_USC%') ident on
#attr.e_id=event_id WHERE attr.name = 'status' and attr.value != '0'
#group by TRANSFORMATION;
def failuresByJobPerWorkflow(options):
    pass

def invokeAction(action, options):
    print action
    if action == "jobsPerDay":
        return jobsPerDay(options)
    elif action == "runtime":
        return runtime(options)
    elif action == "jobsOnHost":
        return jobsOnHost(options)
    elif action == "totalJobsSucceeded":
        return totalJobsSucceeded(options)
    elif action == "breakdownOfJobs":
        return breakdownOfJobs(options)
    elif action == "totalJobs":
        return totalJobs(options)
    elif action == "totalRuntimeOfJobs":
        return totalRuntimeOfJobs(options)
    