import sqlite3
import requests
from bs4 import BeautifulSoup

def create_tables():
    conn = sqlite3.connect("data/approval_data.db")
    cur = conn.cursor()

    cur.execute('''
        CREATE TABLE IF NOT EXISTS ApprovalRatings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            approval INTEGER
        )
    ''')
    conn.commit()
    conn.close()

def scrape_gallup():
    url = "https://news.gallup.com/poll/116677/presidential-approval-ratings-gallup-historical-statistics-trends.aspx"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # You’ll need to inspect the actual HTML table manually in the browser
    # Here’s placeholder code:
    table = soup.find("table")  # Update this with actual table selector
    rows = table.find_all("tr")

    conn = sqlite3.connect("data/approval_data.db")
    cur = conn.cursor()

    for row in rows[1:]:
        cols = row.find_all("td")
        if len(cols) >= 2:
            date = cols[0].text.strip()
            approval = cols[1].text.strip().replace('%', '')
            try:
                approval = int(approval)
                cur.execute("INSERT INTO ApprovalRatings (date, approval) VALUES (?, ?)", (date, approval))
            except:
                continue  # Skip bad rows

    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_tables()
    scrape_gallup()
