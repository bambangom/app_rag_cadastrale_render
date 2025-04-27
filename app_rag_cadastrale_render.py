import streamlit as st
import openai
import pandas as pd
import base64
import os
import json
from PIL import Image
from io import BytesIO

# 🚀 Configuration de la page
st.set_page_config(page_title="📸 IA Cadastrale RAG", layout="wide")

# 📥 Clé API depuis Variables Render
openai.api_key = os.getenv("OPENAI_API_KEY")

# 📈 Fonction d'analyse d'une image
def analyse_image_bytes(image_bytes, modele="gpt-4o"):
    try:
        encoded_image = base64.b64encode(image_bytes).decode('utf-8')
        
        response = openai.chat.completions.create(
            model=modele,
            messages=[
                {"role": "system", "content": "Tu es un expert en évaluation cadastrale. À partir d'une photo d'un bâtiment, tu dois : déterminer le nombre de niveaux (RDC=0, R+1=1, R+2=2, etc.), dire si c'est un immeuble individuel ou collectif, et donner sa catégorie fiscale selon le décret 2010-439 : (A, B, C pour collectif ; 1, 2, 3 pour individuel). Donne aussi une brève description du bâtiment."},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Analyse et réponds en JSON : {'niveaux': ?, 'type_immeuble': 'individuel/collectif', 'categorie': 'A/B/C ou 1/2/3', 'description': '...'}"},
                        {
                            "type": "image_url",
                            "image_url": f"data:image/jpeg;base64,{encoded_image}"
                        },
                    ],
                },
            ],
            temperature=0,
        )
        return response.choices[0].message.content

    except Exception as e:
        st.error(f"❌ Erreur OpenAI Vision : {e}")
        return None

# 📂 Analyse de plusieurs fichiers
def traiter_images(uploaded_files):
    resultats = []

    for uploaded_file in uploaded_files:
        image_bytes = uploaded_file.read()
        analyse = analyse_image_bytes(image_bytes)
        if analyse:
            try:
                analyse_clean = analyse.split("{", 1)[1].rsplit("}", 1)[0]
                analyse_json = json.loads("{" + analyse_clean + "}")

                resultats.append({
                    "NICAD": uploaded_file.name.replace('.png', '').replace('.jpg', '').replace('.jpeg', ''),
                    "Type d'immeuble": analyse_json.get("type_immeuble", "Non précisé"),
                    "Catégorie": analyse_json.get("categorie", "Non précisé"),
                    "Niveaux": analyse_json.get("niveaux", "Non précisé"),
                    "Description": analyse_json.get("description", "Non précisé"),
                })

            except Exception as e:
                st.warning(f"⚠️ Problème de parsing pour {uploaded_file.name} : {e}")

    return resultats

# 🖼️ Interface Utilisateur
st.title("🏢 IA Cadastrale RAG : Analyse Automatique des Immeubles")

uploaded_files = st.file_uploader("📥 Charger vos images (PNG, JPG, JPEG)", accept_multiple_files=True, type=["png", "jpg", "jpeg"])

if uploaded_files:
    st.success(f"✅ {len(uploaded_files)} image(s) chargée(s)")
    if st.button("🔎 Lancer l'analyse"):
        with st.spinner("Analyse en cours..."):
            resultats = traiter_images(uploaded_files)

            if resultats:
                df = pd.DataFrame(resultats)
                st.dataframe(df)

                # 📥 Télécharger résultats
                excel_path = "/tmp/analyse_cadastrale_finale.xlsx"
                df.to_excel(excel_path, index=False)

                with open(excel_path, "rb") as f:
                    st.download_button(
                        "📥 Télécharger le fichier Excel",
                        data=f,
                        file_name="analyse_cadastrale_finale.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
            else:
                st.error("❌ Aucun résultat exploitable.")
