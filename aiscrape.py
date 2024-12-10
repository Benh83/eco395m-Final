import dotenv
import os 
from openai import OpenAI
from dotenv import load_dotenv
from Setup_Content import get_Content
from Setup_Content import get_JSON
import json
import time
dotenv.load_dotenv()
start = time.time()

PERPLEXITY_API_KEY = os.environ["PERPLEXITY_API_KEY"]
client = OpenAI(api_key=PERPLEXITY_API_KEY, base_url="https://api.perplexity.ai")


CACHE_DIR = ".cachedir"





def run_Perplexity(CONTENT,PROMPT): 
	messages = [
    {
        "role": "system",
        "content": CONTENT,
    },
    {   
        "role": "user",
        "content": PROMPT,
    },]
	completion = client.chat.completions.create(
	model="llama-3.1-sonar-large-128k-online",
	messages=messages)
	return completion.choices[0].message.content



def get_Data(Buyer, Target): 
    extracted_data={}
    extracted_data.update({"Buyer":{"Buyer":Buyer,"URL":None}})
    extracted_data.update({"Target":{"Target":Target,"URL":None}})

    for row in get_Content(): 
        CONTENT=row
        variable=row[9:row.index(" in ")]
        PROMPT = f'''Buyer:{Buyer} , Target Company:{Target}'''
        perplexity_content=run_Perplexity(CONTENT,PROMPT)
        JSON_data=get_JSON(perplexity_content)
        JSON_n={variable:JSON_data}
        extracted_data.update(JSON_n)
    return extracted_data  

def clean_values(data):
    mf_values=pd.DataFrame() 
    for i in data.keys():
        a=data[i]
        akey=list(a.keys())
        mf_values.loc[0,i]=a[akey[0]]
    return mf_values

def clean_urls(data):
    mf_url=pd.DataFrame() 
    for i in data.keys():
        a=data[i]
        akey=list(a.keys())
        mf_url.loc[0,i]=a[akey[1]]
    return mf_url






BASE_DIR = "data"
JSONL_PATH = os.path.join(BASE_DIR, "results.jsonl")
with open(JSONL_PATH,"w+", encoding='utf-8') as json_file: 
    json.dump(G_M, json_file, indent=4)

end = time.time()
length = end - start
print(length)



