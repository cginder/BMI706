import altair as alt
import pandas as pd
import streamlit as st
import numpy as np


# Main function to structure the Streamlit app with different pages
  


def overview_page():
        st.title('Overview')
        st.write('Welcome to the Health Trends Dashboard.')


def google_trends_page(merged_df,gtrend_US_df, trend_options, trends, year_range, states):
        st.title('Google Trends Analysis')

    #Trend Selector
        trend_options = gtrend_US_df["Search_Term"].unique().tolist()
        selected_trends = st.sidebar.multiselect("Select Trend(s):", options=trend_options, default=["Cigarette", "Diet", "Statin"])
        chart_3_trend = st.selectbox("Single Trend Selector (For Chart # 3)",
            options = trend_options)
        trend_subset_US_df = merged_df[merged_df["Search_Term"].isin(trends) & 
                               (merged_df['Year'] >= year_range[0]) & (merged_df['Year'] <= year_range[1])]
        trend_subset_state_df = merged_df[(merged_df["Search_Term"] == chart_3_trend) &
                                (merged_df['Year'] >= year_range[0]) & (merged_df['Year'] <= year_range[1]) &
                                (merged_df['State'].isin(states))]
    #Different Google Trends Graph
        chart = alt.Chart(trend_subset_US_df).mark_line(point=True).encode(
            x=alt.X("Year",axis=alt.Axis(format="d", title="Year")),
            y=alt.Y("Annual_Avg_Trend_Value"),
            color=alt.Color("Search_Term",legend=alt.Legend(orient='right'))
        ).properties(
            title="Google Trends Over Time",
            width=550
        )

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
        st.altair_chart(chart,use_container_width=True)
        st.altair_chart(chart3,use_container_width=True)



def mortality_trends_page(cause_average_mortality_rate, state_average_mortality_rate, outcomes):
    st.title('Mortality Trends')
#Different Mortality Trends Over Time
    chart2 = alt.Chart(cause_average_mortality_rate).mark_line(point=True).encode(
        x=alt.X("Year:O",axis=alt.Axis(format="d", title="Year")),
        y=alt.Y("Mortality_Rate:Q",title="Mortality Rate per 100,000"),
        color=alt.Color("cause_of_death",legend=alt.Legend(orient='right'))
    ).properties(
        title="Mortality Trends Over Time",
        width=550
    )
    
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
    st.altair_chart(chart2,use_container_width=True)
    st.altair_chart(chart4,use_container_width=True)


def correlation_analysis_page(gtrend_US_df,trend_options,merged_df,state_average_mortality_rate, mortality_df ,annual_avg_df, outcome_options,states,year_range,trends):
    st.title('Correlation Analysis')
    #Trend Selector
    trend_options = gtrend_US_df["Search_Term"].unique().tolist()
#    selected_trends = st.sidebar.multiselect("Select Trend(s):", options=trend_options, default=["Cigarette", "Diet", "Statin"])
    connected_scatter_trend = st.selectbox("Single Trend Selector (For Connected Scatter Plot)",
        options = trend_options)
    trend_subset_US_df = merged_df[merged_df["Search_Term"].isin(trends) & 
                        (merged_df['Year'] >= year_range[0]) & (merged_df['Year'] <= year_range[1])]
    trend_subset_state_df = merged_df[(merged_df["Search_Term"] == connected_scatter_trend) &
                            (merged_df['Year'] >= year_range[0]) & (merged_df['Year'] <= year_range[1]) &
                            (merged_df['State'].isin(states))]



#Connected Scatter Plots
    connected_scatter_df  = pd.merge(trend_subset_state_df,state_average_mortality_rate,on=['State','Year'],how='inner')

# Creating a slider for the years & selector with legend
    slider = alt.binding_range(min=connected_scatter_df['Year'].min(), max=connected_scatter_df['Year'].max(), step=1, name='Select Year: ')
    select_year = alt.param(name="SelectorName",bind=slider,value=connected_scatter_df['Year'].min())
    state_selection = alt.selection_single(
        fields=["State"],bind='legend',name='SelectState'
    )


    points = alt.Chart(connected_scatter_df).mark_point().encode(
        x=alt.X("Relative_Weighting:Q",title="Relative Search Trend"),
        y=alt.Y("Mortality_Rate:Q",title="Mortality Rate per 100,000"),
        order="Year:O",
        color=alt.condition(state_selection,
                        "State:N",
                        alt.value("white")),
        opacity=alt.condition(
            'datum.Year <= SelectorName',
            alt.value(1),
            alt.value(0.25)
        ),
        tooltip=[
            alt.Tooltip('Mortality_Rate:Q', title='Mortality Rate'),
            alt.Tooltip('State:N', title='State'),
            alt.Tooltip('Relative_Weighting:Q', title='Relative Weighting'),
            alt.Tooltip('Year:O', title='Year') 
        ]
    ).add_params(
     select_year
    ).add_selection(
     state_selection
    )

    lines = alt.Chart(connected_scatter_df).mark_line().encode(
        x="Relative_Weighting:Q",
        y="Mortality_Rate:Q",
        order="Year:O",
        color=alt.condition(state_selection,
                            "State:N",
                            alt.value("lightgrey")),
     detail="State:N"  
    ).transform_filter(
        'datum.Year <= SelectorName'  
    ).add_params(
        select_year
    ).add_selection(
        state_selection
    )

    chart5 = points + lines

    st.altair_chart(chart5,use_container_width=True)




### Heatmap
    US_ave_mortality_df = mortality_df.groupby(['Year','cause_of_death'])[['Deaths','Population']].sum().reset_index()
    US_ave_mortality_df['Mortality_Rate'] = US_ave_mortality_df["Deaths"]/US_ave_mortality_df["Population"] * 100_000
    heatmap_df  = pd.merge(annual_avg_df,US_ave_mortality_df,on='Year',how='inner')

# Function to calculate Pearson correlation for a group
    def calculate_correlation(group):
        return group['Annual_Avg_Trend_Value'].corr(group['Mortality_Rate'])

# Group by 'cause_of_death' and apply the correlation calculation function
    correlation_by_cause = heatmap_df.groupby(['Search_Term','cause_of_death']).apply(calculate_correlation).reset_index(name='Correlation')

    chart6 = alt.Chart(correlation_by_cause).mark_rect().encode(
    x= alt.X ('Search_Term:N', title = 'Search Term'),
    y=alt.Y('cause_of_death:N', title='Cause of Death'),
    color='Correlation:Q'
    ).properties(
        title="Correlation of Google Search Terms with Cause of Mortality",
        width=550
    )

    st.altair_chart(chart6,use_container_width=True)


### Lagging Heatmap
    heat_outcome = st.selectbox("Select Cause of Death",
        options = outcome_options)

    lag_heat_mortality_df = US_ave_mortality_df[US_ave_mortality_df["cause_of_death"] == heat_outcome]

#create lag
    lag_values = range(-5,6)
    correlation_results = {}
    lag_points = []

    for search_term in trend_options:
        correlations = []
        for lag in lag_values:
            temp_df = annual_avg_df.copy()
            # Apply the lag
            temp_df['lag_year'] = temp_df['Year'] + lag
            # Merge based on the lagged year
            merged_df = pd.merge(temp_df, lag_heat_mortality_df, left_on='lag_year', right_on='Year', how='inner')
            # Filter for the specific search_term
            search_term_df = merged_df[merged_df['Search_Term'] == search_term]
            search_term_df['Lag'] = lag
            # Calculate the correlation
            correlation = calculate_correlation(search_term_df)
            correlations.append(correlation)
            #Append DataFrame to list
            lag_points.append(search_term_df)
        correlation_results[search_term] = correlations

    lag_points_df = pd.concat(lag_points,ignore_index=True)
    lag_correlation_df = pd.DataFrame(correlation_results, index=lag_values)

    # Convert the DataFrame to long format
    lag_heatmap_df= lag_correlation_df.reset_index().melt(id_vars='index', var_name='Search_Term', value_name='Correlation')
    # Give the 'index' column a more meaningful name
    lag_heatmap_df.rename(columns={'index': 'Lag'}, inplace=True)

    chart10 = alt.Chart(lag_heatmap_df).mark_rect().encode(
        x='Lag:O',
        y=alt.Y('Search_Term:N', title='Search Term'),
        color='Correlation:Q'
    ).properties(
        title={"text":"Correlation of Google Search Terms with Cause of Mortality, Offset by Lag",
               "subtitle":f"Selected outcome:{heat_outcome}"}, 
        width=550
    )


    st.altair_chart(chart10,use_container_width=True)



# Selector for Lag and Search Term
    lag_heat_selection = alt.selection_multi(fields=['Lag'], on='click',clear='dblclick', toggle=True)
    search_heat_selection = alt.selection_multi(fields=['Search_Term'], on='click',clear='dblclick', toggle=True)

    chart7 = alt.Chart(lag_heatmap_df).mark_rect().encode(
        x='Lag:O',  
        y=alt.Y('Search_Term:N', title='Search Term'),
        color='Correlation:Q',
        opacity=alt.condition(
            lag_heat_selection & 
            search_heat_selection,
            alt.value(1),  
            alt.value(0.5)  
        )
    ).properties(
        title={
            "text": "C7: Correlation of Google Search Terms with Cause of Mortality, Offset by Lag",
            "subtitle": f"Selected outcome: {heat_outcome}"
        },
        width=550
    ).add_selection(
     lag_heat_selection
    ).add_selection(
     search_heat_selection
    )


    chart8 = alt.Chart(lag_points_df).transform_filter(
        search_heat_selection
    ).transform_filter(
     lag_heat_selection
    ).mark_point().encode(
        x= alt.X("Annual_Avg_Trend_Value",title='Annual Average Trend Value'),
        y=alt.Y('Mortality_Rate:Q', title='Mortality Rate'),
        color='Search_Term:N'
    # opacity= alt.condition(search_heat_selection,alt.Color('Search_Term:N'),alt.value('lightgray'))
    ).properties(
         width=550
    ).add_params(
        lag_heat_selection
    ).add_params(
        search_heat_selection
    )

    regression_line = chart8.transform_regression(
        'Annual_Avg_Trend_Value', 'Mortality_Rate', method="linear"
    ).mark_line(
        color='lightgrey', strokeDash=[5, 5]
    )
    combined_chart = alt.vconcat(chart7,chart8+ regression_line)

    st.altair_chart(combined_chart,use_container_width=True)

######################################
def main():
    # Load your data here (if it's not part of page-specific functions)
    
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

    # Global sidebar controls:
    st.sidebar.title('Global Filters')

    # State Selectors
    state_options = mortality_df['State'].unique().tolist()
    default_states = ["Indiana", "Massachusetts"]
    states = st.sidebar.multiselect("State:", options=state_options, default=default_states)

    # Year Range Selector
    year_range = st.sidebar.slider('Years:', 2004, 2019, (2007, 2014))

    # Sex Selector
    sex = st.sidebar.radio("Sex", ["Male", "Female"])

    # Age Group Range Selector
    age_group_range = st.sidebar.select_slider(
        "Select Age Group Range:",
        options=age_group_codes,
        value=('15-24', '75-84')
    )

    # Race Selectors
    race_options = mortality_df["Race"].unique().tolist()
    race = st.sidebar.multiselect("Select Races:", options=race_options, default=race_options)

    # Trend Selector for Chart #1
    trend_options = gtrend_US_df["Search_Term"].unique().tolist()
    default_trend_values = ["Cigarette", "Diet", "Statin"]
    trends = st.sidebar.multiselect("Multiple Trend Selector (For Chart #1):", options=trend_options, default=default_trend_values)

    # Outcome Selector
    outcome_options = mortality_df["cause_of_death"].unique().tolist()
    outcomes = st.sidebar.multiselect("Select Cause(s) of Death:", options=outcome_options, default=["Acute Myocardial Infarction"])

    # Apply filters
    subset = mortality_df[(mortality_df['Year'] >= year_range[0]) & (mortality_df['Year'] <= year_range[1])]
    subset = subset[subset['State'].isin(states)]
    subset = subset[subset['Gender'] == sex]
    age_group_start_factor = age_group_mapping[age_group_range[0]]
    age_group_end_factor = age_group_mapping[age_group_range[1]]
    subset = subset[(subset['Age_Group_Factor'] >= age_group_start_factor) & (subset['Age_Group_Factor'] <= age_group_end_factor)]
    subset = subset[subset['Race'].isin(race)]
    subset = subset[subset['cause_of_death'].isin(outcomes)]
    #Convert Mortality to Rates After Final Filtering
    subset["Mortality_Rate"] = subset["Deaths"] / subset["Population"] * 100_000
    cause_average_mortality_rate = subset.groupby(['cause_of_death','Year'])['Mortality_Rate'].mean().reset_index()
    state_average_mortality_rate = subset.groupby(['State','Year'])['Mortality_Rate'].mean().reset_index()


    # Page Navigation
    st.sidebar.title('Navigation')
    page = st.sidebar.radio("Select a page:", ["Overview", "Mortality Trends", "Google Trends Analysis", "Correlation Analysis"])

    # Page-specific filters and page function calls
    if page == "Overview":
        st.title('Overview')
        st.write('Welcome to the Health Trends Dashboard.')
   

    elif page == "Google Trends Analysis":
          # Place Google Trends Analysis-specific filters in the sidebar
      # Call the page function with the selected trends
      google_trends_page(merged_df,gtrend_US_df, trend_options, trends, year_range, states)

    elif page == "Mortality Trends":
    # If there are specific filters for Mortality Trends, they would go here.
    # As it looks like you've moved all filters globally, there might not be additional filters.
    # If there are, define and use them here.
        mortality_trends_page(cause_average_mortality_rate, state_average_mortality_rate,outcomes)

    elif page == "Correlation Analysis":
    # If there are specific filters for Correlation Analysis, they would be placed here.
         correlation_analysis_page(gtrend_US_df,trend_options,merged_df,state_average_mortality_rate, mortality_df ,annual_avg_df, outcome_options,states,year_range,trends)

if __name__ == "__main__":
    main()