import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine
from check_deal import check_deal_exists
from aiscrape import get_Data
from Clean_Data import clean_values, clean_urls
from tosql import create_tables, append_deal_to_database, create_db_engine

# Load environment variables from the .env file
load_dotenv('final.env')

def main():
    # Step 1: Prompt user for buyer and target company details
    buyer = input("Enter Buyer/Investor: ").strip()
    target = input("Enter Target/Issuer: ").strip()

    # Step 2: Connect to the database
    engine = create_db_engine()
    
    # Step 3: Verify if the deal exists in the database
    print("Checking if the deal already exists in the database...")
    deal_exists = check_deal_exists(target, buyer)

    if deal_exists:
        print("The deal is already in the database.")
    else:
        print("Deal not found in the database. Querying Perplexity API...")

        # Step 4: Query Perplexity API to get deal JSON
        try:
            deal_data = get_Data(buyer, target)
        except Exception as e:
            print(f"Error fetching data from Perplexity API: {e}")
            return

        # Step 5: Process the deal JSON into DataFrames
        print("Processing deal JSON into DataFrames...")
        try:
            deals_df = clean_values(deal_data)
            urls_df = clean_urls(deal_data)
        except Exception as e:
            print(f"Error processing deal JSON: {e}")
            return

        # Step 6: Standardize column names in deals_df
        deals_df.rename(columns={
            'Buyer': 'buyer',
            'Target': 'target',
            'Date announced': 'date_announced',
            'Date closed': 'date_closed',
            'Industry of Target (1 or 2 words maximum)': 'industry_of_target',
            'Acquired percentage of the business': 'acquired_percentage',
            'Private or public deal? (return 1 word - either public or private)': 'private_or_public',
            'Deal size, mln $': 'deal_size',
            'Premium (one-day prior the announcement)': 'premium',
            "Implied Net Debt (preferrably taken from last balance sheet prior to the deal, calculated as target company's total debt minus cash)": 'implied_net_debt',
            'Form of consideration (return either all-cash, all-stock, all-debt, mixture (in this case return )  ': 'form_of_consideration',
            'Short deal description (maximum 125 symbols)': 'short_deal_description',
            'Revenue for the full year of the announcement date (if no information, take the revenue for the year which preceeded the announcement date)': 'ltm_revenue',
            'EBITDA (calculated as operating profit plus depreciation) for the full year of the announcement date (if no information, take the revenue for the year which preceeded the announcement date)': 'ltm_ebitda',
            'Short Business description of target company (maximum 125 symbols)': 'short_business_description',
            'Advisor to Target (seller) company (if several advisors were on the deal, return all known)': 'advisor_to_seller',
            'Advisor to Buyer (acquirer) (if several advisors were on the deal, return all known)': 'advisor_to_buyer',
            'Accretive or Dilutive deal': 'accretive_or_dilutive',
            'Main rationale (why the acquirer purchased the target? - (maximum 125 symbols))': 'main_rationale'
        }, inplace=True)

        # Clean the 'acquired_percentage' column
        if 'acquired_percentage' in deals_df.columns:
            deals_df['acquired_percentage'] = deals_df['acquired_percentage'].str.replace('%', '').astype(float)

        # Clean the 'premium' column
        if 'premium' in deals_df.columns:
            deals_df['premium'] = deals_df['premium'].str.replace('%', '').astype(float) / 100

        print("Renamed Deals DataFrame:")
        print(deals_df.head())
        print("Columns in Renamed Deals DataFrame:", deals_df.columns.tolist())

        # Step 7: Create tables in the database if not already created
        print("Creating tables in the database if not already present...")
        create_tables(engine)

        # Step 8: Append data to the database
        print("Appending deal data to the database...")
        try:
            append_deal_to_database(engine, deals_df, urls_df)
        except Exception as e:
            print(f"Error appending data to the database: {e}")
            return

        print(f"Successfully added the deal for {buyer} acquiring {target} to the database.")

if __name__ == "__main__":
    main()

