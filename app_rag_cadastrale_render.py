import streamlit as st
import pandas as pd
import openai
import dropbox
import os
import json
from datetime import datetime

# ✅ Charger les clés API via variables Render
openai_api_key = os.getenv("OPENAI_API_KEY")
dropbox_token = os.getenv("DROPBOX_ACCESS_TOKEN")

if not openai_api_key:
    st.error("🚨 La clé OpenAI API (OPENAI_API_KEY) est manquante.")
    st.stop()
if not dropbox_token:
    st.error("🚨 Le token Dropbox (DROPBOX_ACCESS_TOKEN) est manquant.")
    st.stop()

openai.api_key = openai_api_key
dbx = dropbox.Dropbox(dropbox_token)

st.success("✅ Connexions établies : OpenAI + Dropbox OK.")

# 📈 Fonction d'analyse IA OpenAI Vision
def analyser_image_url(url):
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Tu es expert cadastral. Analyse une photo pour donner en JSON {'niveaux': ?, 'type_immeuble': 'individuel/collectif', 'categorie': 'A/B/C' ou '1/2/3', 'description': '...'}."},
                {"role": "user", "content": [
                    {"type": "text", "text": "Voici l'image."},
                    {"type": "image_url", "image_url": {"url": url}}
                ]}
            ],
            temperature=0
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        st.error(f"❌ Erreur OpenAI Vision : {e}")
        return None

# 📂 Nouvelle Fonction : uploader directement les bytes
def upload_image_to_dropbox(image_bytes, filename):
    """Uploader une image brute (bytes) vers Dropbox et retourner un lien direct"""
    try:
        dbx.files_upload(
            image_bytes,
            f"/IA_CADASTRE/{filename}",
            mode=dropbox.files.WriteMode.overwrite
        )
        shared_link = dbx.sharing_create_shared_link_with_settings(f"/IA_CADASTRE/{filename}")
        return shared_link.url.replace("?dl=0", "?raw=1")  # 🔥 direct image usable by OpenAI
    except dropbox.exceptions.ApiError as e:
        # Cas où le lien existe déjà
        if isinstance(e.error, dropbox.sharing.CreateSharedLinkWithSettingsError):
            links = dbx.sharing_list_shared_links(path=f"/IA_CADASTRE/{filename}").links
            if links:
                return links[0].url.replace("?dl=0", "?raw=1")
        st.error(f"❌ Erreur Dropbox : {e}")
        return None

# 📥 Upload fichiers
uploaded_files = st.file_uploader(
    "📥 Uploadez vos images (.png, .jpg) ou fichiers (.xlsx, .csv)",
    type=["png", "jpg", "jpeg", "xlsx", "csv"],
    accept_multiple_files=True
)

# 📋 Résultats
resultats = []

# 🚀 Traitement
if uploaded_files:
    with st.spinner("🔎 Analyse en cours..."):
        for file in uploaded_files:
            if file.name.endswith((".png", ".jpg", ".jpeg")):
                image_bytes = file.read()
                url = upload_image_to_dropbox(image_bytes, file.name)
                if url:
                    analyse = analyser_image_url(url)
                    if analyse:
                        resultats.append({
                            "NICAD": os.path.splitext(file.name)[0],
                            "Type d'immeuble": analyse.get("type_immeuble", "Non précisé"),
                            "Catégorie": analyse.get("categorie", "Non précisé"),
                            "Niveaux": analyse.get("niveaux", "Non précisé"),
                            "Description": analyse.get("description", "Non précisé")
                        })
            elif file.name.endswith((".xlsx", ".csv")):
                df = pd.read_excel(file) if file.name.endswith(".xlsx") else pd.read_csv(file)
                st.subheader(f"📄 Aperçu du fichier : {file.name}")
                st.dataframe(df)

# 📦 Export Excel
if resultats:
    df_resultats = pd.DataFrame(resultats)
    st.subheader("📊 Résultats d'analyse")
    st.dataframe(df_resultats)

    os.makedirs("resultats", exist_ok=True)
    fichier_final = f"analyse_ia_cadastrale_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    chemin_final = os.path.join("resultats", fichier_final)
    df_resultats.to_excel(chemin_final, index=False)

    with open(chemin_final, "rb") as f:
        st.download_button(
            label="📥 Télécharger Résultats Excel",
            data=f,
            file_name=fichier_final,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    st.success("✅ Analyse terminée et fichier prêt au téléchargement.")
