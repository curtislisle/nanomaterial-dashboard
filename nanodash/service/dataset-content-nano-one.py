#import bson
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

    # build query for Phoenix. focus returns on middle east countries
    query = {};
    table = dataset_collection.find(query,{'_id':0})

    # copy out of the mongodb cursor type to a python list
    for x in table:
        # now add in binary sets.  In each case, the identify of a multi-valued field is tested and turned
        # into an additional binary set attribute
        x['Aromatic'] = 1 if (x['Aromatic']=='yes') else 0
        x['VHQ-R subset'] = 1 if (x['VHQ-R subset']=='yes') else 0
        x['Macrocyclic'] = 1 if (x['Macrocyclic']=='yes') else 0
        x['VHQ-R subset'] = 1 if (x['VHQ-R subset']=='yes') else 0
  
        # add the extended row to the dataset returned for analysis
        response['data'].append(x)

    table.rewind()

    # find the column headers
    for col in table[0]:
        response['header'].append(col)
   
    print "response:",response
    # convert to string to pass through URL callback
    #tangelo.log(str(response))
    return json.dumps(response)
