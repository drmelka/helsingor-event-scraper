import datetime as dt, re
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

URL = "https://kuto.dk/kalender/"

# ---------- dato-helper ----------
MONTHS = {"januar":1,"februar":2,"marts":3,"april":4,"maj":5,"juni":6,
          "juli":7,"august":8,"september":9,"oktober":10,"november":11,"december":12}
DATE_RE = re.compile(r"(\d{1,2})\.*.*?([a-zæøå]+)\s+(\d{4})", re.I)

def parse_date(txt: str):
    m = DATE_RE.search(txt)
    if not m:
        return None
    d, month_txt, y = m.groups()
    return dt.date(int(y), MONTHS[month_txt.lower()], int(d))

# ---------- hoved-funktion ----------
def parse():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(URL, timeout=60000)
        page.wait_for_selector("h5.ultp-block-title a")      # venter til listen er fremme
        html = page.content()
        browser.close()

    soup = BeautifulSoup(html, "html.parser")
    links = soup.select("h5.ultp-block-title a")
    print(f"DEBUG: fandt {len(links)} links")

    for a in links:
        # datotekst ligger i den følgende div.med class 'ultp-block-excerpt'
        excerpt = a.find_parent("h5").find_next("div", class_="ultp-block-excerpt")
        if not excerpt:
            continue
        start = parse_date(excerpt.get_text(" ", strip=True))
        if not start or start < dt.date.today():
            continue

        yield {
            "Title": a.get_text(strip=True),
            "Start Date": start.isoformat(),
            "Start Time": "",
            "End Date": "",
            "End Time": "",
            "Location": "Kulturværftet / Toldkammeret",
            "Description": "",
            "Link": a["href"],
        }
