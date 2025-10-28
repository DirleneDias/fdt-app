# thinking_limit_analysis.py
# ---------------------------------------------------------
# Script consolidado com testes estatísticos das competências (C2, C3, etc.)
# A função principal test_competencia(df, competencia) executa todos os testes
# ---------------------------------------------------------

import numpy as np
import pandas as pd
from scipy import stats


# ==========================
# Funções auxiliares
# ==========================

def calcular_diferencas(df, competencia):
    """
    Retorna as séries de valores 'sem limitação' e 'com limitação'
    e as diferenças correspondentes.
    """
    col_a = f"{competencia}_no_limit"
    col_b = f"{competencia}_with_limit"

    if col_a not in df.columns or col_b not in df.columns:
        raise ValueError(f"Colunas esperadas: {col_a}, {col_b} não encontradas no DataFrame.")

    paired = df[[col_a, col_b]].dropna().astype(float)
    a, b = paired[col_a].values, paired[col_b].values
    diff = a - b
    return a, b, diff


def calcular_metricas(a, b, diff):
    """Calcula estatísticas descritivas e medidas de efeito."""
    n = len(a)
    if n == 0:
        return {}

    mean_a, mean_b = a.mean(), b.mean()
    mean_diff = diff.mean()
    sd_diff = diff.std(ddof=1) if n > 1 else np.nan
    se_diff = sd_diff / np.sqrt(n) if n > 0 and not np.isnan(sd_diff) else np.nan
    cohen_d = mean_diff / sd_diff if sd_diff not in [0, np.nan] else np.nan

    # Intervalo de confiança de 95%
    t_crit = stats.t.ppf(1 - 0.025, df=n - 1) if n > 1 else np.nan
    ci_lower = mean_diff - t_crit * se_diff if not np.isnan(t_crit) and not np.isnan(se_diff) else np.nan
    ci_upper = mean_diff + t_crit * se_diff if not np.isnan(t_crit) and not np.isnan(se_diff) else np.nan

    return {
        "n": n,
        "mean_a": mean_a,
        "mean_b": mean_b,
        "mean_diff": mean_diff,
        "sd_diff": sd_diff,
        "se_diff": se_diff,
        "ci_95%": (ci_lower, ci_upper),
        "cohen_d": cohen_d
    }


def testar_diferencas(a, b, diff):
    """Aplica o teste de normalidade e escolhe automaticamente entre t-test e Wilcoxon."""
    n = len(diff)
    if n < 3:
        return {"teste": None, "stat": np.nan, "p_value": np.nan}

    # Teste de normalidade de Shapiro-Wilk
    shapiro_stat, shapiro_p = stats.shapiro(diff)
    normal = shapiro_p > 0.05 if not np.isnan(shapiro_p) else False

    if normal:
        test_name = "Paired t-test"
        stat, p_value = stats.ttest_rel(a, b, nan_policy="omit")
    else:
        test_name = "Wilcoxon signed-rank test"
        try:
            stat, p_value = stats.wilcoxon(a, b)
        except ValueError:
            stat, p_value = (np.nan, 1.0)

    return {
        "teste": test_name,
        "stat": stat,
        "p_value": p_value,
        "shapiro_p": shapiro_p,
        "normalidade": "Sim" if normal else "Não"
    }


# ==========================
# Função principal
# ==========================

def test_competencia(df, competencia):
    """
    Executa todas as análises estatísticas para uma competência informada.

    Parâmetros:
        df (pd.DataFrame): dataset com colunas no formato
                           '<competencia>_no_limit' e '<competencia>_with_limit'
        competencia (str): código da competência (ex: 'C2', 'C3')

    Retorna:
        dict com métricas e resultados de teste estatístico.
    """
    a, b, diff = calcular_diferencas(df, competencia)
    metricas = calcular_metricas(a, b, diff)
    teste = testar_diferencas(a, b, diff)

    resultado = {
        "competencia": competencia,
        "metricas": metricas,
        "teste": teste
    }
    return resultado

# ==========================
# Exemplo de uso
# ==========================
# df = pd.read_csv("meu_arquivo.csv")
# resultado_C2 = test_competencia(df, "C2")
# print(resultado_C2)


