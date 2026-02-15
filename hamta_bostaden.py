import requests
from bs4 import BeautifulSoup
import json

url = "https://www.bostaden.umea.se/bostadssokande/lediga-lagenheter/"

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")

annonser = soup.find_all("div", class_="card-item")

bostader = []

for annons in annonser:
    adress = annons.find("span", class_="red-title-arrow")
    adress_text = adress.text.strip() if adress else ""

    omrade = annons.find("h3")
    omrade_text = omrade.text.replace("Område:", "").strip() if omrade else ""

    info = annons.find_all("p")

    typ = info[0].text.replace("Typ:", "").strip() if len(info) > 0 else ""
    yta = info[1].text.replace("Yta:", "").strip() if len(info) > 1 else ""
    hyra = info[2].text.replace("Hyra kr/mån:", "").strip() if len(info) > 2 else ""

    lank = annons.find("a", class_="btn")
    lank_url = lank["href"] if lank else ""

    bostader.append({
        "adress": adress_text,
        "omrade": omrade_text,
        "typ": typ,
        "yta": yta,
        "hyra": hyra,
        "lank": lank_url
    })

# Skapa data-mappen om den inte finns
import os
os.makedirs("data", exist_ok=True)

# Spara till JSON
with open("data/bostaden.json", "w", encoding="utf-8") as f:
    json.dump(bostader, f, ensure_ascii=False, indent=4)

print("Sparade", len(bostader), "lägenheter till data/bostaden.json")
