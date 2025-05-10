import requests, datetime as dt
from bs4 import BeautifulSoup

def parse():
    url = "https://kuto.dk/kalender/"
    soup = BeautifulSoup(requests.get(url, timeout=30).text, "html.parser")

    for card in soup.select("h5.entry-title > a"):
        title = card.get_text(strip=True)
        link  = card["href"]
        date  = card.find_next("p").get_text(strip=True)   # fx 7. august 2025
        try:
            date_parsed = dt.datetime.strptime(date, "%d. %B %Y").date()
        except ValueError:
            # format kunne ikke parses – spring over
            continue

        if date_parsed < dt.date.today():
            continue  # kun fremtidige events

        yield {
            "Title": title,
            "Start Date": date_parsed.isoformat(),
            "Start Time": "",
            "End Date": "",
            "End Time": "",
            "Location": "Kulturværftet (KUTO)",
            "Description": "",
            "Link": link
        }
