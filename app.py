from flask import Flask, render_template, request
import requests
from waitress import serve
from bs4 import BeautifulSoup
from datetime import datetime
import os

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


def get_daymenu(elems):
    info = []
    for jidlo in elems:
        nazev_elem = jidlo.find(class_="col pr-0 flex-grow-1 day-menu-food-title")
        nazev = nazev_elem.get_text(strip=True)
        cena_elem = jidlo.find(class_= "col flex-grow-0 text-right day-menu-food-price text-nowrap")
        cena_text = cena_elem.get_text(strip=True)
        cena = extract_price(cena_text)
        info.append([nazev,cena])
    return info

def znic_polivku(info):
    nove_info = []
    for item in info:
        if item[1] > 100:
            nove_info.append(item)
    return nove_info

def pridej_piti(info):
    info.append(["Karafa vody", 30])
    info.append(["Malá kofola", 35])
    info.append(["Malé pomelo grep", 39])
    return info

def preved(data):
    html = ['<table border="1" cellspacing="0" cellpadding="4">']
    html.append('<tr><th>Název</th><th>Cena</th><th id="zajem">Zájem</th></tr>')
    for row in data:
        html.append('<tr>' + ''.join(f'<td>{cell}</td>' for cell in row) + f'<td></td>' + '</tr>')
    html.append('</table>')
    return '\n'.join(html)

app = Flask(__name__)
@app.route('/')
def get_main_page():
    url = "https://www.vemlyne.cz/pages/day-menu/"
    try:
        response = requests.get(url, timeout=8)
        response.raise_for_status()
    except:
        text = "Došlo k chybě."
        return render_template ('index.html', data = "Error")
    string_html = response.text

    s = BeautifulSoup(string_html, "html.parser")
    elems = s.find_all(class_="row day-menu-food pb-3")
    get_daymenu(elems)
    info = get_daymenu(elems)
    info = znic_polivku(info)
    info = pridej_piti(info)
    tabulka = preved(info)
    return render_template('index.html', data = tabulka)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    serve(app, host="0.0.0.0", port=port)