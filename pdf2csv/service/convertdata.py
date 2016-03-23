import sys, pymongo, os, glob, re, bson.json_util, json, time, datetime, math, subprocess, base64

from bson.objectid import ObjectId

from pymongo import MongoClient

from bson.dbref import DBRef

from bson.json_util import dumps

from bson.code import Code

import string, tangelo

import csv


client = MongoClient('dm-machine.ncifcrf.gov', 27017);


    
def removeBadCharsFromHeaders(header):
    #loop through the columns and remove 
    header2 = []
    for col in range(len(header)):
        newstr = header[col].replace('.','')
        newstr2 = newstr.replace(',','_')
        #print 'replaced:',header[col]," with ",newstr2
        header2.append(newstr2)
    return header2    
    


def run():
	response = {}
	
	db = client["test"]
	fullcoll = db["Nanomaterials"]
	
	result = fullcoll.find({})
	
	NMS = db["NanomaterialStatuses"]
	i = 0
	for d in result:
		#arr = d
		NMSresult = NMS.find({"MaterialStatusID":d['MaterialStatusID']})
		d["NanomaterialStuff"] = NMSresult
		#response[i] = d['MaterialStatusID']
		#i += 1
	
	response['result'] = result	
		
		
	
	tangelo.log(str(response))
	return bson.json_util.dumps(response)
	
	
