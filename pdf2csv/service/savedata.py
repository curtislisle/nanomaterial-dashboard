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
    

def is_integer(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def ConditionAttributeValue(field):
    if is_integer(field):
        return int(field)
    elif is_number(field):
        return float(field)
    else:
        # convert to python string to assist matching
        return str(field)


def run_old(data=None, fileName=None, orientation=None):
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
	


def run(data=None, fileName=None, orientation=None):
    data = json.loads(data)
	
    db = client["NanoDB3"]
    fullcoll = db["saved_pdf_data_rows"]
    response = {}
    response['data'] = []

    #print "savedata:  data:"
    #print data
    #print '------------------'

    # copy out of the mongodb cursor type to a python list
    pdfcount = 0

    if len(data) > 0:
        for jsonlist in data:
            x = {}

            # copy to avoid unicode problems.  Create new dictionary

            for field_dict in jsonlist:
                try:
                    keyname = str(field_dict.keys()[0])
                    value = ConditionAttributeValue(field_dict[keyname])
                    x[keyname] = value
                except:
                    pass
            # at this point, we have recrated a traditional multi-field json object from each particle in the pdf
            # extraction output.  

            # now add in binary sets.  In each case, the identify of a multi-valued field is tested and turned
            # into an additional binary set attribute
            x['Aromatic'] =  1 if ('Aromatic' in x and x['Aromatic']=='yes') else 0
            x['VHQ-R subset'] =  1 if ('VHQ-R subset' in x and x['VHQ-R subset']=='yes') else 0
            x['Macrocyclic'] =  1 if ('Macrocyclic' in x and x['Macrocyclic']=='yes') else 0
            x['VHQ-R subset'] =  1 if ('VHQ-R subset' in x and x['VHQ-R subset']=='yes') else 0
            x['Sugar'] =  1 if ('Sugar' in x and x['Sugar']== 1) else 0
            x['source_pdf'] =  1
            x['source_nano_db'] =  0
  
            # find mappings to fields in nanomaterial registry entries
            x['Material Type'] = x['Macromolecule Type'] if 'Macromolecule Type' in x else ''
            x['Molecular Type'] = x['Macromolecule'] if 'Macromolecule' in x else ''
            x['Molecular Identity'] = x['Name'] if 'Name' in x else ''
            x['NanomaterialID'] = x['PDB ID'] if 'PDB ID' in x else ''
            try:
                x['Mean Primary Particle Size'] = float(x['R']) if 'R' in x else 0
            except: 
                x['Mean Primary Particle Size'] = x['R'] if 'R' in x else 0

            # add the empty columns so the table is always consistent
            x['Product Name'] = x['Product Name'] if 'Product Name' in x else ''
            x['Material Type'] = x['Material Type'] if 'Material Type' in x else ''
            x['Mean Hydrodynamic Diameter'] = x['Mean Hydrodynamic Diameter'] if 'Mean Hydrodynamic Diameter' in x else 0
            x['Primary Particle Size'] = x['Primary Particle Size'] if 'Primary Particle Size' in x else 0
            x['Component Molecular Weight'] = x['Component Molecular Weight'] if 'Component Molecular Weight' in x else 0
            x['Molecular Weight'] = x['Molecular Weight'] if 'Molecular Weight' in x else 0
            x['Lambda Max'] = x['Lambda Max'] if 'Lambda Max' in x else 0
            x['Bulk Density'] = x['Bulk Density'] if 'Bulk Density' in x else 0

            x['Specific Surface Area'] = x['Specific Surface Area'] if 'Specific Surface Area' in x else 0
            x['Zeta Potential'] = x['Zeta Potential'] if 'Zeta Potential' in x else 0

            x['2D Dimensionality'] =  1 if (('Nanoscale Dimensionality' in x) and x['Nanoscale Dimensionality'] =='2D') else 0 
            x['3D Dimensionality'] =  1 if (('Nanoscale Dimensionality' in x) and x['Nanoscale Dimensionality'] =='3D') else 0
    
    #        x['Null Dimensionality'] =  1 if (('Nanoscale Dimensionality' in x) and x['Nanoscale Dimensionality'] =='Null') else 0
            x['Neutral Polarity']   =  1 if (u'Polarity' in x)  and ((x[u'Polarity'] =='Neutral') or (x[u'Polarity'] =='Neutral ')) else 0
            x['Positive Polarity']   =  1 if (u'Polarity' in x) and (x[u'Polarity'] =='Positive') else 0
            x['Negative Polarity']   =  1 if (u'Polarity' in x) and (x[u'Polarity'] =='Negative') else 0
  
            #x['Neutral Polarity'] =  1 if x['Polarity'] =='Neutral' else 0
            #x['Positive Polarity'] =  1 if x['Polarity'] =='Potitive' else 0
            #x['Negative Polarity'] =  1 if x['Polarity'] =='Negative' else 0

            x['Metal'] =  1  if 'Material Type' in x and ( x['Material Type'] =='Metal' ) else 0
            x['Metal Oxide'] =  1  if 'Material Type' in x and ( x['Material Type'] =='Metal Oxide') else 0
            x['Polymer'] =  1  if 'Material Type' in x and ( x['Material Type'] =='Polymer') else 0
            x['Carbohydrate'] =  1  if 'Material Type' in x and ( x['Material Type'] ==u'Carbohydrate') else 0
            x['Group Ii-Vi'] =  1  if 'Material Type' in x and ( x['Material Type'] =='Group Ii-Vi' ) else 0
            x['Group Iv - Non C'] =  1  if 'Material Type' in x and ( x['Material Type'] =='Group Iv - Non C' ) else 0
            x['Dendrimer'] =  1  if 'Material Type' in x and ( x['Material Type'] =='Dendrimer' ) else 0
            x['Lipid'] =  1  if 'Material Type' in x and ( x['Material Type'] =='Lipid' ) else 0
            x['Protein'] =  1  if 'Material Type' in x and ( x['Material Type'] =='Protein' ) else 0
            x['Nucleic Acid'] =  1  if 'Material Type' in x and ( x['Material Type'] =='Nucleic Acid' ) else 0

            # look at state (has six different categorical values)
            x['Agglomerated'] =  1  if 'State' in x and ( x['State'] =='Agglomerated' ) else 0
            x['Aggregated'] =  1  if 'State' in x and ( x['State'] =='Aggregated' ) else 0
            x['Aggreg-Agglom'] =  1  if 'State' in x and ( x['State'] =='Aggregated/Agglomerated' ) else 0
            x['Not Aggreg-Agglom'] =  1 if 'State' in x and ( x['State'] =='Not Aggregated/Agglomerated' ) else 0

            # special cleaning for 'Purity Of' because it has numeric and character and inconsistent values
            x['Purity99+'] =  1 if ('Purity Of' in x and x['Purity Of']>=99) else 0
            x['UltraPure'] =  1 if 'Purity Of' in x and ((x['Purity Of'] == 'Ultrapure') or (x['Purity Of']=='Ultra Pure')) else 0

            # input database has false/true instead of 0/1 needed for UpSet
            x['IsCrystalline'] =  1 if (('IsCrystalline' in x) and (x['IsCrystalline'])) else 0
            #x['Polycrystalline'] =  1 if ((x['Polycrystalline']) else 0
            #x['SingleCrystal'] =  1 if (x['SingleCrystal']) else 0
            #x['Monoclinic'] =  1 if (x['Monoclinic']) else 0
      
            # add the extended row to the dataset returned for analysis
            response['data'].append(x)
            fullcoll.insert(x)

    # convert to string to pass through URL callback
    return 'success' 
