import sqlite3
import time
import urllib.request
from datetime import datetime
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, 'monitoring.db')

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS tests
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  timestamp TEXT,
                  status_code INTEGER,
                  response_time REAL)''')
    conn.commit()
    conn.close()

def test_api():
    # URL de l'API ExchangeRate qui est autorisée par PythonAnywhere
    url = "https://api.exchangerate-api.com/v4/latest/USD"
    
    # On ajoute un User-Agent pour simuler un vrai navigateur
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    
    start_time = time.time()
    status_code = 500
    
    try:
        response = urllib.request.urlopen(req, timeout=5)
        status_code = response.getcode()
    except Exception as e:
        print(f"Erreur: {e}")
    
    end_time = time.time()
    response_time = round(end_time - start_time, 4)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO tests (timestamp, status_code, response_time) VALUES (?, ?, ?)",
              (timestamp, status_code, response_time))
    conn.commit()
    conn.close()
    print(f"Test effectué ! Statut: {status_code}, Temps: {response_time}s")

if __name__ == "__main__":
    init_db()
    test_api()
