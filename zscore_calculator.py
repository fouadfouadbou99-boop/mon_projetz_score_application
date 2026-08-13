import pandas as pd

def calculate_z_scores(file_path):
    """
    Charge le fichier Excel et calcule :
    - Moyenne Historique
    - Ecart-Type
    - Z-Score
    - Z Ajusté
    - Score Pondéré
    - Score Quantitatif Global
    """

    # Lecture du fichier Excel
    df = pd.read_excel(file_path)

    # =====================================================
    # 1. MOYENNE HISTORIQUE
    # =====================================================

    historique_cols = ['N-5', 'N-4', 'N-3', 'N-2', 'N-1']

    df['Moyenne Historique Calculée'] = (
        df[historique_cols]
        .mean(axis=1)
    )

    # =====================================================
    # 2. ECART-TYPE
    # =====================================================

    df['Ecart-Type Calculé'] = (
        df[historique_cols]
        .std(axis=1, ddof=0)
    )

    # =====================================================
    # 3. Z-SCORE
    # =====================================================

    def calcul_z_score(row):

        if row['Ecart-Type Calculé'] == 0:
            return 0

        return (
            (row['N'] - row['Moyenne Historique Calculée'])
            / row['Ecart-Type Calculé']
        )

    df['Z-Score Calculé'] = df.apply(
        calcul_z_score,
        axis=1
    )

    # =====================================================
    # 4. Z AJUSTE
    # =====================================================

    df['Z Ajusté Calculé'] = (
        df['Z-Score Calculé']
        .abs()
    )

    # =====================================================
    # 5. SCORE PONDERE
    # =====================================================

    df['Score Pondéré Calculé'] = (
        df['Z Ajusté Calculé']
        * df['Poids %']
    )

    # =====================================================
    # 6. SCORE GLOBAL
    # =====================================================

    score_quantitatif_global = round(
        df['Score Pondéré Calculé'].sum(),
        2
    )

    # =====================================================
    # RESULTAT
    # =====================================================

    return df, score_quantitatif_global
