import scrapers.kuto as kuto
from sheets import append_rows

def run():
    rows = list(kuto.parse())
    print(f"Found {len(rows)} events")
    append_rows(rows)
    print("Rows written to sheet")

if __name__ == "__main__":
    run()
