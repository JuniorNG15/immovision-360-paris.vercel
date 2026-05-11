import pandas as pd
import os

# Configuration des chemins
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_CSV_PATH = os.path.join(BASE_DIR, "data", "raw", "tabular", "listings.csv.gz")
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
OUTPUT_PATH = os.path.join(PROCESSED_DIR, "filtered_elysee.csv")

# 1. Sélection stratégique des colonnes (Hypothèses A, B et C)
COLS_TO_KEEP = [
    'id',                       # Identifiant unique (Jointure avec images/textes)
    'listing_url',              # Vérification source
    # --- Hypothèse A : Économie de partage vs Industrie ---
    'host_id',                  
    'calculated_host_listings_count', # Détecteur de multipropriétés
    'price',                    
    'property_type',            
    'room_type',                
    'availability_365',         # Intensité de la location à l'année
    # --- Hypothèse B : Déshumanisation / Gestion Pro ---
    'host_response_time',       
    'host_response_rate',       
    'number_of_reviews',        
    'review_scores_rating',     
    # --- Localisation ---
    'neighbourhood_cleansed',   # Pour le filtrage géographique
    'latitude',                 
    'longitude'
]

def run_extraction():
    print("=== DÉBUT DE L'EXTRACTION (ZONE BRONZE -> SILVER) ===")
    
    # Création du dossier processed s'il n'existe pas
    if not os.path.exists(PROCESSED_DIR):
        os.makedirs(PROCESSED_DIR)
        print(f"Dossier créé : {PROCESSED_DIR}")

    try:
        # 2. Chargement du CSV compressé
        print(f"Lecture de : {RAW_CSV_PATH}...")
        df = pd.read_csv(RAW_CSV_PATH, compression='gzip', low_memory=False)
        
        # 3. Filtrage géographique (Quartier Élysée)
        print("Filtrage sur le quartier : Élysée...")
        df_elysee = df[df['neighbourhood_cleansed'] == 'Élysée'].copy()
        
        # 4. Sélection des colonnes utiles
        print(f"Sélection des {len(COLS_TO_KEEP)} colonnes stratégiques...")
        df_final = df_elysee[COLS_TO_KEEP]
        
        # Nettoyage rapide du prix (optionnel ici, mais recommandé)
        # Airbnb stocke le prix en string "$120.00", on le prépare pour le calcul
        if 'price' in df_final.columns:
            df_final['price'] = df_final['price'].replace(r'[\$,]', '', regex=True).astype(float)

        # 5. Sauvegarde en Zone Silver
        df_final.to_csv(OUTPUT_PATH, index=False, encoding='utf-8')
        
        print("-" * 30)
        print(f"SUCCÈS : Extraction terminée.")
        print(f"Volume final : {len(df_final)} annonces retenues.")
        print(f"Fichier sauvegardé : {OUTPUT_PATH}")
        print("-" * 30)

    except FileNotFoundError:
        print(f"ERREUR : Le fichier {RAW_CSV_PATH} est introuvable.")
    except Exception as e:
        print(f"ERREUR INATTENDUE : {e}")

if __name__ == "__main__":
    run_extraction()