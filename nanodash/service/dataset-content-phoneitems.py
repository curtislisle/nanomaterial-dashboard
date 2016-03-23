import bson
import pymongo
import json
from bson import ObjectId
from pymongo import MongoClient
import string
import tangelo



def run():
    # Create an empty response object.
    response = {}
    response['data'] = []
    response['header'] = []


    returneditems = []
    with open('/Users/clisle/proj/xdata/QCR/2015-12-02/LGOptimusG CCU 1235-14.json') as data_file:
        data = json.load(data_file)
        # add columns for the data categories, so first we discover what item types exist
        itemtypes = []
        for key in data:
            itemtypes.append(key)
        print 'found:',itemtypes 
        
        itemcount = 0
        uppercount = 0
        for key in data:
            print "*******",key
            lowercount = 0
            for item in data[key]:
                # add set columns for type, with all set to zero initially
                for itemtype in itemtypes:
                    item[itemtype] = 0
                # indicate set membership for the set that matches this individual item.  This will establish this
                # type of this item by giving it set membership in the "type" set (messages,calls, etc.)
                item[key] = 1
        
                # now add  binary sets.  In each case, the identify of a multi-valued field is tested and turned
                # into an additional binary set attribute
                item['PhoneItemID'] = itemcount
                item['MatchedContact'] = 1 if ('From (Matched)'in item) else 0
                # not all records have this type, so short circuit to test it exists first
                item['Incoming'] = 1 if (('Direction' in item) and ('From (Matched)'in item)) else 0
                item['Sent'] = 1 if (('Status' in item) and (item['Status']=='Sent')) else 0
                item['Unsent'] = 1 if (('Status' in item) and (item['Status']=='Unsent')) else 0
                item['SendFailed'] = 1 if (('Status' in item) and (item['Status']=='Sending Failed')) else 0

                # handle the more complex text fields, which are not always present
                if ('Text' not in item.keys()):
                    item['Text'] = ""
                if ('Name' not in item.keys()):
                    item['Name'] = ""
                if ('Account Name' not in item.keys()):
                    item['Account Name'] = ""
                if ('Email' not in item.keys()):
                    item['Email'] = ""
                # add the extended row to the dataset returned for analysis
                response['data'].append(item)
                itemcount += 1


    # find the column headers
    headeritems = []
    for key in data:
        for item in data[key]:
            for col in item.keys():
                if (col not in headeritems):
                    headeritems.append(col)

    response['header'].append(headeritems)

    print "response:",response
    # convert to string to pass through URL callback
    #tangelo.log(str(response))
    return json.dumps(response)
