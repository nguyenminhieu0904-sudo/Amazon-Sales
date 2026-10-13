import streamlit as st
import pandas as pd 
import numpy as np 
import plotly.express as px
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler

st.set_page_config(
    page_title = 'Product Recommendation',
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
    
    data['full_text'] = (data['product_name'].str.lower() + ' ' + 
                      data['about_product'].str.lower() + ' ' +
                      data['category'].str.lower())

    return data

def extract_num(text, pattern):
    match = re.search(pattern,text, re.IGNORECASE)
    return float(match.group(1)) if match else None

def extract_features(row):
    features = {}
    text = row['full_text']

    features['brand'] = row['product_name'].split(' ')[0].lower()
    features['length_m'] = extract_num(text, r'(\d+)(\.\d+)?\s*m')
    features['length_cm'] = extract_num(text, r'(\d+)(\.\d+)?\s*cm')
    features['length_ft'] = extract_num(text, r'(\d+)(\.\d+)?\s*ft')

    if features['length_cm']: features['length_m'] = features['length_cm'] / 100
    if features['length_ft']: features['length_m'] = features['length_ft'] * 0.3048

    features['watts'] = extract_num(text, r'(\d+)(\.\d+)?\s*w')
    features['type_c'] = ('type-c' in text) or ('type c' in text) or ('usb-c' in text) or ('usb c' in text)
    features['micro_usb'] = int('micro usb' in text)
    features['lightning'] = int('lightning' in text)
    features['usb_a'] = int('usb-a' in text) or ('usb a' in text)

    fast_keywords = ['fast charging','fast charge','quick charge','qc 3.0','power delivery','pd','rapid charge']
    features['fast_charge']= int(any(kw in text for kw in fast_keywords))
    features['braided'] = int('braided' in text)
    features['nylon'] = int('nylon' in text)
    features['metal'] = int('metal' in text)
    features['tangle_free'] = int('tangle' in text)

    colors = ['black','white','red','blue',"green","yellow","silver","gold","grey","pink","purple"]
    for c in colors:
        features[f'color_{c}'] = int(c in text)
    device = ['iphone','ipad','android','samsung','vivo','oppo','oneplus']
    for d in device:
        features[f'supports_{d}'] = int(d in text)

    features['pack_counts'] = extract_num(text, r'pack of (\d+)')
    durability_kw = ['durable','heat-resistant','heavy-duty','premium','strong','reinforced']
    features['durability'] = int(any(kw in text for kw in durability_kw))
    features['price_bucket'] = int(row['discounted_price']//500) if row['discounted_price'] else 0
    features['category_match'] = data['category'].apply(lambda r: str(r).split('|')[0].lower())
    features['keywords'] = text
    return features
    
    data['features'] = data.apply(extract_features,axis=1)

    numeric_cols_for_scaling = ["watts","typec", "fast_charge", "braided","color_black","color_white","color_red","color_blue","color_green",]
    feature_data = pd.DataFrame(data['features'].tolist())

    for col in numeric_cols_for_scaling:
        if col not in feature_data.columns:
            feature_data[col] = np.nan
    data = pd.concat([data, feature_data], axis=1)

    for col in numeric_cols_for_scaling:
        data[col] = data[col].fillna(data[col].fillna(0).astype(float))
    return data, numeric_cols_for_scaling

@st.cache_resource 
def build_similarity_matrix(_data, _numeric_features):
    tfidf = tfidfVectorizer(stop_words='english', max_features=5000)
    text_matrix = tfidf.fit_transform(_data["full_text"])
    text_sim_matrix = cosine_similarity(text_matrix)

    scaler = MinMaxScaler()
    numeric_scaled = scaler.fit_transform(_data[_numeric_features])
    numeric_sim_matrix = cosine_similarity(numeric_scaled)
    return text_sim_matrix, numeric_sim_matrix 

def get_similarity_score(idx1, idx2, text_sim, num_sim, data):
    text_score = text_sim[idx1, idx2]
    cat_boost = 1.2 if data.loc[idx1, "main_category"] == data.loc[idx2,"main_category"] else 1.0
    return (0.6 * text_score + 0.4 * num_score) * cat_boost

def recommend_products(data, product_name, text_sim, num_sim, top_n = 5):
    if product_name not in data["product_name"].values:
        return None

    idx = data.index[data["product_name"] == product_name][0]

    scores = [(i, get_similarity_score(idx, i, text_sim, num_sim, data)) for i in rage(len(data)) if i != idx]
    scores = sorted(scores, key=lambda x : x[1], reverse = True)

    top_indices = [i[0] for i in score[:top_n]]
    return data.loc[top_indices, ["product_name", "main_category","discounted_price","rating"]]

def recommended_page():
    st.title('Product Recommendation Engines')
    st.markdown("""Select a product from the dropdown below to see a list in top 5 similar products.
    """)

    try:
        data, numeric_features = load_and_clean_data()
        text_sim_matrix,numeric_sim_matrix =  build_similarity_matrices(data, numeric_features) 
    except Exception as e:
        st.error("Failed to load data")
        st.exception(e)
        st.stop()
    product_list = data['product_name'].unique()
    select_product = st.selecbox('Choose a Product to get Recommendation for:', product_list, index = 0)

    if st.button('Find Similar Product'):
       with st.spinner('Finding Recommendation ...'):
            recommendation = recommend_product(data, select_product, tex_sim_matrix, numeric_sim_matrix)
            st.subheader(f'Top 5 Recommendation for {select_product} are:')
            if recommendation is not None and not recommendation.empty:
               st.table(recommendation['product_name','main_category','discounted_price'])
               st.markdown("""The table present the top 5 products most similar to your selected data""")
            else: st.warning('Could not find any recommendation')

if __name__ == "__main__":
    recommended_page()