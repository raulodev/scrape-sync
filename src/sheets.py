# pylint: disable=import-error
import enum
import os
from datetime import datetime

import gspread
import pandas as pd
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from gspread_dataframe import set_with_dataframe

from settings import SCOPES, SPREADSHEET_ID


class State(str, enum.Enum):
    NEW = "New"
    MODIFIED = "Modified"
    CANCELLED = "Cancelled"


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


def get_worksheet():

    gc = gspread.oauth(scopes=SCOPES, authorized_user_filename="token.json")

    sheet = gc.open_by_key(SPREADSHEET_ID)

    sheet.update_title(f"Citas - {datetime.now().strftime('%d/%m/%Y')}")

    return sheet.get_worksheet(0)


def write_to_sheet_from_estetical(new_values: list):

    worksheet = get_worksheet()

    current_values = worksheet.get_values("A:G")

    df = pd.DataFrame(
        current_values[1:],
        columns=(
            "id",
            "date",
            "start_time",
            "service",
            "patient",
            "therapist",
            "phone",
        ),
    )

    new_df = pd.DataFrame(new_values)

    df = pd.concat([df[~df["id"].isin(new_df["id"])], new_df], ignore_index=True)

    set_with_dataframe(worksheet, df)

    print("✅ Datos actualizados")


def write_to_sheet_from_gohighlevel(new_values: list):

    worksheet = get_worksheet()

    current_values = worksheet.get_values("A:I")

    columns = (
        "id",
        "date",
        "start_time",
        "service",
        "patient",
        "therapist",
        "phone",
        "appointment_id",
        "last_checked",
    )

    old_df = pd.DataFrame(current_values[1:], columns=columns)

    new_df = pd.DataFrame(new_values, columns=columns)

    df = pd.concat(
        [old_df[~old_df["id"].isin(new_df["id"])], new_df], ignore_index=True
    )

    set_with_dataframe(worksheet, df)

    print("✅ Datos actualizados")
