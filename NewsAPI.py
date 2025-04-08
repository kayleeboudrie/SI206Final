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

import sqlite3
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def join_and_analyze():
    conn = sqlite3.connect("data/approval_data.db")

    df_approval = pd.read_sql("SELECT * FROM ApprovalRatings", conn)
    df_news = pd.read_sql("SELECT * FROM NewsSentiment", conn)

    df_approval['date'] = pd.to_datetime(df_approval['date'])
    df_news['published_date'] = pd.to_datetime(df_news['published_date'])

    # Round dates to the week or align them
    df_approval['day'] = df_approval['date'].dt.date
    df_news['day'] = df_news['published_date'].dt.date

    # Group by day and average
    df_news_grouped = df_news.groupby('day')['sentiment_score'].mean().reset_index()
    df_approval_grouped = df_approval.groupby('day')['approval'].mean().reset_index()

    merged = pd.merge(df_news_grouped, df_approval_grouped, on='day')
    merged.to_csv("data/sentiment_output.txt", index=False)

    return merged

def create_visualizations(df):
    sns.lineplot(x='day', y='sentiment_score', data=df, label="News Sentiment")
    sns.lineplot(x='day', y='approval', data=df, label="Approval Rating")
    plt.xticks(rotation=45)
    plt.title("Trump: Sentiment vs Approval Over Time")
    plt.tight_layout()
    plt.savefig("data/comparison_plot.png")
    plt.show()

if __name__ == "__main__":
    df = join_and_analyze()
    create_visualizations(df)
