import os
import pandas as pd
from fpdf import FPDF
from datetime import datetime

# 📂 Dossier où sauvegarder les fiches
OUTPUT_DIR = "fiches_pdfs"

# 📁 Créer le dossier s'il n'existe pas
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

class PDFGenerator(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, '🏛️ Fiche d\'Évaluation Cadastrale IA', ln=True, align='C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()} - {datetime.now().strftime("%d/%m/%Y")}', align='C')

    def fiche_content(self, data):
        self.set_font('Arial', '', 12)
        for key, value in data.items():
            self.cell(0, 10, f"{key} : {value}", ln=True)
        self.ln(8)

def generer_fiches(df):
    for idx, row in df.iterrows():
        pdf = PDFGenerator()
        pdf.add_page()

        # Construction des données pour chaque fiche
        info = {
            "NICAD / Référence": row.get("Nom du fichier", f"Image_{idx}").replace(".png", "").replace(".jpg", "").replace(".jpeg", ""),
            "Analyse IA": row.get("Analyse IA", "Non disponible")
        }

        pdf.fiche_content(info)

        # 📄 Nom du fichier PDF
        filename = f"{OUTPUT_DIR}/Fiche_{info['NICAD / Référence']}.pdf"
        pdf.output(filename)
        print(f"✅ Fiche générée : {filename}")

if __name__ == "__main__":
    try:
        # Charger le CSV généré par l'app IA
        df = pd.read_csv("resultats_analyse_cadastrale.csv")
        generer_fiches(df)
    except Exception as e:
        print(f"❌ Erreur lors de la génération des fiches : {e}")
