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
        host=host,
        port=port,
        database=database,
        user=username,
        password=password
    )
    st.success("Connected to the database successfully!")
except Exception as e:
    st.error(f"Error: {e}")

    

def run_app():
    """Initializes streamlit application"""
    st.title("Retrieving Mergers and Acquisitions Deal Information")

    target_input = st.text_input("Enter Target Company here: ")
    buyer_input = st.text_input("Enter Buyer Company here: ")

    if st.button("Submit"):
        if target_input and buyer_input:
            st.write("Querying database for deal information...")
            
            # SQL query that filters for inputted target company and buyer company
            query = """
            SELECT * FROM deals
            WHERE buyer = %s AND target = %s;
            """

            try:
                # Execute the query with parameters (to prevent SQL injection)
                with connection.cursor() as cursor:
                    cursor.execute(query, (buyer_input, target_input))
                    # Fetch the results
                    result = cursor.fetchall()

                    if result:
                        # Convert the result to a pandas DataFrame
                        df = pd.DataFrame(result, columns=[desc[0] for desc in cursor.description])
                        st.write(df)
                    else:
                        st.warning("No deals found for the given companies.")
            except Exception as query_error:
                st.error(f"Error querying the database: {query_error}")
        else:
            st.warning("Please enter both target and buyer companies.")



if __name__ == "__main__":
    run_app()