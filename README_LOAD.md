# Documentation du Chargement (Data Warehouse)

## 1. Destination
* **Moteur :** PostgreSQL
* **Base de données :** `immovision_db`
* **Table :** `elysee_listings_silver`

## 2. Processus d'Injection
Le chargement est effectué via **SQLAlchemy**.
* **Volume :** 2625 lignes injectées.
* **Idempotence :** L'option `if_exists='replace'` est utilisée pour permettre de réexécuter le pipeline sans créer de doublons.
* **Validation :** Le succès de l'injection a été confirmé par le message "SUCCÈS : Les données sont maintenant dans PostgreSQL".