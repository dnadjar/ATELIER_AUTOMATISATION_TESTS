from flask import Flask, render_template_string
import sqlite3
import os

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, 'monitoring.db')

@app.get("/")
def dashboard():
    if not os.path.exists(DB_FILE):
        return "<h1>En attente des données...</h1><p>Le script de test n'a pas encore été exécuté.</p>"

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        c.execute("SELECT id, timestamp, status_code, response_time FROM tests ORDER BY timestamp DESC LIMIT 20")
        results = c.fetchall()
        
        c.execute("SELECT AVG(response_time) FROM tests")
        avg_time = c.fetchone()[0] or 0
        
        c.execute("SELECT COUNT(*) FROM tests WHERE status_code = 200")
        success_count = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM tests")
        total_count = c.fetchone()[0]
        uptime = (success_count / total_count * 100) if total_count > 0 else 0
    except sqlite3.OperationalError:
        results, avg_time, uptime = [], 0, 0
    finally:
        conn.close()

    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Dashboard QoS</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background-color: #f8f9fa; }
            .card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px; }
            table { width: 100%; border-collapse: collapse; margin-top: 15px; }
            th, td { padding: 10px; border: 1px solid #ddd; text-align: left; }
            th { background-color: #007BFF; color: white; }
            .ok { color: green; font-weight: bold; }
            .error { color: red; font-weight: bold; }
        </style>
    </head>
    <body>
        <h1>📊 Dashboard de Monitoring API</h1>
        <div class="card">
            <h2>Indicateurs QoS</h2>
            <p><strong>Temps de réponse moyen :</strong> {{ "%.3f"|format(avg_time) }} s</p>
            <p><strong>Taux de disponibilité (Uptime) :</strong> {{ "%.2f"|format(uptime) }} %</p>
        </div>
        <div class="card">
            <h2>Historique des tests</h2>
            <table>
                <tr><th>ID</th><th>Date</th><th>Code HTTP</th><th>Temps (s)</th></tr>
                {% for row in results %}
                <tr>
                    <td>{{ row[0] }}</td><td>{{ row[1] }}</td>
                    <td class="{% if row[2] == 200 %}ok{% else %}error{% endif %}">{{ row[2] }}</td>
                    <td>{{ "%.3f"|format(row[3]) }}</td>
                </tr>
                {% endfor %}
            </table>
        </div>
    </body>
    </html>
    """
    return render_template_string(html_template, results=results, avg_time=avg_time, uptime=uptime)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
