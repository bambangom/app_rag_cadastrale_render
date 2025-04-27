import streamlit as st
import pandas as pd
import openai
from PIL import Image
from io import BytesIO

# ✅ Configuration de la page Streamlit
st.set_page_config(page_title="📊 IA Cadastrale RAG", layout="wide")
st.title("🏢 IA Cadastrale RAG : Analyse automatique")

# 🔑 Clé API OpenAI depuis .env ou variables Render
openai.api_key = st.secrets.get("OPENAI_API_KEY") or st.text_input("🔑 Entrez votre clé OpenAI ici :", type="password")

# 📂 Chargement de fichier(s)
uploaded_files = st.file_uploader("📥 Uploader vos fichiers (Excel ou Images)", type=["xlsx", "csv", "png", "jpg", "jpeg"], accept_multiple_files=True)

# 🚀 Fonction d'analyse via OpenAI Vision
def analyse_image_openai(file_bytes):
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": 
                            "Tu es un expert en fiscalité cadastrale au Sénégal. "
                            "Analyse cette image pour déterminer :\n"
                            "- Type du bâtiment : Individuel ou Collectif\n"
                            "- Nombre d'étages visibles : (RDC = 0, R+1 = 1, etc.)\n"
                            "- Catégorie cadastrale applicable selon le Décret 2010 (ex: 1,2,3 pour Individuel ; A,B,C pour Collectif)\n"
                            "- Ajoute si possible une remarque sur l’état (neuf, dégradé, standing).\n"
                            "Réponds sous forme JSON structuré."
                        },
                        {"type": "file", "file": file_bytes}
                    ]
                }
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"❌ Erreur OpenAI Vision : {e}")
        return None

# 📊 Traitement des fichiers
if uploaded_files:
    for uploaded_file in uploaded_files:
        file_name = uploaded_file.name
        st.info(f"📂 Fichier chargé : {file_name}")

        # Traitement Excel ou CSV
        if file_name.endswith((".xlsx", ".csv")):
            try:
                if file_name.endswith(".csv"):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)
                st.subheader("📄 Aperçu du fichier")
                st.dataframe(df)
            except Exception as e:
                st.error(f"❌ Erreur lors de la lecture du fichier : {e}")

        # Traitement Images
        elif file_name.endswith((".png", ".jpg", ".jpeg")):
            try:
                file_bytes = uploaded_file.getvalue()

                # 📸 Affichage de l'image
                st.image(file_bytes, caption=f"🖼️ Aperçu : {file_name}", use_container_width=True)

                # 🔍 Analyse IA OpenAI
                result = analyse_image_openai(file_bytes)
                if result:
                    st.success("✅ Résultat IA :")
                    st.json(result)

            except Exception as e:
                st.error(f"❌ Erreur lors du traitement de l'image : {e}")

else:
    st.warning("🚨 Merci de charger au moins un fichier pour démarrer l'analyse.")

