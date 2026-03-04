import sqlite3
import time
import urllib.request
from datetime import datetime
import os

# On utilise un chemin absolu pour que la tâche planifiée de PythonAnywhere trouve bien la BDD
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, 'monitoring.db')

def init_db():
    """Crée la table de monitoring si elle n'existe pas."""
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
    """Test l'API et enregistre la performance en BDD."""
    url = "https://catfact.ninja/fact"
    start_time = time.time()
    status_code = 500
    
    try:
        response = urllib.request.urlopen(url, timeout=5)
        status_code = response.getcode()
    except Exception as e:
        print(f"Erreur: {e}")
    
    end_time = time.time()
    response_time = round(end_time - start_time, 4)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Sauvegarde en base de données
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
