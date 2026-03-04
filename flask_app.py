from flask import Flask, render_template_string, redirect, url_for
import sqlite3
import os
import subprocess

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, 'monitoring.db')

@app.route("/run-test")
def trigger_test():
    script_path = "/home/damiennadjar/mysite/run_test.py"
    try:
        subprocess.run(["python3", script_path], check=True)
    except Exception as e:
        print(f"Erreur d'exécution: {e}")
    return redirect(url_for('dashboard'))

@app.get("/")
def dashboard():
    results, avg_time, min_time, max_time, uptime, total_count, last_status = [], 0, 0, 0, 0, 0, None
    
    if os.path.exists(DB_FILE):
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        try:
            c.execute("SELECT id, timestamp, status_code, response_time FROM tests ORDER BY timestamp DESC LIMIT 20")
            results = c.fetchall()
            
            c.execute("SELECT AVG(response_time), MIN(response_time), MAX(response_time), COUNT(*) FROM tests")
            metrics = c.fetchone()
            if metrics[3] > 0:
                avg_time = metrics[0] or 0
                min_time = metrics[1] or 0
                max_time = metrics[2] or 0
                total_count = metrics[3] or 0
                
                c.execute("SELECT COUNT(*) FROM tests WHERE status_code = 200")
                success_count = c.fetchone()[0]
                uptime = (success_count / total_count * 100)
                
                last_status = results[0][2] if results else None
                
        except sqlite3.OperationalError:
            pass 
        finally:
            conn.close()

    html_template = """
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <title>Dashboard QoS - API Monitoring</title>
        <style>
            :root {
                --primary: #0056b3;
                --success: #28a745;
                --danger: #dc3545;
                --dark: #343a40;
                --light: #f4f7f6;
                --card-bg: #ffffff;
            }
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 40px; background-color: var(--light); color: var(--dark); }
            .container { max-width: 1200px; margin: auto; }
            .header-flex { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
            h1 { margin: 0; font-size: 2.2em; color: var(--dark); }
            .api-badge { background: var(--primary); color: white; padding: 5px 15px; border-radius: 20px; font-size: 0.5em; vertical-align: middle; margin-left: 10px; }
            .btn { display: inline-flex; align-items: center; padding: 12px 24px; background-color: var(--primary); color: white; text-decoration: none; border-radius: 8px; font-weight: bold; font-size: 16px; transition: 0.3s; box-shadow: 0 4px 6px rgba(0, 86, 179, 0.2); }
            .btn:hover { background-color: #004494; transform: translateY(-2px); box-shadow: 0 6px 12px rgba(0, 86, 179, 0.3); }
            .global-status { margin-bottom: 30px; font-size: 1.2em; background: var(--card-bg); padding: 15px 25px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); display: inline-block; }
            .kpi-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
            .kpi-card { background: var(--card-bg); padding: 20px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); text-align: center; border-top: 4px solid #6c757d; transition: transform 0.2s; }
            .kpi-card:hover { transform: translateY(-5px); }
            .kpi-title { font-size: 0.85em; color: #6c757d; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px; }
            .kpi-value { font-size: 1.8em; font-weight: bold; color: var(--dark); }
            .table-card { background: var(--card-bg); padding: 25px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }
            .table-card h2, .section-title { margin-top: 0; border-bottom: 2px solid var(--light); padding-bottom: 15px; margin-bottom: 20px; color: var(--dark); }
            table { width: 100%; border-collapse: collapse; }
            th, td { padding: 15px; border-bottom: 1px solid #eee; text-align: left; }
            th { background-color: #f8f9fa; color: #495057; font-weight: 600; text-transform: uppercase; font-size: 0.85em; }
            tr:hover { background-color: #f9fdf9; }
            .status-badge { padding: 6px 12px; border-radius: 20px; font-size: 0.85em; font-weight: bold; display: inline-block; }
            .status-200 { background-color: rgba(40, 167, 69, 0.1); color: var(--success); }
            .status-error { background-color: rgba(220, 53, 69, 0.1); color: var(--danger); }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header-flex">
                <h1>📊 Monitoring Dashboard <span class="api-badge">ExchangeRate API</span></h1>
                <a href="{{ url_for('trigger_test') }}" class="btn">🚀 Lancer un Ping</a>
            </div>
            
            <div class="global-status">
                <strong>État du service :</strong> 
                {% if last_status == 200 %}
                    <span style="color: var(--success); font-weight: bold;">🟢 Opérationnel</span>
                {% elif last_status %}
                    <span style="color: var(--danger); font-weight: bold;">🔴 Incident réseau</span>
                {% else %}
                    <span style="color: #6c757d; font-weight: bold;">⚪ En attente de données...</span>
                {% endif %}
            </div>
            
            <h2 class="section-title">Indicateurs de Qualité de Service (QoS)</h2>
            
            <div class="kpi-grid">
                <div class="kpi-card" style="border-top-color: var(--success);">
                    <div class="kpi-title">Disponibilité (Uptime)</div>
                    <div class="kpi-value" style="color: var(--success);">{{ "%.2f"|format(uptime) }} %</div>
                </div>
                <div class="kpi-card" style="border-top-color: var(--primary);">
                    <div class="kpi-title">Temps Moyen</div>
                    <div class="kpi-value">{{ "%.3f"|format(avg_time) }} s</div>
                </div>
                <div class="kpi-card" style="border-top-color: #17a2b8;">
                    <div class="kpi-title">Temps Min</div>
                    <div class="kpi-value">{{ "%.3f"|format(min_time) }} s</div>
                </div>
                <div class="kpi-card" style="border-top-color: #fd7e14;">
                    <div class="kpi-title">Temps Max</div>
                    <div class="kpi-value">{{ "%.3f"|format(max_time) }} s</div>
                </div>
                <div class="kpi-card" style="border-top-color: #6c757d;">
                    <div class="kpi-title">Requêtes envoyées</div>
                    <div class="kpi-value">{{ total_count }}</div>
                </div>
            </div>

            <div class="table-card">
                <h2>Historique Récent (20 derniers tests)</h2>
                {% if results %}
                <table>
                    <thead>
                        <tr>
                            <th>ID Test</th>
                            <th>Date & Heure</th>
                            <th>Statut HTTP</th>
                            <th>Temps de réponse</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for row in results %}
                        <tr>
                            <td style="color: #6c757d; font-weight: bold;">#{{ row[0] }}</td>
                            <td>{{ row[1] }}</td>
                            <td>
                                <span class="status-badge {% if row[2] == 200 %}status-200{% else %}status-error{% endif %}">
                                    {% if row[2] == 200 %}✅{% else %}❌{% endif %} {{ row[2] }}
                                </span>
                            </td>
                            <td><strong>{{ "%.3f"|format(row[3]) }}</strong> secondes</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
                {% else %}
                <p style="text-align: center; color: #6c757d; padding: 20px;">Aucune donnée enregistrée. Cliquez sur le bouton "Lancer un Ping".</p>
                {% endif %}
            </div>
        </div>
    </body>
    </html>
    """
    return render_template_string(html_template, results=results, avg_time=avg_time, min_time=min_time, max_time=max_time, uptime=uptime, total_count=total_count, last_status=last_status)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
