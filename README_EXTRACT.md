# Documentation de l'Extraction (Zone Silver)

## Objectif
Ce document justifie la sélection des données extraites du Data Lake pour alimenter l'entrepôt de données (Data Warehouse). L'objectif est de réduire la dimensionnalité (passer de 70+ colonnes à une quinzaine) pour maximiser la performance et la pertinence de l'analyse.

## Choix des Features & Hypothèses Métier

### 1. Hypothèse Économique : Professionnalisation du parc
* **Feature :** `calculated_host_listings_count`
* **Justification :** Permet d'isoler les "multi-hébergeurs". Un hôte possédant plus de 3 biens à l'Élysée ne pratique plus l'économie de partage mais une activité hôtelière.
* **Feature :** `availability_365`
* **Justification :** Un bien disponible plus de 120 jours par an est suspecté d'être une résidence dédiée exclusivement au tourisme, au détriment du logement des Parisiens.

### 2. Hypothèse Sociale : Lien social vs Automatisation
* **Features :** `host_response_time` & `host_response_rate`
* **Justification :** Les agences de gestion (conciergeries) répondent en quelques minutes avec un taux de 100%. Un temps de réponse "humain" est souvent plus hétérogène.
* **Feature :** `number_of_reviews`
* **Justification :** Mesure l'intensité d'occupation et la rotation des voyageurs.

### 3. Hypothèse Visuelle (IA)
* **Feature :** `id`
* **Justification :** Bien qu'issue du CSV, cette colonne est la clé étrangère indispensable pour lier les données tabulaires aux images qui seront traitées par le script `05_transform.py`.

## Processus de Filtrage
* **Géographique :** Seules les données du quartier **Élysée** sont conservées.
* **Format :** Les prix ont été convertis de format monétaire (String) en format numérique (Float) pour permettre les calculs statistiques immédiats.