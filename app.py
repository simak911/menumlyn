from flask import Flask, render_template, request
import requests
from waitress import serve
from bs4 import BeautifulSoup
from datetime import datetime
import pytz

def get_weekday():
    try:
        timezone = "Europe/Prague"
        url = f"https://worldtimeapi.org/api/timezone/{timezone}"
        response = requests.get(url)
        data = response.json()
        return data["day_of_week"]
    except:
        timezone = "Europe/Prague"
        tz = pytz.timezone(timezone)
        now = datetime.now(tz)
        return now.isoweekday()

app = Flask(__name__)
@app.route('/')
def get_main_page():
    url = "https://vemlyne.cz/denni-nabidka/"
    text = ""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except:
        text = "Došlo k chybě."
        return render_template ('index.html', chyba="chyba")
    string_html = response.text
    s = BeautifulSoup(string_html, "html.parser")
    wd = get_weekday()
    return render_template('index.html', chyba=f"{wd}")

if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=8000)