#!/usr/bin/env python3
"""
ImmoVision360 - Phase 1 : Ingestion du Data Lake
Script 1 : Ingestion et scraping des images (Périmètre Élysée)
"""

import os
import time
import pandas as pd
import requests
from PIL import Image
from io import BytesIO

# --- CONFIGURATION DES CHEMINS ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, "data", "raw", "tabular", "listings.csv.gz")
OUTPUT_IMAGE_DIR = os.path.join(BASE_DIR, "data", "raw", "images")

# --- PARAMÈTRES DE L'ASPIRATEUR ---
TARGET_NEIGHBOURHOOD = "Élysée"  # À ajuster selon l'orthographe exacte dans votre CSV (ex: "Elysée")
TARGET_SIZE = (320, 320)
SLEEP_TIME = 0.5  # Pause de 500ms entre chaque requête (Courtoisie serveur)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


def main():
    print("=== DÉBUT DE L'INGESTION DES IMAGES ===")
    
    # 1. Vérification et création du dossier de sortie
    if not os.path.exists(OUTPUT_IMAGE_DIR):
        os.makedirs(OUTPUT_IMAGE_DIR)
        print(f"Dossier créé : {OUTPUT_IMAGE_DIR}")

    # 2. Lecture du catalogue listings.csv
    if not os.path.exists(CSV_PATH):
        print(f"Erreur : Le fichier {CSV_PATH} est introuvable. Arrêt du script.")
        return

    try:
        df = pd.read_csv(CSV_PATH, low_memory=False)
    except Exception as e:
        print(f"Erreur lors de la lecture du fichier CSV : {e}")
        return

    # 3. Filtrage sur le périmètre Élysée
    # Remarque : on utilise str.contains avec case=False pour être flexible sur les accents ou la casse.
    if "neighbourhood_cleansed" in df.columns:
        zone_col = "neighbourhood_cleansed"
    elif "neighbourhood" in df.columns:
        zone_col = "neighbourhood"
    else:
        print("Attention : Aucune colonne de quartier détectée. Téléchargement sans filtre de zone.")
        zone_col = None

    if zone_col:
        df_filtered = df[df[zone_col].str.contains(TARGET_NEIGHBOURHOOD, case=False, na=False)]
    else:
        df_filtered = df

    print(f"Nombre d'annonces dans le périmètre '{TARGET_NEIGHBOURHOOD}' : {len(df_filtered)}")

    # Vérification de la présence des colonnes indispensables
    if "id" not in df_filtered.columns or "picture_url" not in df_filtered.columns:
        print("Erreur : Les colonnes 'id' ou 'picture_url' sont absentes du fichier CSV.")
        return

    # 4. Boucle de scraping intelligente
    success_count = 0
    error_count = 0
    skipped_count = 0

    for index, row in df_filtered.iterrows():
        listing_id = str(row["id"])
        img_url = row["picture_url"]

        # Ignorer si l'URL est vide
        if pd.isna(img_url) or img_url == "":
            continue

        # Règle de nommage strict
        output_filename = f"{listing_id}.jpg"
        output_path = os.path.join(OUTPUT_IMAGE_DIR, output_filename)

        # Pilier d'Idempotence : Vérification de l'existence du fichier
        if os.path.exists(output_path):
            skipped_count += 1
            continue

        # Téléchargement et traitement de l'image
        try:
            # Courtoisie serveur (Rate Limiting)
            time.sleep(SLEEP_TIME)

            response = requests.get(img_url, headers=HEADERS, timeout=10)
            
            if response.status_code == 200:
                # Lecture des pixels
                img = Image.open(BytesIO(response.content))
                
                # Conversion en RGB si nécessaire (ex: PNG ou WebP avec transparence vers JPG)
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                
                # Réduction de la taille (Big Data Management)
                img_resized = img.resize(TARGET_SIZE, Image.Resampling.LANCZOS)
                
                # Sauvegarde locale
                img_resized.save(output_path, "JPEG", quality=85)
                success_count += 1
                print(f"[{success_count}] Image téléchargée et optimisée pour l'ID {listing_id}")
            else:
                print(f"Lien mort ou inaccessible (Code {response.status_code}) pour l'ID {listing_id}")
                error_count += 1

        except Exception as e:
            # Gestion des Exceptions (Le script continue même en cas d'erreur)
            print(f"Échec du téléchargement pour l'ID {listing_id} | Erreur : {e}")
            error_count += 1

    # 5. Rapport final d'exécution
    print("\n=== BILAN DE L'INGESTION DES IMAGES ===")
    print(f"Images déjà existantes (idempotence) : {skipped_count}")
    print(f"Images téléchargées avec succès       : {success_count}")
    print(f"Erreurs rencontrées                   : {error_count}")
    print("=======================================")

if __name__ == "__main__":
    main()