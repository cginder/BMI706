import altair as alt
import pandas as pd
import streamlit as st


# Read Data
mortality_df = pd.read_csv("https://raw.githubusercontent.com/cginder/BMI706/main/Data/Merged%20Data/mortality_data.csv")
gtrend_US_df = pd.read_csv("https://raw.githubusercontent.com/cginder/BMI706/main/Data/Merged%20Data/search_US_trends.csv")
gtrend_state_df = pd.read_csv("https://raw.githubusercontent.com/cginder/BMI706/main/Data/Merged%20Data/search_state_based.csv")


#Select Trends
trend_options = gtrend_US_df["Search_Term"].unique().tolist()
trends = st.multiselect("Search_Term",trend_options)

subset = gtrend_US_df[gtrend_US_df["Search_Term"] == trends]


#Test Plot
chart = alt.Chart(subset).mark_line().encode(
    x=alt.X("Month"),
    y=alt.Y("Trend_Value"),
    color="Search_Term"
)

st.altair_chart(chart,use_container_width=True)