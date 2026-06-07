from flask import Flask, render_template, request
import requests
from operator import itemgetter

import settings

import groq
from groq import Groq

import pandas as pd

app = Flask(__name__)

presidents = []
all_contracts = []
all_contracts_csv = ""
all_rankings = []
all_rankings_csv = ""

# the home page retrives always all necessary data from the DB to have lighter transitions later
@app.route('/')
def index():
    
    check_for_data(update_data=True)

    if presidents != []:
        return render_template("index.html", presidents=presidents)

    return "IFESIF"

@app.route("/ioSoBraBOT", methods=["POST"])
def ioSoBraBOT():
    text = request.get_data(as_text=True)
    
    try:
        client = Groq(api_key=settings.GROK_KEY)

        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": settings.LLM_PROMPT + "\nPosizionamenti in classifica:\n" + str(all_rankings_csv)+ "\n\nGiocatori sotto contratto:\n" + str(all_contracts_csv)},
                {"role": "user", "content": text}
            ],
            model="groq/compound-mini"
        )
        return chat_completion.choices[0].message.content
    
    #except groq.APIError as e:
    except Exception as e:
        print("Exception IoSoBraBot:" + str(e))
        print("Exception headers:", dict(e.response.headers))
        return "Ao con calma, famme riposa' un attimo"


# the pres page retrieves data from DB only if needed
@app.route('/pres')
def pres():
    surname = request.args.get("surname")
    name = request.args.get("name")

    check_for_data()

    if all_rankings != []:
        num_league = [r for r in all_rankings if r["posizione"] == 1 and r["competizione"] == "Campionato" and r["cognome_presidente"] == surname]
        num_cup = [r for r in all_rankings if r["posizione"] == 1 and r["competizione"] == "Coppa" and r["cognome_presidente"] == surname]

    if all_contracts != [] and presidents != []:
        contracts = [c for c in all_contracts if c["cognome_presidente"] == surname and c["nome_presidente"] == name]
        contracts = sorted(contracts, key=itemgetter('ruolo'), reverse=True)

        budget = [p for p in presidents if p[0] == surname]
        budget = budget[0][2]

        return render_template("president.html", contracts=contracts, surname=surname, name=name, budget=budget, presidents=presidents, num_league=num_league, num_cup=num_cup)

    return "Presidente non disponibile"

@app.route('/hof')
def hall_of_fame():

    check_for_data()

    if all_rankings != []:
        
        winners_league = [r for r in all_rankings if r["posizione"] == 1 and r["competizione"] == "Campionato"]
        winners_cup = [r for r in all_rankings if r["posizione"] == 1 and r["competizione"] == "Coppa"]

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

        return render_template("hof.html", presidents=presidents, winners=winners)

    return "Albo d'oro non disponibile"


@app.route('/history8p')
def history_8p():

    check_for_data()

    if all_rankings != []:

        rankings_league = [r for r in all_rankings if r["competizione"] == "Campionato" and r["anno"] >= 2023]
        rankings_cup = [r for r in all_rankings if r["competizione"] == "Coppa" and r["anno"] >= 2023]

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
                rec["pres_league"] = next((rl["nome_presidente"]+" "+rl["cognome_presidente"][:1]+"." for rl in rankings_league if rl["anno"] == y and rl["posizione"] == p), "-")
                rec["points_cup"] = str(next((rl["punti"] for rl in rankings_cup if rl["anno"] == y and rl["posizione"] == p), "-")).replace("None", "-")
                rec["pres_cup"] = next((rl["nome_presidente"]+" "+rl["cognome_presidente"][:1]+"." for rl in rankings_cup if rl["anno"] == y and rl["posizione"] == p), "-")

                ranking_table.append(rec)

            rankings_tables.append(ranking_table)

        return render_template("history8p.html", presidents=presidents, rankings_tables=rankings_tables)

    return "Storico 8p non disponibile"


def check_for_data(update_data=False):
    global presidents
    if presidents == [] or update_data == True:
        response = requests.get(settings.DB_URL+"/rest/v1/presidenti?apikey="+settings.DB_KEY)
        if response.status_code == 200:
            result = response.json()
            presidents = [(p["cognome"],p["nome"],p["cash"]) for p in result if p["attivo"] == True]
            presidents = sorted(presidents, key=itemgetter(1))

    global all_contracts
    global all_contracts_csv
    if all_contracts == [] or update_data == True:
        response = requests.get(settings.DB_URL+"/rest/v1/contratti?apikey="+settings.DB_KEY)
        if response.status_code == 200:
            result = response.json()
            all_contracts = [{k: v for k, v in c.items() if k not in ("id", "id_stagione", "id_presidente")} for c in result]
            all_contracts = sorted(all_contracts, key=itemgetter('ruolo'), reverse=True)
            all_contracts = sorted(all_contracts, key=itemgetter('cognome_presidente'))
            all_contracts_csv = pd.DataFrame(all_contracts).to_csv(index=False)

    global all_rankings
    global all_rankings_csv
    if all_rankings == [] or update_data == True:
        response = requests.get(settings.DB_URL+"/rest/v1/classifiche?apikey="+settings.DB_KEY)
        if response.status_code == 200:
            result = response.json()
            all_rankings = [{k: v for k, v in r.items() if k not in ("id", "id_stagione", "id_presidente")} for r in result]
            all_rankings = sorted(all_rankings, key=itemgetter('posizione'))
            all_rankings = sorted(all_rankings, key=itemgetter('competizione'))
            all_rankings = sorted(all_rankings, key=itemgetter('anno'), reverse=True)
            all_rankings_csv = pd.DataFrame(all_rankings).to_csv(index=False)


if __name__ == "__main__":
    app.run()