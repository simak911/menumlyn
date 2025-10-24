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
        response = requests.get(url, timeout=5)
        data = response.json()
        return data["day_of_week"]
    except:
        timezone = "Europe/Prague"
        tz = pytz.timezone(timezone)
        now = datetime.now(tz)
        return now.isoweekday()

def extract_price(text):
    if not text:
        return 0
    part = text.split(',-')[0]  
    digits = ''
    for ch in reversed(part.strip()):
        if ch.isdigit():
            digits = ch + digits
        elif digits:
            break
    return int(digits) if digits else 0


def get_info(item):
    name_elem = item.find(class_="mkdf-ml-title")
    name = name_elem.find(recursive=False).get_text(strip=True)
    price_elem = item.find(class_="mkdf-ml-price")
    price = 0
    if price_elem is not None:
        price = extract_price(price_elem.get_text(strip=True))
    label_elem = item.find(class_="mkdf-ml-label")
    label = ""
    if label_elem is not None:
        label = label_elem.get_text(strip=True)
    return name, price, label

def get_daymenu(elem):
    items = elem.find_all(recursive=False)
    info = []
    for item in items:
        name, price, label = get_info(item)
        info.append([name, label, price])
    return info

def znic_polivku(info):
    nove_info = []
    for item in info:
        if item[2] > 100:
            nove_info.append(item)
    return nove_info

def pridej_piti(info):
    info.append(["Karafa vody", "", 30])
    info.append(["Malá kofola", "", 35])
    return info

def preved(data):
    b = "&nbsp;"*50
    html = ['<table border="1" cellspacing="0" cellpadding="4">']
    html.append('<tr><th>Název</th><th>Příloha</th><th>Cena</th><th>Zájem</th></tr>')
    for row in data:
        html.append('<tr>' + ''.join(f'<td>{cell}</td>' for cell in row) + f'<td>{b}</td>' + '</tr>')
    html.append('</table>')
    return '\n'.join(html)

app = Flask(__name__)
@app.route('/')
def get_main_page():
    url = "https://vemlyne.cz/denni-nabidka/"
    text = ""
    try:
        response = requests.get(url, timeout=8)
        response.raise_for_status()
    except:
        text = "Došlo k chybě."
        return render_template ('index.html', data = "Error")
    string_html = response.text
    s = BeautifulSoup(string_html, "html.parser")
    elems = s.find_all(class_="mkdf-ml-holder")
    wd = get_weekday()
    elem = elems[wd-1]
    info = get_daymenu(elem)
    info = znic_polivku(info)
    info = pridej_piti(info)
    tabulka = preved(info)
    return render_template('index.html', data = tabulka)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)

#if __name__ == "__main__":
#    serve(app, host="0.0.0.0", port=8000)