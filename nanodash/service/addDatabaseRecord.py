import bson
import pymongo
import json
from bson import ObjectId
from pymongo import MongoClient
import string
import tangelo


def run(record):
    # Create an empty response object.
    response = {}
     # Get a handle to the database collection.
    try:
        connection = pymongo.Connection('localhost',27017)
        db = connection['NanoDB3']
        c = db['Nano_combined_0225']

    # if there is a problem connecting to the database, return an error to the caller    
    except pymongo.errors.AutoReconnect as e:
        response['status'] = 'Failure'
        response["error"] = "database error: %s" % (e.message)
        return json.dumps(response)

    #try:
    #    recordJson = json.loads(record)
    #except:
    #    response['status'] = 'Failure'
    #    response["error"] = "can't decode record: %s" % record
    #    return json.dumps(response)     

    # check to see if this material is arleady in the dashboard.  Refuse to add a new record if
    # this material is already present. 
    print record
    recordJson = json.loads(record)

    if (c.find({'NanomaterialID': recordJson['NanomaterialID']}).count() > 0):
        response['status'] = 'Failure'
        response["error"] = "nanomaterial already in database, id: %s" % (recordJson['NanomaterialID'])

    # if this is a new record, then add it to the database
    else:
        c.insert(recordJson)
        response['status'] = 'Success'

    #tangelo.log(str(response))
    return json.dumps(response)
