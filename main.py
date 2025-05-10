from scrapers import kuto
from sheets import append_rows

def run():
    rows = list(kuto.parse())
    append_rows(rows)

if __name__ == "__main__":
    run()
