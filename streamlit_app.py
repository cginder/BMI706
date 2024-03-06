import altair as alt
import pandas as pd
import streamlit as st



#Open Tasks
#[x] combine search term trends into one annual metric (average? Last?)
#[x] get absolute/relative state level trends by multiplying state trend_value * trend value for that year
#[] ?create radio buttons to turn on/off filtering by each condition
#[x] year range 
#[] fixing label size so plots line up better
#[] 


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
merged_df['Relative_Weighting'] = merged_df['Annual_Avg_Trend_Value'] * merged_df['Search_Term_Value'] / 100
merged_df.rename(columns={'Region':'State'},inplace=True)

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

#Year Range Selector
year_range = st.slider('Years:',
        2004,2019,(2007,2014))
subset = subset[(subset['Year'] >= year_range[0]) & (subset['Year'] <= year_range[1])]

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
    options = race_options,
    default=race_options
)
subset = subset[subset["Race"].isin(race)]

#State Selectors
state_options = subset['State'].unique().tolist()
default_states = ["Indiana","Massachusetts"]
states = st.multiselect("State:",
    options = state_options,default=default_states
)
subset = subset[subset["State"].isin(states)]

#Trend Selector -- TWO Different selectors, one for chart 1 and one for chart 2
trend_options = gtrend_US_df["Search_Term"].unique().tolist()
default_trend_values = ["Cigarette","Diet","Statin"]
trends = st.multiselect("Multiple Trend Selector (For Chart # 1)",
    options = trend_options,default = default_trend_values)

#Trend Selector
chart_3_trend = st.selectbox("Single Trend Selector (For Chart # 3)",
    options = trend_options)

trend_subset_US_df = merged_df[merged_df["Search_Term"].isin(trends) & 
                        (merged_df['Year'] >= year_range[0]) & (merged_df['Year'] <= year_range[1])]

trend_subset_state_df = merged_df[(merged_df["Search_Term"] == chart_3_trend) &
                        (merged_df['Year'] >= year_range[0]) & (merged_df['Year'] <= year_range[1]) &
                        (merged_df['State'].isin(states))]


#Outcome Selector
outcome_options = subset["cause_of_death"].unique().tolist()
outcomes = st.multiselect("Select Cause(s) of Death",
    options = outcome_options, default = "Acute Myocardial Infarction"
)
subset = subset[subset["cause_of_death"].isin(outcomes)]


#Convert Mortality to Rates After Final Filtering
subset["Mortality_Rate"] = subset["Deaths"]/subset["Population"] * 100_000
cause_average_mortality_rate = subset.groupby(['cause_of_death','Year'])['Mortality_Rate'].mean().reset_index()
state_average_mortality_rate = subset.groupby(['State','Year'])['Mortality_Rate'].mean().reset_index()

#Different Google Trends Graph
chart = alt.Chart(trend_subset_US_df).mark_line(point=True).encode(
    x=alt.X("Year",axis=alt.Axis(format="d", title="Year")),
    y=alt.Y("Annual_Avg_Trend_Value"),
    color=alt.Color("Search_Term",legend=alt.Legend(orient='right'))
).properties(
    title="ROBABLY DISCARD: Google Trends Over Time",
    width=550
)

st.altair_chart(chart,use_container_width=True)


#Different Mortality Trends Over Time
chart2 = alt.Chart(cause_average_mortality_rate).mark_line(point=True).encode(
    x=alt.X("Year:O",axis=alt.Axis(format="d", title="Year")),
    y=alt.Y("Mortality_Rate:Q",title="Mortality Rate per 100,000"),
    color=alt.Color("cause_of_death",legend=alt.Legend(orient='right'))
).properties(
    title="PROBABLY DISCARD: Mortality Trends Over Time",
    width=550
)
#st.write(subset.head())
st.altair_chart(chart2,use_container_width=True)

#State Based Google Trends
chart3 = alt.Chart(trend_subset_state_df).mark_line(point=True).encode(
    x=alt.X("Year:O",axis=alt.Axis(format="d", title="Year")),
    y=alt.Y("Relative_Weighting:Q"),
    color=alt.Color("State",legend=alt.Legend(orient='right'))
).properties(
    title=f"Google Searches for {chart_3_trend} Over Time By State",
    width=550
)
#st.write(subset.head())
st.altair_chart(chart3,use_container_width=True)

#Different Mortality Trends Over Time
outcomes_title = ', '.join(outcomes)

chart4 = alt.Chart(state_average_mortality_rate).mark_line(point=True).encode(
    x=alt.X("Year:O",axis=alt.Axis(format="d", title="Year")),
    y=alt.Y("Mortality_Rate:Q",title="Mortality Rate per 100,000"),
    color=alt.Color("State",legend=alt.Legend(orient='right'))
).properties(
    title={"text":"Mortality Trends Over Time By State",
           "subtitle":f"Selected outcomes: {outcomes_title}"},
    width=550
)
st.altair_chart(chart4,use_container_width=True)

#Connected Scatter Plots
connected_scatter_df  = pd.merge(trend_subset_state_df,state_average_mortality_rate,on=['State','Year'],how='inner')
slider = alt.binding_range(min=connected_scatter_df['Year'].min(),max=connected_scatter_df['Year'].max(),step=1)
select_year = alt.selection_single(name="Year",fields=['Year'],bind=slider,init={'Year': df['Year'].min()})

chart5 = alt.Chart(connected_scatter_df).mark_line(point=True).encode(
    x=alt.X("Relative_Weighting:Q",title="Relative Search Trend"),
    y=alt.Y("Mortality_Rate:Q",title="Mortality Rate per 100,000"),
    color=alt.Color("State",legend=alt.Legend(orient='right')),
    tooltip=[
        alt.Tooltip('Mortality_Rate:Q', title='Mortality Rate'),
        alt.Tooltip('State:N', title='State'),
        alt.Tooltip('Relative_Weighting:Q', title='Relative Weighting'),
        alt.Tooltip('Year:O', title='Year') 
    ]
).properties(
    title={"text":"Connected Scatter Plot: Mortality by Search Trends",
           "subtitle":[f"Selected outcomes: {outcomes_title}",f"Selected search term: {chart_3_trend}"]},
    width=550
).transform_filter(
    select_year
)
st.altair_chart(chart5,use_container_width=True)
