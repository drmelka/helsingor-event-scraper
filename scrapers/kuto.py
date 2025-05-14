import requests, datetime as dt, re
from bs4 import BeautifulSoup

def parse():
    url  = "https://kuto.dk/kalender/"
    html = requests.get(url, timeout=30).text
    soup = BeautifulSoup(html, "html.parser")

    # find A-tags der peger på en event-side
    for a in soup.select("a[href^='/arrangementer/']"):
        title = a.get_text(strip=True)
        link  = "https://kuto.dk" + a["href"]

        # Datoen står i den efterfølgende tekstnode, fx "Fredag 9. maj 2025"
        date_text = a.find_next(string=re.compile(r"\d{4}")).strip()
        try:
            date_obj = dt.datetime.strptime(date_text, "%d. %B %Y").date()
        except ValueError:
            continue  # spring hvis formatet ikke passer

        if date_obj < dt.date.today():
            continue  # kun fremtidige events

        yield {
            "Title": title,
            "Start Date": date_obj.isoformat(),
            "Start Time": "",
            "End Date": "",
            "End Time": "",
            "Location": "Kulturværftet / Toldkammeret",
            "Description": "",
            "Link": link
        }
