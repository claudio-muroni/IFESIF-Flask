from flask import Flask, render_template, request
import requests
from operator import itemgetter

import settings

import groq
from groq import Groq



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

@app.route("/ioSoBraBOT", methods=["POST"])
def ioSoBraBOT():
    text = request.get_data(as_text=True)
    
    try:
        client = Groq(api_key=settings.GROK_KEY)

        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": settings.LLM_PROMPT
                },
                {
                    "role": "user",
                    "content": text
                }
            ],
            model="groq/compound",
        )
        return chat_completion.choices[0].message.content
    except groq.APIError as e:
        return "Riprovace, mesà che stavo a dormi'"


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

        return render_template("hof.html", winners=winners)

    return "Albo d'oro non disponibile"


@app.route('/history8p')
def history_8p():

    response = requests.get(settings.DB_URL+"/rest/v1/classifiche?apikey="+settings.DB_KEY)
    if response.status_code == 200:
        result = response.json()

        rankings_league = [c for c in result if c["competizione"] == "Campionato" and c["anno"] >= 2023]
        rankings_cup = [c for c in result if c["competizione"] == "Coppa" and c["anno"] >= 2023]

        rankings_league = sorted(rankings_league, key=itemgetter('posizione'))
        rankings_league = sorted(rankings_league, key=itemgetter('anno'), reverse=True)
        rankings_cup = sorted(rankings_cup, key=itemgetter('posizione'))
        rankings_cup = sorted(rankings_cup, key=itemgetter('anno'), reverse=True)

        rankings_tables = []
        last_year = rankings_league[0]["anno"]
        first_year = rankings_league[-1]["anno"]
        for y in range(last_year, first_year-1, -1):

            ranking_table = []
            for p in range(1,8+1):
                rec = {}
                rec["stagione"] = str(y-1)[2:4] + "/" + str(y)[2:4]
                rec["pos"] = p
                rec["points_league"] = str(next((rl["punti"] for rl in rankings_league if rl["anno"] == y and rl["posizione"] == p), "-")).replace("None", "-")
                rec["pres_league"] = next((rl["nome_presidente"]+" "+rl["cognome_presidente"][:1]+"."for rl in rankings_league if rl["anno"] == y and rl["posizione"] == p), "-")
                rec["points_cup"] = str(next((rl["punti"] for rl in rankings_cup if rl["anno"] == y and rl["posizione"] == p), "-")).replace("None", "-")
                rec["pres_cup"] = next((rl["nome_presidente"]+" "+rl["cognome_presidente"][:1]+"."for rl in rankings_cup if rl["anno"] == y and rl["posizione"] == p), "-")

                ranking_table.append(rec)

            rankings_tables.append(ranking_table)

        print(rankings_tables)
        return render_template("history8p.html", rankings_tables=rankings_tables)

    return "Storico 8p non disponibile"





if __name__ == "__main__":
    app.run()