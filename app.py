from flask import Flask
import requests

app = Flask(__name__)

ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZpbHhzbXZnYWhjZWVndmh6ZGVlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mzc4NDQyMzMsImV4cCI6MjA1MzQyMDIzM30.pfSVEKiUtrCDzfH844CER82ce13stzGjTVtCeCwaMhA"

@app.route('/')
def index():

    response = requests.get("https://filxsmvgahceegvhzdee.supabase.co/rest/v1/presidenti?apikey="+ANON_KEY)
    if response.status_code == 200:
            presidents = response.json()
            names = [p["nome"] for p in presidents]
            
            return names


    return "IFESIF"