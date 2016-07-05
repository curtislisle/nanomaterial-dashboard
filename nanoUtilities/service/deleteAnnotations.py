import sys, pymongo, os, glob, re, bson.json_util, json, time, datetime, math, subprocess, base64
from bson.objectid import ObjectId
from pymongo import MongoClient
from bson.dbref import DBRef
from bson.json_util import dumps
from bson.code import Code
import string, tangelo
import csv



def run(filename=None,textpath=None,):

        response = {}
        print 'deleting text annotations for:',filename

        annotationfile = filename[:filename.find('.')]+'.ann'
        fullpath = textpath+'/'+annotationfile
        # delete the existing annotations
        os.remove(fullpath)
        # make a new, empty annotation name
        os.system('touch '+fullpath)
        return bson.json_util.dumps(response)
