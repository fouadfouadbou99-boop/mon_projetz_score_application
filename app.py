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
    "Veuillez télécharger votre fichier Excel afin de calculer les "
    "Z-Scores et le Score Quantitatif Global."
)

# =====================================================
# UPLOAD FICHIER
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

    st.success("Fichier chargé avec succès !")

    try:

        # ===================================
        # CALCULS
        # ===================================

        df_results, global_score = calculate_z_scores(
            temp_file_path
        )

        # ===================================
        # SCORE PONDERE
        # ===================================

        if "Score Pondéré Calculé" not in df_results.columns:

            df_results["Score Pondéré Calculé"] = (
                df_results["Poids %"]
                * df_results["Z Ajusté Calculé"]
            )

        # ===================================
        # APERÇU RESULTATS
        # ===================================

        st.subheader("📊 Aperçu des Z-Scores Calculés")

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

        # ===================================
        # SCORE GLOBAL
        # ===================================

        st.subheader("🎯 Score Quantitatif Global")

        st.metric(
            label="Score Quantitatif Global",
            value=f"{global_score:.2f}"
        )

        # ===================================
        # NOTATION
        # ===================================

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

        # ===================================
        # AFFICHAGE NOTATION
        # ===================================

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                label="Notation",
                value=rating
            )

        with col2:
            st.metric(
                label="Niveau de Risque",
                value=risk
            )

        # ===================================
        # SYNTHESE
        # ===================================

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

        # ===================================
        # EXPORT EXCEL
        # ===================================

        output = io.BytesIO()

        with pd.ExcelWriter(
            output,
            engine="openpyxl"
        ) as writer:

            df_results.to_excel(
                writer,
                sheet_name="Z-Scores",
                index=False
            )

            synthese_df.to_excel(
                writer,
                sheet_name="Synthese",
                index=False
            )

        excel_file = output.getvalue()

        st.subheader("⬇️ Télécharger les Résultats")

        st.download_button(
            label="📥 Télécharger le Rapport Excel",
            data=excel_file,
            file_name=f"Rapport_ZScore_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:

        st.error(
            f"Une erreur est survenue : {e}"
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
