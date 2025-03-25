
FROM python:3.10-slim

# Création de dossier de travail
WORKDIR /app

# Copie des fichiers nécessaires 
COPY projet_total.py /app/projet_total.py
COPY visualisation_graph.py /app/visualisation_graph.py
COPY datapde /app/data

# Installation des dépendances
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Exécution du script principal
CMD ["python", "projet_total.py"]
