import sqlite3
import pandas as pd
import os
import requests
import time
import subprocess

# Configuration des chemins
DB_PATH = "/app/data/analyses.db"
CSV_FOLDER = "/app/data"

# URLs des fichiers à télécharger
urls = {
    "magasins.csv": "https://docs.google.com/spreadsheets/d/e/2PACX-1vSawI56WBC64foMT9pKCiY594fBZk9Lyj8_bxfgmq-8ck_jw1Z49qDeMatCWqBxehEVoM6U1zdYx73V/pub?gid=0&single=true&output=csv",
    "produits.csv": "https://docs.google.com/spreadsheets/d/e/2PACX-1vSawI56WBC64foMT9pKCiY594fBZk9Lyj8_bxfgmq-8ck_jw1Z49qDeMatCWqBxehEVoM6U1zdYx73V/pub?gid=714623615&single=true&output=csv",
    "ventes.csv": "https://docs.google.com/spreadsheets/d/e/2PACX-1vSawI56WBC64foMT9pKCiY594fBZk9Lyj8_bxfgmq-8ck_jw1Z49qDeMatCWqBxehEVoM6U1zdYx73V/pub?gid=760830694&single=true&output=csv"
}

def robust_read_csv(path):
    try:
        return pd.read_csv(path, encoding="utf-8")
    except Exception:
        return pd.read_csv(path, encoding="ISO-8859-1")

# Fonction de téléchargement
def download_csv(url, filename):
    path = os.path.join(CSV_FOLDER, filename)
    if os.path.exists(path):
        print(f"Le fichier existe déjà : {filename}, téléchargement ignoré.")
        return
    try:
        response = requests.get(url)
        response.raise_for_status()
        with open(path, 'wb') as f:
            f.write(response.content)
        print(f"Téléchargement terminé: {filename}")
    except requests.RequestException as e:
        print(f"Erreur lors du téléchargement de {filename}: {e}")

# Télécharger les fichiers
for fname, url in urls.items():
    download_csv(url, fname)

# Connexion à la base de données SQLite
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Création des tables
cursor.executescript("""
DROP TABLE IF EXISTS magasins;
DROP TABLE IF EXISTS produits;
DROP TABLE IF EXISTS ventes;
DROP TABLE IF EXISTS data_global;
DROP TABLE IF EXISTS analyses;

CREATE TABLE magasins (
    "Nom" TEXT,
    "ID Référence produit" TEXT PRIMARY KEY,
    "Prix" REAL,
    "Stock" INTEGER
);

CREATE TABLE produits (
    "Date" TEXT,
    "ID Référence produit" TEXT,
    "Quantité" INTEGER,
    "ID Magasin" INTEGER
);

CREATE TABLE ventes (
    "ID Magasin" INTEGER PRIMARY KEY,
    "Ville" TEXT,
    "Nombre de salariés" INTEGER
);

CREATE TABLE data_global (
    "Date" TEXT,
    "ID Référence produit" TEXT,
    "Quantité" INTEGER,
    "ID Magasin" INTEGER,
    "Nom" TEXT,
    "Prix" REAL,
    "Stock" INTEGER,
    "Ville" TEXT,
    "Nombre de salariés" INTEGER,
    "Chiffre d'affaires" REAL
);

CREATE TABLE analyses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT,
    valeur TEXT
);
""")

# # Pause pour permettre la vérification des tables vides - Presentation VIDEO
print("Pause de 40 secondes pour inspection des tables vides dans la base de données")
time.sleep(40)

# Chargement des fichiers CSV dans les tables
def load_csv_to_db(table_name, filename):
    path = os.path.join(CSV_FOLDER, filename)
    if not os.path.exists(path):
        print(f"Fichier introuvable : {filename}")
        return
    df = robust_read_csv(path)
    df.columns = [col.strip() for col in df.columns]

    if table_name == "produits":
        existing = pd.read_sql("SELECT Date, [ID Référence produit], Quantité, [ID Magasin] FROM produits", conn)
        df = df.merge(existing, on=["Date", "ID Référence produit", "Quantité", "ID Magasin"], how="left", indicator=True)
        df = df[df['_merge'] == 'left_only'].drop(columns=['_merge'])
        if df.empty:
            print("Aucune nouvelle ligne à insérer dans produits.csv")
            return
    elif table_name == "magasins":
        existing = pd.read_sql("SELECT DISTINCT TRIM([ID Référence produit]) AS id FROM magasins", conn)
        df["ID Référence produit"] = df["ID Référence produit"].astype(str).str.strip()
        df = df[~df["ID Référence produit"].isin(existing["id"])]
        if df.empty:
            print("Aucun nouveau produit à insérer dans magasins.csv")
            return
    elif table_name == "ventes":
        existing = pd.read_sql("SELECT [ID Magasin] FROM ventes", conn)
        df = df[~df["ID Magasin"].isin(existing["ID Magasin"])]
        if df.empty:
            print("Aucun nouveau magasin à insérer dans ventes.csv")
            return

    df.to_sql(table_name, conn, if_exists="append", index=False)
    print(f"Chargement terminé: {filename} → {table_name}")

load_csv_to_db("magasins", "magasins.csv")
load_csv_to_db("produits", "produits.csv")
load_csv_to_db("ventes", "ventes.csv")

# Fusion des données dans data_global
df_prod = pd.read_sql("SELECT * FROM produits", conn)
df_mag = pd.read_sql("SELECT * FROM magasins", conn)
df_mag["ID Référence produit"] = df_mag["ID Référence produit"].astype(str).str.strip()
df_ven = pd.read_sql("SELECT * FROM ventes", conn)

df_global = df_prod.merge(df_mag, on="ID Référence produit", how="left")
df_global = df_global.merge(df_ven, on="ID Magasin", how="left")
df_global["Chiffre d'affaires"] = df_global["Quantité"] * df_global["Prix"]

df_global.to_sql("data_global", conn, if_exists="replace", index=False)

# Analyse des données - data_global
total = df_global["Chiffre d'affaires"].sum()
cursor.execute("INSERT INTO analyses (type, valeur) VALUES (?, ?)", ("Chiffre d'affaires total", f"{total:.2f}"))

df_prod = df_global.groupby("Nom")["Chiffre d'affaires"].sum().reset_index()
df_prod.to_csv("/app/data/ventes_par_produit.csv", index=False)
for _, row in df_prod.iterrows():
    valeur = row["Chiffre d'affaires"]
    cursor.execute("INSERT INTO analyses (type, valeur) VALUES (?, ?)",
                   (f"Ventes - {row['Nom']}", f"{valeur:.2f}"))

df_reg = df_global.groupby("Ville")["Chiffre d'affaires"].sum().reset_index()
df_reg.to_csv("/app/data/ventes_par_region.csv", index=False)
for _, row in df_reg.iterrows():
    valeur = row["Chiffre d'affaires"]
    cursor.execute("INSERT INTO analyses (type, valeur) VALUES (?, ?)",
                   (f"Ventes - {row['Ville']}", f"{valeur:.2f}"))

conn.commit()
conn.close()
print(f"Chiffre d'affaires total: {total:.2f} €")
print("Table data_global créée et utilisée avec succès")

print("Lancement du script de visualisation_graph.py ...")
subprocess.run(["python", "/app/visualisation_graph.py"])
