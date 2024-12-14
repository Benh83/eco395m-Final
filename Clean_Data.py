import pandas as pd
import os

def clean_values(data):
    mf_values = pd.DataFrame(columns=['Buyer', 'Target'])
    for i in data.keys():
        a = data[i]
        akey = list(a.keys())
        mf_values.loc[0, i] = a[akey[0]]
    return mf_values


def clean_urls(data):
    mf_url = pd.DataFrame(columns=['Buyer', 'Target'])
    for i in data.keys():
        a = data.get(i)
        akey = list(a.keys())
        mf_url.loc[0, i] = a.get(akey[1])
    return mf_url
    
def clean_column_names(dataframe):
    IN_PATH = os.path.join("setup", "headers.xlsx")
    headers = pd.read_excel(IN_PATH)
    dataframe.columns = headers.columns.str.strip()
    return dataframe


def cleaning(dataframe):
    dataframe=clean_column_names(dataframe)
    #Clean Dates depending on what format they come in. 
    if dataframe["date_announced"].isna()[0]:
        dataframe.loc[0,"date_announced"] = pd.to_datetime(
            dataframe.loc[0,"date_announced"], format="%m/%d/%Y"
    )
    
    elif dataframe.loc[0,"date_announced"].count("/")==2 : 
        dataframe.loc[0,"date_announced"] = pd.to_datetime(
            dataframe.loc[0,"date_announced"], format="%m/%d/%Y"
    )
    elif dataframe.loc[0,"date_announced"].count("/")==1:
        dataframe.loc[0,"date_announced"]=pd.to_datetime(dataframe.loc[0,"date_announced"].split("/")[0]+"/01/"+(dataframe.loc[0,"date_announced"].split("/"))[1])
    else:
        dataframe.loc[0,"date_announced"]=pd.to_datetime(None)


    if dataframe["date_closed"].isna()[0]:
        dataframe.loc[0,"date_closed"] = pd.to_datetime(
            dataframe.loc[0,"date_closed"], format="%m/%d/%Y"
    )
    
    elif dataframe.loc[0,"date_closed"].count("/")==2 : 
        dataframe.loc[0,"date_closed"] = pd.to_datetime(
            dataframe.loc[0,"date_closed"], format="%m/%d/%Y"
    )
    elif dataframe.loc[0,"date_closed"].count("/")==1:
        dataframe.loc[0,"date_closed"]=pd.to_datetime(dataframe.loc[0,"date_closed"].split("/")[0]+"/01/"+(dataframe.loc[0,"date_closed"].split("/"))[1])
    else:
        dataframe.loc[0,"date_closed"]=pd.to_datetime(None)



    dataframe["date_closed"] = pd.to_datetime(
        dataframe["date_closed"], format="%m/%d/%Y"
    )
    float_columns = [
        "acquired_percentage",
        "deal_size",
        "premium",
        "implied_equity_value",
        "implied_net_debt",
        "ly_revenue",
        "ly_ebitda",
    ]

    for col in float_columns:
        if col in dataframe.columns and isinstance(dataframe.loc[0, col], str):
            if "%" in dataframe.loc[0, col]:
                dataframe.loc[0, col] = float(dataframe.loc[0, col].strip("%"))

            else:
                dataframe.loc[0,col] = float(dataframe.loc[0,col])
    dataframe["deal_size"] = dataframe["deal_size"] * 1000000
    dataframe["ly_revenue"] = dataframe["ly_revenue"] * 1000000
    dataframe["ly_ebitda"] = dataframe["ly_ebitda"] * 1000000
    dataframe["implied_equity_value"] = dataframe["implied_equity_value"] * 1000000
    dataframe["implied_net_debt"] = dataframe["implied_net_debt"] * 1000000
    dataframe = ratios(dataframe)
    return dataframe


def ratios(dataframe):
    """Calculating EV/EBITDA and EV/Sales"""
    dataframe = enterprise_value(dataframe)
    EV = dataframe["implied_ev"]
    Sales = dataframe["ly_revenue"]
    EBITDA = dataframe["ly_ebitda"]

    dataframe["ev_ebitda"] = (EV / EBITDA).where(
        pd.notna(Sales) & pd.notna(EBITDA) & (EBITDA > 0), None
    )
    dataframe["ev_sales"] = (EV / Sales).where(pd.notna(Sales) & (Sales != 0), None)

    cols = list(dataframe.columns)
    ebitda_index = cols.index("ly_ebitda")
    ev_ebidta_index = cols.index("ev_ebitda")

    new_cols = (
        cols[: ebitda_index + 1]
        + ["ev_ebitda", "ev_sales"]
        + cols[ebitda_index + 1 : ev_ebidta_index]
    )
    dataframe = dataframe.loc[:, new_cols]

    return dataframe





def enterprise_value(dataframe):
    "Calculating EV from Equity and Net Debt"
    EQ = dataframe["implied_equity_value"]
    ND = dataframe["implied_net_debt"]

    dataframe["implied_ev"] = dataframe.apply(
        lambda row: row["implied_equity_value"]
        if pd.isna(row["implied_net_debt"])
        else (
            row["implied_equity_value"] + row["implied_net_debt"]
            if pd.notna(row["implied_equity_value"])
            else None
        ),
        axis=1,
    )

    cols = list(dataframe.columns)
    nd_index = cols.index("implied_net_debt")
    ie_index = cols.index("implied_ev")
    new_cols = cols[: nd_index + 1] + ["implied_ev"] + cols[nd_index + 1 : ie_index]
    dataframe = dataframe.loc[:, new_cols]

    return dataframe
