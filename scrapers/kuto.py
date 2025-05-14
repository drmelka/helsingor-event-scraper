import datetime as dt, json, re, time, html, requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

URL_LIST = "https://kuto.dk/kalender/"
UA       = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

# ---- helpers ----
DATE_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})T(\d{2}:\d{2})")
today   = dt.date.today()

def iso_parts(iso):
    m = DATE_RE.match(iso or "")
    return (m.group(1), m.group(2)) if m else ("", "")

def clean(txt): return html.unescape(re.sub(r"\s+", " ", txt)).strip()

def ldjson_from(html_text):
    soup = BeautifulSoup(html_text, "html.parser")
    tag  = soup.find("script", type="application/ld+json")
    if not tag: return None
    data = json.loads(tag.string)
    if isinstance(data, list):
        data = next((d for d in data if d.get("@type") == "Event"), None)
    return data

# ---- main ----
def parse():
    with sync_playwright() as p:
        br = p.chromium.launch(headless=True)
        pg = br.new_page()
        pg.goto(URL_LIST, timeout=60000)
        pg.wait_for_selector("h5.ultp-block-title a")
        list_html = pg.content()

        links = BeautifulSoup(list_html, "html.parser").select("h5.ultp-block-title a")
        print(f"DEBUG: fandt {len(links)} links")

        for a in links:
            url  = a["href"]

            # 1) prøv lynhurtigt med requests + UA
            r = requests.get(url, headers=UA, timeout=30)
            data = ldjson_from(r.text)

            # 2) hvis JSON mangler ➜ Playwright-fallback
            if data is None:
                pg.goto(url, timeout=60000)
                data = ldjson_from(pg.content())

            if data is None:
                continue   # stadig intet – spring over

            sd, st = iso_parts(data.get("startDate", ""))
            if sd and dt.date.fromisoformat(sd) < today:
                continue   # gammel event

            ed, et = iso_parts(data.get("endDate", ""))

            yield {
                "Title":       data.get("name", "").strip(),
                "Start Date":  sd,
                "Start Time":  st,
                "End Date":    ed,
                "End Time":    et,
                "Location":    data.get("location", {}).get("name", ""),
                "Description": clean(data.get("description", "")),
                "Image":       data.get("image", ""),
                "Link":        url,
            }
            time.sleep(0.1)   # høflig pause

        br.close()
