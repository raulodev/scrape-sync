from decouple import config

EMAIL = config("EMAIL")
PASSWORD = config("PASSWORD")
SPREADSHEET_ID = config("SPREADSHEET_ID")
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
GOHIGHLEVEL_TOKEN = config("GOHIGHLEVEL_TOKEN")
