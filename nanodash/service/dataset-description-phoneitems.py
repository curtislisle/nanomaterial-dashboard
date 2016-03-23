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
    response['file'] = "http://localhost:8080/service/dataset-content-phoneitems"
    response['name'] = "Phone Item Exploration"
    response['separator'] = ','
    response['skip'] = 0
    response['meta'] = [ 
        { "type": "id", "name": "PhoneItemID" },
        {"type":"string", "index": 6, "name": "Text"},
        {"type":"string", "index": 6, "name": "Name"},
        {"type":"string", "index": 6, "name": "Email"}        ]
    response['sets'] = [
        { "format": "binary", "start": 1, "end": 5}]
    response['setlist'] = ['calls','contacts','messages_and_chats','web_history',
                            'messages','accounts','messages_and_emails','images','networks',
                            'MatchedContact','Incoming','Sent','Unsent','SendFailed'
                            ]
    response['attributelist'] = []
    response['author'] = 'KnowledgeVis, LLC'
    response['description'] = 'created by Tangelo service'
    response['source'] = "QCR program feed"
   

    #tangelo.log(str(response))
    return json.dumps(response)
