# Utiliser une image officielle Python optimisée
FROM python:3.11-slim

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers nécessaires
COPY requirements.txt .
COPY app_rag_cadastrale_render.py .
COPY decret_2010_rag_docs.md .
COPY export/ export/
COPY generer_fiches_pdf.py .
COPY nocodb/ nocodb/
COPY pwa/ pwa/
COPY ui/ ui/

# Installer les dépendances Python
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Exposer le port utilisé par Streamlit
EXPOSE 8501

# Commande pour lancer Streamlit automatiquement
CMD ["streamlit", "run", "app_rag_cadastrale_render.py", "--server.port=8501", "--server.address=0.0.0.0"]
