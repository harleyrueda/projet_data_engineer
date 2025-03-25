import pandas as pd
import matplotlib.pyplot as plt
import os

# Définition des chemins vers les fichiers CSV des résultats et le dossier de données
base_path = "/app/data"
csv_produit = os.path.join(base_path, "ventes_par_produit.csv")
csv_region = os.path.join(base_path, "ventes_par_region.csv")

# Chargement des données depuis les fichiers CSV
df_produit = pd.read_csv(csv_produit)
df_region = pd.read_csv(csv_region)

# --- Graphique 1 : Ventes par produit ---
plt.figure(figsize=(10, 6))
plt.bar(df_produit['Nom'], df_produit["Chiffre d'affaires"], edgecolor='black')
plt.xticks(rotation=45, ha='right')
plt.title('Ventes par produit')
plt.xlabel('Produit')
plt.ylabel("Chiffre d'affaires (€)")
plt.tight_layout()
plt.savefig(os.path.join(base_path, "graph_ventes_par_produit.png"))
plt.show()

# --- Graphique 2 : Répartition des ventes par région ---
plt.figure(figsize=(8, 8))
plt.pie(df_region["Chiffre d'affaires"], labels=df_region['Ville'], autopct='%1.1f%%', startangle=140)
plt.title('Répartition des ventes par région')
plt.tight_layout()
plt.savefig(os.path.join(base_path, "graph_ventes_par_region.png"))
plt.show()
