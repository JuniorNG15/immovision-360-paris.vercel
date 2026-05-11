import pandas as pd
import numpy as np
import os

# Configuration des chemins
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_PATH = os.path.join(BASE_DIR, "data", "processed", "filtered_elysee.csv")
OUTPUT_PATH = os.path.join(BASE_DIR, "data", "processed", "transformed_elysee.csv")

def run_mock_transform():
    print("=== DÉBUT DE LA TRANSFORMATION (MODE SIMULATION) ===")
    
    if not os.path.exists(INPUT_PATH):
        print(f"ERREUR : Fichier {INPUT_PATH} introuvable. Lancez 04_extract.py d'abord.")
        return

    # 1. Chargement des données (les 2625 annonces que tu as extraites)
    df = pd.read_csv(INPUT_PATH)
    print(f"Traitement de {len(df)} lignes...")

    # 2. Génération de données fictives (1, 0, ou -1)
    # Cela simule ce que l'IA aurait répondu
    choices = [1, 0, -1]
    
    print("Simulation du score Vision (Standardization_Score)...")
    df['Standardization_Score'] = np.random.choice(choices, size=len(df))
    
    print("Simulation du score NLP (Neighborhood_Impact)...")
    df['Neighborhood_Impact'] = np.random.choice(choices, size=len(df))

    # 3. Sauvegarde
    df.to_csv(OUTPUT_PATH, index=False)
    
    print("-" * 30)
    print(f"SUCCÈS : Transformation simulée terminée.")
    print(f"Fichier prêt : {OUTPUT_PATH}")
    print("-" * 30)

if __name__ == "__main__":
    run_mock_transform()