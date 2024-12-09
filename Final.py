from aiscrape import get_Data
from aiscrape import clean_values
from aiscrape import clean_urls
from setup import connect_to_db
from setup import search_deals_in_db

#Checks if google Cloud is working
#conn=connect_to_db()

if conn is None: 
	print("Sorry, The database is down at the moment, Please try again later")
else:
	#User Inputs Target Company and Buyer 
	Target = input("Enter Target Company:")
	Buyer = input("Enter Buyer:")
	output=search_deals_in_db(conn, Target,Buyer)
	if output is None: 
		#If merger not in table, Runs the perplexity code and gets the data 
	print("Merger not found. Please wait while we get the information loaded")
	#extracted_data=get_Data(Buyer, Target)
	#df_data=clean_values(data)
	#df_url=clean_urls(data)
	#Vignesh Clean Data 
	#Upload Clean Data 
	#Show Clean Data
	else: 
		#If Merger is in table, returns queried data.








 













