import streamlit as st
import pandas as pd
import openai
import dropbox
import base64
import os
import json
from datetime import datetime

# ✅ Charger les clés depuis variables d'environnement
openai_api_key = os.getenv("OPENAI_API_KEY")
dropbox_token = os.getenv("DROPBOX_ACCESS_TOKEN")

# 🛡️ Vérification des clés
if not openai_api_key or not dropbox_token:
    st.error("🚨 Variables d'environnement manquantes. Configurez OPENAI_API_KEY et DROPBOX_ACCESS_TOKEN sur Render.")
    st.stop()

# 🔑 Initialisation
openai.api_key = openai_api_key
dbx = dropbox.Dropbox(dropbox_token)

# ✅ Message si tout est OK
st.success("✅ Connexions à OpenAI et Dropbox établies avec succès.")

# 📂 Upload de fichiers
uploaded_files = st.file_uploader(
    "📥 Uploader vos fichiers (Excel ou Images)",
    type=["xlsx", "csv", "png", "jpg", "jpeg", "gif", "webp"],
    accept_multiple_files=True
)

# 📂 Fonction upload vers Dropbox et obtenir URL direct
def upload_et_get_url(file):
    try:
        file_path = f"/IA_CADASTRE/{file.name}"
        dbx.files_upload(file.getbuffer(), file_path, mode=dropbox.files.WriteMode.overwrite)
        try:
            shared_link_metadata = dbx.sharing_create_shared_link_with_settings(file_path)
        except dropbox.exceptions.ApiError as e:
            if hasattr(e.error, "is_shared_link_already_exists") and e.error.is_shared_link_already_exists():
                links = dbx.sharing_list_shared_links(path=file_path).links
                if links:
                    shared_link_metadata = links[0]
                else:
                    raise e
            else:
                raise e
        url = shared_link_metadata.url
        if "dropbox.com" in url and "?dl=0" in url:
            url = url.replace("www.dropbox.com", "dl.dropboxusercontent.com").replace("?dl=0", "")
        return url
    except Exception as e:
        st.error(f"❌ Erreur Dropbox : {e}")
        return None

# 📈 Fonction d'analyse OpenAI Vision
def analyser_image_url(url, extension):
    mime_type = "image/jpeg"
    if extension.lower() == ".png":
        mime_type = "image/png"
    elif extension.lower() == ".gif":
        mime_type = "image/gif"
    elif extension.lower() == ".webp":
        mime_type = "image/webp"

    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Tu es un expert en évaluation cadastrale. À partir d'une photo d'un bâtiment, analyse et réponds en JSON {'niveaux': ?, 'type_immeuble': 'individuel/collectif', 'categorie': '1/2/3 ou A/B/C', 'description': '...'}."},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Voici l'image à analyser."},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": url,
                                "mime_type": mime_type
                            }
                        }
                    ]
                }
            ],
            temperature=0
        )
        message = response.choices[0].message.content
        return json.loads(message)
    except Exception as e:
        st.error(f"❌ Erreur OpenAI Vision : {e}")
        return None

# 📋 Collecte des résultats
resultats = []

# 🚀 Traitement principal
if uploaded_files:
    with st.spinner("🔎 Analyse des fichiers en cours..."):
        for file in uploaded_files:
            extension = os.path.splitext(file.name)[1]
            if extension.lower() in [".png", ".jpg", ".jpeg", ".gif", ".webp"]:
                url = upload_et_get_url(file)
                if url:
                    analyse = analyser_image_url(url, extension)
                    if analyse:
                        resultats.append({
                            "NICAD": os.path.splitext(file.name)[0],
                            "Type d'immeuble": analyse.get("type_immeuble", "Non précisé"),
                            "Catégorie": analyse.get("categorie", "Non précisé"),
                            "Niveaux": analyse.get("niveaux", "Non précisé"),
                            "Description": analyse.get("description", "Non précisé")
                        })
            elif extension.lower() in [".xlsx", ".csv"]:
                df = pd.read_excel(file) if extension.lower() == ".xlsx" else pd.read_csv(file)
                st.subheader(f"📄 Aperçu du fichier : {file.name}")
                st.dataframe(df)

# 📦 Export résultats
if resultats:
    df_resultats = pd.DataFrame(resultats)
    st.subheader("📊 Résultats d'analyse")
    st.dataframe(df_resultats)

    nom_fichier = f"analyse_ia_cadastrale_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    chemin_fichier = os.path.join("resultats", nom_fichier)

    os.makedirs("resultats", exist_ok=True)
    df_resultats.to_excel(chemin_fichier, index=False)

    with open(chemin_fichier, "rb") as f:
        st.download_button(
            label="📥 Télécharger les résultats en Excel",
            data=f,
            file_name=nom_fichier,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    st.success("✅ Analyse terminée et fichier prêt au téléchargement.")
