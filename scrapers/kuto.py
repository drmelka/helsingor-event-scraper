import datetime as dt, re, time, html, requests
from bs4 import BeautifulSoup, NavigableString
from playwright.sync_api import sync_playwright

URL_LIST = "https://kuto.dk/kalender/"

# ---------- helpers ----------
MONTHS = {"januar":1,"februar":2,"marts":3,"april":4,"maj":5,"juni":6,
          "juli":7,"august":8,"september":9,"oktober":10,"november":11,"december":12}
DATE_RE  = re.compile(r"(\d{1,2})\.*.*?([a-zæøå]+)\s+(\d{4})", re.I)
CLOCK_RE = re.compile(r"(\d{1,2})[:.](\d{2})")         # fx 19:30

def parse_date(text: str):
    m = DATE_RE.search(text)
    if not m:
        return None
    d, m_txt, y = m.groups()
    return dt.date(int(y), MONTHS[m_txt.lower()], int(d))

def first_time(text: str) -> str:
    m = CLOCK_RE.search(text)
    return f"{int(m.group(1)):02d}:{m.group(2)}" if m else ""

def clean(txt):
    return html.unescape(re.sub(r"\s+", " ", txt)).strip()

# ---------- main ----------
def parse():
    # (1) hent liste-siden m. Playwright
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

    for a in links:
        date_txt = a.find_parent("h5").find_next("div", class_="ultp-block-excerpt").get_text(" ", strip=True)
        start_date = parse_date(date_txt)
        if not start_date or start_date < dt.date.today():
            continue

        url = a["href"]
        ev_html = requests.get(url, timeout=30).text
        ev = BeautifulSoup(ev_html, "html.parser")

        # (2) tid & evt. slutdato i schedule-blokken
        sched = ev.select_one(".tribe-events-schedule, .event-schedule, .ultp-events-time")
        start_time = first_time(sched.get_text(" ", strip=True)) if sched else ""

        # (3) beskrivelse
        desc_block = ev.select_one(".tribe-events-single-event-description, .entry-content")
        description = clean(desc_block.get_text(" ", strip=True)) if desc_block else ""

        yield {
            "Title":       a.get_text(strip=True),
            "Start Date":  start_date.isoformat(),
            "Start Time":  start_time,
            "End Date":    "",     # Kuto viser sjældent sluttid – kan udfyldes senere
            "End Time":    "",
            "Location":    "Kulturværftet / Toldkammeret",
            "Description": description,
            "Link":        url,
        }
        time.sleep(0.2)   # høflig pause
