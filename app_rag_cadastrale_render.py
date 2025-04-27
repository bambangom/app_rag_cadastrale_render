# ===============================
# 📋 IA Cadastrale RAG - Application Principale
# ===============================

import streamlit as st
import pandas as pd
from PIL import Image
import openai
import base64
import os
import io

# 🛠️ Config Streamlit - Doit être tout en haut
st.set_page_config(page_title="📊 IA Cadastrale RAG", layout="wide")

# ===============================
# 🔑 Clé OpenAI via Variables d'environnement
# ===============================

openai_api_key = os.getenv("OPENAI_API_KEY")

if not openai_api_key:
    st.error("❌ Erreur : La clé OPENAI_API_KEY n'est pas définie dans les variables d'environnement.")
    st.stop()

# ✅ Initialisation Client OpenAI
client = openai.OpenAI(api_key=openai_api_key)

# ===============================
# 🎨 Titre principal
# ===============================

st.title("🏢 IA Cadastrale RAG : Analyse automatique 📸")
st.markdown("📥 **Uploader vos fichiers Excel (.xlsx, .csv) ou images (.png, .jpg, .jpeg)**")

# ===============================
# 📥 Upload fichiers (Excel ou Images)
# ===============================

uploaded_files = st.file_uploader(
    "Drag and drop files here",
    type=["xlsx", "csv", "png", "jpg", "jpeg"],
    accept_multiple_files=True
)

# 📂 Résultats collectés
results = []

if uploaded_files:
    for uploaded_file in uploaded_files:
        st.success(f"✅ Fichier chargé : {uploaded_file.name}")

        if uploaded_file.name.endswith((".xlsx", ".csv")):
            # 📄 Traitement Fichier Excel/CSV
            try:
                if uploaded_file.name.endswith(".csv"):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)
                
                st.subheader(f"📄 Aperçu du fichier : {uploaded_file.name}")
                st.dataframe(df)

            except Exception as e:
                st.error(f"❌ Erreur lors de la lecture du fichier : {e}")

        elif uploaded_file.name.endswith((".png", ".jpg", ".jpeg")):
            # 🖼️ Traitement Fichier Image
            try:
                image = Image.open(uploaded_file)
                st.image(image, caption=f"🖼️ Image : {uploaded_file.name}", use_container_width=True)

                # 📸 Analyse avec OpenAI Vision
                with st.spinner("🔍 Analyse IA de l'image en cours..."):

                    # Encode image en base64
                    buffered = io.BytesIO()
                    image.save(buffered, format="PNG")
                    img_base64 = base64.b64encode(buffered.getvalue()).decode()

                    # Appel API OpenAI Vision - GPT-4o
                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {
                                "role": "system",
                                "content": "Tu es un expert en évaluation cadastrale. À partir de l'image d'un bâtiment, donne :"
                                           "\n- Le type (Individuel ou Collectif)"
                                           "\n- Le nombre d'étages (RDC=0, R+1=1, etc.)"
                                           "\n- La catégorie cadastrale (1, 2, 3 pour individuel; A, B, C pour collectif)"
                                           "\n- Un bref commentaire de l'état visuel général."
                            },
                            {
                                "role": "user",
                                "content": [
                                    {
                                        "type": "text",
                                        "text": "Analyse cette image et donne moi les informations demandées."
                                    },
                                    {
                                        "type": "image",
                                        "image": {
                                            "base64": img_base64,
                                            "mime_type": "image/png"
                                        }
                                    }
                                ]
                            }
                        ],
                        max_tokens=500
                    )

                    # 🧠 Résultat de l'analyse
                    analysis_result = response.choices[0].message.content
                    st.success("✅ Analyse terminée")
                    st.text_area(f"📝 Résultat IA pour {uploaded_file.name}", analysis_result, height=200)

                    # 🔥 Sauvegarde dans résultats
                    results.append({
                        "Nom fichier": uploaded_file.name,
                        "Analyse IA": analysis_result
                    })

            except Exception as e:
                st.error(f"❌ Erreur OpenAI Vision : {e}")

# ===============================
# 📤 Sauvegarde résultats ?
# ===============================

if results:
    st.markdown("---")
    st.subheader("📥 Télécharger Résultats")

    df_results = pd.DataFrame(results)

    # 📥 Téléchargement Excel
    excel_output = io.BytesIO()
    with pd.ExcelWriter(excel_output, engine="xlsxwriter") as writer:
        df_results.to_excel(writer, index=False, sheet_name="Résultats")
    excel_output.seek(0)

    st.download_button(
        label="📥 Télécharger Résultats Excel",
        data=excel_output,
        file_name="resultats_ia_cadastrale.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# ===============================
# ✅ Fin
# ===============================
