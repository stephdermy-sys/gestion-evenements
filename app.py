from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)

# Création base de données si elle n'existe pas
def init_db():
    conn = sqlite3.connect("evenements.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS evenements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT,
            prenom TEXT,
            nom_evenement TEXT,
            service TEXT,
            date_demande TEXT,
            date_souhaitee TEXT,
            type_lieu TEXT,
            invites TEXT,
            participants INTEGER,
            centre_cout TEXT,
            budget REAL,
            statut TEXT DEFAULT 'A traiter',
            assigne_a TEXT
        )
    """)

    conn.commit()
    conn.close()

init_db()

@app.route("/")
def formulaire():
    return render_template("formulaire.html")


@app.route("/submit", methods=["POST"])
def submit():
    conn = sqlite3.connect("evenements.db")
    cursor = conn.cursor()

    nom = request.form.get("nom")
    prenom = request.form.get("prenom")
    nom_evenement = request.form.get("nom_evenement")
    service = request.form.get("service")
    date_souhaitee = request.form.get("date_souhaitee")
    type_lieu = request.form.get("type_lieu")
    invites = request.form.get("invites")
    participants = request.form.get("participants")
    centre_cout = request.form.get("centre_cout")
    budget = request.form.get("budget")

    date_demande = datetime.now().strftime("%Y-%m-%d")

    cursor.execute("""
        INSERT INTO evenements (
            nom,
            prenom,
            nom_evenement,
            service,
            date_demande,
            date_souhaitee,
            type_lieu,
            invites,
            participants,
            centre_cout,
            budget
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        nom,
        prenom,
        nom_evenement,
        service,
        date_demande,
        date_souhaitee,
        type_lieu,
        invites,
        participants,
        centre_cout,
        budget
    ))

    conn.commit()
    conn.close()

    return render_template("confirmation.html")


@app.route("/liste")
def liste():
    conn = sqlite3.connect("evenements.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM evenements")
    evenements = cursor.fetchall()

    conn.close()

    return render_template("index.html", evenements=evenements)


@app.route("/statistiques")
def statistiques():
    conn = sqlite3.connect("evenements.db")
    cursor = conn.cursor()

    stats = {}

    cursor.execute("SELECT COUNT(*) FROM evenements")
    stats["total"] = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(budget) FROM evenements")
    total_budget = cursor.fetchone()[0]
    stats["budget_total"] = total_budget if total_budget else 0

    cursor.execute("SELECT service, COUNT(*) FROM evenements GROUP BY service")
    stats["par_service"] = cursor.fetchall()

    cursor.execute("SELECT statut, COUNT(*) FROM evenements GROUP BY statut")
    stats["par_statut"] = cursor.fetchall()

    cursor.execute("SELECT centre_cout, SUM(budget) FROM evenements GROUP BY centre_cout")
    stats["budget_centre"] = cursor.fetchall()

    conn.close()

    html = f"""
    <h1>Statistiques</h1>

    Nombre total d'événements : {stats['total']}<br>
    Budget total : {stats['budget_total']} €<br><br>

    <b>Nombre par service</b><br>
    """

    for s in stats["par_service"]:
        html += f"{s[0]} : {s[1]}<br>"

    html += "<br><b>Nombre par statut</b><br>"

    for s in stats["par_statut"]:
        html += f"{s[0]} : {s[1]}<br>"

    html += "<br><b>Budget par centre de coût</b><br>"

    for c in stats["budget_centre"]:
        html += f"{c[0]} : {c[1]} €<br>"

    return html


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)