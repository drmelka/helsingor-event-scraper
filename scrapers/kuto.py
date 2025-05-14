import requests, datetime as dt

API = (
    "https://kuto.dk/wp-json/tribe/events/v1/events"
    "?per_page=100"                       # max 100 events pr. kald
    "&start_date={today}"                 # kun fremtidige
)

def parse():
    today = dt.date.today().isoformat()
    url   = API.format(today=today)

    data  = requests.get(url, timeout=30).json()
    print(f"DEBUG: modtog {len(data['events'])} events fra API")

    for ev in data["events"]:
        start = dt.datetime.fromisoformat(ev["start_date"]).date()
        if start < dt.date.today():
            continue

        yield {
            "Title": ev["title"],
            "Start Date": start.isoformat(),
            "Start Time": "",                 # kan evt. hentes fra ev["start_date_details"]["time"]
            "End Date": "",
            "End Time": "",
            "Location": ev["venue"]["venue"] or "KUTO",
            "Description": ev["description"] or "",
            "Link": ev["url"]
        }
