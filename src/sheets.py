# pylint: disable=import-error
import os.path
from datetime import datetime

import gspread
import pandas as pd
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from gspread_dataframe import set_with_dataframe

from settings import SPREADSHEET_ID

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def create_google_credential_file():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w", encoding="utf-8") as token:
            token.write(creds.to_json())


def write_to_sheet(new_values: list):

    gc = gspread.oauth(scopes=SCOPES, authorized_user_filename="token.json")
    sheet = gc.open_by_key(SPREADSHEET_ID)
    worksheet = sheet.get_worksheet(0)

    sheet.update_title(f"Citas - {datetime.now().strftime('%d/%m/%Y')}")

    current_values = worksheet.get_values("A:F")

    df = pd.DataFrame(
        current_values[1:],
        columns=("id", "date", "service", "patient", "therapist", "phone"),
    )

    new_df = pd.DataFrame(new_values)

    df = pd.concat([df[~df["id"].isin(new_df["id"])], new_df], ignore_index=True)

    set_with_dataframe(worksheet, df)

    print("✅ Datos actualizados")
