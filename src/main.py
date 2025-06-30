# pylint: disable=import-error
import typer

from extract_from_esteticals import extract_from_esteticals
from gohighlevel import register_appointment, update_appointments, correct_spelling
from sheets import create_google_credential_file, get_worksheet, write_to_sheet

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
    register_appointment()


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
