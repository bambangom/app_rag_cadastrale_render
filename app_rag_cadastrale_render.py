import streamlit as st
import pandas as pd
from PIL import Image
import base64
from openai import OpenAI

# 📌 Initialisation du client OpenAI
client = OpenAI()

# 📄 Configuration de la page
st.set_page_config(page_title="📊 IA Cadastrale RAG", layout="wide")

# 🏷️ Titre
st.title("📊 IA Cadastrale RAG")

# 📂 Upload de fichiers
uploaded_files = st.file_uploader("📥 Charger un ou plusieurs fichiers Excel ou images", type=["xlsx", "csv", "png", "jpg", "jpeg"], accept_multiple_files=True)

# 🔥 Fonction pour encoder en base64 pour GPT-4 Vision
def image_to_base64(image_file):
    return base64.b64encode(image_file.read()).decode('utf-8')

# 🔥 Fonction pour analyser une image via OpenAI GPT-4 Vision
def analyser_image_openai(base64_image):
    try:
        response = client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": """Décris précisément :
- Le type d'immeuble (Individuel ou Collectif).
- Le nombre de niveaux visibles (RDC = 0, R+1 = 1 étage, etc.).
- La catégorie cadastrale selon le décret sénégalais (Maison individuelle : Catégorie 1,2,3... / Immeuble collectif : Catégorie A,B,C,D...).

Réponds en JSON strict : {"type": "...", "nombre_etages": "...", "categorie": "..."}"""},
                        {
                            "type": "image",
                            "image": {
                                "base64": base64_image
                            }
                        }
                    ]
                }
            ],
            max_tokens=500
        )
        result = response.choices[0].message.content
        return result
    except Exception as e:
        return f"❌ Erreur OpenAI Vision : {str(e)}"

# 📄 Traitement des fichiers
if uploaded_files:
    for uploaded_file in uploaded_files:
        st.success(f"✅ Fichier chargé : {uploaded_file.name}")

        if uploaded_file.name.endswith((".xlsx", ".csv")):
            try:
                if uploaded_file.name.endswith(".csv"):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)
                st.subheader(f"📄 Aperçu de {uploaded_file.name}")
                st.dataframe(df)
            except Exception as e:
                st.error(f"Erreur lecture du fichier : {e}")

        elif uploaded_file.name.endswith((".png", ".jpg", ".jpeg")):
            try:
                image = Image.open(uploaded_file)
                st.image(image, caption=f"🖼️ {uploaded_file.name}", use_column_width=True)

                # 🔥 Correction ici : encodage base64
                base64_image = image_to_base64(uploaded_file)

                with st.spinner("🔎 Analyse IA en cours..."):
                    resultat = analyser_image_openai(base64_image)

                st.subheader("📊 Résultat IA")
                st.code(resultat, language="json")

            except Exception as e:
                st.error(f"Erreur analyse image : {e}")

else:
    st.info("📂 Veuillez charger au moins un fichier pour commencer l'analyse.")

