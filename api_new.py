import pymongo
import pandas
import json
import re
import os
from flask import Flask
import more_itertools
from flask_cors import CORS, cross_origin
from flask.json import JSONEncoder
from bson.objectid import ObjectId
from flask import jsonify
from flask import Flask, request, make_response
from sklearn.feature_extraction.text import TfidfVectorizer,CountVectorizer
from extractFile import *
from advance_search_content import *



client = pymongo.MongoClient('mongodb://127.0.0.1:27017/')
db = client["extract_data"]  # Database Name
col = db["file_record"]    # Collection Name

x=db.file_record.find()
all_record=[]
for i in x:
    all_record.append(i)

total_object=len(all_record)
default_skip_limit=0
# print("total_object ",total_object)

app = Flask(__name__)


@app.route('/hc', methods=['GET'])
@cross_origin(supports_credentials=True)
def hc():
    try:
        resp = jsonify({"success": True, 'message': 'Hello World!'})
        return resp
    except Exception as e:
        print(e)
        resp = {"success": False,  'message': 'Some error occurred!'}
        return resp


@app.route('/Normal_search', methods=['POST'])
@cross_origin(supports_credentials=True)
def search_text():
    try:        
        _json = request.json
        print(_json)
        #val1
        count_limit=_json['limit']
        skip_limit_val=_json['skip_limit']

        _json.pop('limit')
        _json.pop('skip_limit')
        #print("_json_after_drop ",_json)
        y=list(set(_json.values()))
        print(y)
        for i in y:
            if i != "":
                validation=True
            else:
                validation=False
        print(validation)
        if validation == True:

            if count_limit =="":
                count_limit=total_object
            else:
                count_limit=int(count_limit)

            if skip_limit_val =="":
                skip_limit=default_skip_limit
            else:
                skip_limit=int(skip_limit_val)



            try:
                query_lst=[]
                main_query={}
                for key,value in _json.items():
                    #print(f"key :{key},value :{value}")
                    sub_query={}
                    query={}
                    if value !="":
                        sub_query["$regex"]=value
                        sub_query["$options"]='i'

                        query[key]=sub_query
                        query_lst.append(query)
                main_query['$and']=query_lst


                data = db.file_record.find(main_query).skip(skip_limit).limit(count_limit)  #{ 'content': { '$regex': res, '$options': 'i' }}
                file_info=[]
                for i in data:
                    #print(i)
                    file_info.append({"filename":i.get("filename"),"data":i.get("main_content")[:200]})

                resp = jsonify({"success" : True, "response":file_info })
                resp.status_code = 200
                return resp
            except Exception as e:
                print(e)
                resp = jsonify({"success" : False, "message": "Something error"})
                resp.status_code = 500
                return resp
        else:
            return "Give at least one value except limit,skip_limit for filtering documents"
    except Exception as e:
        print(e)

@app.route("/file_upload", methods=['POST'])
@cross_origin(supports_credentials=True)
def save_file():
    try:
        #pathDir='/home/mentech/Moumita/metadata_extraction_poc/uploadedFiles/'

        current_dir=os.getcwd()
        pathDir=current_dir+"/uploadedFiles/"
        #print(pathDir)
       
        file1 = request.files.get('file')
        fileName = file1.filename
        #print(file1.filename)
        print(file1)
        if fileName !="":

            path = os.path.join(pathDir, file1.filename)
            print("path    >>>>",path)
            fileName = file1.filename
            file1.save(path)

            record=ExtractFile(fileName,pathDir).getExtractedTextFile()
            col.insert_one(record)

            #os.remove(path)

            resp = jsonify({'success': True,'message':'File uploaded successfully'})
            resp.status_code = 200

            return resp

        else:
            return "You have to upload a file"
    except Exception as e:
        print(e)
        resp = jsonify({"success" : False, "message": "Something error"})
        resp.status_code = 500
        return resp
@app.route('/advance_search', methods=['POST'])
@cross_origin(supports_credentials=True)
def advance_search_():
    try:
        _json = request.json
        print(_json)
        input_string=_json['advanced_search_context']
        object_id=_json['object_id']
        count_limit=_json['limit']

        _json.pop('advanced_search_context')
        _json.pop('object_id')
        _json.pop('limit')
        print("_json_after_drop  :",_json)
        y=list(set(_json.values()))
        print(y)
        for i in y:
            if i != "":
                validation=True
            else:
                validation=False
        print(validation)
        if input_string != "":
            if validation == True:

                if count_limit =="":
                    count_limit=total_object
                else:
                    count_limit=int(count_limit)

                query_lst=[]
                main_query={}
                for key,value in _json.items():
                    #print(f"key :{key},value :{value}")
                    sub_query={}
                    query={}
                    if value !="":
                        sub_query["$regex"]=value
                        sub_query["$options"]='i'

                        query[key]=sub_query

                        query_lst.append(query)

                if object_id != "":
                    query_lst= query_lst + [{"_id": {"$gt": ObjectId(object_id)}}]

                main_query['$and']=query_lst
                print(f"myquery  : {main_query}")
                data = db.file_record.find(main_query).limit(count_limit)

                thresold=0.4
                adv_serch=advance_search(data)
                adv_serch_result1 = adv_serch.advance_content_search(input_string,thresold)
                if type(adv_serch_result1) == list():
                    adv_serch_result=adv_serch_result1[:2]
                else:
                    adv_serch_result=adv_serch_result1
                #total_record=len(adv_serch_result)

                                
                #print("adv_serch_result : ",adv_serch_result)
                resp = jsonify({"success" : True, "response":adv_serch_result })
                resp.status_code = 200
                return resp

            
            else:
                return "Give at least one value except limit,advanced_search_context,object_id for filtering documents"
        else:
            return "You have must give the string for advance search"
    except Exception as e:
        print(e)
        resp = jsonify({"success" : False, "message": "Something error"})
        resp.status_code = 500
        return resp


if __name__ == '__main__':
	app.run(debug=True)

