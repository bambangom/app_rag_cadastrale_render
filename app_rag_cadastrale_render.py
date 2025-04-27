import streamlit as st
import pandas as pd
from PIL import Image
import openai
import base64
import requests
import os

# Configuration de la page
st.set_page_config(page_title="📊 IA Cadastrale RAG", layout="wide")
st.title("🏢 IA Cadastrale RAG : Analyse automatique")

# Charger clé API OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    st.error("🚨 OPENAI_API_KEY manquante. Configure-la dans les variables d'environnement Render !")
    st.stop()

# Fonction pour analyser une image avec OpenAI Vision via base64
def analyse_image_via_openai_base64(image_bytes):
    try:
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }

        base64_image = base64.b64encode(image_bytes).decode("utf-8")

        payload = {
            "model": "gpt-4o",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                "Tu es un expert cadastral. À partir de l'image suivante, "
                                "déduis :\n"
                                "- Type de construction : Maison individuelle ou Immeuble collectif\n"
                                "- Nombre approximatif d'étages visibles\n"
                                "- État général : Neuf, Ordinaire, Dégradé\n"
                                "- Proposition de catégorie :\n"
                                "    * Si Maison individuelle : Catégories 1, 2, 3 selon qualité\n"
                                "    * Si Immeuble collectif : Catégories A, B, C, D selon standing\n"
                                "Sois concis et structuré."
                            )
                        },
                        {
                            "type": "image_file",
                            "image_file": {
                                "data": base64_image,
                                "mime_type": "image/png"
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

# 📥 Upload de fichiers
uploaded_files = st.file_uploader(
    "📥 Uploader vos fichiers (Excel ou Images)",
    type=["xlsx", "csv", "png", "jpg", "jpeg"],
    accept_multiple_files=True
)

# Initialiser les résultats
results = []

if uploaded_files:
    for uploaded_file in uploaded_files:
        st.success(f"📂 Fichier chargé : {uploaded_file.name}")

        if uploaded_file.name.endswith((".xlsx", ".csv")):
            try:
                if uploaded_file.name.endswith(".csv"):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)

                st.subheader(f"📄 Aperçu du fichier {uploaded_file.name}")
                st.dataframe(df)

            except Exception as e:
                st.error(f"❌ Erreur de lecture : {e}")

        elif uploaded_file.name.endswith((".png", ".jpg", ".jpeg")):
            try:
                image = Image.open(uploaded_file)
                st.image(image, caption="🖼️ Image chargée", use_container_width=True)

                image_bytes = uploaded_file.read()
                analyse = analyse_image_via_openai_base64(image_bytes)

                if analyse:
                    st.subheader("🧠 Résultat de l'analyse IA :")
                    st.write(analyse)
                    
                    results.append({
                        "Nom du fichier": uploaded_file.name,
                        "Analyse IA": analyse
                    })

            except Exception as e:
                st.error(f"❌ Erreur d'affichage ou de traitement : {e}")

# 📥 Téléchargement résultats Excel
if results:
    df_results = pd.DataFrame(results)
    st.subheader("📊 Résultats globaux IA")
    st.dataframe(df_results)

    csv = df_results.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Télécharger les résultats en CSV",
        data=csv,
        file_name="resultats_ia_cadastrale.csv",
        mime="text/csv"
    )
