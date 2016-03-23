import bson
import pymongo
import json
from bson import ObjectId
from pymongo import MongoClient
import string
import tangelo


def run(dbname,tablename):
    # Create an empty response object.
    response = {}
    response['data'] = []
    response['header'] = []

    # open a connection and copy the entire database
    connection = MongoClient('localhost', 27017)
    db = connection[dbname]
    dataset_collection = db[tablename]
    table = dataset_collection.find({},{'_id':0})

    # copy out of the mongodb cursor type to a python list
    for x in table:
        response['data'].append(x)

    table.rewind()

    # find the column headers
    for col in table[0]:
        response['header'].append(col)
   
    print "response:",response
    # convert to string to pass through URL callback
    #tangelo.log(str(response))
    return json.dumps(response)
