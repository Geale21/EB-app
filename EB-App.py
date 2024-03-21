import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


path = r"C:\Users\HenryGeale\Ellis Bates Financial Solutions\Investment Team - General\Henry\Python\Morningstar Data Exports/"
df = pd.read_excel(path + "Web App Data - Test.xlsx")
#df = pd.read_excel(path + "Web App Test Data.xlsx", sheet_name="Sheet2")
#dfstyle = pd.read_excel(path + "Web App Data - Style.xlsx")

# Get the rows to add to the other dfs
ports = df.iloc[:,0]

# Get the style data, tidy column names and add portfolio names back in
dfstyle = df.filter(like="Style").copy()
for i in range(len(dfstyle.columns)):
    dfstyle.columns.values[i] = dfstyle.columns.values[i].replace("Equity Style ","")
    dfstyle.columns.values[i] = dfstyle.columns.values[i].replace(" % (Long Rescaled)","") 
dfstyle.insert(0, "Portfolio", ports)

# Get the regional data and tidy column names
dfregions = df.filter(like="Region").copy()
for i in range(len(dfregions.columns)):
    dfregions.columns.values[i] = dfregions.columns.values[i].replace("Equity Region ","")
    dfregions.columns.values[i] = dfregions.columns.values[i].replace(" % (Long Rescaled)","") 

# Remove "Developed" and "Emerging" columns
dfregions.drop(["Developed", "Emerging"], axis=1, inplace=True)

# Calculate Asia & EU total
asia = dfregions.filter(like="Asia").copy()
asia["Asia"] = asia.sum(axis=1)
eu = dfregions.filter(like="Europe").copy()
eu["Europe"] = eu.sum(axis=1)

# Drop originals and insert totals
dfregions.drop(dfregions.filter(like="Asia"), axis=1, inplace=True)
dfregions.insert(1, "Asia", asia.iloc[:,-1])
dfregions.drop(dfregions.filter(like="Europe"), axis=1, inplace=True)
dfregions.insert(1, "Europe", eu.iloc[:,-1])

dfregions = dfregions.sort_index(axis = 1) #sort regions alphabetically
dfregions.insert(0, "Portfolio", ports) #add portfolio names back in
dfregions["Total"] = dfregions.sum(axis=1, numeric_only=True) #total column to check all is 100%

#%% Streamlit Web App
ports = ["Growth (A)", "Growth (B)"]
selection = st.selectbox("Please select a portfolio", ports)

regions = list(dfregions.columns[1:-1])
st.write("Regional Allocation")
fig = px.bar(dfregions, x=[selection, "IA 40-85%"], y=["Asia", "Europe"], orientation='h', barmode="group", text_auto=True)
fig.update_traces(textposition='outside')
st.plotly_chart(fig)

#%%
