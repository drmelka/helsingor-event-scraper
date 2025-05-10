import gspread, os, json, pandas as pd
from gspread_dataframe import set_with_dataframe

def append_rows(rows):
    """Tilføj rækker til nederste linje af Google-arket."""
    if not rows:
        return

    # Hent service-konto-credentials fra GitHub secret
    creds = json.loads(os.environ["GSERVICE_KEY"])
    gc    = gspread.service_account_from_dict(creds)

    # Åbn arket via Sheet-ID (også fra GitHub secret)
    sh = gc.open_by_key(os.environ["SHEET_ID"]).worksheet("Sheet1")

    # Skriv rækkerne uden at overskrive eksisterende data
    set_with_dataframe(
        sh,
        pd.DataFrame(rows),
        include_column_header=False,
        row=sh.row_count + 1,
        resize=False,
    )

