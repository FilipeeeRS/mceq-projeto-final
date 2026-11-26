"""
MCEQ 12576 - Projeto Final
Tempo até o merge: PRs abertos por agentes de IA x PRs abertos por humanos.

Base: AIDev v3 (Li, Zhang e Hassan, 2025), Hugging Face hao-li/AIDev, tag v3, licença CC BY 4.0.

Uso (Colab ou local):
    pip install -r requirements.txt
    python analise.py

Se já tiver os .parquet baixados, aponte a pasta:
    AIDEV_DATA_DIR=dados/brutos python analise.py

Gera:
    dados/limpos/prs_merged.csv
    resultados/tabela_descritiva.csv
    resultados/resultados.json
    figuras/fig1_tempo_merge.png  (e .pdf)
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

# ---------------------------------------------------------------------------
# Parâmetros fixados no protocolo (antes de olhar os dados)
# ---------------------------------------------------------------------------
HF_REPO = "hao-li/AIDev"
HF_REVISION = "v3"          # versão fixa da base (MSR 2026 Mining Challenge)
ALPHA = 0.05
SEED = 2026
N_BOOT = 2000
LIMIAR_MERGE_INSTANTANEO_MIN = 1.0   # usado só na análise exploratória 2

ROOT = Path(__file__).resolve().parent
DIR_LIMPOS = ROOT / "dados" / "limpos"
DIR_RES = ROOT / "resultados"
DIR_FIG = ROOT / "figuras"
for d in (DIR_LIMPOS, DIR_RES, DIR_FIG):
    d.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# 1. Carga dos dados brutos
# ---------------------------------------------------------------------------
def caminho_tabela(nome: str) -> Path:
    pasta = os.environ.get("AIDEV_DATA_DIR")
    if pasta:
        return Path(pasta) / f"{nome}.parquet"
    from huggingface_hub import hf_hub_download
    return Path(hf_hub_download(HF_REPO, f"{nome}.parquet",
                                repo_type="dataset", revision=HF_REVISION))


COLS = ["id", "repo_url", "created_at", "merged_at"]


def carregar() -> pd.DataFrame:
    ag = pd.read_parquet(caminho_tabela("pull_request"))
    hu = pd.read_parquet(caminho_tabela("human_pull_request"))
    print("Colunas pull_request:      ", list(ag.columns))
    print("Colunas human_pull_request:", list(hu.columns))
    for nome, df in (("pull_request", ag), ("human_pull_request", hu)):
        faltando = [c for c in COLS if c not in df.columns]
        if faltando:
            raise SystemExit(f"{nome} não tem as colunas {faltando}; ajuste COLS.")

    ag = ag[COLS + (["agent"] if "agent" in ag.columns else [])].copy()
    ag["grupo"] = "Agente de IA"
    if "agent" not in ag.columns:
        ag["agent"] = "desconhecido"
    hu = hu[COLS].copy()
    hu["grupo"] = "Humano"
    hu["agent"] = "Humano"
    bruto = pd.concat([ag, hu], ignore_index=True)
    print(f"\nBruto: {len(ag):,} PRs de agentes | {len(hu):,} PRs humanos")
    return bruto


# ---------------------------------------------------------------------------
# 2. Limpeza (regras do protocolo)
# ---------------------------------------------------------------------------
def limpar(bruto: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    log = {"bruto_agente": int((bruto.grupo == "Agente de IA").sum()),
           "bruto_humano": int((bruto.grupo == "Humano").sum())}
    df = bruto.drop_duplicates(subset=["id", "grupo"]).copy()
    df["created_at"] = pd.to_datetime(df["created_at"], format="ISO8601", utc=True)
    df["merged_at"] = pd.to_datetime(df["merged_at"], format="ISO8601", utc=True)

    # R1: só PRs integrados (merged)
    df = df[df["merged_at"].notna()]
    log["apos_merged_agente"] = int((df.grupo == "Agente de IA").sum())
    log["apos_merged_humano"] = int((df.grupo == "Humano").sum())

    # VD: horas entre abertura e merge
    df["horas_ate_merge"] = (df["merged_at"] - df["created_at"]).dt.total_seconds() / 3600

    # R2: remove tempos inválidos (negativos ou ausentes)
    invalidos = df["horas_ate_merge"].isna() | (df["horas_ate_merge"] < 0)
    log["excluidos_tempo_invalido"] = int(invalidos.sum())
    df = df[~invalidos]

    # R3: só repositórios que têm PRs dos dois grupos (comparação justa)
    repos_ag = set(df.loc[df.grupo == "Agente de IA", "repo_url"])
    repos_hu = set(df.loc[df.grupo == "Humano", "repo_url"])
    comuns = repos_ag & repos_hu
    df = df[df["repo_url"].isin(comuns)].copy()
    log["repos_em_comum"] = len(comuns)
    log["final_agente"] = int((df.grupo == "Agente de IA").sum())
    log["final_humano"] = int((df.grupo == "Humano").sum())

    df.to_csv(DIR_LIMPOS / "prs_merged.csv", index=False)
    print("\nLimpeza:", json.dumps(log, indent=2, ensure_ascii=False))
    return df, log


# ---------------------------------------------------------------------------
# 3. Estatística
# ---------------------------------------------------------------------------
def efeito_A(x: np.ndarray, y: np.ndarray) -> float:
    """A de Vargha-Delaney = P(X > Y) + 0,5 P(X = Y), como na Aula 08."""
    return float(stats.mannwhitneyu(x, y, alternative="two-sided").statistic / (len(x) * len(y)))


def magnitude_A(a: float) -> str:
    """Limiares de Vargha e Delaney (2000): 0,56 / 0,64 / 0,71 (simétricos em torno de 0,5)."""
    dist = abs(a - 0.5)
    if dist < 0.06:
        return "desprezível"
    if dist < 0.14:
        return "pequeno"
    if dist < 0.21:
        return "médio"
    return "grande"


def r_bisserial(x, y) -> float:
    """Efeito do Wilcoxon pareado (Kerby, 2014), como na Aula 08."""
    d = np.asarray(x) - np.asarray(y)
    r = stats.rankdata(np.abs(d))
    zeros = r[d == 0].sum() / 2
    mais = r[d > 0].sum() + zeros
    menos = r[d < 0].sum() + zeros
    return float((mais - menos) / (mais + menos))


def bootstrap(x, y, rng, n_boot=N_BOOT):
    dif_med, efeitos = np.empty(n_boot), np.empty(n_boot)
    for b in range(n_boot):
        xb = rng.choice(x, len(x), replace=True)
        yb = rng.choice(y, len(y), replace=True)
        dif_med[b] = np.median(xb) - np.median(yb)
        efeitos[b] = efeito_A(xb, yb)
    q = [2.5, 97.5]
    return np.percentile(dif_med, q).tolist(), np.percentile(efeitos, q).tolist()


def descritiva(df: pd.DataFrame, col="horas_ate_merge", por="grupo") -> pd.DataFrame:
    g = df.groupby(por)[col]
    t = pd.DataFrame({
        "n": g.size(),
        "media_h": g.mean(),
        "dp_h": g.std(),
        "Q1_h": g.quantile(0.25),
        "mediana_h": g.median(),
        "Q3_h": g.quantile(0.75),
        "p90_h": g.quantile(0.90),
        "pct_merge_menos_1min": g.apply(lambda s: 100 * (s < 1 / 60).mean()),
    })
    return t.round(3)


def teste_principal(df: pd.DataFrame, rng) -> dict:
    x = df.loc[df.grupo == "Agente de IA", "horas_ate_merge"].to_numpy()
    y = df.loc[df.grupo == "Humano", "horas_ate_merge"].to_numpy()
    mw = stats.mannwhitneyu(x, y, alternative="two-sided")
    a = efeito_A(x, y)
    ic_dif, ic_a = bootstrap(x, y, rng)
    return {
        "teste": "Mann-Whitney U bilateral",
        "n_agente": len(x), "n_humano": len(y),
        "mediana_agente_h": float(np.median(x)),
        "mediana_humano_h": float(np.median(y)),
        "dif_medianas_h": float(np.median(x) - np.median(y)),
        "IC95_dif_medianas_h": ic_dif,
        "U": float(mw.statistic), "p_valor": float(mw.pvalue),
        "alpha": ALPHA, "rejeita_H0": bool(mw.pvalue < ALPHA),
        "A_vargha_delaney": a, "IC95_A": ic_a,
        "magnitude": magnitude_A(a),
        "cliff_delta_equivalente": 2 * a - 1,
    }


# --- Análises exploratórias (fora da hipótese confirmatória) ---------------
def exploratoria_blocos(df: pd.DataFrame) -> dict:
    """Cada repositório é um bloco: mediana do agente x mediana humana."""
    med = df.groupby(["repo_url", "grupo"])["horas_ate_merge"].median().unstack()
    med = med.dropna()
    dif = med["Agente de IA"] - med["Humano"]
    w = stats.wilcoxon(med["Agente de IA"], med["Humano"], alternative="two-sided")
    return {"teste": "Wilcoxon pareado por repositório (exploratória)",
            "n_repos": int(len(med)), "mediana_das_diferencas_h": float(dif.median()),
            "pct_repos_agente_mais_rapido": float(100 * (dif < 0).mean()),
            "W": float(w.statistic), "p_valor": float(w.pvalue),
            "r_bisserial": r_bisserial(med["Agente de IA"], med["Humano"])}


def exploratoria_sem_instantaneos(df: pd.DataFrame, rng) -> dict:
    lim = LIMIAR_MERGE_INSTANTANEO_MIN / 60
    sub = df[df["horas_ate_merge"] >= lim]
    r = teste_principal(sub, rng)
    r["teste"] = f"Mann-Whitney sem merges < {LIMIAR_MERGE_INSTANTANEO_MIN:g} min (exploratória)"
    r["excluidos"] = int(len(df) - len(sub))
    return r


# ---------------------------------------------------------------------------
# 4. Figura
# ---------------------------------------------------------------------------
def figura(df: pd.DataFrame) -> None:
    plt.rcParams.update({"font.family": "serif", "font.size": 9})
    grupos = ["Humano", "Agente de IA"]
    # piso de 1 min só para caber no eixo log (não altera nenhuma estatística)
    dados = [np.clip(df.loc[df.grupo == g, "horas_ate_merge"], 1 / 60, None) for g in grupos]
    fig, ax = plt.subplots(figsize=(3.3, 2.4))
    ax.boxplot(dados, showfliers=False, widths=0.5,
               medianprops={"color": "black", "linewidth": 1.5})
    ax.set_yscale("log")
    ax.set_xticks([1, 2])
    ax.set_xticklabels([f"{g}\n(n = {len(d):,})".replace(",", ".") for g, d in zip(grupos, dados)])
    ax.set_ylabel("Tempo até o merge (log)")
    ax.set_yticks([1 / 60, 1, 24, 24 * 7, 24 * 30])
    ax.set_yticklabels(["1 min", "1 h", "1 dia", "1 sem.", "1 mês"])
    ax.grid(axis="y", color="0.85", linewidth=0.6)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.tight_layout()
    fig.savefig(DIR_FIG / "fig1_tempo_merge.png", dpi=300)
    fig.savefig(DIR_FIG / "fig1_tempo_merge.pdf")
    plt.close(fig)


# ---------------------------------------------------------------------------
def main() -> None:
    rng = np.random.default_rng(SEED)
    df, log = limpar(carregar())

    desc = descritiva(df)
    desc.to_csv(DIR_RES / "tabela_descritiva.csv")
    print("\nDescritiva (horas até o merge):\n", desc.to_string())

    desc_agente = descritiva(df, por="agent")
    desc_agente.to_csv(DIR_RES / "tabela_descritiva_por_agente.csv")

    principal = teste_principal(df, rng)
    print("\nTeste principal:", json.dumps(principal, indent=2, ensure_ascii=False))

    expl = [exploratoria_blocos(df), exploratoria_sem_instantaneos(df, rng)]
    for e in expl:
        print("\n", json.dumps(e, indent=2, ensure_ascii=False))

    figura(df)

    periodo = {g: [str(s.min().date()), str(s.max().date())]
               for g, s in df.groupby("grupo")["created_at"]}
    out = {"base": f"{HF_REPO}@{HF_REVISION}", "seed": SEED, "n_boot": N_BOOT,
           "limpeza": log, "periodo_criacao": periodo,
           "descritiva": desc.reset_index().to_dict(orient="records"),
           "principal": principal, "exploratorias": expl,
           "total_testes_realizados": 1 + len(expl)}
    (DIR_RES / "resultados.json").write_text(
        json.dumps(out, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    print("\nArquivos salvos em resultados/ e figuras/.")


if __name__ == "__main__":
    main()
