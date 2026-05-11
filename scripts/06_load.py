import pandas as pd
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

# --- CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_PATH = os.path.join(BASE_DIR, "data", "processed", "transformed_elysee.csv")

# 1. Chargement sécurisé des variables d'environnement
load_dotenv()
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
host = os.getenv("DB_HOST", "localhost")
port = os.getenv("DB_PORT", "5432")
dbname = os.getenv("DB_NAME")

def run_loading():
    print("=== DÉBUT DU CHARGEMENT DANS LE DATA WAREHOUSE ===")
    
    # Vérification de l'existence du fichier Silver
    if not os.path.exists(INPUT_PATH):
        print(f"ERREUR : Le fichier {INPUT_PATH} n'existe pas. Lancez le script 05_transform.py d'abord.")
        return

    try:
        # 2. Lecture des données transformées
        df = pd.read_csv(INPUT_PATH)
        print(f"Chargement de {len(df)} lignes depuis le CSV...")

        # 3. Création de la connexion SQL (Le moteur)
        # Format : postgresql://user:password@host:port/dbname
        connection_string = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"
        engine = create_engine(connection_string)

        # 4. Injection dans PostgreSQL (Load)
        # 'replace' assure l'idempotence : on écrase et on recrée la table proprement
        print(f"Injection dans la table 'elysee_listings_silver'...")
        df.to_sql(
            "elysee_listings_silver", 
            engine, 
            if_exists="replace", 
            index=False,
            method='multi' # Optimisation pour les insertions groupées
        )

        print("-" * 30)
        print("SUCCÈS : Les données sont maintenant dans PostgreSQL.")
        print("-" * 30)

    except Exception as e:
        print(f"ERREUR lors du chargement : {e}")

if __name__ == "__main__":
    run_loading()