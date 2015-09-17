# Getting started with the Web API #

The web framework is built upon the minimal web.py framework.  It only supports basic routing at this time.


## Sample routing walk through ##

Request URL: http://awp.cs.usfca.edu/workflow/unique
  1. On every request, the first python module called is dispatcher.py. It looks at the url root, in this case, “workflow.” There is a dictionary in dispatcher.py that maps this url section to a controller. In this case, it will route the request to “controllers/workflow.py.”
  1. In every controller module, there must be a method called invokeAction. This method takes in the remaining part of the url and decides which function to call, in the case “unique” gets mapped to a method called “getAllWorkflows.”
  1. The final function does the business logic, then returns the JSON string.

# Templating #

The templates in the framework use the simple templating found in web.py. All templates must be located within the views folder. In general the templates only contain code for the body of the page. To modify the general layout (metadata, header, footer, etc.) look at layout.html.

In some cases, you may not want the layout to be rendered. In this case you should just return a string instead of the normal options[“render”].

Static files are always served out of the /static folder in the project. They are referenced the same way, (ie, ![http://awp.cs.usfca.edu/static/funncatpicture.jpg](http://awp.cs.usfca.edu/static/funncatpicture.jpg)).

For more information about how to construct the actual templates, look at http://webpy.org/docs/0.3/templetor