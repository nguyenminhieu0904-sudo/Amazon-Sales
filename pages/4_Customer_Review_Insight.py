import streamlit as st
import pandas as pd 
import numpy as np 
import plotly.express as px
import re
from wordcloud import WordCloud
import nltk
from nltk.corpus import stopwords
import matplotlib.pyplot as plt

st.set_page_config(
    page_title = 'Customer Review Insight',
    page_icon = '📝',
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

def customer_review_insight_page():
    st.title('📝 Customer Review Insight')
    st.markdown("""Create a detailed analysis of customer reviews and ratings on Amazon.
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
        step = 0.1)

    discount_price_range = st.sidebar.slider(
        'Discounted Price Range',
        min_value = int(data['discounted_price'].min()),
        max_value = int(data['discounted_price'].max()),
        value = (int(data['discounted_price'].min()), int(data['discounted_price'].max())),
        step = 100)

    filtered_data = data[
        (data['main_category'].isin(selected_category)) &
        (data['rating'] >= rating_range[0]) &
        (data['rating'] <= rating_range[1]) &
        (data['discounted_price'] >= discount_price_range[0]) &
        (data['discounted_price'] <= discount_price_range[1])]

    if filtered_data.empty:
        st.warning("No data available for the selected filters.")
        st.stop()
    st.header('How do Ratings Correlate with Popularity?')
    st.markdown("This chart investigates wheher a higher rating corresponds to a higher number of reviews. (rating_count)")

    col_graph1, col_data_1 = st.columns(2)
    with col_graph1:
        fig_price_corr = px.scatter(
            filtered_data, x = 'rating', y = 'rating_count', color = 'main_category', 
            opacity = 0.6, 
            title = 'Rating vs Popularity (Number of Reviews)',
            labels = {
                'rating': 'Average Rating',
                'rating_count': 'Number of Ratings'  
            }
        )
        st.plotly_chart(fig_price_corr, use_container_width = True)
    with col_data_1:
        st.markdown("### Descriptive Statistics")
        st.dataframe(filtered_data[['rating', 'rating_count']].describe())
    
    ratign_popularity_corr = filtered_data['rating'].corr(filtered_data['rating_count'])
    st.markdown('The correlation coefficient between rating and popularity (number of reviews) is: **{:.2f}**'.format(ratign_popularity_corr))

    st.subheader('Most frequent words in customer reviews')
    st.markdown('This word cloud visualizes the most common words found in customer reviews. It can provide insights into what customers are talking about and their sentiments.')

    review_texts = filtered_data['review_content'].dropna()
    if not review_texts.empty:
        filtered_data['keywords'] = review_texts.apply(extract_keywords)
        all_keywords = [kw for sublist in filtered_data['keywords'] for kw in sublist]
        if all_keywords:
            text = ' '.join(all_keywords)
            wordcloud = WordCloud(width=800, height=400, background_color='white',colormap = 'viridis', max_words=100).generate(text)

            col_graph2, col_data_2 = st.columns(2)
            with col_graph2:
                fix, ax = plt.subplots(figsize=(12, 6))
                ax.imshow(wordcloud, interpolation='bilinear')
                ax.axis('off')
                st.pyplot(fix)
            with col_data_2:
                st.markdown("### Common Keywords in Customer Reviews")
                keyword_counts = pd.Series(all_keywords).value_counts().head(10).reset_index()
                keyword_counts.columns = ['Keyword', 'Count']
                st.dataframe(keyword_counts)
            st.markdown("The word cloud above visualizes the most common keywords found in customer reviews, excluding common stopwords. This can help identify trends and popular features in product offerings.")
        else:
            st.warning("No keywords found in the customer reviews for the selected filters.")
    else: 
        st.warning("No customer reviews available for the selected filters.")

if __name__ == "__main__":
    customer_review_insight_page()