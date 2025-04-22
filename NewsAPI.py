import sqlite3
import requests
from eventregistry import *
import json
from datetime import datetime

API_KEY = "359d8fad-ce26-4cd4-8d56-dbbcb7dca803"
er = EventRegistry(apiKey=API_KEY)

def create_tables():
    conn = sqlite3.connect("final_project.db")
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS NewsSentiment")
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

def get_avg_sentiment_for_range(start_date, end_date):
    
    query = {
        "$query": {
            "$and": [
            {
                "conceptUri": "http://en.wikipedia.org/wiki/Donald_Trump"
            },
            {
                "sourceLocationUri": "http://en.wikipedia.org/wiki/United_States"
            },
            {
                "dateStart": start_date.strftime('%Y-%m-%d'),
                "dateEnd": end_date.strftime('%Y-%m-%d'),
                "lang": "eng"
            }
            ]
        }
        }
    
    sentiment_scores = []
    q = QueryArticlesIter.initWithComplexQuery(query)
    for article in q.execQuery(er, sortBy="socialScore", maxItems=100):  # Max items set to 100
        sentiment_score = article.get("sentiment", 0)  # Get the sentiment score, default to 0 if not available
        sentiment_scores.append(sentiment_score)

    if sentiment_scores:
        avg_sentiment = sum(sentiment_scores) / len(sentiment_scores)
    else:
        avg_sentiment = 0  # No articles found, default to 0

    return avg_sentiment
    
def get_sentiment_for_date_ranges(date_ranges):
    sentiment_data = []
    for start_date, end_date in date_ranges:
        avg_sentiment = get_avg_sentiment_for_range(start_date, end_date)
        sentiment_data.append({
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
            'avg_sentiment': avg_sentiment
        })
    return sentiment_data


def store_sentiment_in_db(sentiment_data, batch_size =25):
    conn = sqlite3.connect("final_project.db")
    cur = conn.cursor()
    
    total = len(sentiment_data)
    for i in range(0, total, batch_size):
        batch = sentiment_data[i : i + batch_size]
        for data in batch:
            cur.execute('''
                INSERT OR IGNORE INTO NewsSentiment (published_date, title, sentiment_score)
                VALUES (?, ?, ?)
            ''', (
                data['start_date'],
                f"Sentiment for {data['start_date']} to {data['end_date']}",
                data['avg_sentiment']
            ))
        conn.commit()
    
    conn.close()

if __name__ == "__main__":

    custom_date_ranges = [
        (datetime(2017, 1, 20), datetime(2017, 1, 30)),
        (datetime(2017, 1, 30), datetime(2017, 2, 6)),
    ]
    print(datetime(2017, 1, 20).strftime('%Y-%m-%d'))

    sentiment_data = get_sentiment_for_date_ranges(custom_date_ranges)


    store_sentiment_in_db(sentiment_data)
    
    for data in sentiment_data:
        print(f"Sentiment from {data['start_date']} to {data['end_date']}: {data['avg_sentiment']}")

    

    
