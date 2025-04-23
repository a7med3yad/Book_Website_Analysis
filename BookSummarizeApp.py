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

st.subheader("📄 Sample of Scraped Data")
st.dataframe(df.head(20))

st.subheader("📊 Distribution of Book Prices")
fig1, ax1 = plt.subplots()
sns.histplot(df['price'], bins=30, kde=True, color='teal', ax=ax1)
ax1.set_xlabel("Price (£)")
ax1.set_ylabel("Number of Books")
st.pyplot(fig1)

st.subheader("⭐ Rating Distribution")
fig2, ax2 = plt.subplots()
sns.countplot(x='rating', data=df, palette='viridis', ax=ax2)
ax2.set_xlabel("Rating (Stars)")
st.pyplot(fig2)

st.subheader("💸 Book Prices by Rating")
fig3, ax3 = plt.subplots()
sns.boxplot(x='rating', y='price', data=df, palette='Set2', ax=ax3)
ax3.set_xlabel("Rating")
ax3.set_ylabel("Price (£)")
st.pyplot(fig3)

st.subheader("💰 Top 10 Most Expensive Books")
top_10 = df.nlargest(10, 'price')
fig4, ax4 = plt.subplots()
sns.barplot(x='price', y='title', data=top_10, palette='rocket', ax=ax4)
st.pyplot(fig4)

st.subheader("📈 Average Price per Rating")
avg_price_per_rating = df.groupby('rating')['price'].mean()
fig5, ax5 = plt.subplots()
avg_price_per_rating.plot(kind='bar', color=sns.color_palette('crest', len(avg_price_per_rating)), ax=ax5)
ax5.set_xlabel("Rating")
ax5.set_ylabel("Average Price (£)")
st.pyplot(fig5)

st.subheader("📚 Books with 'Health' in the Title")
health_books = [title for title in df['title'] if re.search(r'health', title, re.IGNORECASE)]
if health_books:
    for title in health_books:
        st.write("- ", title)
else:
    st.write("No books found with 'health' in the title.")

correlation = df['rating'].corr(df['price'])
st.markdown(f"**Correlation between rating and price:** `{correlation:.2f}`")
