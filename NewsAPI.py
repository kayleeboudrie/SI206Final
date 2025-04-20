import sqlite3
import requests
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
nltk.download('vader_lexicon')
API_KEY = "607a3ee5-2c99-4a39-9da1-1b6aba16adf1"

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

def get_avg_sentiment_for_date(date_obj):
    date_str = date_obj.strftime('%Y-%m-%d')
    url = "https://eventregistry.org/api/v1/article/getArticles"
    params = {
        "action": "getArticles",
        "keyword": "Trump",
        "dateStart": date_str,
        "dateEnd": date_str,
        "lang": "eng",
        "articlesPage": 1,
        "articlesCount": 100,
        "apiKey": API_KEY
    }

    response = requests.get(url, params=params)
    articles = response.json().get("articles", {}).get("results", [])
    
    if not articles:
        return None

    scores = []
    for article in articles:
        content = article.get("title", "") + " " + article.get("body", "")
        if content.strip():
            sentiment = sid.polarity_scores(content)
            scores.append(sentiment['compound'])

    return sum(scores) / len(scores) if scores else None

if __name__ == "__main__":
    create_tables()
    
