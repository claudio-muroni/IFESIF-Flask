from flask import Flask, render_template, request
import requests
from operator import itemgetter

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
    response2 = requests.get(settings.DB_URL+"/rest/v1/presidenti?apikey="+settings.DB_KEY)
    if response.status_code == 200 and response2.status_code == 200:
        result = response.json()
        contracts = [c for c in result if c["cognome_presidente"] == pres]
        contracts = sorted(contracts, key=itemgetter('ruolo'), reverse=True)

        result2 = response2.json()
        budget = [p for p in result2 if p["cognome"] == pres]
        budget = budget[0]["cash"]

        return render_template("president.html", contracts=contracts, pres=pres, budget=budget)

    return "Presidente non disponibile"

if __name__ == "__main__":
    app.run()