import streamlit as st
import psycopg2
import pandas as pd


dialect = st.secrets["postgres"]["dialect"]
host = st.secrets["postgres"]["host"]
port = st.secrets["postgres"]["port"]
database = st.secrets["postgres"]["database"]
username = st.secrets["postgres"]["username"]
password = st.secrets["postgres"]["password"]

try:
    connection = psycopg2.connect(
        host=host, port=port, database=database, user=username, password=password
    )
    st.success("Connected to the database successfully!")
except Exception as e:
    st.error(f"Error: {e}")


def run_app():
    """Initializes Streamlit application"""
    st.title("Retrieving Mergers and Acquisitions Deal Information")

    # Input fields for target and buyer company
    target_input = st.text_input("Enter Target Company here: ")
    buyer_input = st.text_input("Enter Buyer Company here: ")

    # When the "Submit" button is clicked
    if st.button("Submit"):
        if target_input and buyer_input:
            st.write("Querying database for Deal and URL information...")

            # SQL query to get data from the 'deals' table
            deals_query = """
            SELECT * FROM deals
            WHERE LOWER(buyer) LIKE LOWER(%s) AND LOWER(target) LIKE LOWER(%s);
            """

            # SQL query to get data from the 'urls' table
            urls_query = """
            SELECT * FROM urls
            WHERE LOWER(buyer) LIKE LOWER(%s) AND LOWER(target) LIKE LOWER(%s);
            """

            try:
                # Converts SQL to dataframe
                deals_df = pd.read_sql_query(deals_query, connection, params=("%" + buyer_input + "%", "%" + target_input + "%"))
                if not deals_df.empty:
                    st.write("Deals Data: ")
                    st.write(deals_df)
                else:
                    st.warning("No deals found ")
                
                urls_df = pd.read_sql_query(urls_query, connection,params=("%" + buyer_input + "%", "%" + target_input + "%") )
                if not urls_df.empty:
                    st.write("URLs Data: ")
                    st.write(urls_df)
                else:
                    st.warning("No URLs found")

                

            except Exception as query_error:
                st.error(f"Error querying the database: {query_error}")
        else:
            st.warning("Please enter both target and buyer companies.")


if __name__ == "__main__":
    run_app()
