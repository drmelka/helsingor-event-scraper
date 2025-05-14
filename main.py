import scrapers.kuto as kuto
from sheets import append_rows

def run():
    rows = list(kuto.parse())
    print(f"Found {len(rows)} events")        # <- DEBUG
    append_rows(rows)
    print("Rows written to sheet")            # <- DEBUG

if __name__ == "__main__":
    run()
