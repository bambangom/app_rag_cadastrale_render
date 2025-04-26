# 📦 Importations
import streamlit as st
import pandas as pd
from PIL import Image
import io
import base64
from openai import OpenAI

# ⚙️ Configuration Streamlit
st.set_page_config(page_title="📊 IA Cadastrale RAG", layout="wide")
st.title("🏢 IA Cadastrale RAG : Analyse automatique des bâtiments")

# 🔑 Connexion à l'API OpenAI (clé doit être dans les variables d'environnement de Render)
client = OpenAI()

# 📥 Uploader plusieurs fichiers (images ou Excel)
uploaded_files = st.file_uploader(
    "📥 Uploader vos fichiers (Excel ou Images)",
    type=["xlsx", "csv", "png", "jpg", "jpeg"],
    accept_multiple_files=True
)

if uploaded_files:
    for uploaded_file in uploaded_files:
        st.markdown(f"### 📂 Fichier chargé : `{uploaded_file.name}`")

        if uploaded_file.name.endswith((".png", ".jpg", ".jpeg")):
            try:
                image = Image.open(uploaded_file)
                st.image(image, caption=f"🖼️ Aperçu de {uploaded_file.name}", use_column_width=True)

                st.info("📡 Envoi de l'image au modèle GPT-4 Vision pour analyse...")

                # Encodage de l'image en base64
                buffered = io.BytesIO()
                image.save(buffered, format="PNG")
                img_bytes = buffered.getvalue()
                encoded_image = base64.b64encode(img_bytes).decode()

                # Requête vers OpenAI Vision
                response = client.chat.completions.create(
                    model="gpt-4-vision-preview",
                    messages=[
                        {
                            "role": "system",
                            "content": "Tu es un expert en évaluation cadastrale au Sénégal. Ta mission est :\
                                1. Détecter le type du bâtiment (Individuel ou Collectif)\
                                2. Estimer le nombre d'étages (RDC, R+1, R+2, etc.)\
                                3. Proposer une catégorie fiscale basée sur l'état du bâtiment selon les décrets sénégalais de 2010 et 2014."
                        },
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": "Analyse cette image selon ton expertise cadastrale."
                                },
                                {
                                    "type": "image",
                                    "image": {"base64": encoded_image}
                                }
                            ]
                        }
                    ],
                    temperature=0.2,
                    max_tokens=1000
                )

                # Résultat IA
                ia_result = response.choices[0].message.content
                st.success("✅ Analyse IA terminée")
                st.markdown("### 🔎 Résultat de l'analyse IA :")
                st.markdown(ia_result)

            except Exception as e:
                st.error(f"❌ Erreur OpenAI Vision : {str(e)}")

        elif uploaded_file.name.endswith((".xlsx", ".csv")):
            try:
                st.info("📊 Lecture du fichier Excel...")
                if uploaded_file.name.endswith(".csv"):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)

                st.success("✅ Fichier chargé avec succès")
                st.dataframe(df)

            except Exception as e:
                st.error(f"❌ Erreur lors de la lecture du fichier : {str(e)}")

else:
    st.info("📥 Veuillez uploader un fichier pour commencer.")

