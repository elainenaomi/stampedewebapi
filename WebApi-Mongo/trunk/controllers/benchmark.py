'''
Created on Feb 3, 2010

@author: jecortez
'''

def run(options):
    return options["render"].benchmark()

def invokeAction(action, options):
    print action
    if action == "run":
        return run(options)