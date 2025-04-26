import os
import pandas as pd

# 📂 Dossier où sont stockées les images
IMAGES_FOLDER = "images"

# 📂 Dossier où sera sauvegardé l'Excel
EXPORT_FOLDER = "export"
EXPORT_FILENAME = "croisement_images_corrige.xlsx"

if not os.path.exists(EXPORT_FOLDER):
    os.makedirs(EXPORT_FOLDER)

def extraire_nom_sans_extension(nom_fichier):
    return os.path.splitext(nom_fichier)[0]

def creer_dataframe_depuis_images(dossier_images):
    data = []
    images = [f for f in os.listdir(dossier_images) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    for img in images:
        nicad = extraire_nom_sans_extension(img)
        data.append({
            "NICAD": nicad,
            "Type": "",  # à remplir par l'IA ou manuellement : "Individuel" ou "Collectif"
            "Nombre d'étages": "",  # à prédire ou à compléter
            "Catégorie": "",  # IA prédira ensuite ou calcul manuel selon décret
            "Commentaires": "",  # Observations IA ou manuelles
            "Analyse": ""  # Analyse détaillée IA si disponible
        })
    return pd.DataFrame(data)

def exporter_dataframe(df, dossier_export, nom_fichier):
    chemin_complet = os.path.join(dossier_export, nom_fichier)
    df.to_excel(chemin_complet, index=False)
    print(f"✅ Fichier Excel exporté avec succès : {chemin_complet}")

if __name__ == "__main__":
    try:
        df_images = creer_dataframe_depuis_images(IMAGES_FOLDER)
        exporter_dataframe(df_images, EXPORT_FOLDER, EXPORT_FILENAME)
    except Exception as e:
        print(f"❌ Erreur lors de l'exportation Excel : {e}")
