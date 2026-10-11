import streamlit as st
import pandas as pd 
import numpy as np 
import plotly.express as px
import nltk
nltk.download('stopwords', quiet=True)
from nltk.corpus import stopwords
st.set_page_config(
    page_title = 'Price and Discount Analysis',
    page_icon = '💰',
    layout = 'wide',
    initial_sidebar_state = 'expanded',
)
@st.cache_data
def load_and_clean_data():
    data = pd.read_csv("amazon.csv")

    data['discounted_price'] = data['discounted_price'].str.replace('₹', '')
    data['discounted_price'] = data['discounted_price'].str.replace(',','')
    data['discounted_price'] = data['discounted_price'].astype(float)

    data['actual_price'] = data['actual_price'].str.replace('₹', '')
    data['actual_price'] = data['actual_price'].str.replace(',','')
    data['actual_price'] = data['actual_price'].astype(float)

    data['discount_percentage'] = data['discount_percentage'].str.replace('%','')
    data['discount_percentage'] = data['discount_percentage'].astype(float)

    data.loc[data['rating']== '|', 'rating'] = '4.0'
    data['rating'] = data['rating'].astype(float)

    data['rating_count'] = data['rating_count'].str.replace(",","").astype(float)
    data['rating_count'] = data['rating_count'].fillna(data['rating_count'].median())

    data.dropna(subset=['category'],inplace=True)

    data['main_category']= data['category'].apply(lambda x: x.split('|')[0])
    return data 

def price_analysis_page():
    st.title('💰 Price and Discount Analysis')
    st.markdown("""This page provides an in-depth analysis of product prices and discounts on Amazon. 
    Explore the distribution of discounted prices, actual prices, and discount percentages across different categories.
    """)

    try:
         data = load_and_clean_data()
    except Exception as e:
        st.error("Failed to load data")
        st.exception(e)
        st.stop()

    st.sidebar.title('Filter Options')
    all_categories = data['main_category'].unique().tolist()
    selected_category = st.sidebar.multiselect(
        'Select Category', options = all_categories, default = all_categories
    )

    rating_range = st.sidebar.slider(
        'Rating Range',
        min_value = float(data['rating'].min()),
        max_value = float(data['rating'].max()),
        value = (float(data['rating'].min()), float(data['rating'].max())),
        step = 0.1
    )

    price_range = st.sidebar.slider(
        'Discounted Price Range',
        min_value = float(data['discounted_price'].min()),
        max_value = float(data['discounted_price'].max()),
        value = (float(data['discounted_price'].min()), float(data['discounted_price'].max())),
        step = 100.0
    )

    price_range = st.sidebar.slider(
        'Discounted Percentage Range',
        min_value = float(data['discount_percentage'].min()),
        max_value = float(data['discount_percentage'].max()),
        value = (float(data['discount_percentage'].min()), float(data['discount_percentage'].max())),
        step = 2.0
    )

    filtered_data = data[
        (data['main_category'].isin(selected_category)) &
        (data['rating'] >= rating_range[0]) &
        (data['rating'] <= rating_range[1]) &
        (data['discounted_price'] >= price_range[0]) &
        (data['discounted_price'] <= price_range[1])
    ]

    if filtered_data.empty:
        st.warning("No data available for the selected filters.")
        st.stop()
    
    st.header('Price Correlation Analysis')
    col_graph1, col_data_1 = st.columns(2)
    with col_graph1:
        fig_price_corr = px.scatter(
            filtered_data, x = 'actual_price', y = 'discounted_price', 
            opacity = 0.6, 
            trendline = 'ols',
            trendline_color_override = 'red',
            labels = {
                'actual_price': 'Actual Price',
                'discounted_price': 'Discounted Price'  
            }
        )
        st.plotly_chart(fig_price_corr, use_container_width = True)
    with col_data_1:
        st.markdown("### Descriptive Statistics")
        st.dataframe(filtered_data[['actual_price', 'discounted_price']].describe())

    st.header('Discount vs Popularity Analysis')
    st.markdown("Does a higher price tag mean a better rating? Lets investigate!")
    col_graph3, col_data_4 = st.columns(2)
    with col_graph3:
        fig_price_rating = px.scatter(
            filtered_data, x = 'discounted_price', y = 'rating_count', 
            opacity = 0.6, 
            labels = {
                'discounted_price': 'Discounted Price',
                'rating_count': 'Rating Count'
            }
        )
        st.plotly_chart(fig_price_rating, use_container_width = True)
    with col_data_4:
        st.markdown("### Descriptive Statistics")
        st.dataframe(filtered_data[['discounted_price', 'rating_count']].describe())
    
    st.header('Price vs Customer Rating Analysis')
    st.markdown("Does a higher price tag mean a better rating? Lets investigate!")
    col_graph5, col_data_6 = st.columns(2)
    with col_graph5:
        fig_price_rating = px.scatter(
            filtered_data, x = 'actual_price', y = 'rating', 
            opacity = 0.6, 
            labels = {
                'actual_price': 'Actual Price',
                'rating': 'Rating (out of 5)'
            }
        )
        st.plotly_chart(fig_price_rating, use_container_width = True)
    with col_data_6:
        st.markdown("### Descriptive Statistics")
        st.dataframe(filtered_data[['actual_price', 'rating']].describe())

if __name__ == "__main__":
    price_analysis_page()
