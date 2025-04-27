import streamlit as st
import pandas as pd
import requests
import openai
import os
from PIL import Image
import tempfile

# 📋 Configuration de la page
st.set_page_config(page_title="📊 IA Cadastrale RAG : Analyse automatique des bâtiments", layout="wide")
st.title("🏢 IA Cadastrale RAG : Analyse automatique des bâtiments")

# 🔑 Configuration OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# 🛠️ Fonction pour uploader un fichier vers Transfer.sh
def upload_to_transfersh(file_path):
    with open(file_path, 'rb') as f:
        files = {'file': (os.path.basename(file_path), f)}
        response = requests.post('https://transfer.sh/', files=files)
        if response.status_code == 200:
            return response.text.strip()
        else:
            return None

# 🧠 Fonction d'analyse avec OpenAI Vision
def analyse_image_openai(image_url):
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Analyse cette image d'un bâtiment pour déterminer :\n"
                                                  "- Le type : Individuel ou Collectif\n"
                                                  "- Le nombre d'étages (RDC=0, R+1=1...)\n"
                                                  "- La catégorie fiscale selon le décret cadastral 2010\n"
                                                  "Donne une réponse courte, sous forme de tableau lisible."},
                        {"type": "image_url", "image_url": image_url}
                    ]
                }
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"❌ Erreur OpenAI Vision : {e}")
        return None

# 📤 Uploader les fichiers
uploaded_files = st.file_uploader("📥 Uploader vos fichiers (Excel ou Images)", type=["xlsx", "csv", "png", "jpg", "jpeg"], accept_multiple_files=True)

if uploaded_files:
    for uploaded_file in uploaded_files:
        file_name = uploaded_file.name
        st.success(f"📂 Fichier chargé : {file_name}")

        # 📄 Si Excel ou CSV
        if file_name.endswith((".xlsx", ".csv")):
            try:
                if file_name.endswith(".csv"):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)
                st.subheader("🗂️ Aperçu du fichier :")
                st.dataframe(df, use_container_width=True)
            except Exception as e:
                st.error(f"❌ Erreur de lecture du fichier : {e}")

        # 🖼️ Si Image
        elif file_name.endswith((".png", ".jpg", ".jpeg")):
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
                    tmp_file.write(uploaded_file.read())
                    tmp_path = tmp_file.name

                st.image(tmp_path, caption=f"🖼️ Aperçu de : {file_name}", use_column_width=True)

                # 🚀 Uploader vers Transfer.sh
                image_url = upload_to_transfersh(tmp_path)
                if image_url:
                    st.info(f"🌐 Image URL temporaire générée : {image_url}")

                    # 🔍 Analyse IA OpenAI
                    result = analyse_image_openai(image_url)
                    if result:
                        st.success("✅ Analyse IA terminée :")
                        st.markdown(result)
                else:
                    st.error("❌ Échec de l'upload sur Transfer.sh. Impossible d'analyser l'image.")

            except Exception as e:
                st.error(f"❌ Erreur lors du traitement de l'image : {e}")

else:
    st.info("📩 Veuillez uploader un fichier pour commencer.")
