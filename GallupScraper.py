
import sqlite3
import requests
from bs4 import BeautifulSoup
from datetime import datetime

def create_tables():

    conn = sqlite3.connect("final_project.db")
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS GallupApproval")
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
    url = "https://www.presidency.ucsb.edu/statistics/data/donald-j-trump-public-approval"
    resp = requests.get(url)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")

    table = soup.find("table")
    if not table:
        raise RuntimeError("No <table> found on page")

    headers = [th.get_text(strip=True) for th in table.thead.find_all("th")]
    date_idx = headers.index("Start Date")
    appr_idx = headers.index("Approving")

    records = []
    for tr in table.tbody.find_all("tr")[:limit]:
        cols = [td.get_text(strip=True) for td in tr.find_all("td")]

        raw_date = cols[date_idx].strip()
        if not raw_date:
            continue

        try:
            dt = datetime.strptime(raw_date, "%m/%d/%Y")
        except ValueError:
            continue

        date_str = dt.strftime("%Y-%m-%d")

        try:
            appr = float(cols[appr_idx])
        except ValueError:
            continue

        records.append({
            "date": date_str,
            "President": "Trump",
            "approval_rating": appr
        })

    return records


def store_gallup_in_db(records, batch_size=25):
    conn = sqlite3.connect("final_project.db")
    cur  = conn.cursor()
    records = sorted(
        records,
        key=lambda d: d['date']
    )

    total = len(records)
    for i in range(0, total, batch_size):
        batch = records[i : i + batch_size]
        for rec in batch:
            cur.execute("""
                INSERT OR IGNORE INTO GallupApproval (date, president, approval_rating)
                VALUES (?, ?, ?)
            """, (
                rec['date'],
                rec['President'],
                rec['approval_rating']
            ))
        conn.commit()  

    conn.close()

def create_poll_changes_table():
    conn = sqlite3.connect("final_project.db")
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS PollChanges")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS PollChanges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            start_date TEXT NOT NULL,
            end_date   TEXT NOT NULL,
            change     REAL NOT NULL,
            UNIQUE(start_date, end_date)
        )
    """)
    conn.commit()
    conn.close()

def store_poll_changes():
   
    conn = sqlite3.connect("final_project.db")
    cur = conn.cursor()

    cur.execute("SELECT date, approval_rating FROM GallupApproval ORDER BY date")
    rows = cur.fetchall()

    changes = []
    for (start_date, start_rating), (end_date, end_rating) in zip(rows, rows[1:]):
        diff = end_rating - start_rating
        changes.append((start_date, end_date, diff))

    for start_date, end_date, diff in changes:
        cur.execute("""
            INSERT OR IGNORE INTO PollChanges (start_date, end_date, change)
            VALUES (?, ?, ?)
        """, (start_date, end_date, diff))

    conn.commit()
    conn.close()

if __name__ == "__main__":

    create_tables()
    records = scrape_gallup()
    store_gallup_in_db(records)
    print(f"Inserted {len(records)} to database")

    create_poll_changes_table()
    
    store_poll_changes()
    print("Poll changes written to the database.")