import os
import base64
import requests
import pandas as pd
import streamlit as st
from PIL import Image
from io import BytesIO

# 📍 Config Streamlit
st.set_page_config(page_title="📊 IA Cadastrale RAG", layout="wide")
st.title("🏢 IA Cadastrale RAG : Analyse automatique")

# 🔑 Chargement clé API OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    st.error("❌ La clé API OpenAI n'est pas définie. Veuillez configurer OPENAI_API_KEY dans Render.")
    st.stop()

# 📂 Upload fichier Excel ou images
uploaded_files = st.file_uploader(
    "📥 Uploader vos fichiers (Excel ou Images)",
    type=["xlsx", "csv", "png", "jpg", "jpeg"],
    accept_multiple_files=True
)

if uploaded_files:
    for uploaded_file in uploaded_files:
        st.success(f"📂 Fichier chargé : {uploaded_file.name}")

    results = []

    for uploaded_file in uploaded_files:
        if uploaded_file.name.endswith((".xlsx", ".csv")):
            try:
                if uploaded_file.name.endswith(".csv"):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)
                st.subheader("📄 Aperçu du fichier")
                st.dataframe(df)
            except Exception as e:
                st.error(f"❌ Erreur lors de la lecture du fichier Excel : {e}")

        elif uploaded_file.name.endswith((".png", ".jpg", ".jpeg")):
            try:
                # 🖼️ Afficher l'image
                image = Image.open(uploaded_file)
                st.image(image, caption="🖼️ Image chargée", use_container_width=True)

                # 📸 Encodage Base64 de l'image
                buffered = BytesIO()
                image.save(buffered, format="PNG")
                img_base64 = base64.b64encode(buffered.getvalue()).decode()

                # 🔥 Appel API OpenAI GPT-4o
                url = "https://api.openai.com/v1/chat/completions"
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
                                {"type": "text", "text": 
                                 """Analyse l'image pour :
                                 - Identifier si c'est une maison individuelle ou un immeuble collectif
                                 - Estimer le nombre d'étages visibles
                                 - Déterminer la catégorie fiscale probable selon le décret 2010 :
                                   * Maison individuelle : Catégories 1, 2, 3, etc.
                                   * Immeuble collectif : Catégories A, B, C, etc.
                                 Donne ta réponse sous forme d'un JSON compact avec les clés suivantes :
                                 {"type": "...", "nombre_etages": "...", "categorie": "...", "commentaire": "..."}
                                 """},
                                {"type": "image", "image": f"data:image/png;base64,{img_base64}"}
                            ]
                        }
                    ],
                    "temperature": 0.2,
                    "max_tokens": 1000
                }

                response = requests.post(url, headers=headers, json=payload)

                if response.status_code == 200:
                    result = response.json()
                    message = result['choices'][0]['message']['content']
                    st.info(f"🔍 Analyse IA : {message}")
                    results.append(message)
                else:
                    st.error(f"❌ Erreur OpenAI Vision : {response.status_code} - {response.json()}")

            except Exception as e:
                st.error(f"❌ Erreur d'analyse : {e}")

    if results:
        st.success("✅ Toutes les analyses terminées !")
        st.download_button("📥 Télécharger résultats en texte", "\n\n".join(results), file_name="analyse_cadastrale.txt")

else:
    st.info("📥 Merci de charger un fichier Excel ou des images pour démarrer l'analyse.")

