import streamlit as st
import pandas as pd
from PIL import Image

st.set_page_config(page_title="IA Cadastrale RAG", layout="wide")
st.title("📊 IA Cadastrale RAG")

# 📂 Upload de fichier
uploaded_file = st.file_uploader("📥 Charger un fichier Excel ou une image", type=["xlsx", "csv", "png", "jpg", "jpeg"])

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
            st.error(f"Erreur lors de la lecture du fichier : {e}")

    elif uploaded_file.name.endswith((".png", ".jpg", ".jpeg")):
        try:
            image = Image.open(uploaded_file)
            st.image(image, caption="🖼️ Image chargée", use_column_width=True)
        except Exception as e:
            st.error(f"Erreur lors de l'affichage de l'image : {e}")

