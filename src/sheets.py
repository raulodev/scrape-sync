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
    CANCELLED = "Cancelled or Outdated"


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

    new_df = pd.DataFrame(new_values)

    new_df = new_df.assign(
        appointment_id=None,
        last_checked=datetime.now().strftime("%d/%m/%Y  %H:%M"),
        status=State.NEW.value,
    )

    worksheet = get_worksheet()

    current_values = worksheet.get_values("A:J")

    current_df = pd.DataFrame(
        current_values[1:],
        columns=current_values[0],
    )

    if current_df.empty:
        set_with_dataframe(worksheet, new_df)
        return

    if "status" not in current_df.columns:

        current_df = current_df.assign(
            status=State.NEW.value,
        )

    if new_values:

        # NOTE: avoid change appointment_id

        # Mofied the current data
        for index, current in current_df.iterrows():

            new_id = current.get("id")

            # locate into new data the current appointment
            new_info = new_df.loc[new_df["id"] == new_id]

            # If no new data is found then the current appointment is cancelled
            if new_info.empty and current.get("status") != State.CANCELLED.value:

                print("❌ Cita cancelada o fuera de fecha:", new_id)
                current_df.at[index, "last_checked"] = datetime.now().strftime(
                    "%d/%m/%Y  %H:%M"
                )
                current_df.at[index, "status"] = State.CANCELLED.value

            # If there is new info
            elif not new_info.empty:

                new_date = new_info.values[0][1]
                start_time = new_info.values[0][2]
                service = new_info.values[0][3]
                patient = new_info.values[0][4]
                therapist = new_info.values[0][5]
                phone = new_info.values[0][6]

                modified_columns = []

                if new_date != current.get("date"):
                    current_df.at[index, "date"] = new_date
                    modified_columns.append("date")
                    print(
                        "✏️ Fecha modificada:",
                        new_id,
                        current.get("date"),
                        "->",
                        new_date,
                    )

                if current.get("start_time") not in start_time:
                    current_df.at[index, "start_time"] = start_time
                    modified_columns.append("start_time")
                    print(
                        "✏️ Hora modificada:",
                        new_id,
                        current.get("start_time"),
                        "->",
                        start_time,
                    )

                if service != current.get("service"):
                    current_df.at[index, "service"] = service
                    modified_columns.append("service")
                    print(
                        "✏️ Servicio modificado:",
                        new_id,
                        current.get("service"),
                        "->",
                        service,
                    )

                if patient != current.get("patient"):
                    current_df.at[index, "patient"] = patient
                    modified_columns.append("patient")
                    print(
                        "✏️ Paciente modificado:",
                        new_id,
                        current.get("patient"),
                        "->",
                        patient,
                    )

                if therapist != current.get("therapist"):
                    current_df.at[index, "therapist"] = therapist
                    modified_columns.append("therapist")
                    print(
                        "✏️ Terapeuta modificada:",
                        new_id,
                        current.get("therapist"),
                        "->",
                        therapist,
                    )

                if current.get("phone") not in phone:
                    current_df.at[index, "phone"] = phone
                    modified_columns.append("phone")
                    print(
                        "✏️ Teléfono modificado:",
                        new_id,
                        current.get("phone"),
                        "->",
                        phone,
                    )

                new_status = f"{State.MODIFIED.value} - {modified_columns}"

                if modified_columns and current.get("status") != new_status:

                    current_df.at[index, "last_checked"] = datetime.now().strftime(
                        "%d/%m/%Y  %H:%M"
                    )
                    current_df.at[index, "status"] = new_status
                    print(f"✏️ Cita modificada: {new_id}")

        # Add new appointments
        for index, new in new_df.iterrows():

            new_id = new.get("id")

            current_info = current_df.loc[current_df["id"] == new_id]

            if current_info.empty:
                print("🆕 Nueva cita:", new_id)
                current_df = pd.concat(
                    [current_df, pd.DataFrame([new.to_dict()])], ignore_index=True
                )

    set_with_dataframe(worksheet, current_df)

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
