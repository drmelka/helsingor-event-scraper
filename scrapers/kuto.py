import requests, datetime as dt, re
from bs4 import BeautifulSoup

MONTHS_DK = {
    "januar": 1, "februar": 2, "marts": 3, "april": 4,
    "maj": 5, "juni": 6, "juli": 7, "august": 8,
    "september": 9, "oktober": 10, "november": 11, "december": 12
}

DATE_RE = re.compile(r"(\d{1,2})\.*\s*(?:–\s*\d{1,2}\.*\s*)?([a-zæøå]+)\s+(\d{4})", re.I)

def parse_date(text: str):
    """Træk første dato ud af tekst som '9. – 21. maj 2025' → datetime.date"""
    m = DATE_RE.search(text)
    if not m:
        return None
    day, month_txt, year = m.groups()
    month = MONTHS_DK[month_txt.lower()]
    return dt.date(int(year), month, int(day))

def parse():
    url  = "https://kuto.dk/kalender/"
    soup = BeautifulSoup(requests.get(url, timeout=30).text, "html.parser")

    for a in soup.select("a[href^='/arrangementer/']"):
        title = a.get_text(strip=True)
        link  = "https://kuto.dk" + a["href"]

        # Dato står lige efter linket i DOM-en
        date_text = a.find_next(string=True).strip()
        start_date = parse_date(date_text)
        if not start_date or start_date < dt.date.today():
            continue        # ingen dato eller allerede afholdt

        yield {
            "Title": title,
            "Start Date": start_date.isoformat(),
            "Start Time": "",
            "End Date": "",
            "End Time": "",
            "Location": "Kulturværftet / Toldkammeret",
            "Description": "",
            "Link": link
        }
