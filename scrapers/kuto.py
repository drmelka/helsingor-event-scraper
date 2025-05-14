import requests, datetime as dt, re
from bs4 import BeautifulSoup

# ---------- hjælpe-funktioner ----------
MONTHS_DK = {
    "januar": 1, "februar": 2, "marts": 3, "april": 4,
    "maj": 5, "juni": 6, "juli": 7, "august": 8,
    "september": 9, "oktober": 10, "november": 11, "december": 12
}

DATE_RE = re.compile(
    r"(\d{1,2})\.*\s*(?:–\s*\d{1,2}\.*\s*)?([a-zæøå]+)\s+(\d{4})",
    re.I
)

def parse_date(text: str):
    """
    Træk første dato ud af fx
    '9. – 21. maj 2025'  eller  '14. maj 2025'
    -> datetime.date
    """
    m = DATE_RE.search(text)
    if not m:
        return None
    day, month_txt, year = m.groups()
    month = MONTHS_DK.get(month_txt.lower())
    if not month:
        return None
    return dt.date(int(year), month, int(day))

# ---------- hoved-parser ----------
def parse():
    url  = "https://kuto.dk/kalender/"
    html = requests.get(url, timeout=30).text
    soup = BeautifulSoup(html, "html.parser")

    anchors = soup.select("a[href^='/arrangementer/']")
    print(f"DEBUG: fandt {len(anchors)} links")

    for idx, a in enumerate(anchors[:10]):           # viser kun de 10 første i log
        title = a.get_text(strip=True)
        next_txt = a.find_next(text=True)
        print(f"DEBUG[{idx}]: '{title}' / '{next_txt.strip() if next_txt else ''}'")

        date_text = next_txt.strip() if next_txt else ""
        start_date = parse_date(date_text)
        if not start_date or start_date < dt.date.today():
            continue

        yield {
            "Title": title,
            "Start Date": start_date.isoformat(),
            "Start Time": "",
            "End Date": "",
            "End Time": "",
            "Location": "Kulturværftet / Toldkammeret",
            "Description": "",
            "Link": "https://kuto.dk" + a["href"]
        }
