from flask import Flask, render_template_string, redirect, url_for
import sqlite3
import os
import subprocess

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, 'monitoring.db')

@app.route("/run-test")
def trigger_test():
    """Cette route lance le script de test et redirige vers l'accueil"""
    # On utilise le chemin absolu que l'on sait fonctionnel
    script_path = "/home/damiennadjar/mysite/run_test.py"
    try:
        # On exécute le script en tâche de fond
        subprocess.run(["python3", script_path], check=True)
    except Exception as e:
        print(f"Erreur d'exécution: {e}")
    
    # Une fois le test terminé, on redirige l'utilisateur vers le Dashboard
    return redirect(url_for('dashboard'))

@app.get("/")
def dashboard():
    # Si la BDD n'existe pas, on initialise des valeurs vides
    if not os.path.exists(DB_FILE):
        results, avg_time, uptime = [], 0, 0
    else:
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
        <title>Dashboard QoS - API Monitoring</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background-color: #f4f4f9; }
            .card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); margin-bottom: 20px; }
            table { width: 100%; border-collapse: collapse; margin-top: 20px; }
            th, td { padding: 12px; border: 1px solid #ddd; text-align: left; }
            th { background-color: #007BFF; color: white; }
            .status-200 { color: green; font-weight: bold; }
            .status-error { color: red; font-weight: bold; }
            .btn { display: inline-block; padding: 12px 24px; background-color: #28a745; color: white; text-decoration: none; border-radius: 5px; font-weight: bold; margin-bottom: 20px; font-size: 16px; border: none; cursor: pointer; }
            .btn:hover { background-color: #218838; }
            .header-flex { display: flex; justify-content: space-between; align-items: center; }
        </style>
    </head>
    <body>
        <div class="header-flex">
            <h1>📊 Dashboard de Monitoring API</h1>
            <a href="{{ url_for('trigger_test') }}" class="btn">🚀 Lancer un test maintenant</a>
        </div>
        
        <div class="card">
            <h2>Indicateurs de Qualité de Service (QoS)</h2>
            <p><strong>Temps de réponse moyen :</strong> {{ "%.3f"|format(avg_time) }} secondes</p>
            <p><strong>Taux de disponibilité (Uptime) :</strong> {{ "%.2f"|format(uptime) }} %</p>
        </div>

        <div class="card">
            <h2>Derniers Tests Exécutés</h2>
            {% if results %}
            <table>
                <tr>
                    <th>ID</th>
                    <th>Date & Heure</th>
                    <th>Code HTTP</th>
                    <th>Temps de réponse</th>
                </tr>
                {% for row in results %}
                <tr>
                    <td>{{ row[0] }}</td>
                    <td>{{ row[1] }}</td>
                    <td class="{% if row[2] == 200 %}status-200{% else %}status-error{% endif %}">{{ row[2] }}</td>
                    <td>{{ "%.3f"|format(row[3]) }} s</td>
                </tr>
                {% endfor %}
            </table>
            {% else %}
            <p>Aucune donnée pour le moment. Cliquez sur le bouton pour lancer un test !</p>
            {% endif %}
        </div>
    </body>
    </html>
    """
    return render_template_string(html_template, results=results, avg_time=avg_time, uptime=uptime)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
