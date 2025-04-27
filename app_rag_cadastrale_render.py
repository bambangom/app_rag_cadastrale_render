import streamlit as st
import pandas as pd
from PIL import Image
import openai
import os

# Configuration de la page
st.set_page_config(page_title="🏢 IA Cadastrale RAG : Analyse automatique des bâtiments", layout="wide")
st.title("🏢 IA Cadastrale RAG : Analyse automatique des bâtiments")

# Récupérer la clé OpenAI
openai_api_key = os.getenv("OPENAI_API_KEY")

if not openai_api_key:
    st.error("❌ Clé OpenAI non trouvée. Veuillez configurer la variable d'environnement OPENAI_API_KEY.")
    st.stop()

openai.api_key = openai_api_key

# Uploader le fichier
uploaded_files = st.file_uploader("📥 Uploader vos fichiers (Excel ou Images)", type=["xlsx", "csv", "png", "jpg", "jpeg"], accept_multiple_files=True)

if uploaded_files:
    for uploaded_file in uploaded_files:
        st.success(f"📂 Fichier chargé : {uploaded_file.name}")

        if uploaded_file.name.endswith((".png", ".jpg", ".jpeg")):
            try:
                img = Image.open(uploaded_file)
                st.image(img, caption=uploaded_file.name, use_column_width=True)

                # Préparer l'upload sur OpenAI pour obtenir un file_id
                uploaded_file.seek(0)
                file_response = openai.files.create(file=uploaded_file, purpose="vision")
                file_id = file_response.id

                with st.spinner("🔎 Analyse IA en cours..."):
                    completion = openai.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": (
                                        "Analyse l'image pour :\n"
                                        "- Déterminer si c'est un bâtiment individuel ou collectif.\n"
                                        "- Compter le nombre d'étages visibles.\n"
                                        "- Proposer une catégorie cadastrale selon décret 2010-439 et 2014.\n"
                                        "- Rédiger un résumé clair pour usage cadastral."
                                    )},
                                    {"type": "file", "file": {"file_id": file_id}}
                                ]
                            }
                        ],
                        temperature=0.2
                    )

                    result = completion.choices[0].message.content
                    st.success("✅ Analyse IA terminée :")
                    st.markdown(result)

            except Exception as e:
                st.error(f"❌ Erreur lors du traitement de l'image : {e}")

        elif uploaded_file.name.endswith((".xlsx", ".csv")):
            try:
                if uploaded_file.name.endswith(".csv"):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)

                st.subheader("📄 Aperçu du fichier")
                st.dataframe(df)

            except Exception as e:
                st.error(f"❌ Erreur lors de la lecture du fichier Excel/CSV : {e}")

else:
    st.info("📂 Veuillez uploader un fichier pour commencer.")
