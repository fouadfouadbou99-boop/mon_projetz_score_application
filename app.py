import streamlit as st
import pandas as pd
from zscore_calculator import calculate_z_scores
import os
import io
from datetime import datetime

# =====================================================
# CONFIGURATION PAGE
# =====================================================

st.set_page_config(
    page_title="Application de Calcul de Z-Score",
    layout="wide"
)

# =====================================================
# TITRE
# =====================================================

st.title("📈 Application de Calcul de Z-Score")

st.write(
    "Veuillez télécharger votre fichier Excel afin de calculer "
    "les Z-Scores, le Score Quantitatif Global et générer "
    "un rapport Excel complet."
)

# =====================================================
# IMPORT FICHIER
# =====================================================

uploaded_file = st.file_uploader(
    "Charger le fichier Excel",
    type=["xlsx"]
)

# =====================================================
# TRAITEMENT
# =====================================================

if uploaded_file is not None:

    temp_file_path = "temp_zscore_data.xlsx"

    with open(temp_file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.success("✅ Fichier chargé avec succès")

    try:

        # =================================================
        # CALCULS
        # =================================================

        df_results, global_score = calculate_z_scores(
            temp_file_path
        )

        # =================================================
        # CONTROLE SCORE PONDERE
        # =================================================

        if "Score Pondéré Calculé" not in df_results.columns:

            df_results["Score Pondéré Calculé"] = (
                df_results["Poids %"]
                * df_results["Z Ajusté Calculé"]
            )

        # =================================================
        # TABLEAU DETAILLE
        # =================================================

        st.subheader("📊 Aperçu des Résultats")

        colonnes = [
            "KPI",
            "Poids %",
            "N",
            "Moyenne Historique Calculée",
            "Ecart-Type Calculé",
            "Z-Score Calculé",
            "Z Ajusté Calculé",
            "Score Pondéré Calculé"
        ]

        st.dataframe(df_results[colonnes])

        # =================================================
        # SCORE GLOBAL
        # =================================================

        st.subheader("🎯 Score Quantitatif Global")

        st.metric(
            "Score Quantitatif Global",
            f"{global_score:.2f}"
        )

        # =================================================
        # NOTATION
        # =================================================

        def get_rating(score):

            if score >= 250:
                return "AAA", "🟢 Très Faible Risque"

            elif score >= 220:
                return "AA", "🟢 Faible Risque"

            elif score >= 190:
                return "A", "🟢 Faible Risque"

            elif score >= 160:
                return "BBB", "🟡 Risque Modéré"

            elif score >= 130:
                return "BB", "🟡 Risque Modéré"

            elif score >= 100:
                return "B", "🟠 Risque Elevé"

            else:
                return "CCC", "🔴 Risque Très Elevé"

        rating, risk = get_rating(global_score)

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "Notation",
                rating
            )

        with col2:
            st.metric(
                "Niveau de Risque",
                risk
            )

        # =================================================
        # SYNTHESE
        # =================================================

        st.subheader("📋 Synthèse")

        synthese_df = pd.DataFrame({

            "Date Calcul":
            [datetime.now().strftime("%d/%m/%Y %H:%M")],

            "Score Quantitatif Global":
            [round(global_score, 2)],

            "Notation":
            [rating],

            "Niveau de Risque":
            [risk]
        })

        st.dataframe(synthese_df)

        # =================================================
        # EXPORT EXCEL
        # =================================================

        output = io.BytesIO()

        with pd.ExcelWriter(
            output,
            engine="openpyxl"
        ) as writer:

            # =============================================
            # FEUILLE 1 : Z-SCORES
            # =============================================

            df_results.to_excel(
                writer,
                sheet_name="Z-Scores",
                index=False
            )

            # =============================================
            # FEUILLE 2 : SYNTHESE
            # =============================================

            synthese_df.to_excel(
                writer,
                sheet_name="Synthese",
                index=False
            )

            # =============================================
            # FEUILLE 3 : DASHBOARD
            # =============================================

            dashboard_df = pd.DataFrame({

                "Indicateur": [
                    "Nombre de KPI",
                    "Score Quantitatif Global",
                    "Score Moyen",
                    "Z-Score Maximum",
                    "Z-Score Minimum",
                    "Score Pondéré Maximum",
                    "Score Pondéré Moyen"
                ],

                "Valeur": [
                    len(df_results),
                    round(global_score, 2),
                    round(df_results["Z-Score Calculé"].mean(), 2),
                    round(df_results["Z-Score Calculé"].max(), 2),
                    round(df_results["Z-Score Calculé"].min(), 2),
                    round(df_results["Score Pondéré Calculé"].max(), 2),
                    round(df_results["Score Pondéré Calculé"].mean(), 2)
                ]
            })

            dashboard_df.to_excel(
                writer,
                sheet_name="Dashboard",
                index=False
            )

            # =============================================
            # FEUILLE 4 : CLASSEMENT KPI
            # =============================================

            classement_df = df_results.sort_values(
                by="Score Pondéré Calculé",
                ascending=False
            )

            classement_df.to_excel(
                writer,
                sheet_name="Classement KPI",
                index=False
            )

            # =============================================
            # FEUILLE 5 : TOP 5 KPI
            # =============================================

            top5_df = classement_df.head(5)

            top5_df.to_excel(
                writer,
                sheet_name="Top 5 KPI",
                index=False
            )

            # =============================================
            # FEUILLE 6 : COMMENTAIRE
            # =============================================

            commentaire = f"""
Score Quantitatif Global : {global_score:.2f}

Notation : {rating}

Niveau de Risque : {risk}

Analyse :

Le score global ressort à {global_score:.2f}.
La notation obtenue est {rating}.
Le niveau de risque est évalué à {risk}.

Les KPI les plus contributifs figurent dans
l'onglet Top 5 KPI.

Cette analyse est basée sur la méthodologie
de Z-Score appliquée aux données historiques.
"""

            commentaire_df = pd.DataFrame({
                "Commentaire": [commentaire]
            })

            commentaire_df.to_excel(
                writer,
                sheet_name="Commentaire",
                index=False
            )

        excel_file = output.getvalue()

        # =================================================
        # BOUTON TELECHARGEMENT
        # =================================================

        st.subheader("⬇️ Télécharger les Résultats")

        st.download_button(
            label="📥 Télécharger le Rapport Excel",
            data=excel_file,
            file_name=f"Rapport_ZScore_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:

        st.error(
            f"Erreur durant le traitement : {e}"
        )

    finally:

        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

else:

    st.info(
        "Veuillez télécharger un fichier Excel pour lancer les calculs."
    )

# =====================================================
# PIED DE PAGE
# =====================================================

st.markdown("---")

st.markdown(
    "Application de scoring quantitatif basée sur la méthode Z-Score."
)
