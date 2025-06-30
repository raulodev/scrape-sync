# pylint: disable=import-error
from datetime import datetime, timedelta

import gspread
import pytz
import requests

from settings import GOHIGHLEVEL_TOKEN, SCOPES, SPREADSHEET_ID

CALENDARS = {
    "Osteopatia": "0LsiMmC6Qgu9YANgSC9t",
    "Osteopatia (cita pagada)": "0LsiMmC6Qgu9YANgSC9t",
    "Fisioterapia y rehabilitacion": "81q3TF7Z990qi0RQjwC5",
    "Fisioterapia y rehabilitacion (cita pagada)": "81q3TF7Z990qi0RQjwC5",
    "terapia emocional - quiromasaje relajante.": "OfI653Xo0PJR7B5Io6fh",
    "terapia emocional - quiromasaje relajante. (cita pagada)": "OfI653Xo0PJR7B5Io6fh",
    "Suelo pelvico": "D2O9n9zSTrFjZsmm2U5M",
    # Estos servicios no existem en las citas extraidas
    "Ejercicios terapéuticos": "Pj5tSBOcAI9SCqDxBdm4",
    "Vértigo": "STaC7Z0nviRMzckclxk7",
    "Terapia Integral": "k1UMisxdlgNZNzcIYBZe",
}

THERAPISTS = {
    "Eva": "4WKfQtBE0JMTSW4xxWYI",
    "Ignacio": "r09hwVy9i62kzuGMHV2s",
    "Isidro Resa": "bbB8jnGwXt0DqYk3ip1F",
    "David Llamas": "bvjMSA8eS7K73CEAD6Hf",
    "Fadma Terapias": "v3fTGfmV9gGNYCvs9wDZ",
}

TIMEZONE = "Europe/Berlin"

DURATION_MINUTES = 55


def search_contact(name: str):

    url = "https://rest.gohighlevel.com/v1/contacts/"

    querystring = {"query": name}

    headers = {"authorization": f"Bearer {GOHIGHLEVEL_TOKEN}"}

    response = requests.get(url, headers=headers, params=querystring, timeout=10)

    data = response.json()

    contact = None
    for row in data.get("contacts", []):
        contact = row
        break

    return contact


def create_contact(name: str, phone: str):

    url = "https://rest.gohighlevel.com/v1/contacts/"

    headers = {"authorization": f"Bearer {GOHIGHLEVEL_TOKEN}"}

    phone = phone if phone.startswith("+") else f"+34{phone}"

    payload = {"name": name, "phone": phone}

    response = requests.post(url, headers=headers, json=payload, timeout=10)

    data = response.json()

    return data.get("contact", None)


def get_appointment(appointment_id: str):

    # Api reference: https://public-api.gohighlevel.com/#52afdbbd-8558-4c2d-bc0f-fc1f88c82503

    url = f"https://rest.gohighlevel.com/v1/appointments/{appointment_id}"

    headers = {"authorization": f"Bearer {GOHIGHLEVEL_TOKEN}"}

    response = requests.get(url, headers=headers, timeout=10)

    return response.json()


def create_appointment(
    contact: dict, calendar_id: str, therapist_id: str, start_time: str, service: str
):
    # Api reference: https://public-api.gohighlevel.com/#1e0867c3-69da-4240-9427-e1286b79472f

    url = "https://rest.gohighlevel.com/v1/appointments/"

    headers = {"authorization": f"Bearer {GOHIGHLEVEL_TOKEN}"}

    selected_slot = pytz.timezone("Europe/Berlin").localize(
        datetime.strptime(start_time, "%d/%m/%Y-%H:%M")
    )

    end_at = selected_slot + timedelta(minutes=DURATION_MINUTES)

    payload = {
        "phone": contact.get("phone"),
        "selectedSlot": selected_slot.isoformat(),
        "endAt": end_at.isoformat(),
        "selectedTimezone": TIMEZONE,
        "calendarId": calendar_id,
        "userId": therapist_id,
        "title": f"Cita automática – {service}",
    }

    response = requests.post(url, headers=headers, json=payload, timeout=10)

    if response.status_code != 200:
        print(f"❌ Error al crear cita: {response.text}")
        return None

    data = response.json()

    return data.get("id")


def update_appointments(appointment_id: str, title: str, start_time: str):

    # Api reference: https://public-api.gohighlevel.com/#7c257ce6-c73a-4cb3-957b-ddbd99dfbd86

    url = f"https://rest.gohighlevel.com/v1/appointments/{appointment_id}"

    headers = {"authorization": f"Bearer {GOHIGHLEVEL_TOKEN}"}

    selected_slot = pytz.timezone("Europe/Berlin").localize(
        datetime.strptime(start_time, "%d/%m/%Y-%H:%M")
    )

    payload = {
        "title": title,
        "selectedSlot": selected_slot.isoformat(),
        "selectedTimezone": TIMEZONE,
    }

    response = requests.put(url, headers=headers, json=payload, timeout=10)

    if response.status_code != 200:
        print(f"❌ Error al actualizar cita: {response.text}")
        return None

    data = response.json()

    return data.get("id")


def add_cols():

    gc = gspread.oauth(scopes=SCOPES, authorized_user_filename="token.json")

    sheet = gc.open_by_key(SPREADSHEET_ID)

    worksheet = sheet.get_worksheet(0)

    headers = worksheet.row_values(1)

    if "appointment_id" not in headers:

        worksheet.add_cols(1)
        worksheet.update_cell(1, len(headers) + 1, "appointment_id")
        headers.append("appointment_id")

    if "last_checked" not in headers:

        worksheet.add_cols(1)
        worksheet.update_cell(1, len(headers) + 1, "last_checked")


def correct_spelling(service: str):

    match service:

        case "Osteopatia":
            return "Osteopatía"

        case "Osteopatia (cita pagada)":
            return "Osteopatía (cita pagada)"

        case "Fisioterapia y rehabilitacion":
            return "Fisioterapia"

        case "Fisioterapia y rehabilitacion (cita pagada)":
            return "Fisioterapia (cita pagada)"

        case "terapia emocional - quiromasaje relajante.":
            return "Terapia emocional - quiromasaje relajante"

        case "terapia emocional - quiromasaje relajante. (cita pagada)":
            return "Terapia emocional - quiromasaje relajante (cita pagada)"

        case "Suelo pelvico":
            return "Suelo pélvico"

        case _:
            return service
