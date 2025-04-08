import sqlite3
import requests
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
nltk.download('vader_lexicon')

def create_tables():
    conn = sqlite3.connect("data/approval_data.db")
    cur = conn.cursor()

    cur.execute('''
        CREATE TABLE IF NOT EXISTS NewsSentiment (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            published_date TEXT,
            title TEXT,
            sentiment_score REAL
        )
    ''')
    conn.commit()
    conn.close()

def fetch_and_store_articles():
    api_key = "your_api_key_here"
    url = "https://api.newsapi.ai/api/v1/article/getArticles"

    # Modify this as needed — based on the API you're using
    headers = {'X-API-KEY': api_key}
    params = {
        "keyword": "Trump",
        "startDate": "2016-11-09",  # example
        "endDate": "2017-03-01",    # example
        "limit": 25
    }

    response = requests.get(url, headers=headers, params=params)
    articles = response.json().get("articles", [])
    
    sid = SentimentIntensityAnalyzer()

    conn = sqlite3.connect("data/approval_data.db")
    cur = conn.cursor()

    for article in articles:
        title = article.get("title", "")
        pub_date = article.get("publishedDate", "")[:10]
        sentiment = sid.polarity_scores(title)["compound"]
        cur.execute("INSERT INTO NewsSentiment (published_date, title, sentiment_score) VALUES (?, ?, ?)", (pub_date, title, sentiment))

    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_tables()
    fetch_and_store_articles()

#wojrouwrguowrngouwrbngouwrFUHWnfiponwrouVBNWOBVIWrbnvgiuwhGOInfvoidwnVOPIejqfoiuwhrbgvojnswpigWHO