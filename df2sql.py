import pandas as pd
   from sqlalchemy import create_engine
engine = create_engine('postgresql+psycopg2://postgres:IBeasy395m@34.41.134.112:5432/ibsheets')
from perplexity_query import (FUNCTION TO GET DATAFRAME)
def append_to_sql():
   try: 
      VIGHNESHDATA = FUNCTION TO GET DATAFRAME()
      if VIGHNESHDATA.empty:
            print("No new data to append.")
            return
      VIGHNESHDATA.to_sql('deals', con=engine, if_exists='append', index=False)
        print(f"Data successfully appended to 'deals'. {len(VIGHNESHDATA)} rows added.")
   except Exception as e:
        print(f"Error appending data to SQL: {e}")
        raise

if __name__ == "__main__":
    append_to_sql()