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
    connection = MongoClient('xd-mongo.xdata.data-tactics-corp.com', 27017)
    db = connection[dbname]
    dataset_collection = db[tablename]

    # build query for Phoenix. focus returns on middle east countries
    query = { '$or' : [
        {'CountryCode': 'IRN'},
        {'CountryCode': 'AFG'},
         {'CountryCode': 'IRQ'},       
        {'CountryCode': 'SYR'},
        {'CountryCode': 'EGY'}     
    ]};
    table = dataset_collection.find(query,{'_id':0})

    # copy out of the mongodb cursor type to a python list
    for x in table:
        # now add the binary sets.  In each case, the identify of a multi-valued field is tested and turned
        # into an additional binary set attribute
        x['Iran'] = 1 if (x['CountryCode']=='IRN') else 0
        x['Iraq'] = 1 if (x['CountryCode']=='IRQ') else 0
        x['Syria'] = 1 if (x['CountryCode']=='SYR') else 0
        x['Egypt'] = 1 if (x['CountryCode']=='EGY') else 0
        x['Afghanistan'] = 1 if (x['CountryCode']=='AFG') else 0 
        x['wn_world'] = 1 if (x['NewsSources']=='wn_world') else 0 
        x['wn_politics'] = 1 if (x['NewsSources']=='wn_politics') else 0
        x['wn_africa'] = 1 if (x['NewsSources']=='wn_africa') else 0
        x['wn_mideast'] = 1 if (x['NewsSources']=='wn_mideast') else 0 
        x['malstar_world'] = 1 if (x['NewsSources']=='malstar_world') else 0
        x['egypt_dailynews'] = 1 if (x['NewsSources']=='egypt_dailynews') else 0
        x['manafn_iraq'] = 1 if (x['NewsSources']=='manafn_iraq') else 0
        x['menafn_syria'] = 1 if (x['NewsSources']=='menafn_syria') else 0
        x['menafn_saudi'] = 1 if (x['NewsSources']=='menafn_saudi') else 0
        x['aljazeera'] = 1 if (x['NewsSources']=='aljazeera') else 0
        x['Neutral'] = 1 if (x['QuadClass']==0) else 0
        x['VerbalCooperation'] = 1 if (x['QuadClass']==1) else 0
        x['MaterialCooperation'] = 1 if (x['QuadClass']==2) else 0
        x['VerbalConflict'] = 1 if (x['QuadClass']==3) else 0
        x['MaterialConflict'] = 1 if (x['QuadClass']==4) else 0
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
