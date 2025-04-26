# 📄 app_rag_cadastrale_render.py

import pandas as pd
from PIL import Image
import openai
import io
import os
import streamlit as st

st.set_page_config(
    page_title="IA Cadastrale RAG",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ⚡ Correction spéciale Render
st.write("")  # force render à générer les fichiers statiques correctement

# 📌 Configuration de la page
st.set_page_config(page_title="📊 IA Cadastrale RAG", layout="wide")
st.title("📊 IA Cadastrale RAG - Assistant Intelligent")

# 📌 Clé API OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# 📌 Fonction d'analyse d'image avec OpenAI GPT-4 Vision
def analyze_image_with_openai(image_bytes):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Décris précisément ce bâtiment : type (individuel ou collectif), matériaux visibles, standing (prestige, ordinaire, économique, dégradé), nombre d'étages visibles."},
                        {"type": "image", "image": {"data": image_bytes}}
                    ]
                }
            ],
            max_tokens=500
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        return f"Erreur OpenAI : {e}"

# 📌 Fonction de détermination de la catégorie cadastrale
def determine_category_from_analysis(analysis_text):
    if "individuel" in analysis_text.lower():
        if "prestige" in analysis_text.lower():
            return "1"
        elif "ordinaire" in analysis_text.lower():
            return "2"
        elif "économique" in analysis_text.lower():
            return "3"
        elif "dégradé" in analysis_text.lower():
            return "4"
        else:
            return "Non déterminé (individuel)"
    elif "collectif" in analysis_text.lower():
        if "prestige" in analysis_text.lower():
            return "A"
        elif "ordinaire" in analysis_text.lower():
            return "B"
        elif "économique" in analysis_text.lower():
            return "C"
        elif "dégradé" in analysis_text.lower():
            return "D"
        else:
            return "Non déterminé (collectif)"
    else:
        return "Non déterminé (type inconnu)"

# 📂 Uploader pour charger plusieurs images
uploaded_files = st.file_uploader(
    "📥 Charger une ou plusieurs images de bâtiments (.png, .jpg, .jpeg)", 
    type=["png", "jpg", "jpeg"], 
    accept_multiple_files=True
)

# 📋 Traitement des fichiers uploadés
if uploaded_files:
    results = []

    for uploaded_file in uploaded_files:
        # 🖼️ Afficher l'image
        image = Image.open(uploaded_file)
        st.image(image, caption=f"🖼️ {uploaded_file.name}", use_column_width=True)

        # 🧠 Appel OpenAI pour analyse
        with st.spinner(f"Analyse de {uploaded_file.name} avec OpenAI..."):
            image_bytes = io.BytesIO()
            image.save(image_bytes, format='PNG')
            image_bytes = image_bytes.getvalue()

            description = analyze_image_with_openai(image_bytes)
            category = determine_category_from_analysis(description)

        # ✅ Résultats individuels
        st.success("✅ Analyse terminée")
        st.write(f"**Description générée :** {description}")
        st.write(f"**Catégorie cadastrale proposée :** {category}")

        results.append({
            "Nom du fichier": uploaded_file.name,
            "Description OpenAI": description,
            "Catégorie cadastrale": category
        })

    # 📊 Consolidation des résultats
    if results:
        st.subheader("📋 Résultats Consolidés")
        df_results = pd.DataFrame(results)
        st.dataframe(df_results)

        # 💾 Exportation Excel
        if st.button("💾 Exporter les résultats vers Excel"):
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df_results.to_excel(writer, index=False, sheet_name="Résultats Cadastraux")
            st.download_button(
                label="📥 Télécharger le fichier Excel",
                data=buffer.getvalue(),
                file_name="resultats_ia_cadastrale.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
else:
    st.info("📂 Veuillez charger une ou plusieurs images de bâtiments pour démarrer l'analyse.")

