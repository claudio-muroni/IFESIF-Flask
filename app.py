from flask import Flask, render_template, request
import requests
from operator import itemgetter
import time

import settings

app = Flask(__name__)

@app.route('/')
def index():
    response = requests.get(settings.DB_URL+"/rest/v1/presidenti?apikey="+settings.DB_KEY)
    if response.status_code == 200:
            result = response.json()
            presidents = [(p["cognome"],p["nome"]) for p in result if p["attivo"] == True]
            return render_template("index.html", presidents=presidents)

    return "IFESIF"

@app.route('/pres')
def pres():
    surname = request.args.get("surname")
    name = request.args.get("name")

    response = requests.get(settings.DB_URL+"/rest/v1/contratti?apikey="+settings.DB_KEY)
    response2 = requests.get(settings.DB_URL+"/rest/v1/presidenti?apikey="+settings.DB_KEY)
    if response.status_code == 200 and response2.status_code == 200:
        result = response.json()
        contracts = [c for c in result if c["cognome_presidente"] == surname and c["nome_presidente"] == name]
        contracts = sorted(contracts, key=itemgetter('ruolo'), reverse=True)

        result2 = response2.json()
        budget = [p for p in result2 if p["cognome"] == surname]
        budget = budget[0]["cash"]

        return render_template("president.html", contracts=contracts, surname=surname, name=name, budget=budget)

    return "Presidente non disponibile"

# simple escamotage to avoid render downtime
@app.route('/keep_alive')
def ping():
    settings.keep_alive = True
    while settings.keep_alive:
        time.sleep(60*10)
        print("pong")
    return "keep_alive = False"

@app.route('/not_keep_alive')
def stop_ping():
    settings.keep_alive = False
    return "keep_alive = False"

if __name__ == "__main__":
    app.run()