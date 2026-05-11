#!/usr/bin/env python3
"""
ImmoVision360 - Phase 1 : Ingestion du Data Lake
Script 3 : Bilan de santé de la donnée (Sanity Check Multimodal)
"""

import os
import pandas as pd

# --- CONFIGURATION DES CHEMINS ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LISTINGS_CSV = os.path.join(BASE_DIR, "data", "raw", "tabular", "listings.csv.gz")
IMAGE_DIR = os.path.join(BASE_DIR, "data", "raw", "images")
TEXT_DIR = os.path.join(BASE_DIR, "data", "raw", "texts")

# --- PARAMÈTRES ---
TARGET_NEIGHBOURHOOD = "Élysée"

def main():
    print("=== DÉBUT DU SANITY CHECK (AUDIT DU DATA LAKE) ===")

    # 1. Chargement de la référence théorique (listings.csv)
    if not os.path.exists(LISTINGS_CSV):
        print(f"Erreur : Le fichier {LISTINGS_CSV} est introuvable. Arrêt.")
        return

    try:
        df = pd.read_csv(LISTINGS_CSV, low_memory=False)
    except Exception as e:
        print(f"Erreur lors de la lecture du CSV : {e}")
        return

    # Extraction des IDs du périmètre Élysée
    zone_col = "neighbourhood_cleansed" if "neighbourhood_cleansed" in df.columns else "neighbourhood"
    
    if zone_col not in df.columns:
        print(f"Erreur : Colonne de quartier introuvable.")
        return

    # Filtrage précis
    df_elysee = df[df[zone_col].str.contains(TARGET_NEIGHBOURHOOD, case=False, na=False)]
    expected_ids = set(df_elysee["id"].astype(str).unique())
    total_expected = len(expected_ids)

    print(f"Périmètre cible : '{TARGET_NEIGHBOURHOOD}'")
    print(f"Annonces de référence attendues : {total_expected}")
    print("-" * 50)

    # 2. Audit de la partie Images
    print("Audit du dossier /images/...")
    images_physiques = set()
    if os.path.exists(IMAGE_DIR):
        for f in os.listdir(IMAGE_DIR):
            if f.endswith(".jpg"):
                images_physiques.add(f.replace(".jpg", ""))
    
    # Statistiques images
    present_images = expected_ids.intersection(images_physiques)
    missing_images = expected_ids - images_physiques
    
    img_completion_rate = (len(present_images) / total_expected * 100) if total_expected > 0 else 0

    # 3. Audit de la partie Textes
    print("Audit du dossier /texts/...")
    textes_physiques = set()
    if os.path.exists(TEXT_DIR):
        for f in os.listdir(TEXT_DIR):
            if f.endswith(".txt"):
                textes_physiques.add(f.replace(".txt", ""))

    # Statistiques textes
    present_texts = expected_ids.intersection(textes_physiques)
    missing_texts = expected_ids - textes_physiques
    
    txt_completion_rate = (len(present_texts) / total_expected * 100) if total_expected > 0 else 0

    # 4. Cohérence croisée (Multimodalité)
    # Annonces qui ont à la fois l'image ET le texte
    perfect_multimodal = present_images.intersection(present_texts)

    # --- GÉNÉRATION DU RAPPORT ---
    print("\n" + "=" * 50)
    print("         RAPPORT DU SANITY CHECK")
    print("=" * 50)
    print(f"Périmètre audité : {TARGET_NEIGHBOURHOOD}")
    print(f"Total annonces de référence (CSV) : {total_expected}")
    print("-" * 50)
    
    print(f"--- VOLET IMAGES ---")
    print(f"Images attendues    : {total_expected}")
    print(f"Images présentes    : {len(present_images)}")
    print(f"Taux de complétion  : {img_completion_rate:.2f}%")
    if missing_images:
        print(f"5 premiers IDs sans image : {list(missing_images)[:5]}")
    
    print(f"\n--- VOLET TEXTES ---")
    print(f"Fichiers textes attendus    : {total_expected}")
    print(f"Fichiers textes présents    : {len(present_texts)}")
    print(f"Taux de complétion          : {txt_completion_rate:.2f}%")
    if missing_texts:
        print(f"5 premiers IDs sans texte  : {list(missing_texts)[:5]}")

    print(f"\n--- COHÉRENCE MULTIMODALE ---")
    print(f"Annonces complètes (Image + Texte) : {len(perfect_multimodal)}")
    print(f"Taux de complétion multimodale     : {(len(perfect_multimodal)/total_expected*100):.2f}%")
    print("=" * 50)

if __name__ == "__main__":
    main()