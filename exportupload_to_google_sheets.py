import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# 📚 Configuration pour accéder à Google Sheets
SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

CREDENTIALS_FILE = "google_credentials.json"  # Fichier de clés JSON à placer dans ton dossier
SPREADSHEET_NAME = "IA_Cadastrale_RAG"         # 🔥 Le nom du Google Sheets que tu veux utiliser
SHEET_NAME = "Fiches"                          # 🔥 L'onglet où seront envoyées les données
EXCEL_FILE = "export/croisement_images_corrige.xlsx"

def uploader_excel_vers_google_sheets(fichier_excel, credentials_file, nom_spreadsheet, nom_sheet):
    try:
        # 🔐 Authentification
        creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_file, SCOPE)
        client = gspread.authorize(creds)

        # 🔎 Accès au Google Spreadsheet
        spreadsheet = client.open(nom_spreadsheet)

        # 🔎 Accès à la feuille (sheet)
        try:
            sheet = spreadsheet.worksheet(nom_sheet)
            sheet.clear()  # On efface l'ancien contenu avant d'uploader
        except gspread.exceptions.WorksheetNotFound:
            sheet = spreadsheet.add_worksheet(title=nom_sheet, rows="1000", cols="20")

        # 🔄 Lecture du fichier Excel
        df = pd.read_excel(fichier_excel)

        # 🔄 Upload
        sheet.update([df.columns.values.tolist()] + df.values.tolist())
        print(f"✅ Données envoyées avec succès dans Google Sheets : {nom_spreadsheet} / {nom_sheet}")

    except Exception as e:
        print(f"❌ Erreur lors de l'upload vers Google Sheets : {e}")

if __name__ == "__main__":
    uploader_excel_vers_google_sheets(EXCEL_FILE, CREDENTIALS_FILE, SPREADSHEET_NAME, SHEET_NAME)
