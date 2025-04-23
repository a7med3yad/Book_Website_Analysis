import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import re
from pymongo import MongoClient

# إعدادات شكل الرسوم
sns.set_style('whitegrid')
plt.rcParams['figure.figsize'] = (10, 5)

# الاتصال بـ MongoDB
@st.cache_data
def load_data():
    client = MongoClient("mongodb+srv://MohamedFathy:MohamedFathy5656@cluster0.lkyzclf.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
    db = client["web_scraping_db"]
    collection = db["scraped_data"]
    data = list(collection.find())
    df = pd.DataFrame(data)
    return df

# تحميل البيانات
df = load_data()

st.title("📚 Book Scraper Dashboard")
st.markdown("بيانات من [books.toscrape.com](http://books.toscrape.com)")

# عرض أول 5 صفوف
st.subheader("أول 5 كتب")
st.dataframe(df.head())

# رسم توزيع الأسعار
st.subheader("توزيع أسعار الكتب")
fig1, ax1 = plt.subplots()
sns.histplot(df['price'], bins=30, kde=True, color='teal', ax=ax1)
st.pyplot(fig1)

# رسم توزيع التقييمات
st.subheader("توزيع التقييمات")
fig2, ax2 = plt.subplots()
sns.countplot(x='rating', data=df, palette='viridis', ax=ax2)
ax2.set_xticklabels(['1★','2★','3★','4★','5★'])
st.pyplot(fig2)

# مقارنة السعر حسب التقييم
st.subheader("متوسط السعر حسب التقييم")
avg_price = df.groupby('rating')['price'].mean()
fig3, ax3 = plt.subplots()
avg_price.plot(kind='bar', color=sns.color_palette('crest', len(avg_price)), ax=ax3)
ax3.set_ylabel("متوسط السعر (£)")
st.pyplot(fig3)

# بحث عن كتب بكلمة معينة
st.subheader("بحث عن كتب تحتوي على كلمة:")
keyword = st.text_input("اكتب كلمة (مثلاً: health, travel, etc.)", "health")
matched_titles = [title for title in df['title'] if re.search(keyword, title, re.IGNORECASE)]

st.markdown(f"### عدد الكتب اللي فيها '{keyword}': {len(matched_titles)}")
for title in matched_titles:
    st.write(f"- {title}")
