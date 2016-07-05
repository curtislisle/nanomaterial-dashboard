import nltk
import numbers

# is a value a number or a string? 
# from http://stackoverflow.com/questions/354038/how-do-i-check-if-a-string-is-a-number-float-in-python

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


# needed for cleaning the file to get rid of specisl characters
def remove_non_ascii(text):
    return ''.join(i for i in text if ord(i)<128)


def run(SearchDistance=200,textpath=None,targetword='toxicity',filename=None):

    startindex = 0
    matchingNumber = -9999
    totalrecordcount = 0
    entitycount = 1
    relationcount = 1

    textfilename = filename[:filename.find('.')]+'.txt'
    f = open(textpath+'/'+textfilename)
    rawtext = f.read()
    # clean by removing all non-ascii characters
    text = remove_non_ascii(rawtext)
    #print 'length of text:',len(text)
  
    # we might be adding additional annotations to an already annotated text, so lets 
    # spin through the annotation file and update the count of entities and relations first
    # so we will appropriately number new annotations.  

    annotationfile = filename[:filename.find('.')]+'.ann'
    fann = open(textpath+'/'+annotationfile)
    anntext = fann.readlines()
    previousEntities = 1
    previousRelations = 1
    for line in anntext:
        if line[0] == 'T':
            previousEntities += 1
        elif line[0] == 'R':
            previousRelations += 1 
    print previousEntities,previousRelations
    fann.close()
    
    # update the staring values according to what was in the file already
    entitycount = previousEntities
    relationcount = previousRelations 

    # open annotations as output file, use append mode since there might be previous
    # annotations we don't want to over-write

    outfilename =  filename[:filename.find('.')]+'.ann'
    print 'outputfile:',outfilename
    fout = open(textpath+'/'+outfilename,'a')

    while startindex < len(text):
        foundindex = text[startindex:].find(targetword)

        # We have found the target property text.  look to the right to find the closest number
        # within the SearchDistance number of characters. Loop through the tokens in this small text
        # The text is first tokenized and then the closest token which is a number is what is returned.

        tokens = nltk.word_tokenize(text[foundindex+startindex:foundindex+startindex+int(SearchDistance)])
        foundNumber = False
        for tok in tokens:
            if is_number(tok):
                foundNumber = True
                matchingNumber = tok
                break
        
        # when we have found all the targetword instances, then stop the loop
        if foundindex < 0:
            break

        # we only want to output target discoveries which have a corresponding number within the search distance
        if foundNumber:

            # T7      Measurement 14542 14556 zeta potential 
            entityname1 = 'T'+str(entitycount)
            entitytype = 'Measurement'
            tokstart = startindex + foundindex
            tokend = tokstart + len(targetword)
            outstring = entityname1 + '\t' + entitytype +' '+str(tokstart) + ' ' + str(tokend)+'\t'+targetword+'\n'
            #print outstring
            fout.write(outstring)
            entitycount += 1
            
            entityname2 = 'T'+str(entitycount)
            entitytype = 'MeasuredValue'
            tokstart = startindex + foundindex + text[startindex + foundindex:].find(matchingNumber)
            tokend = tokstart + len(matchingNumber)
            #print entityname2,'\t',entitytype,tokstart,tokend,'\t',matchingNumber
            outstring = entityname2 + '\t' + entitytype +' '+str(tokstart) + ' ' + str(tokend)+'\t'+matchingNumber+'\n' 
            #print outstring
            fout.write(outstring)
            entitycount += 1
            
            # R3      PropertyValue Arg1:T7 Arg2:T8 
            relname = 'R'+str(relationcount)
            reltype = 'PropertyValue'
            #print relname,'\t',reltype,'Arg1:'+entityname1,'Arg2:'+entityname2
            outstring = relname + '\t' + reltype +' '+'Arg1:'+entityname1+' '+'Arg2:'+entityname2+' \n' 
            fout.write(outstring)
            #print outstring
            relationcount += 1
            
            
        # continue in the text past this discovery and look for the next time the target text is found
        startindex = startindex + foundindex + 1
        totalrecordcount += 1

    fout.close()
    f.close()


        