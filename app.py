import os
import sys
from pathlib import Path
from pymongo import MongoClient
from dotenv import load_dotenv
from pyresparser import ResumeParser
load_dotenv(verbose=True)

''' 
    sys.argv[0] is file name
    sys.argv[1] is pdfName
    sys.argv[2] is user_id to uniquely identify a user 
'''

if len(sys.argv) != 3:
    print('Incorrect number of arguments')
    sys.exit()

try: 
    client = MongoClient(os.getenv("MONGO_URL"))
    db = client[os.getenv("MONGO_DB")]
    print("Connected successfully!!!") 
except:   
    print("Could not connect to MongoDB") 
    sys.exit()

def insert_to_db(data):
    key = {"user_id":data['user_id']}
    parsed_resume = db.parsed_resume #collection name if parsed_resume
    objId = parsed_resume.update(key, data, upsert=True)
    return objId

filePath = os.path.join(os.getenv("DIR_PATH"),sys.argv[1])

if os.path.isfile(filePath):
    data = ResumeParser(filePath).get_extracted_data()
    '''
    adding userId to data for unique identification
    '''
    data['user_id'] = sys.argv[2]

    '''
    data cleanup - removing unneccesary data
    '''
    del data['experience']
    del data['no_of_pages']
    del data['college_name']
    
    isInserted = insert_to_db(data)
    print('bool', isInserted)
    # print('>>>>>',data)


    
# parsedResume = db.parsedResume
# parseId = parsedResume.insert_one(data).inserted_id
# if(parseId):
#     print('inserted Successfull', parseId)
# else:
#     print('Some error occured')

# 