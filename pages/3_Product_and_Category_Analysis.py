import streamlit as st
import pandas as pd 
import numpy as np 
import plotly.express as px
import re
from wordcloud import WordCloud
from nltk.corpus import stopwords
import nltk
import matplotlib.pyplot as plt

st.set_page_config(
    page_title = 'Product and Category Analysis',
    page_icon = '📦',
    layout = 'wide',
    initial_sidebar_state = 'expanded',
)
@st.cache_data
def download_nltk_resources():
    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('stopwords')
def extract_keywords(text):
    if not isinstance(text, str):
        return []
    tokens = re.findall(r"[a-zA-Z0-9]+",text.lower())
    stop_words = set(stopwords.words('english'))
    keywords = [word for word in tokens if word not in stop_words and len(word) > 2]
    return keywords
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

def product_category_analysis_page():
    st.title('📦 Product and Category Analysis')
    st.markdown("""This page provides an in-depth analysis of products and categories on Amazon.""")

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

    discount_price_range = st.sidebar.slider(
        'Discounted Price Range',
        min_value = int(data['discounted_price'].min()),
        max_value = int(data['discounted_price'].max()),
        value = (int(data['discounted_price'].min()), int(data['discounted_price'].max())),
        step = 100
    )

    filtered_data = data[
        (data['main_category'].isin(selected_category)) &
        (data['rating'] >= rating_range[0]) &
        (data['rating'] <= rating_range[1]) &
        (data['discounted_price'] >= discount_price_range[0]) &
        (data['discounted_price'] <= discount_price_range[1])
    ]
    if filtered_data.empty:
        st.warning("No data available for the selected filters.")
        st.stop()
    st.header('Analysis by Product Category')
    st.subheader('Product Count by Main Category')
    
    col_graph_1, col_data_1 = st.columns([2,1])
    with col_data_1:
        st.markdown("### Category metrics")
        st.dataframe(filtered_data.groupby('main_category').agg(
            total_products=('product_name', 'count'),
            avg_rating=('rating', 'mean'),
            avg_discount=('discount_percentage', 'mean')
            ).reset_index().sort_values(by='total_products', ascending=False),
            hide_index = True 
            )

    
    category_counts = filtered_data['main_category'].value_counts().reset_index()
    category_counts.columns = ['main_category','total_products']
    
    with col_graph_1:    
        fig_category = px.bar(category_counts,
                        x='total_products', y='main_category', orientation='h',  
                        labels = {'total_products':'Number of Products', 'main_category':'Product Category'}, 
                        color='total_products', color_continuous_scale='Blues',
                        title = 'Number of Products by Main Category',
                        hover_data = ['main_category', 'total_products'])
        fig_category.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_category, use_container_width=True)
    
    st.markdown("This chart and table provide insights into the distribution of products across different main categories. You can filter the data using the sidebar options to focus on specific categories, rating ranges, and discounted price ranges.")

    st.header('Most Popular Products')    
    st.markdown("Products ranked by their rating count, which indicates their popularity among customers.")

    st.markdown("### Top 10 Products by Rating Count")
    col_graph_2, col_data_2 = st.columns(2)
    popular_product = filtered_data.sort_values(by='rating_count', ascending=True).head(10)
    with col_graph_2:
        fig_popular = px.bar(popular_product, 
                        y='product_name', x ='rating_count', orientation='h',  
                        labels = {'rating_count':'Rating Count', 'product_name':'Product Name'}, 
                        color='rating_count', color_continuous_scale='Blues',
                        title = 'Top 10 Products by Rating Count',
                        hover_data = ['main_category', 'discounted_price']
                        )
        st.plotly_chart(fig_popular, use_container_width=True)
    with col_data_2:
        st.markdown("### Top 10 Popular Products by Rating Count")
        st.dataframe(filtered_data[['product_name','main_category','rating_count']])
    st.markdown("This bar chart display the top 10 products based on their rating count, providing insights into which products are most popular among customers. The accompanying table lists the product names, their main categories, and their respective rating counts for further analysis.")

    st.header('Common Keywords in Product Names')
    st.markdown("The word cloud below visualizes the most common keywords found in product names, excluding common stopwords. This can help identify trends and popular features in product offerings.")
    filtered_data['keywords'] = filtered_data['product_name'].apply(extract_keywords)
    all_keywords = [keyword for sublist in filtered_data['keywords'] for keyword in sublist]
    
    if all_keywords:
        text = ' '.join(all_keywords)
        wordcloud = WordCloud(width=800, height=400, background_color='white', colormap='viridis', max_words=100).generate(text)

        col_graph_3, col_data_3 = st.columns(2)
        with col_graph_3:
                fig,ax = plt.subplots(figsize=(12, 6))
                ax.imshow(wordcloud, interpolation='bilinear')
                ax.axis('off')
                st.pyplot(fig)
        with col_data_3:
                st.markdown("### Common Keywords in Product Names")
                keyword_counts = pd.Series(all_keywords).value_counts().head(10).reset_index()
                keyword_counts.columns = ['Keyword', 'Count']
                st.dataframe(keyword_counts)
    else:
        st.warning("No keywords found in the product names for the selected filters.")












if __name__ == "__main__":
    product_category_analysis_page()