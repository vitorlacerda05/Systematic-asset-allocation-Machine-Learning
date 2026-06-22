"""
Engenharia de features.

Produzimos um PAINEL em formato longo, com índice (data, ativo). Para cada
par (mês, classe de ativo) montamos um vetor de atributos que COMBINA:

  (A) Sinais técnicos do próprio ativo  -> momentum, volatilidade, reversão
  (B) Contexto macro compartilhado      -> juro real, inflação, dólar, curva

Essa combinação (técnico + macro, em vários ativos ao mesmo tempo) é o que
diferencia a estratégia das regras de uma série só vistas em aula.

IMPORTANTE (anti-lookahead): toda feature da linha do mês t usa apenas
informação disponível ATÉ t. O alvo (target) que olha t+1 é criado em labels.py.
"""
import numpy as np
import pandas as pd

from config import (INVESTABLE, MOMENTUM_WINDOWS, VOL_WINDOWS, MA_WINDOWS,
                    RISK_FREE)
from data import load_levels, monthly_returns


def _yoy(series: pd.Series) -> pd.Series:
    """Variação em 12 meses (para níveis de preço, ex.: IPCA, IGPM)."""
    return series.pct_change(12)


def build_macro_features(levels: pd.DataFrame) -> pd.DataFrame:
    """
    Features macro COMPARTILHADAS por todos os ativos num dado mês.
    Capturam o 'regime' de mercado.
    """
    rets = monthly_returns(levels)
    m = pd.DataFrame(index=levels.index)

    # Inflação acumulada em 12m (níveis IPCA/IGPM são índices de preço)
    ipca_yoy = _yoy(levels["IPCA"])
    igpm_yoy = _yoy(levels["IGPM"])
    m["ipca_yoy"] = ipca_yoy
    m["igpm_yoy"] = igpm_yoy

    # Juro real ex-post: Selic meta (a.a., em %) menos inflação 12m
    selic = levels["SELIC-META"] / 100.0
    m["selic_meta"] = selic
    m["juro_real"] = selic - ipca_yoy

    # Variação do juro (afrouxando/apertando) -> regime monetário
    m["delta_selic_3m"] = selic - selic.shift(3)

    # Inclinação implícita da curva de inflação: momentum 12m de NTN-B longa
    # menos a curta. Spread positivo => mercado precificando juros longos caindo.
    m["curva_imab"] = rets["IMAB"].rolling(12).mean() - rets["IMAB5"].rolling(12).mean()

    # Dólar: tendência (risco/aversão) em 1,3,6m
    for w in (1, 3, 6):
        m[f"usd_mom_{w}"] = levels["USD"].pct_change(w)

    # Equity global (S&P em US$): tendência 3 e 6m
    for w in (3, 6):
        m[f"spx_mom_{w}"] = levels["SP500USD"].pct_change(w)

    return m


def build_asset_features(levels: pd.DataFrame, rets: pd.DataFrame) -> dict:
    """
    Para cada ativo investível, um DataFrame de features próprias indexado
    por data. Retorna {ativo: DataFrame}.
    """
    rf_ret = rets[RISK_FREE]
    out = {}
    for a in INVESTABLE:
        r = rets[a]
        lv = levels[a]
        f = pd.DataFrame(index=levels.index)

        # (1) Momentum multi-horizonte (seguidor de tendência)
        for w in MOMENTUM_WINDOWS:
            f[f"mom_{w}"] = lv.pct_change(w)

        # (2) Volatilidade realizada (gestão de risco / regime de risco)
        for w in VOL_WINDOWS:
            f[f"vol_{w}"] = r.rolling(w).std()

        # (3) Reversão à média: distância do preço à média móvel (z-score)
        for w in MA_WINDOWS:
            ma = lv.rolling(w).mean()
            sd = lv.rolling(w).std()
            f[f"dist_ma_{w}"] = (lv - ma) / sd

        # (4) Momentum em EXCESSO ao caixa (o que realmente importa p/ alocar)
        for w in MOMENTUM_WINDOWS:
            f[f"xs_mom_{w}"] = lv.pct_change(w) - rf_ret.rolling(w).sum()

        # (5) Último retorno e aceleração (mudança no momentum de 3m)
        f["ret_1"] = r
        f["accel_3"] = lv.pct_change(3) - lv.pct_change(3).shift(3)

        out[a] = f
    return out


def build_panel(one_hot_asset: bool = True) -> pd.DataFrame:
    """
    Monta o painel longo final: índice (data, ativo) com todas as features
    (próprias + macro). NÃO inclui o target (criado em labels.py).
    """
    levels = load_levels()
    rets = monthly_returns(levels)

    macro = build_macro_features(levels)
    per_asset = build_asset_features(levels, rets)

    frames = []
    for a, f in per_asset.items():
        df = f.join(macro, how="left")          # acopla o contexto macro
        df["asset"] = a
        df["date"] = df.index
        frames.append(df)

    panel = pd.concat(frames, ignore_index=True)

    if one_hot_asset:
        # Identidade do ativo como variável categórica (one-hot): permite ao
        # modelo aprender prêmios de risco distintos por classe.
        dummies = pd.get_dummies(panel["asset"], prefix="is")
        panel = pd.concat([panel, dummies], axis=1)

    panel = panel.set_index(["date", "asset"]).sort_index()
    return panel


def feature_columns(panel: pd.DataFrame) -> list:
    """Colunas que entram no modelo (tudo menos colunas auxiliares/target)."""
    drop = {"target", "fwd_ret", "fwd_rf"}
    return [c for c in panel.columns if c not in drop]


if __name__ == "__main__":
    panel = build_panel()
    print("Painel:", panel.shape, "(linhas = mês x ativo)")
    print("N features:", len(feature_columns(panel)))
    print("\nFeatures:")
    for c in feature_columns(panel):
        print("  -", c)
    print("\nAmostra (últimas linhas de um mês):")
    last_date = panel.index.get_level_values("date").max()
    cols_show = ["mom_1", "mom_12", "vol_12", "dist_ma_12", "juro_real", "usd_mom_3"]
    print(panel.loc[last_date][cols_show].round(3).to_string())
