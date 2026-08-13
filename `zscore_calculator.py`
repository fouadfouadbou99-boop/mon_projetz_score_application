import pandas as pd

def calculate_z_scores(file_path):
    """
    Loads an Excel file, calculates Z-scores and related metrics,
    and returns the updated DataFrame and the global quantitative score.
    """
    df = pd.read_excel(file_path)

    # 1. Calculer la Moyenne Historique sur les colonnes N-5 à N-1
    df['Moyenne Historique Calculée'] = df[['N-5', 'N-4', 'N-3', 'N-2', 'N-1']].mean(axis=1)

    # 2. Calculer l'Écart-Type sur les colonnes N-5 à N-1 (ddof=0 pour l'écart-type de la population)
    df['Ecart-Type Calculé'] = df[['N-5', 'N-4', 'N-3', 'N-2', 'N-1']].std(axis=1, ddof=0)

    # 3. Calculer le Z-Score
    # Gérer la division par zéro si l'écart-type est 0 pour éviter les erreurs
    df['Z-Score Calculé'] = df.apply(lambda row:
        (row['N'] - row['Moyenne Historique Calculée']) / row['Ecart-Type Calculé']
        if row['Ecart-Type Calculé'] != 0 else 0, axis=1)

    # 4. Calculer le Z Ajusté
    df['Z Ajusté Calculé'] = df['Z-Score Calculé'].abs()

    # 5. Calculer le Score Pondéré
    # Convertir 'Poids %' en décimal avant de multiplier
    df['Score Pondéré Calculé'] = df['Z Ajusté Calculé'] * (df['Poids %'] / 100)

    # 6. Calculer le Score Quantitatif Global
    score_quantitatif_global = df['Score Pondéré Calculé'].sum()

    return df, score_quantitatif_global
