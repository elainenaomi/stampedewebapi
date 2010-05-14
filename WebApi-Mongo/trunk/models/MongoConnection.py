'''
Created on Nov 1, 2009

@author: jecortez
'''
from pymongo.connection import Connection

class MongoConnection(object):
    '''
    classdocs
    '''
    def __init__(self, database=None, host="localhost", port=27017, options={}):
        port = options.get("dbPort", port)
        host = options.get("dbhost", host)
        database = options.get("dbname", database)
        
        self.dbconnection = Connection(host, port)
        self.db = self.dbconnection[database]

        
    def _getCollection(self, name):
        return self.db[name]
    
    def insert(self, collection, values):
        table = self._getCollection(collection)
        table.insert(values)
        
    def findAll(self, collection):
        table = self._getCollection(collection)
        return table.find()
        
    def find(self, collection, query, size=10, page=1, fields=[]):
        skip=(page-1)*size
        table = self._getCollection(collection)
        params = {}
        
        if len(fields)>0: params["fields"]=fields
        if size > 1:
            params["limit"]=size
            params["skip"]=skip
        
        if size == 1:
            params["spec_or_object_id"]=query
            return table.find_one(**params)
        else:
            params["spec"]=query
            return table.find(**params)
            
        
    def save(self, collection, item):
        table = self._getCollection(collection)
        table.save(item)
        
    def getUnique(self, collection, key):
        table = self._getCollection(collection)
        return table.distinct(key)
    
    def drop(self, collection):
        self.db.drop_collection(collection)