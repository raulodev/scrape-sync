# pylint: disable=import-error
import typer

from extract_from_esteticals import extract_from_esteticals
from gohighlevel import (
    CALENDARS,
    THERAPISTS,
    correct_spelling,
    create_appointment,
    create_contact,
    search_contact,
    update_appointments,
)
from sheets import (
    State,
    create_google_credential_file,
    get_worksheet,
    write_to_sheet_from_estetical,
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
    write_to_sheet_from_estetical(data)


@app.command()
def register():
    """
    Register appointments from google sheets to GoHighLevel

    - Only take rows without appointment_id

    """
    create_google_credential_file()

    worksheet = get_worksheet()

    appointments = worksheet.get_values("A:J")[1:]

    without_calendar = 0
    already_registered = 0
    new_registered = 0

    for appointment in appointments:

        id = appointment[0]
        date = appointment[1]
        start_time = appointment[2]
        service = appointment[3]
        patient = appointment[4].title()
        therapists = appointment[5]
        phone = appointment[6]
        appointment_id = appointment[7]
        status = appointment[9]
        calendar_id = CALENDARS.get(service)
        therapist_id = THERAPISTS.get(therapists)

        if appointment_id:
            # update status
            if status != State.CANCELLED.value:
                appointment[9] = State.UNCHANGED.value
            already_registered += 1
            continue

        if not calendar_id:
            print(f"⚠️ No se encontró calendario para {service}")
            without_calendar += 1
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

            title = f"{correct_spelling(service)} - {patient} - {therapists}"

            print(f"Creando cita: {id} ...")
            new_appointment_id = create_appointment(
                contact, calendar_id, therapist_id, f"{date}-{start_time}", title
            )

            if new_appointment_id:
                appointment[7] = new_appointment_id
                appointment[9] = State.UNCHANGED.value
                print(f"✅ Se creó la cita: {new_appointment_id}")
                new_registered += 1
        except Exception as exc:
            print(f"⚠️ Error al crear la cita {id}: {exc}")

    print(f"✅ Se registraron {new_registered} citas nuevas")
    print(f"✅ Se encontraron {already_registered} citas ya registradas")
    print(f"⚠️ Se encontraron {without_calendar} citas sin calendario en GoHighLevel")

    write_to_sheet_from_gohighlevel(appointments)


@app.command()
def update():
    """
    Update appointments in GoHighLevel

    - Only take rows with status == UNCHANGED

    """
    create_google_credential_file()

    worksheet = get_worksheet()

    appointments = worksheet.get_all_values("A:J")[1:]

    for appointment in appointments:

        appointment_id = appointment[7]
        status = appointment[9]

        if not appointment_id or State.MODIFIED.value not in status:
            continue

        date = appointment[1]
        start_time = appointment[2]
        service = appointment[3]
        patient: str = appointment[4].title()
        therapists = appointment[5]
        phone = appointment[6]
        calendar_id = CALENDARS.get(service)
        therapist_id = THERAPISTS.get(therapists)

        if not calendar_id:
            print(f"⚠️ No se encontró calendario para {service}")
            continue

        contact = None

        try:
            contact = search_contact(patient.lower())
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

        title = f"{correct_spelling(service)} - {patient} - {therapists}"

        new_id_or_is_updated = update_appointments(
            appointment_id,
            f"{date}-{start_time}",
            title,
            calendar_id,
            contact,
            therapist_id,
        )

        if new_id_or_is_updated:
            print(f"✅ Actualizada la cita: {new_id_or_is_updated}")
            appointment[7] = new_id_or_is_updated
            appointment[9] = State.UNCHANGED.value

    write_to_sheet_from_gohighlevel(appointments)


if __name__ == "__main__":
    app()
