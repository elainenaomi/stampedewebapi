'''
Created on Nov 1, 2009

@author: jecortez
'''
import web
#from controllers import charts
from controllers import workflow
#from controllers import benchmark
#from controllers import benchmarkQueries
#from controllers import benchmarkMySQLQueries

#web.config.debug = False

urls = (
        '/(.*)', 'index'
)

controllers = {'workflow':workflow
               #'charts':charts,
               #'benchmark':benchmark,
               #'benchmarkQueries':benchmarkQueries, 
               #'benchmarkMySQLQueries':benchmarkMySQLQueries
               }

app = web.application(urls, globals())


options = {"render_plain": web.template.render('views/'),
           "render": web.template.render('views/', base='layout'),
           "dbhost": "bass02",
           "dbname": "pegasusLigoCombined2",
           "dbeventtable": "netlogger"
           }

class index:
    def GET(self, query):
        query = str(web.webapi.ctx.path)
        
        #strip trailing /'s
        if query[-1] == "/":
            query = query[:-1]
        
        splitQuery = query.split("/", 2)
        controller = splitQuery[1]
        action=""
        if len(splitQuery)>2:
            action = splitQuery[2]
        controllerClass=controllers[controller]
        return controllerClass.invokeAction(action, options)
    def POST(self, query):
        return self.GET(query)

#if __name__ == "__main__": app.run()
application = web.application(urls, globals()).wsgifunc()
