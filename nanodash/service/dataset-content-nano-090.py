#import bson
import pymongo
import json
from bson import ObjectId
from pymongo import MongoClient
import string
import tangelo
import sys

# is a value a number or a string? 
# from http://stackoverflow.com/questions/354038/how-do-i-check-if-a-string-is-a-number-float-in-python

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

# this value is likely a unicode string which is either a string (e.g. 'Araomatic') or a number (e.g. '-3.454').
# lets convert them to matching values and return them

def ConditionValue(field):
    if is_integer(field):
        return int(field)
    elif is_number(field):
        return float(field)
    else:
        # convert to python string to assist matching
        return str(field)





def run(dbname,tablename):

    
    # Create an empty response object.
    response = {}
    response['data'] = []
    response['header'] = []

    # open a connection and copy the entire database
    connection = MongoClient()
    db = connection[dbname]
    dataset_collection = db[tablename]

    # build query for . 
    query = {}
    table = dataset_collection.find(query,{'_id':0})

    # copy but ignore sub-dictionaries
    print 'returned record count:',table.count()


    rows = []
    for thisrow in table:
        row = {}

        # copy all of the regular (non-dictionary) valuws across
        for x in thisrow:
            if not isinstance(thisrow[x],dict):
                row[x] =thisrow[x]

        # now bring over any important, special values which were embedded in dictionaries
        row['dashboard_data_source'] = thisrow['dashboard_data_source'] if 'dashboard_data_source' in thisrow else ''
        row['UpdatedAt'] = thisrow['mat_UpdatedAt']
        row['DataSource'] = thisrow['mat_DataSource']
        row['CuratedBy'] = thisrow['mat_CuratedBy']
        row['DataSourceURL'] = thisrow['mat_DataSourceURL']
        row['source_pdf'] = 1 if  thisrow['dashboard_data_source'] == 'pdf_extraction' else 0 
        row['source_nano_db'] = 1 if thisrow['dashboard_data_source'] == 'nano_database' else 0         

        rows.append(row)

    #print 'records:', rows
    #sys.stdout.flush()


    # copy out of the mongodb cursor type to a python list
    for x in rows:

        row['dashboard_data_source'] = x['dashboard_data_source'] if 'dashboard_data_source' in x else ''
        row['UpdatedAt'] = x['mat_UpdatedAt'] if 'mat_UpdatedAt' in x else ''
        row['DataSource'] = x['mat_DataSource'] if 'mat_DataSource' in x else ''
        row['CuratedBy'] = x['mat_CuratedBy'] if 'mat_CuratedBy' in x else ''
        row['DataSourceURL'] = x['mat_DataSourceURL'] if 'mat_DataSourceURL' in x else ''
        row['source_pdf'] = 1 if  x['dashboard_data_source'] == 'pdf_extraction' else 0 
        row['source_nano_db'] = 1 if x['dashboard_data_source'] == 'nano_database' else 0         

        # many of the attributes we test for are not in all the particles, so fill in the table here using conditional expressions.  The value
        # is passed through if it exists, otherwise it is not. 

        x['NanomaterialID'] = x['NanomaterialID'] if 'NanomaterialID' in x else ''

        x['Mean Hydrodynamic Diameter'] = x['Mean Hydrodynamic Diameter'] if 'Mean Hydrodynamic Diameter' in x else 0
        x['Molecular Type'] = x['Molecular Type'] if 'Molecular Type' in x else ''
        x['Material Type'] = x['Material Type'] if 'Material Type' in x else ''
        x['Product Name'] = x['Product Name'] if 'Product Name' in x else ''
        x['Mean Hydrodynamic Diameter'] = x['Mean Hydrodynamic Diameter'] if 'Mean Hydrodynamic Diameter' in x else 0
        x['Mean Primary Particle Size'] = x['Mean Primary Particle Size'] if 'Mean Primary Particle Size' in x else 0
        x['Component Molecular Weight'] = x['Component Molecular Weight'] if 'Component Molecular Weight' in x else 0
        x['Molecular Weight'] = x['Molecular Weight'] if 'Molecular Weight' in x else 0
        x['Lambda Max'] = x['Lambda Max'] if 'Lambda Max' in x else 0
        x['Bulk Density'] = x['Bulk Density'] if 'Bulk Density' in x else 0
        x['Primary Particle Size'] = x['Primary Particle Size'] if 'Primary Particle Size' in x else 0
        x['Specific Surface Area'] = x['Specific Surface Area'] if 'Specific Surface Area' in x else 0
        x['Zeta Potential'] = x['Zeta Potential'] if 'Zeta Potential' in x else 0

        x['2D Dimensionality'] = 1 if (('Nanoscale Dimensionality' in x) and x['Nanoscale Dimensionality'] =='2D') else 0 
        x['3D Dimensionality'] = 1 if (('Nanoscale Dimensionality' in x) and x['Nanoscale Dimensionality'] =='3D') else 0    
#        x['Null Dimensionality'] = 1 if (('Nanoscale Dimensionality' in x) and x['Nanoscale Dimensionality'] =='Null') else 0    
        x['Neutral Polarity']   = 1 if (u'Polarity' in x)  and ((x[u'Polarity'] =='Neutral') or (x[u'Polarity'] =='Neutral ')) else 0  
        x['Positive Polarity']   = 1 if (u'Polarity' in x) and (x[u'Polarity'] =='Positive') else 0  
        x['Negative Polarity']   = 1 if (u'Polarity' in x) and (x[u'Polarity'] =='Negative') else 0  
        #x['Neutral Polarity'] = 1 if x['Polarity'] =='Neutral' else 0
        #x['Positive Polarity'] = 1 if x['Polarity'] =='Potitive' else 0
        #x['Negative Polarity'] = 1 if x['Polarity'] =='Negative' else 0

        x['Metal'] = 1  if 'Material Type' in x and ( x['Material Type'] =='Metal' ) else 0
        x['Metal Oxide'] = 1  if 'Material Type' in x and ( x['Material Type'] =='Metal Oxide') else 0
        x['Polymer'] = 1  if 'Material Type' in x and ( x['Material Type'] =='Polymer') else 0
        x['Carbohydrate'] = 1  if 'Material Type' in x and ( x['Material Type'] ==u'Carbohydrate') else 0
        x['Group Ii-Vi'] = 1  if 'Material Type' in x and ( x['Material Type'] =='Group Ii-Vi' ) else 0
        x['Group Iv - Non C'] = 1  if 'Material Type' in x and ( x['Material Type'] =='Group Iv - Non C' ) else 0
        x['Dendrimer'] = 1  if 'Material Type' in x and ( x['Material Type'] =='Dendrimer' ) else 0
        x['Lipid'] = 1  if 'Material Type' in x and ( x['Material Type'] =='Lipid' ) else 0
        x['Protein'] = 1  if 'Material Type' in x and ( x['Material Type'] =='Protein' ) else 0
        x['Nucleic Acid'] = 1  if 'Material Type' in x and ( x['Material Type'] =='Nucleic Acid' ) else 0

        # look at state (has six different categorical values)
        x['Agglomerated'] = 1  if 'State' in x and ( x['State'] =='Agglomerated' ) else 0
        x['Aggregated'] = 1  if 'State' in x and ( x['State'] =='Aggregated' ) else 0
        x['Aggreg-Agglom'] = 1  if 'State' in x and ( x['State'] =='Aggregated/Agglomerated' ) else 0
        x['Not Aggreg-Agglom'] = 1  if 'State' in x and ( x['State'] =='Not Aggregated/Agglomerated' ) else 0

        # special cleaning for Molecular Identity - usually a string, but at least one number value exists
        x['Molecular Identity'] = str(x['Molecular Identity']) if 'Molecular Identity' in x  else ''

        # special cleaning for 'Purity Of' because it has numeric and character and inconsistent values
        x['Purity99+'] = 1 if ('Purity Of' in x and x['Purity Of']>=99) else 0
        x['UltraPure'] = 1 if 'Purity Of' in x and ((x['Purity Of'] == 'Ultrapure') or (x['Purity Of']=='Ultra Pure')) else 0

        # input database has false/true instead of 0/1 needed for UpSet
        x['IsCrystalline'] = 1 if (('IsCrystalline' in x) and (x['IsCrystalline'])) else 0
        #x['Polycrystalline'] = 1 if ((x['Polycrystalline']) else 0
        #x['SingleCrystal'] = 1 if (x['SingleCrystal']) else 0        
        #x['Monoclinic'] = 1 if (x['Monoclinic']) else 0  


        # put in the fields that are in the PDf extraction to make sure these records have them, too
        x['Aromatic'] = 1 if ('Aromatic' in x and x['Aromatic']=='yes') else 0
        x['VHQ-R subset'] = 1 if ('VHQ-R subset' in x and x['VHQ-R subset']=='yes') else 0
        x['Macrocyclic'] = 1 if ('Macrocyclic' in x and x['Macrocyclic']=='yes') else 0
        x['VHQ-R subset'] = 1 if ('VHQ-R subset' in x and x['VHQ-R subset']=='yes') else 0
        x['source_pdf'] = 1 if  x['dashboard_data_source'] == 'pdf_extraction' else 0 
        x['source_nano_db'] = 1 if x['dashboard_data_source'] == 'nano_database' else 0  

 
      
        # return cleaned tuple
        response['data'].append(x)

    #table.rewind()

    # find the column headers
   # for col in x:
    #    if not isinstance(col,dict):
    #        response['header'].append(col)


    #-------------------------------------------------------------------------
    # now look in the PDF scraping collection and bring these records in
    #-------------------------------------------------------------------------

    # open a connection and copy the entire database
    #dataset_collection = db['pdf_output_processed']
    dataset_collection = db['saved_pdf_data']

    # build query for Phoenix. focus returns on middle east countries
    query = {};
    table = dataset_collection.find(query,{'_id':0})
    #print 'pdf-table:',table[0]


    # copy out of the mongodb cursor type to a python list
    pdfcount = 0

    if table.count() > 0:
        for jsonlist in table[0]['data']:
            x = {}

            # copy to avoid unicode problems.  Create new dictionary

            for field_dict in jsonlist:
                #print field_dict
                try:
                    keyname = str(field_dict.keys()[0])
                    value = ConditionValue(field_dict[keyname])
                    x[keyname] = value
                except:
                    pass

            #print 'pdf-dict:',x
            #sys.stdout.flush()

            # pdfcount += 1
            # if pdfcount > 2:
            #     break;

            # at this point, we have recrated a traditional multi-field json object from each particle in the pdf
            # extraction output.  Now we can proceed with testing

            # now add in binary sets.  In each case, the identify of a multi-valued field is tested and turned
            # into an additional binary set attribute
            x['Aromatic'] = 1 if ('Aromatic' in x and x['Aromatic']=='yes') else 0
            x['VHQ-R subset'] = 1 if ('VHQ-R subset' in x and x['VHQ-R subset']=='yes') else 0
            x['Macrocyclic'] = 1 if ('Macrocyclic' in x and x['Macrocyclic']=='yes') else 0
            x['VHQ-R subset'] = 1 if ('VHQ-R subset' in x and x['VHQ-R subset']=='yes') else 0
            x['Sugar'] = 1 if ('Sugar' in x and x['Sugar']==1) else 0
            x['source_pdf'] = 1 
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

            x['2D Dimensionality'] = 1 if (('Nanoscale Dimensionality' in x) and x['Nanoscale Dimensionality'] =='2D') else 0 
            x['3D Dimensionality'] = 1 if (('Nanoscale Dimensionality' in x) and x['Nanoscale Dimensionality'] =='3D') else 0    
    #        x['Null Dimensionality'] = 1 if (('Nanoscale Dimensionality' in x) and x['Nanoscale Dimensionality'] =='Null') else 0    
            x['Neutral Polarity']   = 1 if (u'Polarity' in x)  and ((x[u'Polarity'] =='Neutral') or (x[u'Polarity'] =='Neutral ')) else 0  
            x['Positive Polarity']   = 1 if (u'Polarity' in x) and (x[u'Polarity'] =='Positive') else 0  
            x['Negative Polarity']   = 1 if (u'Polarity' in x) and (x[u'Polarity'] =='Negative') else 0  
            #x['Neutral Polarity'] = 1 if x['Polarity'] =='Neutral' else 0
            #x['Positive Polarity'] = 1 if x['Polarity'] =='Potitive' else 0
            #x['Negative Polarity'] = 1 if x['Polarity'] =='Negative' else 0

            x['Metal'] = 1  if 'Material Type' in x and ( x['Material Type'] =='Metal' ) else 0
            x['Metal Oxide'] = 1  if 'Material Type' in x and ( x['Material Type'] =='Metal Oxide') else 0
            x['Polymer'] = 1  if 'Material Type' in x and ( x['Material Type'] =='Polymer') else 0
            x['Carbohydrate'] = 1  if 'Material Type' in x and ( x['Material Type'] ==u'Carbohydrate') else 0
            x['Group Ii-Vi'] = 1  if 'Material Type' in x and ( x['Material Type'] =='Group Ii-Vi' ) else 0
            x['Group Iv - Non C'] = 1  if 'Material Type' in x and ( x['Material Type'] =='Group Iv - Non C' ) else 0
            x['Dendrimer'] = 1  if 'Material Type' in x and ( x['Material Type'] =='Dendrimer' ) else 0
            x['Lipid'] = 1  if 'Material Type' in x and ( x['Material Type'] =='Lipid' ) else 0
            x['Protein'] = 1  if 'Material Type' in x and ( x['Material Type'] =='Protein' ) else 0
            x['Nucleic Acid'] = 1  if 'Material Type' in x and ( x['Material Type'] =='Nucleic Acid' ) else 0

            # look at state (has six different categorical values)
            x['Agglomerated'] = 1  if 'State' in x and ( x['State'] =='Agglomerated' ) else 0
            x['Aggregated'] = 1  if 'State' in x and ( x['State'] =='Aggregated' ) else 0
            x['Aggreg-Agglom'] = 1  if 'State' in x and ( x['State'] =='Aggregated/Agglomerated' ) else 0
            x['Not Aggreg-Agglom'] = 1  if 'State' in x and ( x['State'] =='Not Aggregated/Agglomerated' ) else 0


            # special cleaning for 'Purity Of' because it has numeric and character and inconsistent values
            x['Purity99+'] = 1 if ('Purity Of' in x and x['Purity Of']>=99) else 0
            x['UltraPure'] = 1 if 'Purity Of' in x and ((x['Purity Of'] == 'Ultrapure') or (x['Purity Of']=='Ultra Pure')) else 0

            # input database has false/true instead of 0/1 needed for UpSet
            x['IsCrystalline'] = 1 if (('IsCrystalline' in x) and (x['IsCrystalline'])) else 0
            #x['Polycrystalline'] = 1 if ((x['Polycrystalline']) else 0
            #x['SingleCrystal'] = 1 if (x['SingleCrystal']) else 0        
            #x['Monoclinic'] = 1 if (x['Monoclinic']) else 0  


      
            # add the extended row to the dataset returned for analysis
            response['data'].append(x)

            table.rewind()

        print 'done with pdf extraction data'

        # find the column headers; only add the new columns to the header record, don't repeat the others
        for col in table[0]:
            response['header'].append(col)
   
    connection.close()

    #print "response:",response
    #tangelo.log(str(response))

    # convert to string to pass through URL callback
    return json.dumps(response)
