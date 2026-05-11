# ImmoVision 360 - Pipeline de Data Lake Multimodal

## 1. Titre et Contexte
Ce projet s'inscrit dans la Phase 1 du projet **ImmoVision 360**. L'objectif est de concevoir un Data Lake robuste et performant capable d'ingérer et d'aligner des données multimodales (images et textes) pour les futurs modèles d'IA Vision et de NLP. 

Le pipeline extrait les données d'annonces Airbnb (Open Data), filtre le périmètre géographique sur le quartier de l'**Élysée** (Paris), puis télécharge, nettoie et stocke les données localement de manière idempotente.

---

## 2. Structure du Répertoire

Voici l'arborescence physique du projet après l'exécution complète du pipeline :


/ImmoVision360_DataLake
├── /data
│   └── /raw
│       ├── /tabular
│       │   ├── listings.csv.gz
│       │   └── reviews.csv.gz
│       ├── /images
│       │   └── [ID].jpg (Fichiers physiques redimensionnés à 320x320)
│       └── /texts
│           └── [ID].txt (Commentaires agrégés et nettoyés par annonce)
├── /scripts
│   ├── 00_data.ipynb
│   ├── 01_ingestion_images.py
│   ├── 02_ingestion_textes.py
│   └── 03_sanity_check.py
├── .gitignore
└── README.md
---


## 3. Notice d'Exécution
Pour déployer et tester ce pipeline, suivez scrupuleusement ces étapes dans un environnement Python 3.8+ :

Installation des dépendances :

Bash
pip install pandas pillow requests

Phase 1 - Ingestion des Images : Lancez le script pour scraper et redimensionner les visuels des annonces du périmètre Élysée.

Bash
python scripts/01_ingestion_images.py


Phase 2 - Ingestion du Texte : Lancez le script pour transformer les commentaires bruts en fichiers textes structurés.

Bash
python scripts/02_ingestion_textes.py

Phase 3 - Audit Qualité : Vérifiez l'intégrité du Data Lake.

Bash
python scripts/03_sanity_check.py
---

## 4. Audit des Données (Résultats du Sanity Check)
Les chiffres ci-dessous représentent les résultats obtenus lors de la dernière exécution du script 03_sanity_check.py.

         RAPPORT DU SANITY CHECK
==================================================
Périmètre audité : Élysée
Total annonces de référence (CSV) : 2625
--------------------------------------------------
--- VOLET IMAGES ---
Images attendues    : 2625
Images présentes    : 2456
Taux de complétion  : 93.56%
5 premiers IDs sans image : ['6921651', '1228068090962171923', '1091961025280792346', '1354999947860771115', '1478205461701053763']

--- VOLET TEXTES ---
Fichiers textes attendus    : 2625
Fichiers textes présents    : 1961
Taux de complétion          : 74.70%
5 premiers IDs sans texte  : ['760690417963220848', '25790941', '1062029016198078232', '1076807723521029683', '929631223197428026']

--- COHÉRENCE MULTIMODALE ---
Annonces complètes (Image + Texte) : 1835
Taux de complétion multimodale     : 69.90%

---

## 5. Analyse des Pertes
Une déperdition de données est observée entre le catalogue théorique et le stockage physique. Cette perte est inévitable dans un projet de Big Data Scraping et s'explique par les raisons techniques suivantes :

Obsolescence des URLs (404) : Le fichier listings.csv.gz est un instantané. Entre le moment de l'extraction et l'ingestion, certaines annonces ont été supprimées ou modifiées sur Airbnb, rendant les liens picture_url inactifs.

Filtrage NLP (Empty Reviews) : De nombreuses annonces n'ont aucun commentaire associé dans reviews.csv.gz. Par souci d'optimisation du Data Lake, aucun fichier .txt n'est créé pour ces IDs.

Protection Serveur & Timeouts : Malgré l'implémentation du Rate Limiting (pause entre les requêtes) et d'un User-Agent professionnel, certains serveurs de contenu peuvent rejeter les requêtes après un certain seuil ou subir des lenteurs réseau (Timeouts).

Fichiers Corrompus : Certaines images téléchargées ne respectent pas les formats standard JPEG/PNG et sont rejetées lors de la phase de redimensionnement pour garantir l'intégrité de la Phase IA Vision.


## Phase ETL

Voici l'arborescence de la Zone Silver et les scripts ETL en place :

/ImmoVision360_Project
├── /data
│   ├── /raw                          <-- Zone "Bronze" (Inchangée)
│   │   ├── /tabular
│   │   │   ├── listings.csv
│   │   │   └── reviews.csv
│   │   ├── /images/                  <-- [ID].jpg
│   │   └── /texts/                   <-- [ID].txt
│   │
│   └── /processed                    <-- Zone "Silver" (NOUVEAU)
│       ├── filtered_elysee.csv        <-- Généré par 0.4_extract.py
│       └── transformed_elysee.csv     <-- Généré par 0.5_transform.py
│
├── /scripts
│   ├── 01_ingestion_images.py
│   ├── 02_ingestion_textes.py
│   ├── 03_sanity_check.py
│   ├── 04_extract.py                 <-- Filtrage & Sélection métier (Pandas)
│   ├── 05_transform.py               <-- IA : Image2Feature & Text2Feature
│   └── 06_load.py                    <-- Injection PostgreSQL (SQLAlchemy)
│
├── .env                               <-- Config (DB_USER, DB_PASSWORD)
├── .gitignore                         <-- Exclut /data/* et .env
├── README_DATALAKE.md                <-- Description du Data Lake (brut/processed, conventions)
├── README_EXTRACT.md                 <-- Justification du choix d'extraction (features & hypothèses)
├── README_TRANSFORM.md               <-- Justification & description des transformations (CSV + images .jpg + textes .txt)
├── README_DATAPROFILIING.md          <-- Profiling sur filtered_elysee.csv (NaN, min/max, outliers)
├── README_LOAD.md                    <-- Documentation du chargement (PostgreSQL, table, méthode, idempotence)
└── README.md                          <-- Documentation du Pipeline

## Notice d'exécution phase ETL

### 1. Installation
pip install pandas numpy sqlalchemy psycopg2-binary python-dotenv

## 2 Configuration
Créez un fichier .env à la racine avec vos accès PostgreSQL :
DB_NAME=immovision_db, etc.

## 3 Exécution
Lancez les scripts dans cet ordre précis :

python scripts/04_extract.py : Extraction et filtrage (Élysée).

python scripts/05_transform.py : Simulation de l'enrichissement IA.

python scripts/06_load.py : Chargement dans PostgreSQL.