# 📚 Importations
import streamlit as st
import pandas as pd
from PIL import Image
import openai
import base64
import os

# 🛠️ Configuration immédiate de la page
st.set_page_config(
    page_title="📊 IA Cadastrale RAG",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 🎯 Titre principal
st.title("📊 IA Cadastrale RAG - Assistant Intelligent")

# 🔑 Configuration API OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# 📥 Upload de plusieurs fichiers
uploaded_files = st.file_uploader(
    "📥 Charger un ou plusieurs fichiers Excel (.xlsx, .csv) ou Images (.png, .jpg, .jpeg)",
    type=["xlsx", "csv", "png", "jpg", "jpeg"],
    accept_multiple_files=True
)

# 📦 Traitement des fichiers
if uploaded_files:
    for uploaded_file in uploaded_files:
        st.success(f"✅ Fichier {uploaded_file.name} chargé avec succès")

        if uploaded_file.name.endswith((".xlsx", ".csv")):
            try:
                if uploaded_file.name.endswith(".csv"):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)

                st.subheader(f"📄 Aperçu du fichier : {uploaded_file.name}")
                st.dataframe(df)

            except Exception as e:
                st.error(f"❌ Erreur lors de la lecture du fichier {uploaded_file.name} : {e}")

        elif uploaded_file.name.endswith((".png", ".jpg", ".jpeg")):
            try:
                image = Image.open(uploaded_file)
                st.image(image, caption=f"🖼️ {uploaded_file.name}", use_column_width=True)

                if st.button(f"🔍 Analyser {uploaded_file.name}", key=uploaded_file.name):
                    with st.spinner('⏳ Analyse IA en cours...'):

                        try:
                            # Convertir l'image en base64
                            buffered = open(uploaded_file.name, "rb")
                            img_base64 = base64.b64encode(buffered.read()).decode()

                            # Appel OpenAI GPT-4-Vision (fonction image)
                            response = openai.ChatCompletion.create(
                                model="gpt-4-vision-preview",
                                messages=[
                                    {"role": "system", "content": "Tu es un assistant cadastral expert. À partir de la photo, déduis : Type d'immeuble (individuel ou collectif), nombre de niveaux, et catégorie selon décret 2010-439 et décret 2014."},
                                    {"role": "user", "content": f"Analyse cette image : {img_base64}"}
                                ],
                                max_tokens=800
                            )

                            resultat = response.choices[0].message.content
                            st.success("✅ Analyse réussie")
                            st.markdown(resultat)

                        except Exception as e:
                            st.error(f"❌ Erreur avec l'API OpenAI Vision : {e}")

            except Exception as e:
                st.error(f"❌ Erreur lors de l'affichage de {uploaded_file.name} : {e}")

# ℹ️ Footer
st.markdown("---")
st.caption("© 2025 - Projet IA Cadastrale RAG | Décret 2010-439 et Décret 2014 appliqués")
