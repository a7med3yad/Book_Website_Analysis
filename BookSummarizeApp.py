import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(layout="wide")
st.title("📚 Book Scraper from books.toscrape.com")

BASE_URL = 'http://books.toscrape.com/catalogue/page-{}.html'

@st.cache_data
def scrape_books():
    all_books = []
    for page_num in range(1, 51):
        url = BASE_URL.format(page_num)
        response = requests.get(url)
        if response.status_code != 200:
            continue
        soup = BeautifulSoup(response.text, 'html.parser')
        book_items = soup.find_all('article', class_='product_pod')
        for book in book_items:
            title = book.h3.a['title']
            price = book.find('p', class_='price_color').text
            availability = book.find('p', class_='instock availability').text.strip()
            rating_class = book.p['class'][1]
            rating = {'One':1, 'Two':2, 'Three':3, 'Four':4, 'Five':5}.get(rating_class, 0)
            all_books.append({
                'title': title,
                'price': float(re.sub(r'[^\d\.]', '', price)),
                'availability': availability,
                'rating': rating
            })
    return pd.DataFrame(all_books)

df = scrape_books()

# Sidebar options
st.sidebar.header("📋 Filters & Options")
show_data = st.sidebar.checkbox("Show Raw Data", value=True)
selected_chart = st.sidebar.selectbox("📈 Choose a Chart", [
    "Price Distribution", 
    "Rating Distribution", 
    "Boxplot (Price vs Rating)", 
    "Top 10 Expensive Books", 
    "Average Price per Rating",
    "Scatter Plot: Rating vs. Price"
])
price_range = st.sidebar.slider("💰 Filter by Price", float(df['price'].min()), float(df['price'].max()), (float(df['price'].min()), float(df['price'].max())))
rating_filter = st.sidebar.multiselect("⭐ Filter by Rating", options=sorted(df['rating'].unique()), default=sorted(df['rating'].unique()))

# Apply filters
filtered_df = df[(df['price'] >= price_range[0]) & (df['price'] <= price_range[1]) & (df['rating'].isin(rating_filter))]

if show_data:
    st.subheader("📄 Filtered Data Sample")
    st.dataframe(filtered_df.head(20))

# Chart display
st.subheader(f"📊 {selected_chart}")
fig, ax = plt.subplots()

if selected_chart == "Price Distribution":
    sns.histplot(filtered_df['price'], bins=30, kde=True, color='teal', ax=ax)
    ax.set_xlabel("Price (£)")
    ax.set_ylabel("Number of Books")

elif selected_chart == "Rating Distribution":
    sns.countplot(x='rating', data=filtered_df, palette='viridis', ax=ax)
    ax.set_xlabel("Rating (Stars)")
    ax.set_ylabel("Count")

elif selected_chart == "Boxplot (Price vs Rating)":
    sns.boxplot(x='rating', y='price', data=filtered_df, palette='Set2', ax=ax)
    ax.set_xlabel("Rating")
    ax.set_ylabel("Price (£)")

elif selected_chart == "Top 10 Expensive Books":
    top_10 = filtered_df.nlargest(10, 'price')
    sns.barplot(x='price', y='title', data=top_10, palette='rocket', ax=ax)
    ax.set_xlabel("Price (£)")
    ax.set_ylabel("Book Title")

elif selected_chart == "Average Price per Rating":
    avg_price = filtered_df.groupby('rating')['price'].mean()
    avg_price.plot(kind='bar', color=sns.color_palette('crest', len(avg_price)), ax=ax)
    ax.set_xlabel("Rating")
    ax.set_ylabel("Average Price (£)")

elif selected_chart == "Scatter Plot: Rating vs. Price":
    sns.scatterplot(x='rating', y='price', data=filtered_df, ax=ax)
    ax.set_xlabel("Rating (Stars)")
    ax.set_ylabel("Price (£)")

st.pyplot(fig)

# Health-related books section
st.subheader("📚 Books with 'Health' in the Title")
health_books = [title for title in filtered_df['title'] if re.search(r'health', title, re.IGNORECASE)]
if health_books:
    for title in health_books:
        st.write("- ", title)
else:
    st.write("No books found with 'health' in the title.")

# Correlation
correlation = filtered_df['rating'].corr(filtered_df['price'])
st.markdown(f"**Correlation between rating and price:** `{correlation:.2f}`")
