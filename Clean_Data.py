import pandas as pd
import os

pd.set_option('display.max_columns', None) 

def clean_column_names(dataframe): 
    IN_PATH = os.path.join("data", "headers.xlsx")
    headers=pd.read_excel(IN_PATH)
    dataframe.columns=headers.columns
    return dataframe

def cleaning(dataframe): 
    dataframe['date_announced'] = pd.to_datetime(dataframe['date_announced'], format='%m/%d/%Y')
    dataframe['date_closed'] = pd.to_datetime(dataframe['date_closed'], format='%m/%d/%Y')


    dataframe["acquired_percentage"]=float(dataframe.loc[0,"acquired_percentage"].strip('%'))
    dataframe["deal_size"]=dataframe["deal_size"]*1000000
    return dataframe 


def implied_equity(dataframe):
    "Calculating Equity from EV and Net Debt"
    EV = dataframe["implied_ev"]
    ND = dataframe["implied_net_debt"]
    if pd.notna(EV).all() and pd.notna(ND).all():
        dataframe["implied_equity"] = EV - ND
    else:
        dataframe["implied_equity"] = None

    cols = list(dataframe.columns)
    ev_index = cols.index("implied_ev")
    nd_index = cols.index("implied_net_debt")
    ie_index = cols.index("implied_equity")
    new_cols = cols[:nd_index+1] + ["implied_equity"] + cols[nd_index+1:ie_index]
    dataframe = dataframe.loc[:, new_cols]
    
    return dataframe

def ratios(dataframe):
    """Calculating EV/EBITDA and EV/Sales"""
    EV = dataframe["implied_ev"]
    Sales = dataframe["ltm_revenue"]
    EBITDA = dataframe["ltm_ebitda"]
    
    if pd.notna(Sales).all() and pd.notna(EBITDA).all():
        
        if (EBITDA > 0).all():
            dataframe["ev_ebitda"] = EV / EBITDA
        else:
            dataframe["ev_ebitda"] = None
            

        if (Sales != 0).all():
            dataframe["ev_sales"] = EV / Sales
        else:
            dataframe["ev_sales"] = None

    else:
        dataframe["ev_ebitda"] = None
        dataframe["ev_sales"] = None

    cols = list(dataframe.columns)
    ebitda_index = cols.index("ltm_ebitda")
    ev_ebidta_index = cols.index("ev_ebitda")
  
    new_cols = cols[:ebitda_index+1] + ["ev_ebitda", "ev_sales"] + cols[ebitda_index+1:ev_ebidta_index]
    dataframe = dataframe.loc[:, new_cols]
    
    return dataframe

def clean_values(data):
    mf_values=pd.DataFrame() 
    for i in data.keys():
        a=data[i]
        akey=list(a.keys())
        mf_values.loc[0,i]=a[akey[0]]
    return mf_values

def clean_urls(data):
    mf_url=pd.DataFrame() 
    for i in data.keys():
        a=data[i]
        akey=list(a.keys())
        mf_url.loc[0,i]=a[akey[1]]
    return mf_url



