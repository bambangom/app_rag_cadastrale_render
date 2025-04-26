import streamlit as st
import pandas as pd

st.set_page_config(page_title="Filtres Résultats - IA Cadastrale RAG", layout="wide")
st.title("🔍 Visualisation & Filtres des Résultats IA Cadastrale")

# 📥 Charger un fichier Excel corrigé
uploaded_file = st.file_uploader("📂 Charger le fichier d'analyse croisée (Excel)", type=["xlsx", "csv"])

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        st.success("✅ Fichier chargé avec succès")

        # 🎯 Choix des filtres
        st.sidebar.title("🧹 Filtres")

        types_disponibles = df["Type"].dropna().unique().tolist()
        type_selection = st.sidebar.multiselect("Type d'immeuble", options=types_disponibles, default=types_disponibles)

        categories_disponibles = df["Catégorie"].dropna().unique().tolist()
        categorie_selection = st.sidebar.multiselect("Catégorie fiscale", options=categories_disponibles, default=categories_disponibles)

        nombre_niveaux = df["Nombre d'étages"].dropna().unique().tolist()
        niveau_selection = st.sidebar.multiselect("Nombre d'étages", options=sorted(nombre_niveaux), default=nombre_niveaux)

        # 📊 Application des filtres
        df_filtre = df[
            (df["Type"].isin(type_selection)) &
            (df["Catégorie"].isin(categorie_selection)) &
            (df["Nombre d'étages"].isin(niveau_selection))
        ]

        st.subheader(f"📋 Résultats filtrés ({len(df_filtre)} enregistrements)")
        st.dataframe(df_filtre, use_container_width=True)

        # 📤 Exportation
        st.download_button(
            label="💾 Télécharger le fichier filtré (Excel)",
            data=df_filtre.to_excel(index=False, engine='openpyxl'),
            file_name="résultats_filtrés.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        st.error(f"Erreur lors de la lecture du fichier : {e}")

else:
    st.info("Veuillez charger un fichier pour commencer.")
