# app.py
# ---------------------------------------------------------
# Interface Streamlit para comparar dois arquivos (original vs alterado)
# e testar diferenças estatísticas nas competências
# ---------------------------------------------------------

import streamlit as st
import pandas as pd
from thinking_limit_analysis import test_competencia


# --- Configuração da página ---
st.set_page_config(page_title="Análise de Competências", page_icon="📊", layout="centered")

st.title("📊 Comparador de Competências")
st.write("Envie dois arquivos CSV — o **original** e o **com alteração** — para comparar as competências.")


# --- Upload dos arquivos ---
col1, col2 = st.columns(2)

with col1:
    file_original = st.file_uploader("📁 Arquivo ORIGINAL (sem limitação)", type=["csv"], key="original")

with col2:
    file_alterado = st.file_uploader("📁 Arquivo ALTERADO (com limitação)", type=["csv"], key="alterado")


# --- Processamento após upload ---
if file_original and file_alterado:
    df_original = pd.read_csv(file_original)
    df_alterado = pd.read_csv(file_alterado)

    st.success("✅ Arquivos carregados com sucesso!")

    # Detecta colunas em comum
    colunas_comuns = list(set(df_original.columns) & set(df_alterado.columns))
    if not colunas_comuns:
        st.error("❌ Nenhuma coluna em comum entre os arquivos. Verifique se ambos possuem o mesmo formato.")
        st.stop()

    # Detecta colunas de competências
    competencias = [col for col in colunas_comuns if col.startswith("C")]
    if not competencias:
        st.warning("⚠️ Nenhuma coluna de competência (ex: C2, C3) encontrada.")
        st.stop()

    competencia = st.selectbox("Escolha a competência para comparar:", competencias)

    if st.button("Rodar análise"):
        try:
            # --- Cria dataframe combinado ---
            df_comparado = pd.DataFrame()
            df_comparado[f"{competencia}_no_limit"] = df_original[competencia]
            df_comparado[f"{competencia}_with_limit"] = df_alterado[competencia]

            # --- Executa análise ---
            resultado = test_competencia(df_comparado, competencia)

            st.subheader(f"📈 Resultados para {competencia}")

            # Métricas descritivas
            metricas = resultado["metricas"]
            st.markdown("### Estatísticas descritivas")
            st.json(metricas)

            # Resultado do teste estatístico
            teste = resultado["teste"]
            st.markdown("### Teste estatístico aplicado")
            st.write(f"**Teste:** {teste['teste']}")
            st.write(f"**p-valor:** {teste['p_value']:.5f}")
            st.write(f"**Normalidade (Shapiro):** p = {teste['shapiro_p']:.5f} → {teste['normalidade']}")

            # Interpretação automática
            if teste["p_value"] < 0.05:
                st.success("🔹 Diferença estatisticamente significativa (p < 0.05).")
            else:
                st.info("🔸 Diferença **não significativa** (p ≥ 0.05).")

        except Exception as e:
            st.error(f"Erro ao processar: {e}")

else:
    st.info("📂 Por favor, envie os dois arquivos CSV para começar.")
