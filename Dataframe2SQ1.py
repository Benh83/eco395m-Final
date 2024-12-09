import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
from aiscrape import get_Data, clean_values, clean_urls  # Ensure these imports are correct

# Load environment variables from final.env
load_dotenv('final.env')

# Database connection parameters
db_host = os.getenv('DB_HOST')
db_name = os.getenv('DB_NAME')
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_port = os.getenv('DB_PORT', 5432)

# Create SQLAlchemy engine for PostgreSQL
engine = create_engine(f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}')

def create_tables(engine):
    with engine.connect() as connection:
        connection.execute('''
            CREATE TABLE IF NOT EXISTS deals (
                id SERIAL PRIMARY KEY,
                buyer TEXT,
                target TEXT,
                date_announced DATE,
                seller TEXT,
                industry_of_target TEXT,
                acquired_percentage FLOAT,
                private_or_public TEXT,
                deal_size FLOAT,
                premium FLOAT,
                implied_ev FLOAT,
                implied_net_debt FLOAT,
                form_of_consideration TEXT,
                short_deal_description TEXT,
                ltm_revenue FLOAT,
                ltm_ebitda FLOAT,
                short_business_description TEXT,
                advisor_to_seller TEXT,
                advisor_to_buyer TEXT,
                accretive_or_dilutive TEXT,
                main_rationale TEXT
            )
        ''')
        connection.execute('''
            CREATE TABLE IF NOT EXISTS urls (
                id SERIAL PRIMARY KEY,
                deal_id INTEGER REFERENCES deals(id),
                url TEXT
            )
        ''')

# Access cleaned data from aiscrape.py
try:
    Buyer = str(input("Input Buyer Company here: "))
    Target = str(input("Input Target Company here: "))
    B_T = get_Data(Buyer, Target)
    deals_df = clean_values(B_T)
    urls_df = clean_urls(B_T)

    # Trim whitespace from column names
    deals_df.columns = deals_df.columns.str.strip()

    print("Clean Deals DataFrame:")
    print(deals_df.head())
    print("Columns in Deals DataFrame:", deals_df.columns.tolist())

    print("Clean URLs DataFrame:")
    print(urls_df.head())
    print("Columns in URLs DataFrame:", urls_df.columns.tolist())

except Exception as e:
    print(f"Error accessing data from aiscrape.py: {e}")
    exit()

# Create tables in the database
create_tables(engine)

# Insert data into deals and urls tables
try:
    with engine.connect() as connection:
        deals_df.to_sql('deals', con=connection, if_exists='append', index=False)
        print("Deals data inserted successfully.")
except Exception as e:
    print(f"Error inserting deals data: {e}")

try:
    with engine.connect() as connection:
        urls_df.to_sql('urls', con=connection, if_exists='append', index=False)
        print("URLs data inserted successfully.")
except Exception as e:
    print(f"Error inserting URLs data: {e}")

print("Database created and populated successfully.")