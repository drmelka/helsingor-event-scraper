import gspread, os, json, pandas as pd
from gspread_dataframe import set_with_dataframe

def append_rows(rows):
    """Tilføj rækker til nederste linje af Google-arket."""
    if not rows:
        return

    # Credentials fra GitHub secret
    creds = json.loads(os.environ["GSERVICE_KEY"])
    gc    = gspread.service_account_from_dict(creds)

    # Åbn første fane i arket
    sh = gc.open_by_key(os.environ["SHEET_ID"]).worksheet("Sheet1")

    # Konverter til DataFrame og tilføj under sidste eksisterende række
    df = pd.DataFrame(rows)
    set_with_dataframe(
        sh, df,
        include_column_header=False,
        row=sh.row_count + 1,   # skriv efter sidste udfyldte række
        resize=False
    )
