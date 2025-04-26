import os
import streamlit as st
import pandas as pd
import requests
from PIL import Image
from io import BytesIO

# 📄 Configuration de la page
st.set_page_config(page_title="🏢 IA Cadastrale RAG", layout="wide")

# 📢 Affichage du titre principal
st.title("🏢 IA Cadastrale RAG : Analyse automatique")

# 📥 Uploader un ou plusieurs fichiers
uploaded_files = st.file_uploader(
    "📥 Uploader vos fichiers (Excel ou Images)", 
    type=["xlsx", "csv", "png", "jpg", "jpeg"], 
    accept_multiple_files=True
)

# 🔑 Clé API OpenAI depuis l'environnement Render
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# 🔗 Fonction pour envoyer une image en tant que URL vers OpenAI
def analyse_image_via_openai_url(image_url):
    try:
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "gpt-4o",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Voici une image d'un bâtiment. Décris-moi son type (individuel/collectif), le nombre approximatif d'étages visibles, l'état général (neuf, ordinaire, dégradé) et propose une catégorie cadastrale selon un décret foncier."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_url
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 1000
        }

        response = requests.post(
            "https://api.openai.com/v1/chat/completions", 
            headers=headers, 
            json=payload
        )

        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"]
        else:
            st.error(f"❌ Erreur OpenAI Vision : {response.status_code} - {response.json()}")
            return None

    except Exception as e:
        st.error(f"❌ Erreur OpenAI Vision : {e}")
        return None

# 🚀 Si des fichiers sont uploadés
if uploaded_files:
    for uploaded_file in uploaded_files:
        st.success(f"📂 Fichier chargé : {uploaded_file.name}")

        if uploaded_file.name.endswith((".xlsx", ".csv")):
            try:
                if uploaded_file.name.endswith(".csv"):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)
                st.subheader("📄 Aperçu du fichier Excel")
                st.dataframe(df)
            except Exception as e:
                st.error(f"❌ Erreur de lecture du fichier : {e}")

        elif uploaded_file.name.endswith((".png", ".jpg", ".jpeg")):
            try:
                image = Image.open(uploaded_file)
                st.image(image, caption="🖼️ Image chargée", use_container_width=True)

                # ⬆️ Upload temporaire de l'image vers un service pour obtenir une URL
                temp_path = f"/tmp/{uploaded_file.name}"
                image.save(temp_path)

                # ⚡ Utilisation de file.io pour héberger temporairement l'image (ou un autre service temporaire)
                with open(temp_path, "rb") as img_file:
                    upload_response = requests.post(
                        "https://file.io",
                        files={"file": img_file}
                    )
                    upload_data = upload_response.json()
                    image_url = upload_data.get("link")

                if image_url:
                    st.info(f"🌐 Image uploadée temporairement à : {image_url}")

                    # 🎯 Analyse de l'image via OpenAI Vision
                    analyse = analyse_image_via_openai_url(image_url)

                    if analyse:
                        st.subheader("📋 Résultat de l'analyse IA")
                        st.write(analyse)
                    else:
                        st.error("⚠️ Impossible d'analyser l'image avec OpenAI.")
                else:
                    st.error("⚠️ Impossible d'uploader temporairement l'image.")

            except Exception as e:
                st.error(f"❌ Erreur d'affichage ou de traitement : {e}")
