# from tika import parser
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import pdf2image
import pytesseract
import numpy as np
import cv2
from pytesseract import Output

path="/home/oem/python-webscrap-policy-main/test_country/hong_kong/CyberSecurity/G3-v9.1_EN.pdf"

class content_extractor:
	def __init__(self,path):
		self.path=path


	def text_filter(self,text):
		try:
			swa=[]
			for i in text:
				if i != '':
					if i !=' ':
						swa.append(i.strip())
			return swa
		except Exception as e:
			print(e)


	def content(self):
		try:
			files=pdf2image.convert_from_path(self.path)

			text=[]
			for file in files:
				#text = pytesseract.image_to_string(file)
				#print(text)
				image = np.array(file)
				rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
				results = pytesseract.image_to_data(rgb, output_type=Output.DICT)
				text=text+results['text']
			#print(f"text   ",text)

			swa_1= self.text_filter(text)
			main_content="  ".join(str(x) for x in swa_1)
			#print(f"main_content  : {main_content}" )

			filtered_words = [word for word in swa_1 if word not in stopwords.words('english')]
			#print(filtered_words)
			stop_content= " ".join(str(x) for x in filtered_words)

			#print(f"stop_content  : {stop_content}")

			return main_content,stop_content
		except Exception as e:
			print(e)

def word_count(str):
    counts = dict()
    words = str.split()

    for word in words:
        if word in counts:
            counts[word] += 1
        else:
            counts[word] = 1

    return counts

content_pdf=content_extractor(path)
main_content,stop_content=content_pdf.content()
word_count_in_pdf = word_count(str(stop_content.lower()))

sorted_word_count_in_pdf = sorted(word_count_in_pdf.items(), key=lambda x:x[1], reverse=True)
print("word_count_in_pdf : ",sorted_word_count_in_pdf)





