import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import seaborn as sns
import matplotlib.pyplot as plt
from pymongo import MongoClient

# Configure seaborn
sns.set_style('whitegrid')
plt.rcParams['figure.figsize'] = (10, 6)

# Web scraping setup
print("Starting to scrape book data...")

BASE_URL = 'http://books.toscrape.com/catalogue/page-{}.html'
books = []

# Scrape all 50 pages
for page in range(1, 51):
    url = BASE_URL.format(page)
    response = requests.get(url)
    
    if response.status_code != 200:
        print(f"Failed to load page {page}")
        continue
    
    soup = BeautifulSoup(response.text, 'html.parser')
    items = soup.find_all('article', class_='product_pod')
    
    for item in items:
        title = item.h3.a['title']
        price = item.find('p', class_='price_color').text
        availability = item.find('p', class_='instock availability').text.strip()
        rating_class = item.p['class'][1]
        rating = ['Zero', 'One', 'Two', 'Three', 'Four', 'Five'].index(rating_class) if rating_class in ['One', 'Two', 'Three', 'Four', 'Five'] else 0
        
        books.append({
            'title': title,
            'price': price,
            'availability': availability,
            'rating': rating
        })

print(f"Total books scraped: {len(books)}")

# DataFrame creation and cleaning
df = pd.DataFrame(books)
df['price'] = df['price'].apply(lambda x: float(re.sub(r'[^\d.]', '', x)))

# Save cleaned data
df.to_csv('books_cleaned.csv', index=False)
print("Data saved to books_cleaned.csv")

# Books with 'health' in the title
health_books = df[df['title'].str.contains('health', flags=re.IGNORECASE, regex=True)]
print("Books containing 'health' in the title:")
for title in health_books['title']:
    print(f"- {title}")

# Visualizations
# Price distribution
plt.figure()
sns.histplot(df['price'], bins=30, kde=True, color='teal')
plt.title('Distribution of Book Prices')
plt.xlabel('Price (£)')
plt.ylabel('Count')
plt.show()

# Rating distribution
plt.figure()
sns.countplot(x='rating', data=df, palette='viridis')
plt.title('Book Ratings Distribution')
plt.xlabel('Rating')
plt.ylabel('Count')
plt.xticks(ticks=[0,1,2,3,4], labels=['1★','2★','3★','4★','5★'])
plt.show()

# Price vs Rating boxplot
plt.figure()
sns.boxplot(x='rating', y='price', data=df, palette='Set2')
plt.title('Price by Book Rating')
plt.xlabel('Rating')
plt.ylabel('Price (£)')
plt.xticks(ticks=[0,1,2,3,4], labels=['1★','2★','3★','4★','5★'])
plt.show()

# Top 10 most expensive books
top_books = df.nlargest(10, 'price')
plt.figure()
sns.barplot(x='price', y='title', data=top_books, palette='rocket')
plt.title('Top 10 Most Expensive Books')
plt.xlabel('Price (£)')
plt.ylabel('Book Title')
plt.tight_layout()
plt.show()

# Average price per rating
avg_price = df.groupby('rating')['price'].mean()
print("Average price per rating:")
print(avg_price)

plt.figure()
avg_price.plot(kind='bar', color=sns.color_palette('crest', len(avg_price)))
plt.title('Average Price by Rating')
plt.xlabel('Rating')
plt.ylabel('Average Price (£)')
plt.show()

# Rating vs Price scatterplot
plt.figure()
sns.scatterplot(x='rating', y='price', data=df)
plt.title('Rating vs Price')
plt.xlabel('Rating')
plt.ylabel('Price (£)')
plt.show()

# MongoDB Integration
client = MongoClient("mongodb+srv://MohamedFathy:MohamedFathy5656@cluster0.lkyzclf.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["web_scraping_db"]
collection = db["scraped_data"]
collection.insert_many(df.to_dict('records'))
print("Data successfully inserted into MongoDB")

# Show some sample data from MongoDB
for item in collection.find().limit(5):
    print(item)
