import streamlit as st
import pandas as pd
import openai
import base64
import os
from PIL import Image
from io import BytesIO

# 📌 Configuration de la page
st.set_page_config(page_title="📊 IA Cadastrale RAG", layout="wide")
st.title("🏢 IA Cadastrale RAG - Analyse Automatique d'Images")

# 📌 Clé API OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# 📂 Upload multiple d'images
uploaded_files = st.file_uploader("📥 Charger une ou plusieurs images", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

# 📋 DataFrame pour enregistrer les résultats
results = []

def analyser_image_vision(file_bytes):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                "Analyse l'image et donne :\n"
                                "- Type d'immeuble : 'Individuel' ou 'Collectif'\n"
                                "- Nombre d'étages (RDC=0, R+1=1, R+2=2, etc.)\n"
                                "- Catégorie cadastrale : pour 'Individuel' choisis parmi [1,2,3,4] ; pour 'Collectif' choisis parmi [A,B,C,D]\n"
                                "- Une observation rapide sur le standing et l'état du bâtiment\n"
                                "Sois concis, professionnel et structuré."
                            )
                        },
                        {
                            "type": "image",
                            "image": {
                                "data": base64.b64encode(file_bytes).decode('utf-8')
                            }
                        }
                    ]
                }
            ],
            max_tokens=1000,
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        return f"❌ Erreur OpenAI Vision : {str(e)}"

# 📊 Traitement des images uploadées
if uploaded_files:
    st.success(f"✅ {len(uploaded_files)} image(s) chargée(s)")

    for uploaded_file in uploaded_files:
        try:
            # Lire l'image
            image_bytes = uploaded_file.read()
            image = Image.open(BytesIO(image_bytes))
            
            # Afficher l'image
            st.image(image, caption=uploaded_file.name, use_column_width=True)

            # 📤 Envoyer à OpenAI Vision pour analyse
            st.info(f"🔎 Analyse IA de : {uploaded_file.name} ...")
            result_text = analyser_image_vision(image_bytes)

            # Afficher le résultat brut
            st.code(result_text, language='markdown')

            # Sauvegarder pour DataFrame
            results.append({
                "Nom du fichier": uploaded_file.name,
                "Analyse IA": result_text
            })

        except Exception as e:
            st.error(f"Erreur lors du traitement de l'image {uploaded_file.name} : {e}")

# 📥 Télécharger les résultats
if results:
    df_results = pd.DataFrame(results)
    st.subheader("📄 Résultats complets")
    st.dataframe(df_results)

    st.download_button(
        label="📥 Télécharger les résultats en CSV",
        data=df_results.to_csv(index=False).encode('utf-8'),
        file_name="resultats_analyse_cadastrale.csv",
        mime="text/csv"
    )
