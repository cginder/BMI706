import altair as alt
import pandas as pd
import streamlit as st



#Open Tasks
#[x] combine search term trends into one annual metric (average? Last?)
#[x] get absolute/relative state level trends by multiplying state trend_value * trend value for that year
#[] ?create radio buttons to turn on/off filtering by each condition


##Read Data
mortality_df = pd.read_csv("https://raw.githubusercontent.com/cginder/BMI706/main/Data/Merged%20Data/mortality_data.csv")
gtrend_US_df = pd.read_csv("https://raw.githubusercontent.com/cginder/BMI706/main/Data/Merged%20Data/search_US_trends.csv")
gtrend_state_df = pd.read_csv("https://raw.githubusercontent.com/cginder/BMI706/main/Data/Merged%20Data/search_state_based.csv")

##Data Processing
#Combine US Trend Data Into Annual Data
gtrend_US_df['Month'] = pd.to_datetime(gtrend_US_df['Month'])
gtrend_US_df['Year'] = gtrend_US_df['Month'].dt.year #convert to date/time format
annual_avg_df = gtrend_US_df.groupby(['Year', 'Search_Term'])['Trend_Value'].mean().reset_index() #calculate average per year
annual_avg_df.rename(columns={'Trend_Value': 'Annual_Avg_Trend_Value'}, inplace=True) #rename for clarity

#Merge State Level Data to Get Relative Ranking (Annual Search Term Value * Relative Search Term Value for that state, that year)
merged_df = pd.merge(gtrend_state_df, annual_avg_df, on=['Year', 'Search_Term'], how='left')
merged_df['Relative_Weighting'] = merged_df['Annual_Avg_Trend_Value'] * merged_df['Search_Term_Value']

#Convert Age Group Codes to Factors
age_group_mapping = {
    '15-24': 1,
    '25-34': 2,
    '35-44': 3,
    '45-54': 4,
    '55-64': 5,
    '65-74': 6,
    '75-84': 7,
    '85+': 8  
}
age_group_codes = list(age_group_mapping.keys())
mortality_df['Age_Group_Factor'] = mortality_df['Ten-Year Age Groups Code'].map(age_group_mapping)

##Master Filter Chart
subset = mortality_df

#Year Selector
year = st.slider('Year',1999,2019,2009)
subset = subset[subset['Year'] == year]

#Sex Selector
sex = st.radio("Sex",["Male","Female"])
subset = subset[subset['Gender'] == sex]

#Age Group Range Selector
age_group_range = st.select_slider(
    "Select Age Group Range:",
    options=age_group_codes,
    value=('15-24','75-84')
)
age_group_start_factor = age_group_mapping[age_group_range[0]]
age_group_end_factor = age_group_mapping[age_group_range[1]]

subset = subset[(subset['Age_Group_Factor'] >= age_group_start_factor) &
    (subset['Age_Group_Factor'] <= age_group_end_factor)
]

#Race Selectors
race_options = subset["Race"].unique().tolist()
race = st.multiselect("Select Races:",
    options = race_options
)
subset = subset[subset["Race"].isin(race)]

#State Selectors
state_options = subset['State'].unique().tolist()
default_states = ["Indiana","Massachusetts"]
states = st.multiselect("State:",
    options = state_options,default=default_states
)
subset = subset[subset["State"].isin(states)]

#Trend Selector
trend_options = gtrend_US_df["Search_Term"].unique().tolist()
default_trend_values = ["Cigarette","Diet","Statin"]
trends = st.multiselect("Search_Term",
    options = trend_options,default = default_trend_values)

trend_subset = merged_df[merged_df["Search_Term"].isin(trends)]

#Outcome Selector
outcome_options = subset["cause_of_death"].unique().tolist()
outcomes = st.multiselect("Select Cause(s) of Death",
    options = outcome_options
)
subset = subset[subset["cause_of_death"].isin(outcomes)]

#Test Plot 1
chart = alt.Chart(trend_subset).mark_line().encode(
    x=alt.X("Year",axis=alt.Axis(format="d", title="Year")),
    y=alt.Y("Annual_Avg_Trend_Value"),
    color="Search_Term"
)

st.altair_chart(chart,use_container_width=True)


#Test Plot 2
chart2 = alt.Chart(subset).mark_bar().encode(
    x=alt.X("Year",axis=alt.Axis(format="d", title="Year")),
    y=alt.Y("sum(Deaths):Q"),
    color="cause_of_death"
)
st.write(subset.head())
st.altair_chart(chart2,use_container_width=True)