import requests, datetime as dt, re
from bs4 import BeautifulSoup, NavigableString

# --- dansk månedstabeller ---
MONTHS = {
    "januar":1,"februar":2,"marts":3,"april":4,"maj":5,"juni":6,
    "juli":7,"august":8,"september":9,"oktober":10,"november":11,"december":12
}
DATE_PAT = re.compile(r"(\d{1,2})\.*\s*(?:–\s*\d{1,2}\.*\s*)?([a-zæøå]+)\s+(\d{4})", re.I)

def first_date(text):
    """Returner datetime.date eller None fra dato-streng"""
    m = DATE_PAT.search(text)
    if not m:
        return None
    d, m_txt, y = m.groups()
    month = MONTHS.get(m_txt.lower())
    return dt.date(int(y), month, int(d))

def parse():
    url  = "https://kuto.dk/kalender/"
    soup = BeautifulSoup(requests.get(url, timeout=30).text, "html.parser")

    links = soup.select("h5 > a[href]")
    print(f"DEBUG: {len(links)} <h5><a> fundet")

    for a in links:
        # Find første tekst-node efter <a> der ikke kun er whitespace
        nxt = a.next_sibling
        while nxt and (not isinstance(nxt, NavigableString) or not nxt.strip()):
            nxt = nxt.next_sibling

        date_txt = nxt.strip() if nxt else ""
        date_obj = first_date(date_txt)
        if not date_obj or date_obj < dt.date.today():
            continue

        yield {
            "Title": a.get_text(strip=True),
            "Start Date": date_obj.isoformat(),
            "Start Time": "",
            "End Date": "",
            "End Time": "",
            "Location": "Kulturværftet / Toldkammeret",
            "Description": "",
            "Link": "https://kuto.dk" + a["href"]
        }
