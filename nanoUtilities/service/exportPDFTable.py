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
        particlecount = 1

        db = client[database]
        #fullcoll = db["saved_pdf_data"]
        fullcoll = db[collection]
        query = {};
        result = fullcoll.find(query)

        outtable = []
        # put in the header row for the CSV
        entry = ['ID','Name','Measurement','Value']
        outtable.append(entry)

        # now loop through the records in the database and output them one per line into the outtable variable
        for record in result:
            for attrib in record:
                if attrib != 'ID':

                    # support several ID cases: (1) user assigned ID to be assigned to all output
                    # rows, (2) find and use a field called 'ID' or ' ID', (3) assign sequential numbers
                    # to the different rows from the original table.  These options give us the
                    # ability to process several different table organizations

                    if materialid != '' :
                        outputID = int(materialid)
                    elif 'ID' in record:
                        outputID = record['ID']
                    # tabula may have a bug where a space is inserted before the ID
                    elif ' ID' in record:
                        outputID = record[' ID']
                    else:
                        outputID = particlecount

                    # support same material cases: (1) user assigned name to be assigned to all output
                    # rows, (2) find and use a field called 'name' or 'Name', (3) assign unique values 
                    # to the different rows from the original table.  These options give us the
                    # ability to process several different table organizations

                    if materialname != '' :
                        outputname = materialname
                    elif 'name' in record:
                        outputname = record['name']
                    # tabula may have a bug where a space is inserted before the ID
                    elif 'Name' in record:
                        outputname = record['Name']
                    else:
                        outputname = 'mat'+str(particlecount)

                    # build the output line one field at a teim, copy the particle information each time
                    entry = []
                    entry.append(outputID)
                    entry.append(outputname)
                    #print 'found attrib:',attrib
                    entry.append(attrib)
                    entry.append(record[attrib])
                outtable.append(entry)
            #print 'found new particle'
            particlecount += 1
        response['result'] = outtable

        #tangelo.log(str(response))
        return bson.json_util.dumps(response)
