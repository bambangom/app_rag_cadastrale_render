import streamlit as st
import pandas as pd
import openai
import dropbox
import base64
import os
import json
from datetime import datetime

# 🔒 Charger les clés API depuis l'environnement
openai_api_key = os.getenv("OPENAI_API_KEY")
dropbox_token = os.getenv("DROPBOX_ACCESS_TOKEN")

# 🚨 Vérification des clés
if not openai_api_key or not dropbox_token:
    st.error("🚨 Les variables d'environnement OPENAI_API_KEY et DROPBOX_ACCESS_TOKEN doivent être définies.")
    st.stop()

# 🔑 Initialiser OpenAI et Dropbox
openai.api_key = openai_api_key
dbx = dropbox.Dropbox(dropbox_token)

# 📄 Configuration Streamlit
st.set_page_config(page_title="📊 IA Cadastrale RAG", layout="wide")
st.title("🏢 IA Cadastrale RAG : Analyse automatique")

# 📂 Dossier de résultats
RESULTS_DIR = "resultats"
os.makedirs(RESULTS_DIR, exist_ok=True)

# 📂 Upload de fichiers
uploaded_files = st.file_uploader(
    "📥 Uploader vos fichiers (Excel ou Images)",
    type=["xlsx", "csv", "png", "jpg", "jpeg"],
    accept_multiple_files=True
)

# 🔼 Fonction upload Dropbox
def upload_image_to_dropbox(image_bytes, filename):
    try:
        if isinstance(image_bytes, memoryview):
            image_bytes = image_bytes.tobytes()

        dbx.files_upload(
            image_bytes,
            f"/{filename}",
            mode=dropbox.files.WriteMode.overwrite
        )

        try:
            shared_link = dbx.sharing_create_shared_link_with_settings(f"/{filename}")
        except dropbox.exceptions.ApiError as e:
            # Si le lien existe déjà, récupérer
            if hasattr(e.error, "is_shared_link_already_exists") and e.error.is_shared_link_already_exists():
                links = dbx.sharing_list_shared_links(path=f"/{filename}").links
                if links:
                    shared_link = links[0]
                else:
                    raise e
            else:
                raise e

        url = shared_link.url
        if "dropbox.com" in url and "?dl=0" in url:
            url = url.replace("www.dropbox.com", "dl.dropboxusercontent.com").replace("?dl=0", "")

        return url

    except Exception as e:
        st.error(f"❌ Erreur Dropbox : {e}")
        return None

# 🔎 Fonction d'analyse OpenAI Vision
def analyser_image_via_openai(image_url):
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Tu es un expert cadastral. À partir d'une photo de bâtiment, "
                        "donne un JSON : {'niveaux': ?, 'type_immeuble': 'individuel/collectif', "
                        "'categorie': '1/2/3 pour individuel, A/B/C pour collectif', 'description': '...'}."
                    )
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Analyse ce bâtiment."},
                        {"type": "image_url", "image_url": {"url": image_url}}
                    ]
                }
            ],
            temperature=0
        )

        message_content = response.choices[0].message.content
        return json.loads(message_content)

    except Exception as e:
        st.error(f"❌ Erreur OpenAI Vision : {e}")
        return None

# 📦 Liste pour stocker les résultats
resultats = []

# 🚀 Traitement principal
if uploaded_files:
    with st.spinner("🔎 Analyse en cours..."):
        for file in uploaded_files:
            if file.name.endswith((".png", ".jpg", ".jpeg")):
                url = upload_image_to_dropbox(file.getbuffer(), file.name)
                if url:
                    analyse = analyser_image_via_openai(url)
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
                st.subheader(f"📄 Aperçu du fichier {file.name}")
                st.dataframe(df)

# 💾 Export des résultats
if resultats:
    df_resultats = pd.DataFrame(resultats)
    st.subheader("📊 Résultats d'analyse")
    st.dataframe(df_resultats)

    nom_fichier_excel = f"analyse_ia_cadastrale_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    chemin_fichier = os.path.join(RESULTS_DIR, nom_fichier_excel)

    df_resultats.to_excel(chemin_fichier, index=False)

    with open(chemin_fichier, "rb") as f:
        st.download_button(
            label="📥 Télécharger les résultats en Excel",
            data=f,
            file_name=nom_fichier_excel,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    st.success("✅ Analyse terminée et fichier prêt à être téléchargé.")

