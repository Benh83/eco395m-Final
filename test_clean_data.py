import pandas as pd
from Clean_Data import clean_column_names, cleaning, implied_equity, ratios

# create a sample dataframe
data = {
    'date_announced': ['03/08/2022', '02/15/2021'],
    'date_closed': ['09/12/2022', '08/30/2021'],
    'acquired_percentage': ['100%', '50%'],
    'deal_size': [5400, 1200],
    'implied_ev': [6000, 1300],
    'implied_net_debt': [600, 100],
    'ltm_revenue': [3000, 500],
    'ltm_ebitda': [600, 200]
}

df = pd.DataFrame(data)

# test each function
print("Original DataFrame:")
print(df)

# test `cleaning`
df_cleaned = cleaning(df.copy())
print("\nAfter `cleaning`:")
print(df_cleaned)

# test `implied_equity`
df_with_equity = implied_equity(df_cleaned.copy())
print("\nAfter `implied_equity`:")
print(df_with_equity)

# test `ratios`
df_with_ratios = ratios(df_with_equity.copy())
print("\nAfter `ratios`:")
print(df_with_ratios)