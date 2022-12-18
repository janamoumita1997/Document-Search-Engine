
from sklearn.feature_extraction.text import TfidfVectorizer,CountVectorizer
import pymongo
import more_itertools


client = pymongo.MongoClient('mongodb://127.0.0.1:27017/')
db = client["extract_data"]   # Database Name
col = db["file_record"]     # Collection Name

class advance_search:
  def __init__(self,data):
    self.data=data

  def advance_content_search(self,input_string,thresold):

    content_list=[]
    list_dictionary=[]
    for i in self.data:
      #print(i)

      content_list.append(i.get("main_content"))
      list_dictionary.append({"id":str(i.get("_id")),"filename":i.get("filename"),"main_content":i.get("main_content")})

    #print(f"content_list :      {content_list}")


    
    breake_string=input_string.split(" ")
    #print(breake_string)
    docwise_score=[]
    #document_list=[content_1,content_2]
    for n in list_dictionary:
      sent=n["main_content"].split("  ")
      filter_sent=[x for x in sent if x]

      tfidfvectorizer = TfidfVectorizer(analyzer='word',use_idf=True,norm='l2',stop_words='english')# Instantiate the Vectorizer object
      tfidf = tfidfvectorizer.fit_transform(filter_sent)
      tfidf_tokens=tfidfvectorizer.get_feature_names_out()
      idf = tfidfvectorizer.idf_
      tfidf_score=dict(zip(tfidf_tokens, idf))

      #print(f"tfidf_score >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",tfidf_score.keys())
      score_=[]
      for j in breake_string:
        #print(f" j >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>{j}")
        if j.lower() in tfidf_score.keys():
          score_.append(tfidf_score[j.lower()])
          #print(tfidf_score[j])
      docwise_score.append(sum(score_))

    #print(f"docwise_score   :  {docwise_score}")
    if max(docwise_score) != 0:
      norm = [float(i)/max(docwise_score) for i in docwise_score]
      #print(norm)
      output=dict(zip(content_list,norm))
      sorted_dict = {r: output[r] for r in sorted(output, key=output.get, reverse=True)}
      #print(f"sorted_dict   >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>   {sorted_dict}")

      filter_object=[]
      for i in sorted_dict:
          if output[i]>thresold:
            for d in list_dictionary:
              if d['main_content']==i:
                filter_object.append(d)

      new_filter_object=[]
      for i in filter_object:
        content=i['main_content'].replace("  "," ").strip()[:200]
        i.update({'main_content':content})
        new_filter_object.append(i)

      return new_filter_object
    else:
      return "your seach text not match throught out all documents"



# data=col.find()
# print(data)
# input_string="Microsoft Office Word"
# thresold=0.9
# adv_serch=advance_search(data)
# print(adv_serch.advance_content_search(input_string,thresold))










