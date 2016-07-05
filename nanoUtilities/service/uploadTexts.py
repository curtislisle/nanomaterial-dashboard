import sys, pymongo, os, glob, re, bson.json_util, json, time, datetime, math, subprocess, base64
from bson.objectid import ObjectId
from pymongo import MongoClient
from bson.dbref import DBRef
from bson.json_util import dumps
from bson.code import Code
import string, tangelo
import csv



def run(filename=None,filecontents=None,directory=None,):

        response = {}

        print filename,filecontents, directory
        
    	print 'uploading ',filename
        fullpath = directory+'/'+filename
        fout = open(fullpath,'w')
        fout.write(filecontents)
        fout.close()
        response['results'] = filename
        return bson.json_util.dumps(response)
