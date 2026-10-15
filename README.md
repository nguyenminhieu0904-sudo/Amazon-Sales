# 🛒 Amazon Product Analytics & Recommendation App

An interactive data analytics project built with **Python, Pandas, Plotly, Scikit-learn, and Streamlit** to explore Amazon product listings, analyze pricing and customer reviews, and recommend similar products based on product attributes.

🔗 **Live Demo: https://amazon-sales-analysee.streamlit.app/Price_and_Discount_Analysis
💻 **GitHub Repository: https://github.com/nguyenminhieu0904-sudo/Amazon-Sales.git

## 1. Project Overview

### Background

E-commerce platforms contain large volumes of product information, pricing data, ratings, and customer reviews. Analyzing these data can help identify product trends, understand customer feedback, compare pricing patterns, and discover similar products.

### Objectives

This project aims to:

- Clean and transform raw product data into an analysis-ready dataset.
- Explore product prices, discounts, ratings, review counts, and category distributions.
- Identify frequently occurring keywords in product names and customer reviews.
- Build an interactive dashboard for exploring product data.
- Develop a content-based recommendation system that suggests similar products.

**Note:** The dataset contains product listings and review-related information, rather than actual transaction-level sales data. Therefore, rating counts are used as a proxy for product popularity, not as a direct measure of sales volume.

---

## 2. Dataset

The project uses an Amazon product dataset containing **1,465 product records and 16 original columns**.

**Product information:** `product_id`, `product_name`, `category`, `about_product`

**Pricing:** `actual_price`, `discounted_price`, `discount_percentage`

**Customer ratings:** `rating`, `rating_count`

**Customer reviews:** `review_title`, `review_content`

**Additional information:** `user_id`, `review_id`, `img_link`, `product_link`

The dataset includes product information across multiple categories, including Electronics, Computers & Accessories, and Home & Kitchen.

## 3. Data Cleaning & Preparation

The raw dataset contains currency symbols, percentage signs, numeric values stored as strings, and missing values. The project applies the following preprocessing steps:

- **Data type conversion:** Remove currency symbols (`₹`), commas, and percentage signs before converting price, discount, and rating-count columns into numeric formats.
- **Rating correction:** Replace the invalid `|` rating value with `4.0`, following an explicit assumption in the preprocessing logic.
- **Missing value handling:** Fill missing values in `rating_count` using the column median.
- **Category processing:** Remove records with missing category information and extract the main category from the hierarchical category field.
- **Text preprocessing:** Combine product names, product descriptions, and category information into a text field for similarity analysis.
- **Feature extraction:** Use regular expressions and keyword matching to extract selected product attributes, including wattage, connector types, fast-charging support, braided cables, and colors.

The resulting dataset supports both exploratory data analysis and product recommendation.

---

## 4. Exploratory Data Analysis & Key Insights

The dashboard allows users to interactively explore the dataset using category, rating, and price filters.

### 4.1 Product ratings and discounts

- The average product rating in the cleaned dataset is approximately **4.10 out of 5**.
- The average listed discount is approximately **47.69%**.
- Discounts between 50% and 60% form one of the most frequent discount ranges in the dataset.

These figures describe the products in this dataset and should not be interpreted as representative statistics for all Amazon products.

### 4.2 Discount and product popularity

The Pearson correlation between `discount_percentage` and `rating_count` is approximately **0.01** in the cleaned dataset.

This indicates almost no linear relationship between discount percentage and rating count in this sample. A higher listed discount does not necessarily correspond to a higher number of ratings.

However, rating count is only a proxy for popularity. The dataset does not establish the causal effect of discounts on actual purchases or revenue.

### 4.3 Price and customer ratings

The Pearson correlation between `actual_price` and `rating` is approximately **0.12**, indicating a weak positive linear relationship in this sample.

This suggests that listed price alone is not a strong indicator of customer ratings. Other factors, such as product quality, features, and customer expectations, may also matter.

### 4.4 Product categories and customer reviews

The category analysis highlights how products are distributed across categories and identifies products with high rating counts.

Keyword-frequency visualizations help reveal recurring terms in product names and customer reviews. These patterns can support further investigation into product features and customer concerns.

*The results above are descriptive findings, not proof of causation. The dashboard can be used to explore whether patterns differ across product categories.*

---

## 5. Business Recommendations

Based on the exploratory analysis, the following are potential recommendations for further investigation:

1. **Evaluate discount effectiveness beyond discount depth.** Compare discount levels with rating counts and other available product attributes. Transaction and conversion data would be needed to determine the effect on sales and profitability.
2. **Use category-level analysis to guide merchandising.** Identify categories with a large number of listed products and investigate their pricing, ratings, and popularity patterns before making assortment decisions.
3. **Use review keywords to identify customer priorities.** Frequently mentioned product features can inform further review analysis and product-description improvements. Keyword frequency alone does not establish positive or negative customer sentiment.
4. **Improve product discovery through recommendations.** Use the recommendation feature to surface products with similar descriptions and selected attributes, making it easier to explore alternatives within the catalogue.

These recommendations are hypotheses generated from the available dataset; they should be validated with additional business data before implementation.

---

## 6. Interactive Dashboard

The application is organized into five analytical pages.

### Page 1 — Overview

- Key performance indicators:
  - Total products analyzed
  - Average product rating
  - Average discount percentage
  - Number of product categories
- Rating and discount distributions
- Top 10 most represented product categories
- Interactive category, rating, and price filters

### Page 2 — Price & Discount Analysis

- Comparison of actual and discounted prices
- Scatter plots for exploring price and rating-count relationships
- Correlation analysis and descriptive statistics
- Exploration of pricing and discount patterns

### Page 3 — Product & Category Analysis

- Product counts by main category
- Category-level summary statistics
- Top 10 products ranked by rating count
- Word cloud and keyword-frequency analysis of product names

### Page 4 — Customer Review Insights

- Relationship between product ratings and rating counts
- Correlation coefficient and descriptive statistics
- Word cloud of frequently occurring customer-review keywords
- A table of the most frequent review keywords

This page focuses on keyword frequency, rather than a trained sentiment-classification model.

### Page 5 — Product Recommendation

- Select a product from the available catalogue.
- Generate the top five similar products.
- Review recommended products alongside their category, discounted price, and rating.

The five pages are intended to form one Streamlit multi-page application.

---

## 7. Product Recommendation System

The recommendation system converts product descriptions and selected attributes (e.g., wattage, connector type, fast-charging support, and color) into numerical vectors using TF-IDF, keyword extraction, and feature scaling. It calculates cosine similarity for both textual and numerical features, then combines them into a weighted score: 60% text similarity and 40% numerical similarity. A category adjustment factor of 1.2 is applied to products in the same main category, compared with 1.0 for products in different categories. The system then ranks products by their final similarity scores and returns the top 5 most similar products.

### Limitations of the recommendation system

- Recommendations depend on the quality of product names, descriptions, categories, and extracted attributes.
- Some product specifications may be missing or inconsistently described.
- The system does not use user purchase histories, user–item interactions, or collaborative filtering.
- The category adjustment is a manually defined heuristic and has not been established as optimal through offline evaluation or A/B testing.

---

### Skills demonstrated

- Data cleaning and preprocessing
- Exploratory data analysis (EDA)
- Descriptive statistics and correlation analysis
- Data visualization and dashboard development
- Text preprocessing and feature extraction
- Content-based recommendation systems
- Python application development and deployment preparation

---

## 8. Assumptions & Limitations

- The dataset represents a limited collection of product listings, not the entire Amazon catalogue.
- The available fields do not provide verified transaction-level sales, revenue, profit, conversion, or customer acquisition data.
- `rating_count` is used as a proxy for product popularity, not as a direct measure of sales.
- Rating values and missing rating counts are handled using explicit preprocessing assumptions; these choices can influence the results.
- Review keyword frequency does not independently identify sentiment, intent, or customer satisfaction.
- Correlation measures linear association and does not establish causation.
- The recommendation engine relies on product content and selected attributes, without user-level behavioral data.
- Results may change with different filters, data-cleaning choices, or dataset versions.

---

## Author

**Nguyen Minh Hieu**  
