from flask import Flask, render_template, request
import requests
from operator import itemgetter

import settings

app = Flask(__name__)

presidents = []
all_contracts = []

# the home page retrives always all necessary data from the DB to have lighter transitions later
@app.route('/')
def index():
    global all_contracts
    response = requests.get(settings.DB_URL+"/rest/v1/contratti?apikey="+settings.DB_KEY)
    if response.status_code == 200:
        result = response.json()
        all_contracts = [c for c in result]
    
    global presidents
    response = requests.get(settings.DB_URL+"/rest/v1/presidenti?apikey="+settings.DB_KEY)
    if response.status_code == 200:
            result = response.json()
            presidents = [(p["cognome"],p["nome"],p["cash"]) for p in result if p["attivo"] == True]
            presidents = sorted(presidents, key=itemgetter(1))
            return render_template("index.html", presidents=presidents)

    return "IFESIF"

# the pres page retrieves data from DB only if needed
@app.route('/pres')
def pres():
    surname = request.args.get("surname")
    name = request.args.get("name")

    global presidents
    if presidents == []:
        response = requests.get(settings.DB_URL+"/rest/v1/presidenti?apikey="+settings.DB_KEY)
        if response.status_code == 200:
            result = response.json()
            presidents = [(p["cognome"],p["nome"],p["cash"]) for p in result if p["attivo"] == True]
            presidents = sorted(presidents, key=itemgetter(1))

    global all_contracts
    if all_contracts == []:
        response = requests.get(settings.DB_URL+"/rest/v1/contratti?apikey="+settings.DB_KEY)
        if response.status_code == 200:
            result = response.json()
            all_contracts = [c for c in result]

    if all_contracts != [] and presidents != []:
        contracts = [c for c in all_contracts if c["cognome_presidente"] == surname and c["nome_presidente"] == name]
        contracts = sorted(contracts, key=itemgetter('ruolo'), reverse=True)

        budget = [p for p in presidents if p[0] == surname]
        budget = budget[0][2]

        return render_template("president.html", contracts=contracts, surname=surname, name=name, budget=budget, presidents=presidents)

    return "Presidente non disponibile"


if __name__ == "__main__":
    app.run()