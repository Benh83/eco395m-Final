import os
from openai import OpenAI
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import markdown
import json
import pandas as pd


def get_Content():
    IN_PATH = os.path.join("setup", "Guide.xlsx")
    guide = pd.read_excel(IN_PATH)
    list_content = []
    for _, row in guide.iterrows():
        list_content.append(
            f"retrieve {row['Variable']} in {row['Format']} format. If not found return null. Provide only {row['Variable']} and full URL. Return only JSON with 2 key-value pairs and NOTHING ELSE "
        )
    return list_content


def get_JSON(content):
    html = markdown.markdown(content)
    soup = BeautifulSoup(html, features="lxml")
    txt = soup.find_all("code")[0].text.replace("json", "")
    dict_ = json.loads(txt)
    return dict_


def run_Perplexity(CONTENT, PROMPT):
    load_dotenv()
    PERPLEXITY_API_KEY = os.environ["PERPLEXITY_API_KEY"]
    client = OpenAI(api_key=PERPLEXITY_API_KEY, base_url="https://api.perplexity.ai")
    messages = [
        {
            "role": "system",
            "content": CONTENT,
        },
        {
            "role": "user",
            "content": PROMPT,
        },
    ]
    completion = client.chat.completions.create(
        model="llama-3.1-sonar-large-128k-online", messages=messages
    )
    return completion.choices[0].message.content


def get_Data(Buyer, Target):
    extracted_data = {}
    extracted_data.update({"Buyer": {"Buyer": Buyer, "URL": None}})
    extracted_data.update({"Target": {"Target": Target, "URL": None}})

    for row in get_Content():
        CONTENT = row
        variable = row[9 : row.index(" in ")]
        PROMPT = f"""Buyer:{Buyer} , Target Company:{Target}"""
        perplexity_content = run_Perplexity(CONTENT, PROMPT)
        JSON_data = get_JSON(perplexity_content)
        JSON_n = {variable: JSON_data}
        extracted_data.update(JSON_n)
    with open(os.path.join("raw_data", f"{Buyer}_{Target}.json"), "w") as json_file:
        json.dump(extracted_data, json_file, indent=4)

    return extracted_data
