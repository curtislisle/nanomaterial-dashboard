import bson.json_util
import json
from bson import ObjectId
import string
import tangelo

from os import listdir
from os.path import isfile, join

# used for sorting dictionary alphabetically
import operator

# NOTE:  This file is identical to exportBratAnnotations.py except for the different
# output format, which outputs using named columns.

# start annotations as an empty dictionary, each type will have a key and its
# own dictionary indexed by name/identifier

annotations = dict()
annotations['entities'] = dict()
annotations['relations'] = dict()

# needed for cleaning the file to get rid of specisl characters
def remove_non_ascii(text):
    return ''.join(i for i in text if ord(i)<128)

# test this this particular row's identifier shows it is a relation (not an entity)
def isRelation(ident):
    return (ident[0] == 'R')

def foundEntity(ident,value):
    # the entity name had non-ascii characters and always an extra \n at the end
    annotations['entities'][ident] = remove_non_ascii(value)[:-1]

def foundBinaryRelation(ident,name,arg1,arg2):
    annotations['relations'][ident] = {'type': name, 'arg1': arg1, 'arg2':arg2}
    
# this routine looks through the entities and returns the value that matches a property
# when it has been assigned through a relationship in the text
def returnValueIdentForAttributeIdentity(ident):
    for rel in annotations['relations']:
        if annotations['relations'][rel]['type'] == 'PropertyValue':
            if annotations['relations'][rel]['arg1'] == ident:
                return annotations['relations'][rel]['arg2']
            elif annotations['relations'][rel]['arg2'] == ident:
                return annotations['relations'][rel]['arg1']
 


# output the header row in alphabetic order with single letter columns coming before multiple letter 
# columns.  This only supports up to 2-letter columns, though it could be generalized for arbitrary length

def generateFormattedHeaderRow(name,formats):
    selectedformat = None
    for form in formats:
        if form['title'] == name:
            selectedformat = form
            break
    if selectedformat != None:
        # found a good format, write in order by finding the sorted order from the format dictionary
        sorted_cols = sorted(selectedformat['format'].items(), key=operator.itemgetter(0))
        # now we have a list of columns in alphabetic order, without regard to length, sadly "AA" is before "Q"
        # so we need to handle the single letter cases first
        print sorted_cols
        # start with the ID and name columns already in place
        entry = ['A','B']
        # go through as pass=1 and pass=2 to add single letter names first, then two letter names
        for algorithm_pass in range(1,3): 
            for keyvalue in sorted_cols:
                if len(keyvalue[0]) == algorithm_pass:
                    entry.append(keyvalue[0])
    #print entry
    return entry


def generateFormattedMaterialPropertyEntry(materialid,entName,attrib,value,formatname,formats):
    pass


def generateFormattedMeasurementEntry(materialid,materialname,propName,value, formatname, formats):
    selectedformat = None
    for form in formats:
        if form['title'] == formatname:
            selectedformat = form
            break
    if selectedformat != None:
        # found a good format, write in order by finding the sorted order from the format dictionary
        sorted_cols = sorted(selectedformat['format'].items(), key=operator.itemgetter(0))
        # now we have a list of columns in alphabetic order, without regard to length, sadly "AA" is before "Q"
        # so we need to handle the single letter cases first
        print sorted_cols
        # start with the ID and name columns already in place
        entry = [materialid,materialname]
        # go through as pass=1 and pass=2 to add single letter names first, then two letter names
        for algorithm_pass in range(1,3): 
            for keyvalue in sorted_cols:
                if len(keyvalue[0]) == algorithm_pass:
                    # output the value from the format spec unless it is the value keyword, which is replaced by
                    # the actual value
                    entry.append(keyvalue[1].replace('<value>',value))
    #print entry
    return entry


# this loop goes through all annotations and outputs them in a format compatible with the nanomaterial
# registry or further processing.  It uses two passes: first pass outputs properties which are assigned
# to specific nanomaterials through the "NanoProperty" relation.  

# this algorithm is a simple extension of the algorithm used in the unformatted (direct) output. only the formatting
# of the lines has been adjusted by calling re-ordering functions instead.
    
def processAnnotations(materialname,materialid,formatname,formats):
    outstring = ''
    outtable = []
    # put in the header row for the CSV

    entry = generateFormattedHeaderRow(formatname,formats)
    outtable.append(entry)

    # now loop through all the relations and output rows for each
    for rel in annotations['relations']:
        #print rel
        # find the properties actually assigned to a nanomaterial
        if annotations['relations'][rel]['type'] == 'NanoProperty':
            # still need to check for out of order args. This assumes it is material, property
            entName = annotations['entities'][annotations['relations'][rel]['arg1']]
            attrib  = annotations['entities'][annotations['relations'][rel]['arg2']]
            attribIdent  = annotations['relations'][rel]['arg2']
            # we know somewhere else in the rules, is a value for this property, so find this rule.
            # but if there isn't a rule, this might be a dangling particle/property pair, skip it if no
            # match is found
            try:
                valueIdent = returnValueIdentForAttributeIdentity(attribIdent)
                value = annotations['entities'][valueIdent]
                #print "(",entName,attrib, value,")"
                #outstring += materialid + ','+ entName + ',' + attrib + ',' + value+ '\n'
                entry = generateFormattedMaterialPropertyEntry(materialid,entName,attrib,value,formatname,formats)
                outtable.append(entry)
            except:
                pass
            
    print "output properties and values:"
    for rel in annotations['relations']:
        #print rel
        # find the properties actually assigned to a nanomaterial.  We are trying a complex 
        # reference to look for the entity
        if annotations['relations'][rel]['type'] == 'PropertyValue':
            # actually need to check for out of order args
            try:
                propName = annotations['entities'][annotations['relations'][rel]['arg1']]
                #print 'found propname:', propName
                value  = annotations['entities'][annotations['relations'][rel]['arg2']]
                #print 'found value:',value
                entry = generateFormattedMeasurementEntry(materialid,materialname,propName,value,formatname,formats)
                outtable.append(entry)
            except:
                pass
    #print outtable
    return outtable


# create a simple service that looks for files in a directory and retuns ones with the 
# type extension .ann  


def run(filename=None,materialname=None,materialid=None,directory=None,formatname=None,configstring=None):
    # Create an empty response object.
    response = {}

    # we have to decode the dictionary from its stringified version required to pass through AJAX
    config = json.loads(configstring)
    #print 'config=',config

   # if the user assigned an ID, it is to be assigned to all unassigned records.
   # Therefore, any records that don't have a particle name specifically annotated will 
   # have derived values assigned.

    outputID = int(materialid) if materialid != '' else None
    outputname = materialname if materialname != '' else None


    f = open(directory+'/'+filename)
    for line in f:
        #print line
        splits = line.split('\t')
        ident = splits[0]
        name = splits[1].split(' ')[0]
        if isRelation(ident):
            arg1 = splits[1].split(' ')[1].split(':')[1]
            arg2 = splits[1].split(' ')[2].split(':')[1].split('\n')[0]
            # sometimes the second argument might have a \n at the end, so trim
            if arg2[len(arg2)-1] == '\n':
                arg2 = arg2[:-1]
            foundBinaryRelation(ident,name,arg1,arg2)
        else:
            # after the second tab is the identifier value
            value = splits[2]
            foundEntity(ident, value)
    annotations = processAnnotations(outputname,outputID,formatname,config['output_formats'])
    f.close()


    # Pack the results into the response object, and return it.
    response['result'] = annotations

    # Return the response object.
    #tangelo.log(str(response))
    return bson.json_util.dumps(response)
