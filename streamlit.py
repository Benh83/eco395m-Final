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
            WHERE buyer = %s AND target = %s;
            """

            # SQL query to get data from the 'urls' table
            urls_query = """
            SELECT * FROM urls
            WHERE buyer = %s AND target = %s;
            """

            try:
                # Execute the query for 'deals' table
                with connection.cursor() as cursor:
                    # Query for deals
                    cursor.execute(deals_query, (buyer_input, target_input))
                    deals_result = cursor.fetchall()

                    if deals_result:
                        # Convert the result to a pandas DataFrame
                        deals_df = pd.DataFrame(
                            deals_result,
                            columns=[desc[0] for desc in cursor.description],
                        )
                        st.write("Deals Data:")
                        st.write(deals_df)
                    else:
                        st.warning("No deals found for the given companies.")

                    # Query for URLs
                    cursor.execute(urls_query, (buyer_input, target_input))
                    urls_result = cursor.fetchall()

                    if urls_result:
                        # Convert the result to a pandas DataFrame
                        urls_df = pd.DataFrame(
                            urls_result,
                            columns=[desc[0] for desc in cursor.description],
                        )
                        st.write("URLs Data:")
                        st.write(urls_df)
                    else:
                        st.warning("No URLs found for the given companies.")

            except Exception as query_error:
                st.error(f"Error querying the database: {query_error}")
        else:
            st.warning("Please enter both target and buyer companies.")


if __name__ == "__main__":
    run_app()
