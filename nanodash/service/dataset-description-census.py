import bson
import pymongo
import json
from bson import ObjectId
from pymongo import MongoClient
import string
import tangelo


def run():
    # Create an empty response object.
    response = {}
    response['datasource'] = 'remote'
    response['file'] = "http://localhost:8080/service/dataset-content-census/census_hackathon/permits_alligned"
    response['name'] = "Census Building Permit Alignment"
    response['separator'] = ','
    response['skip'] = 0
    response['meta'] = [ 
        { "type": "id", "name": "RetrieveCount" },
        {"type":"string", "index": 6, "name": "category"},
        {"type":"string", "index": 6, "name": "status"},
        {"type":"string", "index": 6, "name": "permit_type"},
        {"type":"string", "index": 6, "name": "ReceiverKey"}        
           ]
    response['sets'] = [
        { "format": "binary", "start": 1, "end": 5}]
    response['setlist'] = ['Boston','Seattle','Baltimore',
                            'SingleFamily','MultiFamily','Commercial','UnknownType','IssuedPermit','Occupancy'
                            ]
    response['attributelist'] = []
    response['author'] = 'KnowledgeVis, LLC'
    response['description'] = 'Building Permit Data Auto-retrieved'
    response['source'] = "Harvested from Smart Cities API"
   

    #tangelo.log(str(response))
    return json.dumps(response)
