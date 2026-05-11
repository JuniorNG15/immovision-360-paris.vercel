#!/usr/bin/env python3
"""
ImmoVision360 - Phase 1 : Ingestion du Data Lake
Script 2 : Ingestion et structuration des textes (Corpus NLP)
"""

import os
import pandas as pd
import re

# --- CONFIGURATION DES CHEMINS ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LISTINGS_CSV = os.path.join(BASE_DIR, "data", "raw", "tabular", "listings.csv.gz")
REVIEWS_CSV = os.path.join(BASE_DIR, "data", "raw", "tabular", "reviews.csv.gz")
OUTPUT_TEXT_DIR = os.path.join(BASE_DIR, "data", "raw", "texts")

# --- PARAMÈTRES ---
TARGET_NEIGHBOURHOOD = "Élysée"

def clean_html(text):
    """Supprime les balises HTML simples et nettoie les espaces."""
    if not isinstance(text, str):
        return ""
    # Supprime <br/>, <p>, etc.
    clean = re.sub(r'<.*?>', ' ', text)
    # Supprime les sauts de ligne multiples et espaces superflus
    clean = re.sub(r'\s+', ' ', clean).strip()
    return clean

def main():
    print("=== DÉBUT DE L'INGESTION DES TEXTES ===")

    # 1. Préparation du dossier de sortie
    if not os.path.exists(OUTPUT_TEXT_DIR):
        os.makedirs(OUTPUT_TEXT_DIR)
        print(f"Dossier créé : {OUTPUT_TEXT_DIR}")

    # 2. Chargement de listings.csv pour filtrer le périmètre
    try:
        print("Chargement du catalogue listings...")
        df_listings = pd.read_csv(LISTINGS_CSV, low_memory=False)
        
        # Identification de la colonne de quartier
        zone_col = "neighbourhood_cleansed" if "neighbourhood_cleansed" in df_listings.columns else "neighbourhood"
        
        # Filtrage Élysée
        elysee_ids = df_listings[df_listings[zone_col].str.contains(TARGET_NEIGHBOURHOOD, case=False, na=False)]["id"].unique()
        elysee_ids_set = set(elysee_ids.astype(str)) # Pour une recherche rapide O(1)
        
        print(f"Nombre d'annonces identifiées dans '{TARGET_NEIGHBOURHOOD}' : {len(elysee_ids_set)}")
    except Exception as e:
        print(f"Erreur lors de la lecture de listings.csv : {e}")
        return

    # 3. Chargement et filtrage de reviews.csv
    try:
        print("Chargement des commentaires (cela peut prendre un moment)...")
        # On ne charge que les colonnes nécessaires pour économiser la RAM
        df_reviews = pd.read_csv(REVIEWS_CSV, usecols=["listing_id", "comments"], low_memory=False)
        
        # Filtrage : On ne garde que les commentaires dont le listing_id est dans notre set Élysée
        df_reviews["listing_id"] = df_reviews["listing_id"].astype(str)
        df_elysee_reviews = df_reviews[df_reviews["listing_id"].isin(elysee_ids_set)].copy()
        
        print(f"Nombre de commentaires trouvés pour ce périmètre : {len(df_elysee_reviews)}")
    except Exception as e:
        print(f"Erreur lors de la lecture de reviews.csv : {e}")
        return

    # 4. Regroupement et Écriture (Idempotence & Robustesse)
    success_count = 0
    skipped_count = 0

    # On groupe par listing_id pour fusionner les commentaires d'une même annonce
    grouped = df_elysee_reviews.groupby("listing_id")

    for listing_id, group in grouped:
        output_file = os.path.join(OUTPUT_TEXT_DIR, f"{listing_id}.txt")

        # Pilier d'Idempotence
        if os.path.exists(output_file):
            skipped_count += 1
            continue

        try:
            # Récupération et nettoyage des commentaires
            comments_list = group["comments"].dropna().tolist()
            cleaned_comments = [clean_html(str(c)) for c in comments_list if len(str(c)) > 5]

            if not cleaned_comments:
                continue

            # Écriture du fichier final
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(f"Commentaires pour l'annonce {listing_id}:\n")
                for comment in cleaned_comments:
                    f.write(f"- {comment}\n")
            
            success_count += 1
            if success_count % 50 == 0:
                print(f"Progression : {success_count} fichiers textes générés...")

        except Exception as e:
            print(f"Erreur lors de l'écriture pour l'ID {listing_id} : {e}")

    # 5. Rapport Final
    print("\n=== BILAN DE L'INGESTION DES TEXTES ===")
    print(f"Fichiers déjà existants (idempotence) : {skipped_count}")
    print(f"Nouveaux fichiers .txt créés         : {success_count}")
    print(f"Total d'annonces avec commentaires   : {success_count + skipped_count}")
    print("=======================================")

if __name__ == "__main__":
    main()