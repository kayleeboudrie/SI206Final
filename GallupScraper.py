import sqlite3
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pandas as pd
import matplotlib.pyplot as plt

def create_tables():
    conn = sqlite3.connect("/Users/kayleeboudrie/SI206Final/final_project.db")

    cur = conn.cursor()

    cur.execute('''
        CREATE TABLE IF NOT EXISTS GallupApproval (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT UNIQUE,
            president TEXT,
            approval_rating INTEGER
        )
    ''')
    conn.commit()
    conn.close()

def scrape_gallup(limit=1000):
    url = "https://news.gallup.com/poll/116677/presidential-approval-ratings-gallup-historical-statistics-trends.aspx"
    base_url = "https://news.gallup.com"

    output_dir = "gallup_csvs"
    os.makedirs(output_dir, exist_ok=True)
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "lxml")
    csv_links = soup.find_all("a", string="Get the data")
    conn = sqlite3.connect("/Users/kayleeboudrie/SI206Final/final_project.db")

    cur = conn.cursor()
    inserted = 0

    for link in csv_links:
        href = link.get("href", "")
        if "trump" in href.lower():
            trump_csv_url = urljoin(base_url, href)
        print(f"Found Trump CSV: {trump_csv_url}")

        response = requests.get(trump_csv_url)
        with open("presapp_trump.csv", "wb") as f:
            f.write(response.content)
            break
        df = pd.read_csv("presapp_trump.csv")

        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df = df.dropna(subset=['Date', 'Approve'])
        df['Approve'] = pd.to_numeric(df['Approve'], errors='coerce')
        df['President'] = 'Trump'

        df_to_insert = df[['President', 'Date', 'Approve']].rename(columns={
        'President': 'president',
        'Date': 'date',
        'Approve': 'approve'
        })

        conn = sqlite3.connect("approval_ratings.db")
        cur = conn.cursor()

        cur.execute('''
        CREATE TABLE IF NOT EXISTS ApprovalRatings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        president TEXT,
        date TEXT,
        approve REAL
        )
        ''')

        df_to_insert.to_sql('ApprovalRatings', conn, if_exists='append', index=False)

        conn.commit()
        conn.close()