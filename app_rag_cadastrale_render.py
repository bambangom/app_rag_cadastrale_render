import streamlit as st
import pandas as pd
import openai
import os
from PIL import Image
import tempfile

# Configuration Streamlit
st.set_page_config(page_title="🏢 IA Cadastrale RAG : Analyse automatique des bâtiments", layout="wide")

# Clé API OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# Titre principal
st.title("🏢 IA Cadastrale RAG : Analyse automatique des bâtiments")

# Uploader fichiers
uploaded_files = st.file_uploader("📥 Uploader vos fichiers (Excel ou Images)", type=["xlsx", "csv", "png", "jpg", "jpeg"], accept_multiple_files=True)

if not uploaded_files:
    st.info("📂 Veuillez uploader un fichier pour commencer.")
else:
    for uploaded_file in uploaded_files:
        filename = uploaded_file.name
        st.success(f"📂 Fichier chargé : {filename}")

        # Si Excel
        if filename.endswith((".xlsx", ".csv")):
            if filename.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)

            st.subheader("📄 Aperçu du fichier Excel")
            st.dataframe(df)

        # Si Image
        elif filename.endswith((".png", ".jpg", ".jpeg")):
            try:
                # Tempfile pour créer un lien temporaire
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpfile:
                    tmpfile.write(uploaded_file.getvalue())
                    tmpfile_path = tmpfile.name

                image = Image.open(tmpfile_path)
                st.image(image, caption=f"🖼️ {filename}", use_column_width=True)

                # Création d'une URL locale pour OpenAI
                # (Nous allons simuler une url car en Render ce sera un problème sans vraie URL publique)
                st.warning("⚠️ Mode simulation : en local le modèle OpenAI Vision nécessite des URLs publiques. Sur Render réel, il faudra utiliser un CDN temporaire ou upload direct.")
                # On génère seulement la description basée sur le contenu binaire brut.

                with open(tmpfile_path, "rb") as image_file:
                    image_bytes = image_file.read()

                response = openai.chat.completions.create(
                    model="gpt-4-vision-preview",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": "Décris ce bâtiment en précisant : nombre d'étages, type (immeuble collectif ou maison individuelle), état apparent, matériaux visibles et niveau de standing. Sois concis et technique."},
                                {"type": "image", "image": {"data": image_bytes, "mime_type": "image/png"}}
                            ]
                        }
                    ],
                    max_tokens=800
                )

                # Résultat
                generated_description = response.choices[0].message.content
                st.success("✅ Analyse IA terminée :")
                st.markdown(generated_description)

            except Exception as e:
                st.error(f"❌ Erreur OpenAI Vision : {e}")

