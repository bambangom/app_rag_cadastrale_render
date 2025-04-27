import streamlit as st
import pandas as pd
import os
import openai
import requests
from PIL import Image
from io import BytesIO
from datetime import datetime

st.set_page_config(page_title="📊 IA Cadastrale RAG", layout="wide")

# 🔑 Chargement de la clé API OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

if not openai.api_key:
    openai.api_key = st.text_input("🔑 Entrez votre clé OpenAI ici :", type="password")

# 📂 Upload des fichiers
st.title("🏢 IA Cadastrale RAG : Analyse automatique")

uploaded_files = st.file_uploader(
    "📥 Uploader vos fichiers (Excel ou Images)",
    type=["xlsx", "csv", "png", "jpg", "jpeg"],
    accept_multiple_files=True
)

def envoyer_vers_transfersh(file_bytes, filename):
    """Uploader temporairement l'image sur transfer.sh pour OpenAI Vision."""
    try:
        response = requests.put(
            f"https://transfer.sh/{filename}",
            data=file_bytes,
            headers={"Max-Downloads": "1", "Max-Days": "1"}
        )
        if response.status_code == 200:
            return response.text.strip()
        else:
            st.error(f"Erreur Upload transfer.sh : {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Erreur de connexion à transfer.sh : {e}")
        return None

def analyser_image_via_openai(url):
    """Envoyer l'URL publique de l'image à OpenAI Vision."""
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Tu es un expert en diagnostic immobilier cadastral."},
                {"role": "user", "content": [
                    {"type": "text", "text": "Analyse l'image immobilière. Donne : 1) Nombre de niveaux, 2) Type d'immeuble (individuel ou collectif), 3) Catégorie fiscale (A, B, C, D, 1, 2, 3, 4) selon le standing."},
                    {"type": "image_url", "image_url": {"url": url}}
                ]}
            ],
            temperature=0.3
        )
        result = response.choices[0].message.content
        return result
    except Exception as e:
        st.error(f"❌ Erreur OpenAI Vision : {e}")
        return None

def traiter_fichier_excel(file):
    try:
        if file.name.endswith(".csv"):
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)
        st.success("✅ Fichier Excel chargé")
        st.dataframe(df)
        return df
    except Exception as e:
        st.error(f"Erreur chargement Excel : {e}")
        return None

def traiter_image(file):
    try:
        image = Image.open(file)
        st.image(image, caption="🖼️ Image chargée", use_column_width=True)
        file_bytes = file.read()
        upload_url = envoyer_vers_transfersh(file_bytes, file.name)
        if upload_url:
            st.info(f"🔗 URL de l'image : {upload_url}")
            resultat = analyser_image_via_openai(upload_url)
            if resultat:
                st.success("✅ Analyse de l'image terminée")
                st.markdown(f"### 📋 Résultat de l'analyse :\n{resultat}")
            else:
                st.error("❌ Échec de l'analyse de l'image")
    except Exception as e:
        st.error(f"Erreur traitement image : {e}")

# 🎯 Traitement principal
if uploaded_files:
    for file in uploaded_files:
        st.subheader(f"📂 Fichier chargé : {file.name}")
        if file.name.endswith((".xlsx", ".csv")):
            traiter_fichier_excel(file)
        elif file.name.endswith((".png", ".jpg", ".jpeg")):
            traiter_image(file)
