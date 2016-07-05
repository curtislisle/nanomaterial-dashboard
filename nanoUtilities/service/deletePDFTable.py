import sys, pymongo, os, glob, re, bson.json_util, json, time, datetime, math, subprocess, base64
from bson.objectid import ObjectId
from pymongo import MongoClient
from bson.dbref import DBRef
from bson.json_util import dumps
from bson.code import Code
import string, tangelo
import csv


client = MongoClient('localhost', 27017);


def run(database='NanoDB3',collection='saved_pdf_output',materialid='',materialname=''):
        response = {}

        db = client[database]
        fullcoll = db[collection]
        result = fullcoll.drop()

        response['result'] = result
        return bson.json_util.dumps(response)
