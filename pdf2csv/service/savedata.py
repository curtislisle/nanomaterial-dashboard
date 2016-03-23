import sys, pymongo, os, glob, re, bson.json_util, json, time, datetime, math, subprocess, base64

from bson.objectid import ObjectId

from pymongo import MongoClient

from bson.dbref import DBRef

from bson.json_util import dumps

from bson.code import Code

import string, tangelo

import csv

#client = MongoClient('fr-s-ivg-mdb.ncifcrf.gov', 29022);
client = MongoClient();
    
def removeBadCharsFromHeaders(header):
    #loop through the columns and remove 
    header2 = []
    for col in range(len(header)):
        newstr = header[col].replace('.','')
        newstr2 = newstr.replace(',','_')
        #print 'replaced:',header[col]," with ",newstr2
        header2.append(newstr2)
    return header2    
    


def run(data=None, fileName=None, orientation=None):
	data = json.loads(data)
	
	db = client["NanoDB3"]
	fullcoll = db["saved_pdf_data"]
	response = {}
	tmpDict = {}
	tmpDict['data'] = data
	tmpDict['fileName'] = fileName
	tmpDict['orientation'] = orientation
	tmpDict['datetime'] = datetime.datetime.utcnow()
	fullcoll.insert(tmpDict)
	response['success'] = "insert successful"
	
	#tangelo.log(str(response))
	return bson.json_util.dumps(response)
	
	
