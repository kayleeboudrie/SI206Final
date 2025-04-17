import sqlite3
import requests
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
nltk.download('vader_lexicon')

def create_tables():
    conn = sqlite3.connect("/Users/kayleeboudrie/SI206Final/final_project.db")
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
    api_key = "607a3ee5-2c99-4a39-9da1-1b6aba16adf1"
    url = "https://api.newsapi.ai/api/v1/article/getArticles"

    headers = {'X-API-KEY': api_key}
    params = {
        "keyword": "Trump",
        "startDate": "2016-11-09",
        "endDate": "2017-03-01",
        "limit": 25
    }

    response = requests.get(url, headers=headers, params=params)
    articles = response.json().get("articles", [])
    
    sid = SentimentIntensityAnalyzer()

    conn = sqlite3.connect("/Users/kayleeboudrie/SI206Final/final_project.db")
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
