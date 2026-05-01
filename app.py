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

@app.route('/hof')
def hall_of_fame():

    response = requests.get(settings.DB_URL+"/rest/v1/classifiche?apikey="+settings.DB_KEY)
    if response.status_code == 200:
        result = response.json()
        
        winners_league = [c for c in result if c["posizione"] == 1 and c["competizione"] == "Campionato"]
        winners_cup = [c for c in result if c["posizione"] == 1 and c["competizione"] == "Coppa"]

        winners_league = sorted(winners_league, key=itemgetter('anno'), reverse=True)
        winners_cup = sorted(winners_cup, key=itemgetter('anno'), reverse=True)

        winners = []
        last_year = winners_league[0]["anno"]
        first_year = winners_league[-1]["anno"]
        for y in range(last_year, first_year-1, -1):
            rec = {}
            rec["n"] = y-first_year+1
            rec["Stagione"] = str(y-1) + "/" + str(y)
            rec["Campionato"] = next((w["nome_presidente"]+" "+w["cognome_presidente"][:1]+"." for w in winners_league if w["anno"] == y), "-")
            rec["Coppa"] = next((w["nome_presidente"]+" "+w["cognome_presidente"][:1]+"." for w in winners_cup if w["anno"] == y), "-")
            winners.append(rec)

        print(winners)

    return render_template("hof.html", winners=winners)

    return "Albo d'oro non disponibile"

if __name__ == "__main__":
    app.run()