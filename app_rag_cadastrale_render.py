import os
import base64
import requests
import streamlit as st
import pandas as pd
from PIL import Image
from io import BytesIO

# ⚙️ CONFIG
st.set_page_config(page_title="📊 IA Cadastrale RAG", layout="wide")
st.title("🏢 IA Cadastrale RAG : Analyse automatique")

# 🛡️ Sécurité
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# 📥 UPLOADER
uploaded_files = st.file_uploader(
    "📥 Uploader vos fichiers (Excel ou Images)",
    type=["xlsx", "csv", "png", "jpg", "jpeg"],
    accept_multiple_files=True
)

# 📊 Préparation résultat
results = []

# 📜 Définition de la fonction d'analyse d'images via OpenAI Vision
def analyze_image_with_openai(image_file, image_name):
    if not OPENAI_API_KEY:
        st.error("🔑 Clé API OpenAI manquante. Vérifiez votre environnement.")
        return None

    try:
        image_bytes = image_file.read()
        encoded_image = base64.b64encode(image_bytes).decode('utf-8')

        url = "https://api.openai.com/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "gpt-4-vision-preview",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Analyse cette image de bâtiment. Donne-moi uniquement : \n- Le type (Individuel ou Collectif)\n- Le nombre d'étages (RDC = 0, R+1 = 1, etc.)\n- La catégorie fiscale (si Individuel : 1,2,3... ; si Collectif : A,B,C...) selon les critères du décret 2010-439."},
                        {"type": "image", "image": {"base64": encoded_image}}
                    ]
                }
            ],
            "max_tokens": 1000
        }

        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()

        data = response.json()
        content = data["choices"][0]["message"]["content"]

        st.success(f"✅ Analyse IA terminée pour : {image_name}")
        return content

    except Exception as e:
        st.error(f"❌ Erreur OpenAI Vision : {e}")
        return None

# 🚀 TRAITEMENT DES FICHIERS UPLOADÉS
if uploaded_files:
    for uploaded_file in uploaded_files:
        filename = uploaded_file.name
        st.markdown(f"📂 **Fichier chargé : {filename}**")

        if filename.endswith((".png", ".jpg", ".jpeg")):
            # Image
            image = Image.open(uploaded_file)
            st.image(image, caption=f"🖼️ Aperçu : {filename}", use_column_width=True)

            uploaded_file.seek(0)  # Revenir au début du fichier
            result = analyze_image_with_openai(uploaded_file, filename)

            if result:
                results.append({
                    "Nom fichier": filename,
                    "Analyse IA": result
                })

        elif filename.endswith((".xlsx", ".csv")):
            # Excel ou CSV
            try:
                if filename.endswith(".csv"):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)

                st.subheader(f"📄 Aperçu du fichier : {filename}")
                st.dataframe(df)

            except Exception as e:
                st.error(f"❌ Erreur lecture fichier : {e}")

# 📊 Résultats finaux
if results:
    st.subheader("📋 Résultats d'analyse")
    result_df = pd.DataFrame(results)
    st.dataframe(result_df, use_container_width=True)

    # 📥 Bouton de téléchargement Excel
    to_download = result_df.to_excel(index=False)
    st.download_button("📥 Télécharger Résultats Excel", to_download, file_name="resultats_ia_cadastrale.xlsx")

    # 🌐 Option d'envoi vers NocoDB (TODO en option selon besoin)
