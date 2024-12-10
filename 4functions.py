import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
from aiscrape import get_Data, clean_values, clean_urls  # Ensure these imports are correct

# Load environment variables from final.env
load_dotenv('final.env')

def create_tables(engine):
    with engine.connect() as connection:
        connection.execute(text('''
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
        '''))
        connection.execute(text('''
            CREATE TABLE IF NOT EXISTS urls (
                id SERIAL PRIMARY KEY,
                deal_id INTEGER REFERENCES deals(id),
                buyer TEXT,
                target TEXT,
                date_announced TEXT,
                seller TEXT,
                industry_of_target TEXT,
                acquired_percentage TEXT,
                private_or_public TEXT,
                deal_size TEXT,
                premium TEXT,
                implied_ev TEXT,
                implied_net_debt TEXT,
                form_of_consideration TEXT,
                short_deal_description TEXT,
                ltm_revenue TEXT,
                ltm_ebitda TEXT,
                short_business_description TEXT,
                advisor_to_seller TEXT,
                advisor_to_buyer TEXT,
                accretive_or_dilutive TEXT,
                main_rationale TEXT
            )
        '''))
    print("Tables created successfully.")


def append_deal_to_database(engine, buyer, target):
    # Get data using the functions from the referenced file
    deal_data = get_Data(buyer, target)
    
    # Clean the data
    deals_df = clean_values(deal_data)
    urls_df = clean_urls(deal_data)
    
    # Ensure column names are clean
    deals_df.columns = deals_df.columns.str.strip()
    urls_df.columns = urls_df.columns.str.strip()
    
    # Append deal data to the deals table
    with engine.connect() as connection:
        deals_df.to_sql('deals', con=connection, if_exists='append', index=False)
        
        # Get the id of the newly inserted deal
        result = connection.execute("SELECT lastval()")
        deal_id = result.scalar()
        
        # Add deal_id to the urls_df
        urls_df['deal_id'] = deal_id
        
        # Append URL data to the urls table
        urls_df.to_sql('urls', con=connection, if_exists='append', index=False)
    
    print(f"Deal for {buyer} acquiring {target} appended successfully with id: {deal_id}")
    return deal_id
def append_urls_to_database(engine, buyer, target, deal_id):
    # Get data using the functions from the referenced file
    deal_data = get_Data(buyer, target)
    
    # Clean the URL data
    urls_df = clean_urls(deal_data)
    
    # Ensure column names are clean
    urls_df.columns = urls_df.columns.str.strip()
    
    # Add deal_id to the urls_df
    urls_df['deal_id'] = deal_id
    
    # Reshape the DataFrame to have one URL per row
    urls_long = urls_df.melt(id_vars=['deal_id'], var_name='column_name', value_name='url')
    
    # Remove rows with null URLs
    urls_long = urls_long.dropna(subset=['url'])
    
    # Append URL data to the urls table
    with engine.connect() as connection:
        for _, row in urls_long.iterrows():
            query = text('''
                INSERT INTO urls (deal_id, column_name, url)
                VALUES (:deal_id, :column_name, :url)
            ''')
            connection.execute(query, {
                'deal_id': row['deal_id'],
                'column_name': row['column_name'],
                'url': row['url']
            })
    
    print(f"URLs for deal {deal_id} ({buyer} acquiring {target}) appended successfully")


def create_db_engine():
    # Load environment variables
    load_dotenv('final.env')

    # Get database connection parameters from environment variables
    db_host = os.getenv('DB_HOST')
    db_name = os.getenv('DB_NAME')
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    db_port = os.getenv('DB_PORT', 5432)  # Default to 5432 if not specified

    # Create the database URL
    db_url = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'

    # Create and return the SQLAlchemy engine
    engine = create_engine(db_url)
    
    print("Database engine created successfully.")
    return engine