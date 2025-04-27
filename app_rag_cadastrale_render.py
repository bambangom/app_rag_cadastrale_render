import streamlit as st
import pandas as pd
from PIL import Image
import openai
import os
import io
import requests

# 🚀 Configuration Streamlit
st.set_page_config(page_title="📊 IA Cadastrale RAG", layout="wide")
st.title("🏢 IA Cadastrale RAG : Analyse automatique")

# 🔐 Lecture de la clé API OpenAI
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    st.error("🚨 Clé API OpenAI non trouvée dans les variables d'environnement.")
    st.stop()

openai.api_key = openai_api_key

# 📥 Upload de fichiers
uploaded_files = st.file_uploader(
    "📥 Uploader vos fichiers (Excel ou Images)",
    type=["xlsx", "csv", "png", "jpg", "jpeg"],
    accept_multiple_files=True
)

def upload_to_transfer_sh(file_name, file_bytes):
    """Uploader l'image sur transfer.sh pour obtenir une URL publique temporaire."""
    try:
        files = {'file': (file_name, file_bytes)}
        response = requests.post('https://transfer.sh/', files=files)
        if response.status_code == 200:
            return response.text.strip()
        else:
            return None
    except Exception as e:
        st.error(f"❌ Erreur de connexion à transfer.sh : {e}")
        return None

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
                st.error(f"❌ Erreur de lecture du fichier : {e}")

        elif uploaded_file.name.endswith((".png", ".jpg", ".jpeg")):
            try:
                image = Image.open(uploaded_file)
                st.image(image, caption=f"🖼️ {uploaded_file.name}", use_container_width=True)

                with st.spinner("🔎 Analyse IA de l'image en cours..."):
                    # 🔵 Uploader l'image sur transfer.sh
                    img_bytes = io.BytesIO()
                    image.save(img_bytes, format="PNG")
                    img_bytes.seek(0)

                    image_url = upload_to_transfer_sh(uploaded_file.name, img_bytes.getvalue())

                    if not image_url:
                        st.error("❌ Impossible d'uploader l'image pour analyse IA.")
                        st.stop()

                    # 🔵 Appel à OpenAI avec image_url
                    vision_response = openai.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": "Analyse cette image : identifie si c'est un bâtiment individuel ou collectif, donne le nombre d'étages visibles, et propose une catégorie cadastrale."},
                                    {"type": "image_url", "image_url": {"url": image_url}}
                                ]
                            }
                        ],
                        temperature=0.2
                    )

                    result_text = vision_response.choices[0].message.content

                    st.subheader("📋 Résultat IA")
                    st.success(result_text)

            except Exception as e:
                st.error(f"❌ Erreur lors du traitement de l'image : {e}")

else:
    st.info("📂 Veuillez uploader un ou plusieurs fichiers pour commencer.")
