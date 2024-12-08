#JSON to pandas dataframe

import json
import pandas as pd
import os
import re


pd.set_option('display.max_rows', None)  # No limit on rows
pd.set_option('display.max_columns', None)  # No limit on columns

BASE_DIR = "./eco395m-Final/data" 
JSONL_PATH = os.path.join(BASE_DIR, "results.jsonl")


with open(JSONL_PATH, 'r') as file:
    data = json.load(file)

df = pd.json_normalize(data, sep='_')


def url_links(dataframe):
    """Takes a dataframe and returns a list of unique URL's in it"""
    list_of_links = []
    for column_name, column_data in dataframe.items():
        if 'URL' in column_name or 'url' in column_name:
            for value in column_data:
                if value and value not in list_of_links:
                    list_of_links.append(value)
    return list_of_links


def clean_text(dataframe):
    """Cleans all the column names of the dataframe"""
    dataframe.columns = [column_name.split("_")[0] for column_name in dataframe.columns]
    dataframe = dataframe.loc[:, ~dataframe.columns.duplicated()]
    
    return dataframe


def write_to_csv(dataframe):
    "Writes all the cleaned data to a CSV"
    links = url_links(dataframe) 
    df_clean_text = clean_text(dataframe)
    df_cleaned = df_clean_text.drop(columns=[column_name for column_name in df_clean_text.columns if 'URL' in column_name or 'url' in column_name])
    df_cleaned["Links"] = [", ".join(links)] * len(df_cleaned)

    output_path = './m&a_data.csv' 
    df_cleaned.to_csv(output_path, index=False)
    

write_to_csv(df)
