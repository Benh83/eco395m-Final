import re
import os
import pandas as pd
from aiscrape import get_Data
from tosql import create_tables, create_db_engine, append_deal_to_database
from Clean_Data import (
    clean_column_names,
    clean_values,
    clean_urls,
    cleaning,
)

from dotenv import load_dotenv

def clean_company_name(name):
    name=re.sub(r'[.,\\ /:;]', '', name.strip())
    return name

engine = create_db_engine()
create_tables(engine)

mode = input(
    "Select mode:\n1. Manually input Target and Buyer\n2. Process deals from file\nEnter 1 or 2: "
).strip()

if mode == "1":
    # Manual input mode
    Target = input("Please input Target Company:").strip()
    Buyer = input("Please input Buyer:").strip()
    targets_buyers = [(Target, Buyer)]
elif mode == "2":
    # File processing mode
    file_path = os.path.join("setup", "Top-100 deals.xls")
    deals_df = pd.read_excel(file_path)
    targets_buyers = deals_df[["Target/Issuer", "Buyers/Investors"]].values.tolist()
else:
    print("Invalid selection. Exiting.")
    exit()

for Target, Buyer in targets_buyers:

    print(f"Processing deal for Target: {Target}, Buyer: {Buyer}")

    query_values = (
        "SELECT * FROM deals WHERE LOWER(target) LIKE %s AND LOWER(buyer)  LIKE %s"
    )
    # Parameters dictionary
    params = (f"%{Target.lower()}%", f"%{Buyer.lower()}%")
    sql_values = pd.read_sql_query(query_values, engine, params=params)

    found = "yes"
    if len(sql_values) > 1:
        print("Possible results \n")
        print(sql_values["id", "buyer", "seller"])
        found = input("Is the deal you are looking for there?(yes or no):")
        while found != "yes" and found != "no":
            found = input(
                "Input not Valid. Is the deal you are looking for there?(yes or no):"
            )
        if found == "yes":
            found_id = input("Please enter id of the deal you want to see.")
            query_values = "SELECT * FROM deals WHERE id=%s"
            params = (found_id,)
            sql_values = pd.read_sql_query(query_values, engine, params=params)

    elif len(sql_values) == 0 or found == "no":
        print("Extracting The Data from Internet")

        Target = clean_company_name(Target)
        Buyer = clean_company_name(Buyer)
        extracted_data = get_Data(Buyer, Target)
        df_data = clean_values(extracted_data)
        df_url = clean_urls(extracted_data)
        df_url = clean_column_names(df_url)
        df_data = clean_column_names(df_data)
        clean_data = cleaning(df_data)
        df_url["buyer"] = clean_data["buyer"]
        df_url["target"] = clean_data["target"]
        deal_id = append_deal_to_database(engine, clean_data, df_url)
        query_values = "SELECT * FROM deals WHERE id=%s"
        params = (deal_id,)
        sql_values = pd.read_sql_query(query_values, engine, params=params

    deal_id = sql_values.loc[0, "id"]
    query_url = "Select*from urls where deal_id=%s"
    params = (float(deal_id),)
    sql_urls = pd.read_sql_query(query_url, engine, params=params)
    OUTPATH_PATH = os.path.join("data", f"{Target}_{Buyer}.xlsx")

    with pd.ExcelWriter(OUTPATH_PATH, engine="xlsxwriter") as writer:
        sql_values.to_excel(writer, sheet_name="data", index=False)
        sql_urls.to_excel(writer, sheet_name="urls", index=False)

    print(f"File found at {OUTPATH_PATH}")
