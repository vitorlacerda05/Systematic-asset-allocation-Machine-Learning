"""
Criação do rótulo (saída) supervisionado.

Alvo escolhido (ORIGINAL): classificação binária
    y(d) = 1  se  retorno do ativo de d->d+1  >  retorno do caixa (Selic) de d->d+1
    y(d) = 0  caso contrário

Ou seja: "vale a pena estar neste ativo em vez de ficar no CDI no próximo mês?".
A probabilidade prevista P(y=1) será usada como CONVICÇÃO para dimensionar a
posição (etapa de alocação).

Timing (sem lookahead): em pé no fim do mês d usamos features(d) -> prevemos
y(d), cujo resultado só se realiza em d+1. Guardamos fwd_ret(d) (retorno de
d->d+1) para o backtest.
"""
import pandas as pd

from config import RISK_FREE
from data import load_levels, monthly_returns
from features import build_panel, feature_columns


def build_labeled_panel(one_hot_asset: bool = True):
    """
    Retorna (panel, feat_cols):
      panel: índice (date, asset) com features + 'fwd_ret', 'fwd_rf', 'target'
      feat_cols: lista de colunas de entrada do modelo
    """
    panel = build_panel(one_hot_asset=one_hot_asset)
    feat_cols = feature_columns(panel)

    levels = load_levels()
    rets = monthly_returns(levels)
    rf = rets[RISK_FREE]

    # Retorno futuro (d -> d+1) de cada ativo e do caixa
    fwd = rets.shift(-1)            # retorno realizado no mês SEGUINTE
    fwd_rf = rf.shift(-1)

    panel = panel.copy()
    # Mapear fwd_ret e fwd_rf para cada linha (date, asset)
    dates = panel.index.get_level_values("date")
    assets = panel.index.get_level_values("asset")

    panel["fwd_ret"] = [fwd.loc[d, a] if d in fwd.index else float("nan")
                        for d, a in zip(dates, assets)]
    panel["fwd_rf"] = fwd_rf.reindex(dates).values
    panel["target"] = (panel["fwd_ret"] > panel["fwd_rf"]).astype("float")

    # Linhas sem fwd_ret (último mês) não têm rótulo -> target NaN
    panel.loc[panel["fwd_ret"].isna(), "target"] = float("nan")
    return panel, feat_cols


if __name__ == "__main__":
    panel, feat_cols = build_labeled_panel()
    valid = panel.dropna(subset=["target"])
    print("Linhas com rótulo:", len(valid))
    print("\nFrequência de 'bateu o caixa' por ativo (%):")
    freq = valid.groupby(level="asset")["target"].mean().mul(100).round(1)
    print(freq.to_string())
    print("\nMédia geral (%):", round(valid["target"].mean() * 100, 1))
