#import bson
import pymongo
import json
from bson import ObjectId
from pymongo import MongoClient
import string
import tangelo


def run():
    # Create an empty response object.
    response = {}
    response['datasource'] = 'remote'
    response['file'] = "http://localhost:8080/service/dataset-content-nano-02/NanoDB2/Nano_combined_0122_upset"
    response['name'] = "Nano Database Dashboard v0.8.2"
    response['separator'] = ','
    response['skip'] = 0
    response['meta'] = [ 
        { "type": "id", "name": "NanomaterialID" },
        { "type": "string", "name": "Molecular Identity" },
        { "type": "string", "name": "Material Type" },  
        {"type":"string","name":"Product Name"},             
#        {'name':'Mean Hydrodynamic Diameter','type':'float'}, 
       {'name':'Mean Primary Particle Size','type':'float'},         
#        {'name':'Component Molecular Weight','type':'float'}, 
#        {'name':'Molecular Weight','type':'float'},
        {'name':'Lambda Max','type':'float'},
#        {'name':'Bulk Density','type':'float'},
#        {'name':'Primary Particle Size','type':'float'},
        {'name':'Specific Surface Area','type':'float'},
        {'name':'Zeta Potential','type':'float'}     
    ]
    response['sets'] = [
        { "format": "binary", "start": 1, "end": 5}]
    response['setlist'] = ['2D Dimensionality','3D Dimensionality','Metal','Metal Oxide','Polymer','Carbohydrate',
    'Protein','Nucleic Acid','Group Ii-Vi','Dendrimer','Lipid','Group Iv - Non C',
    'Agglomerated','Aggregated','Positive Polarity','Negative Polarity','Purity99+','IsCrystalline']
    #'Monoclinic','SingleCrystal','Polycrystalline','Amorphous','Anatase','Tetragonal','Rutile','Cubic','Brookite','Wurtzite','Zincite']
    response['attributelist'] = []
    response['author'] = 'ABCC IVG & KnowledgeVis'
    response['description'] = 'Nanomaterial database v2'
    response['source'] = "Nanomaterials reference database"
   

    #tangelo.log(str(response))
    return json.dumps(response)
