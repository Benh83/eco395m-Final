import os 
import pandas as pd 
import json
import re
import markdown
from bs4 import BeautifulSoup


def get_Content():
	IN_PATH = os.path.join("data", "Guide.xlsx")
	guide=pd.read_excel(IN_PATH)
	list_content=[]
	for _, row in guide.iterrows(): 
		list_content.append(f"retrieve {row['Variable']} in {row['Format']} format. If not found return null. Provide only {row['Variable']} and full URL. Return only JSON with 2 key-value pairs and NOTHING ELSE ")
	return list_content

def get_JSON(content): 
	html = markdown.markdown(content)
	soup = BeautifulSoup(html,features="lxml")
	txt = soup.find_all("code")[0].text.replace("json", "")
	dict_ = json.loads(txt)
	return dict_

# print(html)








