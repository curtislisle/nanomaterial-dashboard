import bson
import pymongo
import json
from bson import ObjectId
from pymongo import MongoClient
import string
import tangelo


def run(recordList):
    # Create an empty response object.
    response = {}
    response['status'] = ''
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
    #print record
    recordListJson = json.loads(recordList)

    # support a list of records, and check each one individually for a new NanomaterialID
    for rec in recordListJson:
        if (c.find({'NanomaterialID': rec['NanomaterialID']}).count() > 0):
            response["status"] = response['status'] + "nanomaterial already in database, id: %s\n" % (rec['NanomaterialID'])

        # if this is a new record, then add it to the database
        else:
            c.insert(rec)
            response["status"] = response['status'] + "added material id: %s\n" % (rec['NanomaterialID'])

    #tangelo.log(str(response))
    return json.dumps(response)
