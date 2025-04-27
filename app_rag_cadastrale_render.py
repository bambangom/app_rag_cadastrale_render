# 🚀 Imports
import streamlit as st
import openai
import pandas as pd
import requests
import json
import base64
import os
from io import BytesIO
from PIL import Image
from datetime import datetime

# 🛡️ Clé API OpenAI (depuis Variables Render ou secrets)
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    st.error("❌ OPENAI_API_KEY non trouvé dans l'environnement.")
    st.stop()
openai.api_key = openai_api_key

# 📦 Token Dropbox (à stocker aussi dans Variables Render)
dropbox_token = os.getenv("DROPBOX_ACCESS_TOKEN")
if not dropbox_token:
    st.error("❌ DROPBOX_ACCESS_TOKEN non trouvé dans l'environnement.")
    st.stop()

# 📂 Fonctions Dropbox
def upload_to_dropbox(file_bytes, filename):
    """Upload le fichier dans Dropbox et retourne l'URL partagée"""
    try:
        # Upload dans Dropbox
        headers = {
            "Authorization": f"Bearer {dropbox_token}",
            "Content-Type": "application/octet-stream",
            "Dropbox-API-Arg": json.dumps({
                "path": f"/{filename}",
                "mode": "add",
                "autorename": True,
                "mute": False
            })
        }
        upload_url = "https://content.dropboxapi.com/2/files/upload"
        response = requests.post(upload_url, headers=headers, data=file_bytes)

        if response.status_code == 200:
            # Créer un lien partagé
            create_shared_link_url = "https://api.dropboxapi.com/2/sharing/create_shared_link_with_settings"
            headers_link = {
                "Authorization": f"Bearer {dropbox_token}",
                "Content-Type": "application/json"
            }
            data_link = {
                "path": json.loads(response.content)["path_display"],
                "settings": {"requested_visibility": "public"}
            }
            response_link = requests.post(create_shared_link_url, headers=headers_link, json=data_link)
            if response_link.status_code == 200:
                url = response_link.json()["url"].replace("?dl=0", "?raw=1")  # Important : passer en URL directe
                return url
            else:
                st.error(f"Erreur création lien partagé Dropbox : {response_link.text}")
        else:
            st.error(f"Erreur upload Dropbox : {response.text}")
    except Exception as e:
        st.error(f"Erreur Dropbox : {e}")
    return None

# ⚙️ Fonction d'analyse OpenAI Vision
def analyser_batiment(image_url):
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Tu es un expert en évaluation cadastrale d'immeubles."},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Analyse la photo et réponds en JSON {'niveaux': ?, 'type_immeuble': 'individuel/collectif', 'categorie': '1/2/3/A/B/C', 'description': '...'} selon le décret 2010-439."},
                        {
                            "type": "image_url",
                            "image_url": {"url": image_url}
                        },
                    ],
                },
            ],
            temperature=0
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"❌ Erreur OpenAI Vision : {e}")
        return None

# 🖥️ Interface Streamlit
st.set_page_config(page_title="IA Cadastrale RAG", layout="wide")
st.title("🏢 IA Cadastrale RAG : Analyse Automatique des Immeubles")

uploaded_files = st.file_uploader("📥 Charger vos images (PNG, JPG, JPEG)", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

if uploaded_files:
    st.success(f"✅ {len(uploaded_files)} image(s) chargée(s)")
    if st.button("🚀 Lancer l'analyse"):
        resultats = []
        for fichier in uploaded_files:
            st.write(f"Analyse de : **{fichier.name}**")
            try:
                # Lire l'image
                image = Image.open(fichier)
                buffered = BytesIO()
                image.save(buffered, format="PNG")
                file_bytes = buffered.getvalue()

                # Upload sur Dropbox
                dropbox_url = upload_to_dropbox(file_bytes, fichier.name)
                if not dropbox_url:
                    continue

                # Appel OpenAI
                analyse = analyser_batiment(dropbox_url)
                if analyse:
                    try:
                        analyse_json = json.loads(analyse)
                    except:
                        st.error(f"⚠️ Format inattendu pour {fichier.name}")
                        continue

                    resultats.append({
                        "NICAD": fichier.name.rsplit('.', 1)[0],
                        "Type d'immeuble": analyse_json.get("type_immeuble", "Non précisé"),
                        "Catégorie": analyse_json.get("categorie", "Non précisé"),
                        "Niveaux": analyse_json.get("niveaux", "Non précisé"),
                        "Description": analyse_json.get("description", "Non précisé")
                    })
            except Exception as e:
                st.error(f"Erreur avec {fichier.name} : {e}")

        if resultats:
            df = pd.DataFrame(resultats)
            st.dataframe(df)
            # Export Excel
            now = datetime.now().strftime("%Y%m%d%H%M%S")
            output_path = f"resultats_ia_cadastrale_{now}.xlsx"
            df.to_excel(output_path, index=False)
            st.success("✅ Analyse terminée. Télécharger le fichier Excel ci-dessous :")
            with open(output_path, "rb") as f:
                st.download_button(label="📥 Télécharger le fichier Excel", data=f, file_name=output_path)
        else:
            st.error("❌ Aucun résultat exploitable.")
else:
    st.info("📂 Veuillez uploader un fichier pour commencer.")

