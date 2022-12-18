import pathlib
from pathlib import Path
import os
from extractFile import *
import pymongo

fileDirectory ="/home/mentech/Moumita/metadata_extraction_poc/uploadedFiles/"
folder_content=[]
for txt_path in Path(fileDirectory).glob("*"):
  #print(txt_path)
  filename=os.path.basename(txt_path)
  folder_content.append(filename)
  #print("filename.........",filename)
print("filename.........",folder_content)

all_records=[]
for i in folder_content:
	#all_records.append(ExtractFile(i))
	all_records.append(ExtractFile(i,fileDirectory).getExtractedTextFile())
	# extractfile=ExtractFile("Recruitment Consultant-converted.pdf")
# rocords=extractfile.getExtractedTextFile()


#print(f"all_records      {all_records}")

client=pymongo.MongoClient('mongodb://127.0.0.1:27017/')
mydb=client['extract_data']
datainfo=mydb.file_record


for j in all_records:
	if j != None:

		datainfo.insert_one(j)


print("....................insert successfully complete.........................")