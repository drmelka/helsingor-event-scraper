import datetime as dt, re, time, html
import requests
from bs4 import BeautifulSoup, NavigableString
from playwright.sync_api import sync_playwright

URL_LIST = "https://kuto.dk/kalender/"

# ---------------- helpers ----------------
MONTHS = {"januar":1,"februar":2,"marts":3,"april":4,"maj":5,"juni":6,
          "juli":7,"august":8,"september":9,"oktober":10,"november":11,"december":12}
DATE_RE = re.compile(r"(\d{1,2})\.*.*?([a-zæøå]+)\s+(\d{4})", re.I)
TIME_RE = re.compile(r"(\d{1,2})[:.](\d{2})")

def parse_date(text: str):
    m = DATE_RE.search(text)
    if not m:
        return None
    d, m_txt, y = m.groups()
    return dt.date(int(y), MONTHS[m_txt.lower()], int(d))

def clean(txt):
    return html.unescape(re.sub(r"\s+", " ", txt)).strip()

# ---------------- main ----------------
def parse():
    # 1) hent forsiden med Playwright for at få alle links
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
        # dato-tekst ligger i næste div
        date_txt = a.find_parent("h5").find_next("div", class_="ultp-block-excerpt").get_text(" ", strip=True)
        start_date = parse_date(date_txt)
        if not start_date or start_date < dt.date.today():
            continue

        # 2) hent selve event-siden for detaljer
        url = a["href"]
        page_soup = BeautifulSoup(requests.get(url, timeout=30).text, "html.parser")

        # start / slut tid i <meta>
        st_meta = page_soup.find("meta", {"property": "event:start_time"})
        start_time = st_meta["content"][:5] if st_meta else ""

        en_meta = page_soup.find("meta", {"property": "event:end_time"})
        end_time = en_meta["content"][:5] if en_meta else ""

        en_d_meta = page_soup.find("meta", {"property": "event:end_date"})
        end_date = ""
        if en_d_meta:
            y,m,d = en_d_meta["content"].split("-")
            end_date = dt.date(int(y), int(m), int(d)).isoformat()

        # beskrivelse
        desc_block = page_soup.select_one(".tribe-events-single-event-description")
        description = clean(desc_block.get_text(" ", strip=True)) if desc_block else ""

        yield {
            "Title":       a.get_text(strip=True),
            "Start Date":  start_date.isoformat(),
            "Start Time":  start_time,
            "End Date":    end_date,
            "End Time":    end_time,
            "Location":    "Kulturværftet / Toldkammeret",
            "Description": description,
            "Link":        url,
        }
        time.sleep(0.3)   # høflig pause så vi ikke spammer webserveren
