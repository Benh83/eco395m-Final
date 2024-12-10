import json
import pandas as pd
import os
import re
from aiscrape import get_Data
from aiscrape import clean_values
from aiscrape import clean_urls
import pandas as pd

pd.set_option('display.max_columns', None) 

Buyer = input("Enter Buyer here: ")
Target = input("Enter Target here: ")
B_T = get_Data(Buyer,Target)
clean_data=clean_values(B_T)
#clean_url=clean_urls(B_T)


def implied_equity(dataframe):
    "Calculating Equity from EV and Net Debt"
    EV = dataframe["Implied EV"]
    ND = dataframe["Implied Net Debt"]
    if pd.notna(EV).all() and pd.notna(ND).all():
        dataframe["Implied Equity"] = EV - ND
    else:
        dataframe["Implied Equity"] = None

    cols = list(dataframe.columns)
    ev_index = cols.index("Implied EV")
    nd_index = cols.index("Implied Net Debt")
    
    new_cols = cols[:nd_index+1] + ["Implied Equity"] + cols[nd_index+1:]
    dataframe = dataframe[new_cols]
    
    return dataframe



def ratios(dataframe):
    """Calculating EV/EBITDA and EV/Sales"""
    EV = dataframe["Implied EV"]
    Sales = dataframe["LTM Revenue"]
    EBITDA = dataframe["LTM EBITDA"]
    
    if pd.notna(Sales).all() and pd.notna(EBITDA).all():
        
        if (EBITDA > 0).all():
            dataframe["EV/EBITDA"] = EV / EBITDA
        else:
            dataframe["EV/EBITDA"] = None
            

        if (Sales != 0).all():
            dataframe["EV/Sales"] = EV / Sales
        else:
            dataframe["EV/Sales"] = None

    else:
        dataframe["EV/EBITDA"] = None
        dataframe["EV/Sales"] = None

    cols = list(dataframe.columns)
    ebitda_index = cols.index("LTM EBITDA")
    
  
    new_cols = cols[:ebitda_index+1] + ["EV/EBITDA", "EV/Sales"] + cols[ebitda_index+1:]
    dataframe = dataframe[new_cols]
    
    return dataframe


clean_data = implied_equity(clean_data)
clean_data = ratios(clean_data)

print(clean_data)
