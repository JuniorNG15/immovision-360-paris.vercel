# Stratégie de Transformation (Zone Silver)

## 1. Approche de Simulation (Mocking)
Compte tenu des limitations de quotas et de temps, le script `05_transform.py` a été configuré pour simuler l'enrichissement par l'IA. 
* **Méthode :** Utilisation de `numpy.random.choice` pour attribuer des scores.
* **Valeurs possibles :** * `1` : Catégorie "Industrialisé" / "Hôtélisé"
    * `0` : Catégorie "Personnel" / "Voisinage naturel"
    * `-1` : "Autre" ou donnée manquante.

## 2. Intégrité des Données
Le script traite l'intégralité des 2625 annonces extraites du quartier Élysée. Cette approche permet de valider la robustesse du pipeline de données (Data Pipeline) avant un passage à l'échelle avec des modèles LLM réels.

## 3. Évolutivité
L'architecture est prête pour l'intégration de `google-genai`. Il suffira de remplacer la fonction de simulation par les appels API configurés dans le fichier `.env`.