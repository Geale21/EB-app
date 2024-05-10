import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt

st.set_page_config(page_title="Portfolio Dashboard", layout="wide")
pd.options.display.float_format = '{:.2f}%'.format

path = r"C:\Morningstar Exports/"
df_main = pd.read_excel(path + "Web App Data - Test.xlsx")

# Get the portfolio names and tidy them
ports = df_main.iloc[:,0].copy()
for i in range(len(ports)):
    ports[i] = ports[i].replace("EBIP ","")
    ports[i] = ports[i].replace(" - P+","")
    ports[i] = ports[i].replace("Mixed Investment ","")
    ports[i] = ports[i].replace(" Shares","")
pheader = "Portfolio" #we can name the column this in each df rather than typing it, so we can change in one place if needed

bmark = {
    "Growth (A)" : "IA 40-85%",
    "Growth (B)" : "IA 40-85%",
}

# Set naming convention for relative columns
rel = " Diff"

#%% FUNCTIONS

def getdata(name):
    df = df_main.filter(like=name).copy() #copy columns from df_main
    return df

def addportnames(df):
    df.insert(0, pheader, ports) #add portfolio names back in
    return df

# Transpose data so portfolios are columns (for charts)
def transpose(df, name):
    df = df.set_index(pheader).T
    df.reset_index(inplace=True)
    df.columns.values[0] = name
    return df

def renamecols(df, name):
    df[name] = df[name].str.replace(" % (Long Rescaled)","")
    if name == "Style":
        df[name] = df[name].str.replace("Equity Style ","")
    elif name == "Region":
        df[name] = df[name].str.replace("Equity Region ","")
    return df

def relativecols(df):
    for i in range(1, len(df.columns)-1):
        df[df.columns[i] + rel] = df[df.columns[i]] - df[list(bmark.values())[i-1]]
    return df

#%% STYLE DATA

df_style = getdata("Style")
df_style = addportnames(df_style)
df_style = transpose(df_style, "Style")
df_style = renamecols(df_style, "Style")
df_style = relativecols(df_style)

#%% REGIONAL DATA

df_regions = df_main.filter(like="Region").copy() #copy columns from df_main
# Remove Developed and Emerging columns
df_regions.drop(df_regions.filter(like="Developed"), axis=1, inplace=True)
df_regions.drop(df_regions.filter(like="Emerging"), axis=1, inplace=True)

#Create totals for Asia/EU, drop original columns and add new ones
asia = df_main.filter(like="Asia").sum(axis=1)
europe = df_main.filter(like="Europe").sum(axis=1)
df_regions.drop(df_regions.filter(like="Asia"), axis=1, inplace=True)
df_regions.drop(df_regions.filter(like="Europe"), axis=1, inplace=True)
df_regions["Asia"] = asia
df_regions["Europe"] = europe

df_regions = addportnames(df_regions)
df_regions = transpose(df_regions, "Region")
df_regions = renamecols(df_regions, "Region")
df_regions = relativecols(df_regions)

# Sort regions alphabetically and reset index
df_regions.sort_values("Region", inplace=True)
df_regions.reset_index(drop=True, inplace=True)

#%% Streamlit Web App

# Pick portfolio
selection = st.selectbox("Please select a portfolio", ports.iloc[:-1])

#Regional Chart
traces = []
buttons = []

traces.append(go.Bar(x=df_regions[selection], y=df_regions["Region"], visible=True, orientation='h', marker_color='#072C54', text=df_regions[selection],  name=selection))
traces.append(go.Bar(x=df_regions[bmark[selection]], y=df_regions["Region"], visible=True, orientation='h', marker_color='#E6B200', text=df_regions[bmark[selection]], name=bmark[selection]))
traces.append(go.Bar(x=df_regions[selection + rel], y=df_regions["Region"],visible=False, orientation='h', marker_color='#A01C4A', name=selection + rel))

buttons.append(dict(label="Absolute",
                    method="update",
                    args=[{"visible": [True, True, False]},
                          {"xaxis.title.text": "Allocation",},],))

buttons.append(dict(label="Relative",
                    method="update",
                    args=[{"visible": [False, False, True]},
                          {"xaxis.title.text": "Relative Allocation",},],))

# Create the layout 
layout = go.Layout(updatemenus=[dict(type='buttons',buttons= buttons, direction='left',x=0,y=1.2,showactive=False)], showlegend=True)

fig = go.Figure(data=traces, layout=layout)
fig.update_traces(textposition='outside')
fig.update_xaxes(title_text='Allocation')
fig.update_yaxes(title_text='Region')
fig.update_traces(textposition='outside')
fig.update_traces(texttemplate= "%{value:.1f}%")
fig.update_traces(hovertemplate = "%{value:.1f}%")

st.write("Regional Allocation")
st.plotly_chart(fig)#, use_container_width=True)

#%% STYLE CHART

#Build stylebox df
stylebox = pd.DataFrame(index=["Large", "Mid", "Small"], columns=["Value", "Core", "Growth"])
stylebox_rel = pd.DataFrame(index=["Large", "Mid", "Small"], columns=["Value", "Core", "Growth"])


for c in range(len(stylebox.columns)):
    for r in range(len(stylebox.index)):
        stylebox.iloc[r, c] = df_style.at[df_style.query(
        "Style == '" + stylebox.index[r] + " " + stylebox.columns[c] + "'").index[0], selection]

for c in range(len(stylebox_rel.columns)):
    for r in range(len(stylebox_rel.index)):
        stylebox_rel.iloc[r, c] = df_style.at[df_style.query(
        "Style == '" + stylebox_rel.index[r] + " " + stylebox_rel.columns[c] + "'").index[0], selection + rel]

# Absolute
stylebox = stylebox.astype(float)
stylebox = stylebox.round(1)

# Relative
stylebox_rel = stylebox_rel.astype(float)
stylebox_rel = stylebox_rel.round(1)

#Style table
stylesum = df_style[["Style", selection, bmark[selection], selection + rel]].iloc[:6].round(1)
stylesum_rel = df_style[["Style", selection + rel, bmark[selection]]].iloc[:6].round(1)

col1, col2 = st.columns(2, gap="large")
        
with col1:
    st.checkbox("Relative", value=False, key="Relative")
    if st.session_state.Relative == True:
        fig = px.imshow(stylebox_rel, text_auto=True)
    else:
        fig = px.imshow(stylebox, text_auto=True)
    st.plotly_chart(fig)

with col2:
    if st.session_state.Relative == True:
        st.dataframe(stylesum_rel, width=None, hide_index=True)
    else:
        st.dataframe(stylesum, width=None, hide_index=True)

#st.column_config.NumberColumn("Weight”, format=”% %f")
#fig.update_traces(texttemplate = "%{label}: %{value:$,s}")
