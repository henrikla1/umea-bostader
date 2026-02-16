import requests
from bs4 import BeautifulSoup
import json
import os

session = requests.Session()

url = "https://minasidor.rikshem.se/ledigt/lagenhet?objectgroup=&selectedarea=AREAUMEA"

headers = {
    "User-Agent": "Mozilla/5.0"
}

bostader = []
unika_adresser = set()

# Hämta första sidan
response = session.get(url, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")

def hamta_objekt(soup):
    rows = soup.find_all("tr", class_=["listitem-odd", "listitem-even"])

    for row in rows:
        cells = row.find_all("td")
        if len(cells) < 8:
            continue

        link_tag = cells[1].find("a")
        if not link_tag:
            continue

        adress = link_tag.text.strip()

        if adress in unika_adresser:
            continue

        unika_adresser.add(adress)

        omrade = cells[0].text.strip()
        rum = cells[3].text.strip()
        storlek = cells[4].text.strip()
        hyra = cells[5].text.strip().replace("\xa0", " ")
        tilltrade = cells[6].text.strip()

        lank = "https://minasidor.rikshem.se/ledigt/" + link_tag["href"]

        bostader.append({
            "adress": adress,
            "omrade": omrade,
            "rum": rum,
            "storlek": storlek,
            "hyra": hyra,
            "tilltrade": tilltrade,
            "lank": lank
        })

# Hämta sida 1
print("Hämtar sida 1")
hamta_objekt(soup)

# Kolla hur många sidor som finns
page_info = soup.find("span", id="ctl00_ctl01_DefaultSiteContentPlaceHolder1_Col1_ucNavBar_lblNoOfPages")

total_pages = 1
if page_info and page_info.text.strip().isdigit():
    total_pages = int(page_info.text.strip())

print("Totalt antal sidor:", total_pages)

# Loopa genom resterande sidor (om fler än 1)
for page in range(2, total_pages + 1):
    print(f"Hämtar sida {page}")

    data = {
        "__VIEWSTATE": soup.find("input", {"id": "__VIEWSTATE"})["value"],
        "__VIEWSTATEGENERATOR": soup.find("input", {"id": "__VIEWSTATEGENERATOR"})["value"],
        "__EVENTVALIDATION": soup.find("input", {"id": "__EVENTVALIDATION"})["value"],
        "__EVENTTARGET": f"ctl00$ctl01$DefaultSiteContentPlaceHolder1$Col1$ucNavBar$rptButtons$ctl0{page-1}$btnPage",
        "__EVENTARGUMENT": ""
    }

    response = session.post(url, data=data, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    hamta_objekt(soup)

os.makedirs("data", exist_ok=True)

with open("data/rikshem.json", "w", encoding="utf-8") as f:
    json.dump(bostader, f, ensure_ascii=False, indent=4)

print("Sparade", len(bostader), "Rikshem-lägenheter")
