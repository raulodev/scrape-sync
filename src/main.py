# pylint: disable=import-error
import typer

from extract_from_esteticals import extract_from_esteticals
from gohighlevel import (
    CALENDARS,
    THERAPISTS,
    add_cols,
    correct_spelling,
    create_appointment,
    create_contact,
    search_contact,
    update_appointments,
)
from sheets import (
    create_google_credential_file,
    get_worksheet,
    write_to_sheet,
    write_to_sheet_from_gohighlevel,
)

app = typer.Typer()


@app.command()
def authenticate():
    """Authenticate to Google Sheets"""
    create_google_credential_file()
    print("✅ Creado archivo token.json")


@app.command()
def extract():
    """Extract appointments from Estetical website"""
    create_google_credential_file()
    data = extract_from_esteticals()
    write_to_sheet(data)


@app.command()
def register():
    """Register appointments from google sheets to GoHighLevel"""
    create_google_credential_file()
    add_cols()

    worksheet = get_worksheet()

    appointments = worksheet.get_values("A:I")[1:]

    for appointment in appointments:

        date = appointment[1]
        start_time = appointment[2]
        service = appointment[3]
        patient = appointment[4].title()
        therapits = appointment[5]
        phone = appointment[6]
        appointment_id = appointment[7]
        calendar_id = CALENDARS.get(service)
        therapist_id = THERAPISTS.get(therapits)

        if appointment_id:
            print(f"✅ Cita ya creada: {appointment_id}")
            continue

        if not calendar_id:
            print(f"⚠️ No se encontró calendario para {service}")
            continue

        try:
            contact = search_contact(patient)
        except Exception as exc:
            print(f"⚠️ Error al buscar contacto para {patient}: {exc}")
            continue

        if not contact:
            print(f"✖️  No fue encontrado un contacto para {patient}")

            attempts = 0
            while not contact and attempts < 5:
                try:
                    contact = create_contact(patient, phone)
                    print(f"✅ Se creó el contacto {contact}")
                    break
                except Exception as exc:
                    print(f"⚠️ Error al crear contacto para {patient}: {exc}")
                attempts += 1

        try:

            new_appointment_id = create_appointment(
                contact, calendar_id, therapist_id, f"{date}-{start_time}", service
            )
            if new_appointment_id:
                appointment[7] = new_appointment_id
                print(f"✅ Se creó la cita: {new_appointment_id}")
        except Exception as exc:
            print(f"⚠️ Error al crear la cita: {exc}")

    write_to_sheet_from_gohighlevel(appointments)


@app.command()
def update_appointments_title():
    """Update title of sheet with appointments"""
    create_google_credential_file()

    worksheet = get_worksheet()

    values = worksheet.get_all_values("A:H")[1:]

    for row in values:

        appointment_id = row[7]

        if not appointment_id:
            continue

        date = row[1]
        start_time = row[2]
        service = row[3]
        patient = row[4].title()
        therapists = row[5]

        title = f"{correct_spelling(service)} - {patient} - {therapists}"

        is_updated = update_appointments(appointment_id, title, f"{date}-{start_time}")

        if is_updated:
            print(f"✅ Actualizado titulo para {appointment_id}")


if __name__ == "__main__":
    app()
