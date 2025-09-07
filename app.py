from flask import Flask, render_template, request
import requests
import settings

app = Flask(__name__)

@app.route('/')
def index():
    response = requests.get(settings.DB_URL+"/rest/v1/presidenti?apikey="+settings.DB_KEY)
    if response.status_code == 200:
            result = response.json()
            presidents = [p["cognome"] for p in result if p["attivo"] == True]
            return render_template("index.html", presidents=presidents)

    return "IFESIF"

@app.route('/pres')
def pres():
    pres = request.args.get("name")

    response = requests.get(settings.DB_URL+"/rest/v1/contratti?apikey="+settings.DB_KEY)
    if response.status_code == 200:
        result = response.json()
        contracts = [c for c in result if c["cognome_presidente"] == pres]
        return render_template("president.html", contracts=contracts)

    return "Presidente"