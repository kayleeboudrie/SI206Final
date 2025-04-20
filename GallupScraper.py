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
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    tables = soup.find_all("table")

    conn = sqlite3.connect("/Users/kayleeboudrie/SI206Final/final_project.db")
    cur = conn.cursor()
    inserted = 0

    for table in tables:
        heading = table.find_previous("h3")
        president = heading.get_text(strip=True) if heading else "Unknown"

        if president != "Trump":
            continue

        rows = table.find_all("tr")
        for row in rows[1:]:
            cols = row.find_all("td")
            if len(cols) >= 2:
                date = cols[0].get_text(strip=True)
                approval = cols[1].get_text(strip=True).replace('%', '')
                try:
                    approval = int(approval)
                    cur.execute('''
                        INSERT OR IGNORE INTO GallupApproval (date, president, approval_rating)
                        VALUES (?, ?, ?)
                    ''', (date, president, approval))
                    if cur.rowcount > 0:
                        inserted += 1
                    if inserted >= limit:
                        break
                except ValueError:
                    continue

        if inserted >= limit:
            break


if __name__ == "__main__":
    create_tables()
    scrape_gallup()
