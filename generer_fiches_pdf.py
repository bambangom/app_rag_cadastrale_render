import os
import pandas as pd
from fpdf import FPDF
from datetime import datetime

# 📂 Dossier de sauvegarde des fiches générées
OUTPUT_DIR = "fiches_pdfs"

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

class PDFGenerator(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, '📋 Fiche Évaluation Cadastrale', ln=True, align='C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()} - Généré le {datetime.now().strftime("%d/%m/%Y")}', align='C')

    def fiche_content(self, data):
        self.set_font('Arial', '', 12)
        for key, value in data.items():
            self.cell(0, 10, f"{key} : {value}", ln=True)
        self.ln(10)

def extraire_nom_sans_extension(nom_fichier):
    return os.path.splitext(nom_fichier)[0]

def generer_fiches(df, dossier_images=None):
    # Si dossier images est fourni, on fait un croisement intelligent
    if dossier_images:
        images = [extraire_nom_sans_extension(f) for f in os.listdir(dossier_images) if f.endswith((".png", ".jpg", ".jpeg"))]
        df = df[df["NICAD"].isin(images)]

    for idx, row in df.iterrows():
        pdf = PDFGenerator()
        pdf.add_page()

        info = {
            "NICAD": row.get("NICAD", "Non précisé"),
            "Type de bâtiment": row.get("Type", "Non précisé"),
            "Nombre d'étages": row.get("Nombre d'étages", "Non précisé"),
            "Catégorie fiscale": row.get("Catégorie", "Non précisé"),
            "Observations IA": row.get("Commentaires", "Aucune observation"),
            "Analyse IA": row.get("Analyse", "Non disponible")
        }

        pdf.fiche_content(info)

        filename = f"{OUTPUT_DIR}/Fiche_{row.get('NICAD', idx)}.pdf"
        pdf.output(filename)
        print(f"✅ Fiche générée : {filename}")

if __name__ == "__main__":
    try:
        df = pd.read_excel("croisement_images_corrige.xlsx")
        generer_fiches(df, dossier_images="images")  # ← dossier où sont stockées les images
    except Exception as e:
        print(f"Erreur lors de la génération : {e}")

