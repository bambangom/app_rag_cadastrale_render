import streamlit as st
import pandas as pd
import os
import openai
from PIL import Image
from io import BytesIO

# 🎯 Configurer la page Streamlit dès le début
st.set_page_config(page_title="📊 IA Cadastrale RAG", layout="wide")
st.title("🏢 IA Cadastrale RAG : Analyse automatique")

# 🔑 Récupérer la clé API OpenAI depuis les variables d'environnement
openai.api_key = os.getenv("OPENAI_API_KEY")

# 📤 Upload multiple autorisé
uploaded_files = st.file_uploader("📥 Uploader vos fichiers (Excel ou Images)", accept_multiple_files=True, type=["xlsx", "csv", "png", "jpg", "jpeg"])

# 🧠 Fonction pour analyser une image avec OpenAI Vision
def analyze_image_with_openai(file_bytes):
    try:
        response = openai.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Analyse cette image d'un immeuble pour déterminer le type d'immeuble (individuel ou collectif), estimer le nombre de niveaux (RDC, R+1, etc.) et proposer la catégorie cadastrale selon la réglementation sénégalaise."},
                        {"type": "image", "image": file_bytes}
                    ],
                }
            ],
            max_tokens=500,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ Erreur OpenAI Vision : {e}"

# 📊 Si des fichiers sont uploadés
if uploaded_files:
    for uploaded_file in uploaded_files:
        st.subheader(f"📂 Fichier chargé : {uploaded_file.name}")

        if uploaded_file.name.endswith((".png", ".jpg", ".jpeg")):
            try:
                # 📸 Afficher l'image
                image = Image.open(uploaded_file)
                st.image(image, caption="🖼️ Image chargée", use_column_width=True)

                # 🧠 Analyse OpenAI
                file_bytes = uploaded_file.read()
                analysis_result = analyze_image_with_openai(file_bytes)
                st.success("✅ Analyse IA terminée :")
                st.write(analysis_result)

            except Exception as e:
                st.error(f"Erreur lors du traitement de l'image : {e}")

        elif uploaded_file.name.endswith((".xlsx", ".csv")):
            try:
                if uploaded_file.name.endswith(".csv"):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)
                
                st.dataframe(df)

            except Exception as e:
                st.error(f"Erreur lors de la lecture du fichier : {e}")
else:
    st.info("📤 Veuillez uploader un ou plusieurs fichiers (Excel ou Images) pour commencer.")
