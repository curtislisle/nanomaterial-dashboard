import bson.json_util
import json
from bson import ObjectId
import string
import tangelo

from os import listdir
from os.path import isfile, join

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
                
    
# this loop goes through all annotations and outputs them in a format compatible with the nanomaterial
# registry or further processing.  It uses two passes: first pass outputs properties which are assigned
# to specific nanomaterials through the "NanoProperty" relation. 
    
def processAnnotations(materialname,materialid):
    outstring = ''
    outtable = []
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
                entry = [materialid,entName,attrib,value]
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
                print 'found propname:', propName
                value  = annotations['entities'][annotations['relations'][rel]['arg2']]
                print 'found value:',value
                entry = [materialid,materialname,propName,value]
                outtable.append(entry)
            except:
                pass
    print outtable
    return outtable


# create a simple service that looks for files in a directory and retuns ones with the 
# type extension .ann  


def run(filename=None,materialname=None,materialid=None,directory=None):
    # Create an empty response object.
    response = {}

    # assign default directory if none is provided
    if directory == None:
        directory = '/Users/clisle/code/brat-v1.3_Crunchy_Frog/data/nano_papers/'
    if filename == None:
        filename = '01-body.ann'
             
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
    annotations = processAnnotations(outputname,outputID)
    f.close()


    # Pack the results into the response object, and return it.
    response['result'] = annotations

    # Return the response object.
    #tangelo.log(str(response))
    return bson.json_util.dumps(response)
