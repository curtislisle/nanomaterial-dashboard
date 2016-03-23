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
    response['file'] = "http://localhost:8080/service/dataset-content-phoenix/ist-qcr/phoenix"
    response['name'] = "Phoenix Event QCR mongoDB feed"
    response['separator'] = ','
    response['skip'] = 0
    response['meta'] = [ 
        { "type": "id", "name": "EventID" },
        {'name': 'NormIntensityUnique','type':'float'}, 
        {'name': 'NormIntensityTotal','type':'float'}, 
        {'name': 'PropTotalSources','type':'float'},
        {'name': 'UniqueSources','type':'string'},
        {'name': 'GoldsteinScore','type':'float'},
        {'name': 'SourceActorFull','type':'string'},
        {'name': 'TargetActorFull','type':'string'},
        {'name': 'SampleTitle','type':'string'},
        {'name': 'Lat','type':'float'},
        {'name': 'Lon','type':'float'}]
    response['sets'] = [
        { "format": "binary", "start": 1, "end": 5}]
    response['setlist'] = ['Neutral','VerbalCooperation','MaterialCooperation','VerbalConflict','MaterialConflict',
                'Iran','Iraq','Eqypt','Syria','Afghanistan',
                'wn_world','wn_politics','wn_africa','wn_mideast','malstar_world',
                'egypt_dailynews', 'manafn_iraq', 'menafn_syria','menafn_saudi','aljazeera'
                ]
    response['attributelist'] = []
    response['author'] = 'KnowledgeVis, LLC'
    response['description'] = 'created by Tangelo service'
    response['source'] = "QCR program feed"
   

    #tangelo.log(str(response))
    return json.dumps(response)
