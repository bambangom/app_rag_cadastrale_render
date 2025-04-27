import streamlit as st
import pandas as pd
import openai
import dropbox
import base64
import os
import requests
import json

# 📍 Configuration
st.set_page_config(page_title="IA Cadastrale RAG", layout="wide")
st.title("🏢 IA Cadastrale RAG : Analyse automatique des bâtiments")

# 📍 Récupérer la clé OpenAI et Dropbox (via secrets ou env)
openai_api_key = st.secrets.get("OPENAI_API_KEY", None) or os.getenv("OPENAI_API_KEY")
dropbox_token = st.secrets.get("DROPBOX_TOKEN", None) or os.getenv("DROPBOX_TOKEN")

if not openai_api_key or not dropbox_token:
    st.error("🚨 Configuration manquante. Assurez-vous d'avoir défini OPENAI_API_KEY et DROPBOX_TOKEN.")
    st.stop()

openai.api_key = openai_api_key
dbx = dropbox.Dropbox(dropbox_token)

# 📂 Upload de fichiers
uploaded_files = st.file_uploader(
    "📥 Uploader vos fichiers (Excel ou Images)",
    type=["xlsx", "csv", "png", "jpg", "jpeg"],
    accept_multiple_files=True
)

# 📈 Fonction d'analyse OpenAI Vision
def analyser_image_url(url):
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Tu es un expert en évaluation cadastrale. À partir d'une photo d'un bâtiment, déduis : {'niveaux': ?, 'type_immeuble': 'individuel/collectif', 'categorie': '1/2/3' pour individuel ou 'A/B/C' pour collectif, 'description': '...'}."},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Voici l'image à analyser."},
                        {"type": "image_url", "image_url": {"url": url}}
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

# 📂 Fonction upload Dropbox ➔ lien direct
# 📂 Fonction upload Dropbox ➔ lien direct (corrigé shared_link_already_exists)
def upload_et_get_url(file):
    try:
        file_path = f"/IA_CADASTRE/{file.name}"
        dbx.files_upload(file.getbuffer(), file_path, mode=dropbox.files.WriteMode.overwrite)

        try:
            # 🔥 Essayer de créer un lien
            shared_link_metadata = dbx.sharing_create_shared_link_with_settings(file_path)
        except dropbox.exceptions.ApiError as e:
            # 🔥 Si lien existe déjà ➔ récupérer les liens existants
            if isinstance(e.error, dropbox.sharing.CreateSharedLinkWithSettingsError) and e.error.is_shared_link_already_exists():
                links = dbx.sharing_list_shared_links(path=file_path).links
                if links:
                    shared_link_metadata = links[0]
                else:
                    raise e
            else:
                raise e

        url = shared_link_metadata.url

        # 🔥 Corriger pour obtenir un lien direct
        if "dropbox.com" in url and "?dl=0" in url:
            url = url.replace("www.dropbox.com", "dl.dropboxusercontent.com").replace("?dl=0", "")

        return url

    except Exception as e:
        st.error(f"❌ Erreur Dropbox : {e}")
        return None

# 📋 Collecte des résultats
resultats = []

# 🚀 Traitement principal
if uploaded_files:
    with st.spinner("🔎 Analyse des fichiers en cours..."):
        for file in uploaded_files:
            if file.name.endswith((".png", ".jpg", ".jpeg")):
                url = upload_et_get_url(file)
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
