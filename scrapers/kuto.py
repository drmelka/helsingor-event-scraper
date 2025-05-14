import asyncio, datetime as dt
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

URL = "https://kuto.dk/kalender/"

def parse():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(URL, timeout=60000)
        page.wait_for_selector("h5.entry-title > a")     # vent til events er rendret
        html = page.content()
        browser.close()

    soup = BeautifulSoup(html, "html.parser")

    for a in soup.select("h5.entry-title > a"):
        title = a.get_text(strip=True)
        date_txt = a.find_next("p").get_text(strip=True)  # fx "9. – 21. maj 2025"
        date = _parse_date(date_txt)
        if not date or date < dt.date.today():
            continue
        yield {
            "Title": title,
            "Start Date": date.isoformat(),
            "Start Time": "",
            "End Date": "",
            "End Time": "",
            "Location": "Kulturværftet / Toldkammeret",
            "Description": "",
            "Link": a["href"],
        }

# --- lille dato-helper
import re
MONTHS = {"januar":1,"februar":2,"marts":3,"april":4,"maj":5,"juni":6,
          "juli":7,"august":8,"september":9,"oktober":10,"november":11,"december":12}
DATE_RE = re.compile(r"(\d{1,2})\.*.*?([a-zæøå]+)\s+(\d{4})", re.I)
def _parse_date(text):
    m = DATE_RE.search(text)
    if not m:
        return None
    d,mn,y = m.groups()
    return dt.date(int(y), MONTHS[mn.lower()], int(d))
