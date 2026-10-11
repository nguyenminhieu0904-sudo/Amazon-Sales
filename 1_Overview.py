import streamlit as st
import pandas as pd 
import numpy as np 
import plotly.express as px

st.set_page_config(
    page_title = 'Amazone Sales Analysis',
    page_icon = '🛒',
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

def main():
    st.title('🛒 Amazon Sales Dashboard')
    st.markdown("""Welcome to Amazon Sales Analysis Dashboard. This interactive tool explores over 1,000 Amazon products.
    Uses the sidebar to navigate through different deep dive analyses.
    """)

    try:
         data = load_and_clean_data()
    except:
        st.error("Failed to load data")
        st.stop()

    st.sidebar.title('Filter Options')
    all_categories = data['main_category'].unique().tolist()
    selected_category = st.sidebar.multiselect(
        'Select Category', options = all_categories,default = all_categories)

    rating_range = st.sidebar.slider('Rating Range',
    min_value = float(data['rating'].min()),
    max_value = float(data['rating'].max()),
    value = (float(data['rating'].min()), float(data['rating'].max())),
    step = 0.1
    )

    price_range = st.sidebar.slider('Price Range',
    min_value = int(data['actual_price'].min()),
    max_value = int(data['actual_price'].max()),
    value = (int(data['actual_price'].min()), int(data['actual_price'].max())),
    step = 100
    )

    filtered_data = data[
    (data['main_category'].isin(selected_category)) &
    (data['rating'] >= rating_range[0]) &
    (data['rating']<= rating_range[1]) &
    (data['discounted_price'] >= price_range[0]) &
    (data['discounted_price'] <= price_range[1])
    ]
    if filtered_data.empty:
        st.warning('No data available for the selected filters. Please adjust your filter criteria.')
        st.stop()

    st.header('Data Overview')
    st.markdown(""""This section provides high level view of dataset and key performance indicators.""")

    st.subheader('Key Performance Indicators')
    col1,col2,col3,col4 = st.columns(4)
    total_categories = filtered_data['main_category'].nunique()
    avg_rating = round(filtered_data['rating'].mean(),2)
    avg_discount = round(filtered_data['discount_percentage'].mean(),2)
    total_products = filtered_data.shape[0]

    col1.metric('Total Product Analyzed', f'{total_products:,}')
    col2.metric('Average Rating', f'{avg_rating}')
    col3.metric('Average Discount', f'{avg_discount}%')
    col4.metric('Total Categories', f'{total_categories}')

    st.header('Initial Visual Insights')
    st.subheader('Distribution of Products Rating')
    fig_rating = px.histogram(filtered_data, x='rating', nbins=20, labels={'rating':'Product Rating'}, color_discrete_sequence=['#636EFA'])
    fig_rating.update_layout(bargap=0.1)
    st.plotly_chart(fig_rating, use_container_width=True)

    st.header('Distribution of Products Discounts')
    st.subheader('Distribution of Products Discounts')
    fig_discount = px.histogram(filtered_data, x='discount_percentage', nbins=20, labels={'discount_percentage':'Discount Percentage'}, color_discrete_sequence=['#1F77B4'])
    fig_discount.update_layout(bargap=0.1)
    st.plotly_chart(fig_discount, use_container_width=True)

    st.header('Top 10 Most Frequent Product Categories')
    category_counts = filtered_data['main_category'].value_counts().nlargest(10).reset_index()
    category_counts.columns = ['Category', 'Count']
    fig_category = px.bar(category_counts, x='Count', y='Category', orientation='h', title='Top 10 Product Categories', labels = {'Count':'Number of Products', 'Category':'Product Category'}, color='Count', color_continuous_scale='Blues')
    fig_category.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_category, use_container_width=True)

    st.markdown("The bar chart above shows the top 10 most frequent product categories in the filtered dataset. This provides insights into which categories are most represented among the products analyzed.")
    
if __name__ == '__main__':    
    main()