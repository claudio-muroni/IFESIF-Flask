from flask import Flask, render_template
import requests

app = Flask(__name__)

ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZpbHhzbXZnYWhjZWVndmh6ZGVlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mzc4NDQyMzMsImV4cCI6MjA1MzQyMDIzM30.pfSVEKiUtrCDzfH844CER82ce13stzGjTVtCeCwaMhA"

@app.route('/')
def index():
    response = requests.get("https://filxsmvgahceegvhzdee.supabase.co/rest/v1/presidenti?apikey="+ANON_KEY)
    if response.status_code == 200:
            result = response.json()
            presidents = [p["cognome"] for p in result]
            return render_template("index.html", presidents=presidents)

    return "IFESIF"

@app.route('/pres')
def pres():
    return "Presidente"