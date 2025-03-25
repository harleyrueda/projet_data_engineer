# Projet : Analyse des ventes d'une PME

## Objectif

Ce projet a été réalisé dans le cadre de la sélection pour le parcours **Data Engineer** chez Simplon.  
L'objectif est de concevoir une architecture conteneurisée qui automatise le traitement de fichiers de ventes, leur insertion en base de données SQLite, et l'analyse des résultats.

---

## Architecture technique

- Un conteneur Docker unique (`analyse_container`)
- Orchestration avec `docker-compose`
- Scripts Python exécutés automatiquement au démarrage
- Base de données SQLite utilisée pour stocker les données et résultats
- Génération de fichiers CSV et graphiques en sortie

---

## Arborescence du projet

PROJET_DATA_ENGINEER_HARLEY_RUEDA_SIMPLON/
├── Dockerfile
├── docker-compose.yml
├── projet_total.py
├── visualisation_graph.py
├── requirements.txt
├── datapde/
│   ├── magasins.csv
│   ├── produits.csv
│   ├── ventes.csv
│   ├── ventes_par_produit.csv
│   ├── ventes_par_region.csv
│   ├── graph_ventes_par_produit.png
│   ├── graph_ventes_par_region.png
│   └── analyses.db
├── Livrables/
│   ├── Docs/
│   │   ├── Fiche_synthese_des_resultats.pdf
│   │   └── Presentation_generale_du_projet.pdf
│   ├── Schemas/
│   │   ├── Schema_Architecture_Projet.png
│   │   └── Schema_Architecture_Base.png
│   └── Video/

---

## Instructions d'exécution

1. Cloner le dépôt et se placer à la racine du projet
2. Lancer les services Docker avec la commande :

```bash
docker-compose up --build
```

3. Le script `projet_total.py` :
   - Télécharge les fichiers CSV (si nécessaires)
   - Crée les tables dans la base de données
   - Insère les données, en évitant les doublons
   - Calcule les résultats (chiffre d'affaires total, par produit, par région)
   - Enregistre les résultats dans des fichiers CSV et dans la base SQLite
   - Effectue une pause de 40 secondes après la création des tables pour permettre la vérification de la base vide (exigence du brief pour la vidéo)
   - Lance `visualisation_graph.py` pour générer deux graphiques automatiques

---

## Résultats

- **Base de données** : `analyses.db` avec 5 tables
- **Exports CSV** :
  - `ventes_par_produit.csv`
  - `ventes_par_region.csv`
- **Graphiques générés** :
  - `graph_ventes_par_produit.png`
  - `graph_ventes_par_region.png`
- **Table `analyses`** : contient les résultats clés directement consultables


## Merci pour votre attention. 

Cordialement,
--- Harley RUEDA OSMA --- 
--- Candidat motivé pour intégrer le program Data Engineer - Simplon ---

