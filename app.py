from flask import Flask, render_template, request
import requests
from waitress import serve

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
        return render_template ('index.html', ukaz="chyba")
    html = response.text
    return render_template('index.html', ukaz=html)

if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=8000)