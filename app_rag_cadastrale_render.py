import streamlit as st
import pandas as pd
from PIL import Image
import openai
import os
import io

# 🚀 Configuration initiale Streamlit
st.set_page_config(page_title="📊 IA Cadastrale RAG", layout="wide")
st.title("🏢 IA Cadastrale RAG : Analyse automatique")

# 🔐 Clé API OpenAI depuis environnement Render (via st.secrets ou variable d'environnement)
openai_api_key = os.getenv("OPENAI_API_KEY")

if not openai_api_key:
    st.error("🚨 Clé API OpenAI non configurée. Veuillez définir 'OPENAI_API_KEY'.")
    st.stop()

openai.api_key = openai_api_key

# 📥 Upload de fichiers
uploaded_files = st.file_uploader(
    "📥 Uploader vos fichiers (Excel ou Images)", 
    type=["xlsx", "csv", "png", "jpg", "jpeg"], 
    accept_multiple_files=True
)

if uploaded_files:
    for uploaded_file in uploaded_files:
        st.success(f"📂 Fichier chargé : {uploaded_file.name}")

        if uploaded_file.name.endswith((".xlsx", ".csv")):
            try:
                if uploaded_file.name.endswith(".csv"):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)
                st.subheader(f"📄 Aperçu de {uploaded_file.name}")
                st.dataframe(df)
            except Exception as e:
                st.error(f"❌ Erreur lors de la lecture du fichier : {e}")

        elif uploaded_file.name.endswith((".png", ".jpg", ".jpeg")):
            try:
                image = Image.open(uploaded_file)
                st.image(image, caption=f"🖼️ {uploaded_file.name}", use_container_width=True)

                # 🧠 Analyse de l'image via OpenAI
                with st.spinner("🔎 Analyse IA en cours..."):

                    # 🔵 Enregistrer temporairement l'image en mémoire
                    img_bytes = io.BytesIO()
                    image.save(img_bytes, format="PNG")
                    img_bytes.seek(0)

                    # 🔵 Upload du fichier vers OpenAI
                    file_response = openai.files.create(
                        file=img_bytes,
                        purpose="vision"
                    )

                    file_id = file_response.id

                    # 🔵 Demande d'analyse à OpenAI Vision
                    vision_response = openai.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": "Décris précisément le type de bâtiment (individuel ou collectif), le nombre d'étages visibles, et donne la catégorie fiscale estimée selon les critères cadastraux du Sénégal."},
                                    {"type": "file", "file_id": file_id}
                                ]
                            }
                        ],
                        temperature=0.2
                    )

                    result_text = vision_response.choices[0].message.content

                    st.subheader("📋 Résultat de l'analyse IA")
                    st.success(result_text)

            except Exception as e:
                st.error(f"❌ Erreur OpenAI Vision : {e}")
else:
    st.info("📂 Veuillez uploader un ou plusieurs fichiers pour commencer l'analyse.")
