# pylint: disable=import-error
import typer

from extract_from_esteticals import extract_from_esteticals
from sheets import create_google_credential_file, write_to_sheet
from gohighlevel import register_appointment

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
    register_appointment()


if __name__ == "__main__":
    app()
