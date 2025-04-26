import os
import tempfile
import streamlit as st
import pandas as pd
from PIL import Image
import openai

# 📌 Configuration Streamlit (toujours en premier !)
st.set_page_config(page_title="📊 IA Cadastrale RAG", layout="wide")
st.title("📊 IA Cadastrale RAG - Analyse Immeubles et Catégorisation Décret 2010-439")

# 📂 Clé API OpenAI (venant de ton .env ou config Render)
openai.api_key = os.getenv("OPENAI_API_KEY")

# 📂 Upload du fichier
uploaded_file = st.file_uploader("📥 Charger un fichier Excel (.xlsx/.csv) ou une image (.png/.jpg)", type=["xlsx", "csv", "png", "jpg", "jpeg"])

if uploaded_file is not None:
    st.success("✅ Fichier chargé avec succès")

    if uploaded_file.name.endswith((".xlsx", ".csv")):
        try:
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)

            st.subheader("📄 Aperçu du fichier")
            st.dataframe(df)

        except Exception as e:
            st.error(f"❌ Erreur lors de la lecture du fichier : {e}")

    elif uploaded_file.name.endswith((".png", ".jpg", ".jpeg")):
        try:
            # 📂 Sauvegarder temporairement l'image uploadée
            temp_dir = tempfile.gettempdir()
            temp_path = os.path.join(temp_dir, uploaded_file.name)
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            # 📷 Afficher l'image
            image = Image.open(uploaded_file)
            st.image(image, caption="🖼️ Image chargée", use_column_width=True)

            # 📋 Demander à l'utilisateur une description rapide (facultatif mais utile pour contextualiser)
            description = st.text_area("✏️ Décrire brièvement l'image (ex: maison moderne, immeuble ancien, etc.)")

            if st.button("🔍 Lancer l'analyse IA"):
                with st.spinner("⏳ Analyse de l'image en cours avec OpenAI Vision..."):

                    with open(temp_path, "rb") as file:
                        response = openai.chat.completions.create(
                            model="gpt-4-vision-preview",
                            messages=[
                                {"role": "user", "content": [
                                    {"type": "text", "text": f"""Voici la description utilisateur : {description}.

À partir de l'image suivante :
- Décris le type de bâtiment : maison individuelle ou immeuble collectif.
- Estime le nombre de niveaux visibles.
- Classe la construction selon le décret 2010-439 :
    - Pour maisons individuelles ➔ Catégorie 1, 2, 3, etc.
    - Pour immeubles collectifs ➔ Catégorie A, B, C, etc.
- Donne une synthèse : état apparent, standing des matériaux, état d'entretien.
"""},
                                    {"type": "image_file", "image_file": {"file": file}},
                                ]}
                            ],
                            max_tokens=600,
                        )

                    # 📋 Résultats affichés
                    st.success("✅ Analyse terminée")
                    st.json(response.model_dump())

        except Exception as e:
            st.error(f"❌ Erreur OpenAI Vision : {e}")
