import datetime as dt, json, re, time, requests, html
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

URL_LIST = "https://kuto.dk/kalender/"

# ---------- helpers ----------
def iso_to_parts(iso: str):
    """2025-05-16T19:00:00+02:00  ->  ('2025-05-16', '19:00')"""
    if not iso:
        return ("", "")
    date_part, time_part = iso.split("T")
    return (date_part, time_part[:5])        # HH:MM

def clean(txt: str) -> str:
    return html.unescape(re.sub(r"\s+", " ", txt)).strip()

# ---------- main ----------
def parse():
    # 1) hent listen én gang med Playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(URL_LIST, timeout=60000)
        page.wait_for_selector("h5.ultp-block-title a")
        html_list = page.content()
        browser.close()

    soup = BeautifulSoup(html_list, "html.parser")
    links = soup.select("h5.ultp-block-title a")
    print(f"DEBUG: fandt {len(links)} links")

    today = dt.date.today()

    for a in links:
        url = a["href"]
        ev_html = requests.get(url, timeout=30).text
        ev = BeautifulSoup(ev_html, "html.parser")

        # 2) hent ld+json script-blokken
        json_tag = ev.find("script", type="application/ld+json")
        if not json_tag:
            continue
        try:
            data = json.loads(json_tag.string)
            # Hvis siden indeholder List & Event, find den med "@type": "Event"
            if isinstance(data, list):
                data = next(d for d in data if d.get("@type") == "Event")
        except Exception:
            continue

        # 3) træk felter ud
        start_date, start_time = iso_to_parts(data.get("startDate", ""))
        end_date,   end_time   = iso_to_parts(data.get("endDate",   ""))

        # spring gamle events over
        if start_date and dt.date.fromisoformat(start_date) < today:
            continue

        yield {
            "Title":        data.get("name", a.get_text(strip=True)),
            "Start Date":   start_date,
            "Start Time":   start_time,
            "End Date":     end_date,
            "End Time":     end_time,
            "Location":     data.get("location", {}).get("name", ""),
            "Description":  clean(data.get("description", "")),
            "Image":        data.get("image", ""),        # NY kolonne
            "Link":         url,
        }
        time.sleep(0.2)     # høflig pause
