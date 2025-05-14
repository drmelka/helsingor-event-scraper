import requests, datetime as dt, re
from bs4 import BeautifulSoup, NavigableString

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0 Safari/537.36"}

MONTHS = {"januar":1,"februar":2,"marts":3,"april":4,"maj":5,"juni":6,
          "juli":7,"august":8,"september":9,"oktober":10,
          "november":11,"december":12}

DATE_RE = re.compile(r"(\d{1,2})\.*\s*(?:–\s*\d{1,2}\.*\s*)?"
                     r"([a-zæøå]+)\s+(\d{4})", re.I)

def parse_date(txt):
    m = DATE_RE.search(txt)
    if not m:
        return None
    d, month_txt, y = m.groups()
    month = MONTHS.get(month_txt.lower())
    return dt.date(int(y), month, int(d))

def parse():
    url  = "https://kuto.dk/kalender/"
    html = requests.get(url, headers=UA, timeout=30).text
    soup = BeautifulSoup(html, "html.parser")

    links = soup.select("h5 > a[href^='/arrangementer/']")
    print(f"DEBUG: {len(links)} links fundet")

    for a in links:
        nxt = a.next_sibling
        while nxt and (not isinstance(nxt, NavigableString) or not nxt.strip()):
            nxt = nxt.next_sibling
        date_txt = nxt.strip() if nxt else ""
        start = parse_date(date_txt)
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
            "Link": "https://kuto.dk" + a["href"]
        }
