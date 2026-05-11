# Audit de Santé des Données (Data Profiling) - Quartier Élysée

## 1. Analyse des Manquants (NaN)
* **Colonnes Critiques (0% NaN) :** `id`, `neighbourhood_cleansed`, `price`.
* **Colonnes avec NaN :** * `host_response_time` (~15%) : Absence de réponse ou nouvel hôte.
    * `review_scores_rating` (~10%) : Logements sans aucun commentaire.
* **Décision :** Imputation par la médiane pour les scores et valeur "N/A" pour les délais de réponse.

## 2. Statistiques & Valeurs Aberrantes
* **Prix :** Min: 45€ / Max: 8500€. 
    * *Outlier détecté :* Un appartement à 0€ (à supprimer).
    * *Cap :* Les prix > 2000€ seront plafonnés pour ne pas fausser la moyenne globale.
* **Disponibilité :** `availability_365` à 0 (logement retiré du marché ou complet).

## 3. Stratégies de Nettoyage
* **Price :** Conversion String -> Float réussie.
* **Drop :** Suppression des lignes sans `id` ou avec prix nul.