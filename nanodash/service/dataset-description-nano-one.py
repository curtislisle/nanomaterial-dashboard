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
    response['file'] = "http://localhost:8080/service/dataset-content-nano-one/nano/nano0826"
    response['name'] = "Nano Database Prototype"
    response['separator'] = ','
    response['skip'] = 0
    response['meta'] = [ 
        { "type": "id", "name": "OpenEye Name" },
        {'name':'Bmean','type':'float'}, 
        {'name':'Solvent','type':'float'}, 
        {'name':'nheavy_atoms','type':'integer','index':7}]
    response['sets'] = [
        { "format": "binary", "start": 1, "end": 5}]
    response['setlist'] = ['Aromatic','Macrocyclic','Sugar','VHQ-R subset', 'UHQ-R subset']
    response['attributelist'] = []
    response['author'] = 'KnowledgeVis, LLC'
    response['description'] = 'created by Tangelo service'
    response['source'] = "ABCC Imaging and Visualization Group"
   

    #tangelo.log(str(response))
    return json.dumps(response)
