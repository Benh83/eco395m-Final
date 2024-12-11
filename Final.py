import os
import json
import pandas as pd
from aiscrape import get_Data
from tosql import create_tables,create_db_engine,append_deal_to_database
from Clean_Data import enterprise_value,ratios,clean_column_names,clean_values,clean_urls,cleaning

engine=create_db_engine()
create_tables(engine)
Target=input("Please input Target Company:").strip()
Buyer=input("Please input Buyer:").strip()
query_values = "SELECT * FROM deals WHERE LOWER(target) LIKE %s AND LOWER(buyer)  LIKE %s"
# Parameters dictionary
params = (f'%{Target.lower()}%',f'%{Buyer.lower()}%')
sql_values=pd.read_sql_query(query_values, engine, params=params)
found="yes"
if len(sql_values)>1:
	print("Possible results \n")
	print(sql_results["id","buyer","seller"])
	found=input("Is the deal you are looking for there?(yes or no):")
	while found!="yes" and found!="no": 
		found=input("Input not Valid. Is the deal you are looking for there?(yes or no):")	
	if found=="yes": 
			found_id=input("Please enter id of the deal you want to see.")
			query_values="SELECT * FROM deals WHERE id=%s"
			params=(found_id,)
			sql_values=pd.read_sql_query(query_values, engine,params=params)
elif len(sql_values)==0 or found=="no": 
	print("Extracting The Data from Internet")
	extracted_data=get_Data(Buyer, Target)
	df_data=clean_values(extracted_data)
	df_url=clean_urls(extracted_data)
	clean_urls=clean_column_names(df_url)
	df_data=clean_column_names(df_data)
	clean_data=cleaning(df_data)
	#clean_data=ratios(clean_data)
	clean_urls["buyer"]=clean_data["buyer"]
	clean_urls["target"]=clean_data["target"]
	deal_id=append_deal_to_database(engine,clean_data,clean_urls)
	query_values="SELECT * FROM deals WHERE id=%s"
	params=(deal_id,)
	sql_values=pd.read_sql_query(query_values, engine,params=params)


deal_id=sql_values.loc[0,"id"]
query_url="Select*from urls where deal_id=%s"
params=(float(deal_id),)
sql_urls=pd.read_sql_query(query_url, engine,params=params)
OUTPATH_VALUES= os.path.join("data", f"{Target}_{Buyer}_values.xlsx")
OUTPATH_URLS=os.path.join("data", f"{Target}_{Buyer}_urls.xlsx")


sql_values.to_excel(OUTPATH_VALUES,index=False)
sql_urls.to_excel(OUTPATH_URLS,index=False)

print(f"Data file found at {OUTPATH_VALUES}")
print(f"URL file found at {OUTPATH_URLS}")
 













