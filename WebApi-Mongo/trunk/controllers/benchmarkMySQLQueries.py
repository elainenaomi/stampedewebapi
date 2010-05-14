'''
Created on Feb 1, 2010

@author: jecortez
'''
import MySQLdb

def getMySqlConnection():
    return MySQLdb.connect(host = "bass03",
                           user = "dang",
                           passwd = "hang10",
                           db = "pegasus")

def jobsPerDay(options):
    connection = getMySqlConnection()
    cursor = connection.cursor()
    cursor.execute("select count(event.id) from event where time >= unix_timestamp('2007-11-30') and time < unix_timestamp('2007-12-01') and name = 'pegasus.invocation';")
    
    return options['render_plain'].empty(cursor.fetchall())

def runtime(options):
    connection = getMySqlConnection()
    cursor = connection.cursor()
    cursor.execute("select sum(value) from attr join event on e_id = event.id where time >= unix_timestamp('2007-11-30') and time < unix_timestamp('2007-12-01') and event.name = 'pegasus.invocation'  and attr.name = 'duration';")
    
    return options['render_plain'].empty(cursor.fetchall())

def jobsOnHost(options):
    connection = getMySqlConnection()
    cursor = connection.cursor()
    cursor.execute("""select count(event.id), value from event join attr on e_id = event.id 
                        where event.name = 'pegasus.invocation' and attr.name = 'host' 
                        group by value;""")
    
    return options['render_plain'].empty(cursor.fetchall())

def totalJobs(options):
    connection = getMySqlConnection()
    cursor = connection.cursor()
    cursor.execute("""select count(attr.e_id) from attr join ident on attr.e_id = ident.e_id
                        where  attr.name = 'status' and ident.name='workflow' and ident.value
                        LIKE 'CyberShake_WNGC%';""")
    
    return options['render_plain'].empty(cursor.fetchall())

def totalJobsSucceeded(options):
    connection = getMySqlConnection()
    cursor = connection.cursor()
    cursor.execute("""select count(attr.e_id) from attr join ident on attr.e_id = ident.e_id
                    where  attr.name = 'status' and attr.value = '0' and
                    ident.name='workflow' and ident.value LIKE 'CyberShake_%';""")
    
    return options['render_plain'].empty(cursor.fetchall())

def breakdownOfJobs(options):
    connection = getMySqlConnection()
    cursor = connection.cursor()
    cursor.execute("""select attr.value, count(attr.e_id) from attr 
                        join ident on attr.e_id = ident.e_id
                        where  ident.name='workflow' and ident.value LIKE 'CyberShake_%'  and
                        attr.name='type' group by attr.value;""")
    
    return options['render_plain'].empty(cursor.fetchall())

def totalRuntimeOfJobs(options):
    connection = getMySqlConnection()
    cursor = connection.cursor()
    cursor.execute("""select sum(attr.value) from attr join ident on attr.e_id=ident.e_id
                        where attr.name='duration' and ident.name='workflow' and ident.value
                        LIKE 'CyberShake_%';""")
    
    return options['render_plain'].empty(cursor.fetchall())

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
    