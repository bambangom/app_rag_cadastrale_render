import streamlit as st
import pandas as pd
from PIL import Image
import openai
import os
import io
import base64

# 🎯 Config Streamlit
st.set_page_config(page_title="📊 IA Cadastrale RAG", layout="wide")
st.title("🏢 IA Cadastrale RAG : Analyse automatique")

# 🔐 Clé API OpenAI
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    st.error("🚨 Clé API OpenAI non trouvée. Définis ta variable d'environnement dans Render.com")
    st.stop()

openai.api_key = openai_api_key

# 📥 Uploader fichiers
uploaded_files = st.file_uploader(
    "📥 Uploader vos fichiers (Excel ou Images)",
    type=["xlsx", "csv", "png", "jpg", "jpeg"],
    accept_multiple_files=True
)

# 🔥 Fonction : encoder l'image Base64
def encode_image_to_base64(image_file):
    return base64.b64encode(image_file.read()).decode('utf-8')

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
                st.error(f"❌ Erreur de lecture fichier : {e}")

        elif uploaded_file.name.endswith((".png", ".jpg", ".jpeg")):
            try:
                img = Image.open(uploaded_file)
                st.image(img, caption=f"🖼️ {uploaded_file.name}", use_container_width=True)

                with st.spinner("🔎 Analyse IA en cours..."):
                    uploaded_file.seek(0)
                    base64_img = encode_image_to_base64(uploaded_file)

                    response = openai.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": "Analyse cette image pour déterminer : 1) Type d'immeuble (individuel ou collectif), 2) Nombre d'étages visibles, 3) Catégorie cadastrale correcte selon décret 2010-439 et décret 2014."},
                                    {"type": "file", "file": {"base64": base64_img, "name": uploaded_file.name}}
                                ]
                            }
                        ],
                        temperature=0.2
                    )

                    result = response.choices[0].message.content
                    st.subheader("📋 Résultat IA")
                    st.success(result)

            except Exception as e:
                st.error(f"❌ Erreur lors du traitement de l'image : {e}")

else:
    st.info("📂 Merci de uploader un fichier pour commencer l'analyse.")
