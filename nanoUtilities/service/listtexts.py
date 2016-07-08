import bson.json_util
import json
from bson import ObjectId
import string
import tangelo

from os import listdir
from os.path import isfile, join


# create a simple service that looks for files in a directory and retuns ones with the 
# type extension .ann  

# this is used, in our case, to return a list of annotation files in the brat directory 

def run(directory=None):
    # Create an empty response object.
    response = {}

    # assign default directory if none is provided
    if directory == None:
	print 'warning: python service listtexts.py using hard-coded pathname'
        directory = '/home/vagrant/brat-v1.3_Crunchy_Frog/data/nano_papers/'

    # build a list of files returned from the listdir() call on the target directory
    onlyfiles = [f for f in listdir(directory) if isfile(join(directory, f))]
    # filter this list for files with the annotation type extension .ann
    annfiles = [x for x in onlyfiles if ".txt" in x]


    # Pack the results into the response object, and return it.
    response['result'] = annfiles

    # Return the response object.
    #tangelo.log(str(response))
    return bson.json_util.dumps(response)
