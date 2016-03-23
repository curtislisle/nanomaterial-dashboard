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
    response['file'] = "http://localhost:8080/service/dataset-content/nano/fruit"
    response['name'] = "Fruit Info"
    response['separator'] = ','
    response['skip'] = 0
    response['meta'] = [ 
        { "type": "id", "index": 0, "name": "Name" },
        {'name':'Taste','type':'string', 'index':6}, 
        {'name':'Weight','type':'float','index':7}]
    response['sets'] = [
        { "format": "binary", "start": 1, "end": 5}]
    response['setlist'] = ['Green','Red','Vegetable','Fruit','Delicious']
    response['attributelist'] = []
    response['author'] = 'Curt'
    response['description'] = 'created by Tangelo service'
    response['source'] = "http://comtrade.un.org/"
   

    #tangelo.log(str(response))
    return json.dumps(response)
