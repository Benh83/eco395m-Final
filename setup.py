import pandas as pd
import psycopg2
from psycopg2 import sql
import os
import subprocess
import sys

def connect_to_db():
    """Establishes a connection to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(
            dbname="ibsheets",
            user="postgres",
            password="IBeasy395m",
            host="34.41.134.112",
            port="5432"        
        )
        return conn
    except psycopg2.Error as e:
        print(f"Error connecting to the database: {e}")
        return None
    
def search_deals_in_db(conn, target, buyer):
    """Searches for a specific deal in the PostgreSQL database."""
    try:
        query = """
        SELECT * FROM deals
        WHERE target = %s AND buyer = %s
        """
        with conn.cursor() as cur:
            cur.execute(query, (target, buyer))
            result = cur.fetchall()
            return result
    except psycopg2.Error as e:
        print(f"Error querying the database: {e}")
        return None

def add_deal_to_db(conn, target, buyer, date_announced, source):
    """Adds a new deal to the PostgreSQL database."""
    try:
        query = """
        INSERT INTO deals (target, buyer, date_announced, source)
        VALUES (%s, %s, %s, %s)
        """
        with conn.cursor() as cur:
            cur.execute(query, (target, buyer, date_announced, source))
            conn.commit()
    except psycopg2.Error as e:
        print(f"Error inserting into the database: {e}")

def process_deals(csv_path='deal.csv', perplexity_script='perplexity_query.py'):
    """Processes each deal from the CSV file."""
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"The file '{csv_path}' does not exist.")
    
    # Load deals from CSV
    deals_df = pd.read_csv(csv_path)
    
    if 'Target' not in deals_df.columns or 'Buyer' not in deals_df.columns:
        raise ValueError("The CSV file must contain 'Target' and 'Buyer' columns.")
    
    # Connect to the PostgreSQL database
    conn = connect_to_db()
    if not conn:
        print("Database connection failed. Exiting.")
        return
    
    # Process each deal in the CSV
    for _, row in deals_df.iterrows():
        target = row['Target']
        buyer = row['Buyer']
        
        print(f"Processing deal: Target={target}, Buyer={buyer}...")
        
        # Search for the deal in the database
        matching_deals = search_deals_in_db(conn, target, buyer)
        
        if matching_deals:
            print("Matching deal(s) found in the database:")
            for deal in matching_deals:
                print(deal)
        else:
            print("No matching deal found. Executing perplexity_query.py...")
            
            # Run the Perplexity script and capture its output
            result = subprocess.run(
                [sys.executable, perplexity_script],  # Runs the script using the current Python interpreter
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                print(f"Error running Perplexity script: {result.stderr}")
                continue
            
            # Parse the output from the Perplexity script
            output = result.stdout.strip()
            print(f"Perplexity script output: {output}")
            
            # Expecting the output to be structured as:
            # "Date Announced: <date>, Source: <source>"
            try:
                date_announced, source = map(
                    lambda x: x.split(":")[1].strip(),
                    output.split(", ")
                )
            except Exception as e:
                print(f"Error parsing output from Perplexity script: {e}")
                continue
            
            # Add the new deal to the database
            add_deal_to_db(conn, target, buyer, date_announced, source)
            print(f"New deal added to the database: Target={target}, Buyer={buyer}, Date={date_announced}, Source={source}")
    
    # Close the database connection
    conn.close()


# Run the program
process_deals(csv_path='deal.csv')

