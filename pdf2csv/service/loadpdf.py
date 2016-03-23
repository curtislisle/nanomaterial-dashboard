import sys, pymongo, os, glob, re, bson.json_util, json, time, datetime, math, subprocess, base64

from bson.objectid import ObjectId

from pymongo import MongoClient

from bson.dbref import DBRef

from bson.json_util import dumps

from bson.code import Code

import string, tangelo

import csv



    
def removeBadCharsFromHeaders(header):
    #loop through the columns and remove 
    header2 = []
    for col in range(len(header)):
        newstr = header[col].replace('.','')
        newstr2 = newstr.replace(',','_')
        #print 'replaced:',header[col]," with ",newstr2
        header2.append(newstr2)
    return header2    
    

def run(data=None):
	response = {}
	data = json.loads(data)
	data = data.split(',')[1];
	#data = base64.decode(data);
	f = open('/vagrant/dashboard/pdf2csv/data.pdf', 'w')
	f.write(base64.decodestring(data))
	f.close()
	#response['data'] = data



	##java -jar target/tabula-0.8.0-jar-with-dependencies.jar --pages 1 document.pdf --outfile item1.csv
	##output = os.popen('/usr/bin/java -jar ../jar/tabula-java/target/tabula-0.8.0-jar-with-dependencies.jar --pages 1 ../jar/tabula-java/document.pdf --outfile ../dump/item1.csv').read()
	output = subprocess.check_output(['/usr/bin/java', '-jar', '/vagrant/dashboard/pdf2csv/jar/tabula-java/target/tabula-0.8.0-jar-with-dependencies.jar', '/vagrant/dashboard/pdf2csv/data.pdf', '--pages', '1', '--silent', '--outfile', '/vagrant/dashboard/pdf2csv/dump/item1.csv'], shell=False, stderr=subprocess.STDOUT)
	sourcefile = '/vagrant/dashboard/pdf2csv/dump/item1.csv'	


	characterList = []
	csv.field_size_limit(sys.maxsize)	
	with open(sourcefile, 'rbU') as csvfile:
		reader = csv.reader(csvfile)
		reader.next()
		rownum = 0
		response['newheader'] = []
		csvcolumnarr = []
		for row in reader:
			csvcolumnarr.append(row[1:])
			response['newheader'].append(row[0])
			if rownum == 0:
				header1 = row
				header = removeBadCharsFromHeaders(header1)
				response["header"] = header
			else:
				characterEntry = dict()
				for colnum in range(len(row)):
					columnContents = row[colnum]
					if (len(columnContents)>0):
						#print "column: ",colnum, "header: ",header[colnum]," contents: ",columnContents
						# add each attribute name and value as an entry in the dict
						characterEntry[header[colnum]] = columnContents
						# now insert the dictonary as a single entry in the collection
				characterList.append(characterEntry)

			rownum += 1
			
	columncharList = []

	for colnum in range(len(csvcolumnarr)):
		for rownum in range(len(csvcolumnarr[colnum])):
			if colnum == 0:
				characterEntry = dict()
				columncharList.append(characterEntry)
			columncharList[rownum][response['newheader'][colnum]] = csvcolumnarr[colnum][rownum]		

			
#		columncharList.append(characterEntry)
		#rownum = 0
		#characterEntry = dict()
		#for colnum in range(len(colrow)):
		#	try:
		#		columnContents = colrow[colnum]
		#		if (len(columnContents)>0):
		#			if rownum == 0:
		#				columnContents = removeBadCharsFromHeaders(columnContents)
		#			characterEntry[response['newheader'][colnum]] = columnContents
		#		
		#		columncharList.append(characterEntry)
		#		rownum += 1
		#	except IndexError:
		#		continue
	
	csvfile.close();
	response["characterList"] = characterList
	response["columncharacterList"] = columncharList
	#tangelo.log(str(response))
	return bson.json_util.dumps(response)
	
	
