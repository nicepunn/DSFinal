import streamlit as st
import pandas as pd
import pydeck as pdk
import plotly.express as px

st.title("Analysis of the Thailand Rain Daily Dataset from RainDaily_Tabular")

@st.cache_data
def load_data():
    df = pd.read_csv("./RainDaily_Tabular.csv")
    return df

# Load the dataset
df = load_data()
df['date'] = pd.to_datetime(df.date)

# Get the unique values of the province and date columns
province = df.province.unique()
date = df.date.unique()

provinces = st.sidebar.multiselect("provinces", province)

# Select all provinces
selectAllProvinces = st.sidebar.checkbox("Select all provinces", value=False)
if selectAllProvinces:
    provinces = province

startDate = st.sidebar.date_input("start date", date[0])
endDate = st.sidebar.date_input("end date", date[-1])
dates = pd.date_range(startDate, endDate)

# Display the dataset
st.write(df.head())

st.write(df["province"].value_counts()[df["province"].value_counts().min() == df["province"].value_counts()])

# Filter the dataset by selected provinces and dates
df_filtered = df[df.province.isin(provinces)]
df_filtered = df_filtered[df_filtered.date.isin(dates)]

# Display the filtered dataset
st.subheader("Average rain from selected province:")

# Plot the average rain by province

# Bar chart
if df_filtered.empty:
    st.write("")
else:
    fig = px.bar(df_filtered.groupby('province').rain.mean(), y='rain', title='Average rain by province').update_layout(
        xaxis_title="Province",
        yaxis_title="Average rain",
    )
    st.plotly_chart(fig)

# Line chart

if df_filtered.empty:
    st.write("")
else:
    # Create an empty list to store data for each province
    data_for_plot = []

    # Iterate over selected provinces
    for province in provinces:
        df_filtered_province = df_filtered[df_filtered.province == province]
        # Append data for this province to the list
        data_for_plot.append(df_filtered_province.groupby('date').rain.mean().rename(province))

    # Concatenate the data into a single DataFrame
    df_for_plot = pd.concat(data_for_plot, axis=1)

    # Plot using Streamlit's line chart
    fig = px.line(df_for_plot, title='Average rain from selected province').update_layout(
        xaxis_title="Date",
        yaxis_title="Average rain",
    )
    st.plotly_chart(fig)

avg_rain_by_province = df_filtered.groupby('province')

#pydeck map for the average rain by province
province_map = df_filtered.groupby('province')[['longitude', 'latitude','rain']].mean()

# Display the map
st.subheader("Map of rain")

# Map show rain in each area
layer = pdk.Layer(
    "ScatterplotLayer",
    province_map,
    pickable=True,
    filled=True,
    radius_scale=2500,
    radius_min_pixels=1,
    radius_max_pixels=100,
    line_width_min_pixels=1,
    get_position= ["longitude", "latitude"],
    get_radius = ["rain"] ,
    get_fill_color=[200, 100, 100],
    opacity=0.6
)

if df_filtered.empty:
    view_state = pdk.ViewState(
        longitude=df.longitude.mean(),
        latitude=df.latitude.mean(),
        zoom=4,
    )
    r = pdk.Deck(
        map_style="mapbox://styles/mapbox/light-v9",
        initial_view_state= view_state,
    )
    st.pydeck_chart(r)
else:
    view_state = pdk.ViewState(
        longitude=province_map.longitude.mean(),
        latitude=province_map.latitude.mean(),
        zoom=4.5,
    )
    r = pdk.Deck(
        map_style="mapbox://styles/mapbox/light-v9",
        layers=[layer],
        initial_view_state=view_state,
        tooltip={"text": "Rain: {rain} mm"},
    )
    st.pydeck_chart(r)

# Display summary 
st.subheader("Summary of Rainfall Analysis")

if df_filtered.empty:
    summary_text = ""
# Display summary text
    st.write(summary_text)
else: 
    highest_rain = avg_rain_by_province.rain.mean().max()
    lowest_rain = avg_rain_by_province.rain.mean().min()

    summary_text = f"The analysis of the rainfall data shows that the province with the highest average rainfall is {avg_rain_by_province.rain.mean().idxmax()} with an average of {highest_rain:.2f} mm. The province with the lowest average rainfall is {avg_rain_by_province.rain.mean().idxmin()} with an average of {lowest_rain:.2f} mm."
    st.write(summary_text)

# Display the source code
st.subheader("Source Code")
with open('Rain.py', "r", encoding="utf-8") as f:
    code = f.read()
st.code(code, language="python")