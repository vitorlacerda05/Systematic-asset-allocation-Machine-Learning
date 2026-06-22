"""
Alocação (estratégia + gestão de risco) e backtest com custos.

Transformamos as probabilidades P(bater caixa) em pesos de carteira:

  convicção_i = max(P_i - threshold, 0)            (só ativos atraentes)
  peso_bruto_i = convicção_i * (1 / vol_i)         (inverso da volatilidade)
  pesos_i = peso_bruto_i / soma(peso_bruto)        (normaliza p/ soma <= 1)
  cada peso é limitado a MAX_WEIGHT                 (diversificação)
  sobra (1 - soma pesos) -> CAIXA (Selic)           (piso de proteção)

Justificativa (gestão de risco, aula de trading sistemático):
  - inverso da vol = risk budgeting (cada ativo contribui risco parecido)
  - teto por ativo = limite de exposição por posição
  - caixa como default = controle de perdas quando o modelo não vê oportunidade
"""
import numpy as np
import pandas as pd

from config import (PROB_THRESHOLD, MAX_WEIGHT, COST_PER_TURNOVER,
                    ANNUALIZATION, RISK_FREE)


def _weights_for_month(sub: pd.DataFrame, threshold: float) -> pd.Series:
    """Calcula pesos dos ativos (índice=asset) para um mês. Resto vai p/ caixa."""
    conv = (sub["proba"] - threshold).clip(lower=0)
    vol = sub["vol_3"].replace(0, np.nan)
    inv_vol = 1.0 / vol
    raw = conv * inv_vol
    total = raw.sum()
    if total <= 0 or not np.isfinite(total):
        return pd.Series(0.0, index=sub.index.get_level_values("asset"))

    w = raw / total
    w.index = sub.index.get_level_values("asset")

    # Aplica teto por ativo e re-normaliza iterativamente
    for _ in range(10):
        over = w > MAX_WEIGHT
        if not over.any():
            break
        excess = (w[over] - MAX_WEIGHT).sum()
        w[over] = MAX_WEIGHT
        free = ~over & (w > 0)
        if not free.any():
            break
        w[free] += excess * w[free] / w[free].sum()
    return w.clip(upper=MAX_WEIGHT)


def backtest(pred: pd.DataFrame, panel: pd.DataFrame,
             threshold: float = PROB_THRESHOLD,
             cost: float = COST_PER_TURNOVER) -> dict:
    """
    pred: saída do walk-forward (proba, fwd_ret, fwd_rf por (date,asset))
    panel: painel com features (precisamos de vol_3 p/ o risk budgeting)
    Retorna dict com séries de retorno da estratégia e histórico de pesos.
    """
    # Anexa vol_3 às previsões (necessário para inverso da vol)
    pred = pred.join(panel[["vol_3"]], how="left")
    dates = np.sort(pred.index.get_level_values("date").unique())

    strat_rets, weight_rows, cash_hist = {}, [], {}
    prev_w = pd.Series(dtype=float)

    for d in dates:
        sub = pred[pred.index.get_level_values("date") == d]
        w = _weights_for_month(sub, threshold)
        w = w[w > 0]

        cash_w = max(0.0, 1.0 - w.sum())

        # Retornos realizados deste mês (d -> d+1)
        fwd = sub["fwd_ret"]
        fwd.index = sub.index.get_level_values("asset")
        rf = sub["fwd_rf"].iloc[0]

        port_ret = (w * fwd.reindex(w.index)).sum() + cash_w * rf

        # Custo de transação sobre o giro (mudança absoluta de pesos)
        all_assets = prev_w.index.union(w.index)
        turnover = (w.reindex(all_assets, fill_value=0)
                    - prev_w.reindex(all_assets, fill_value=0)).abs().sum()
        port_ret -= turnover * cost

        strat_rets[d] = port_ret
        cash_hist[d] = cash_w
        weight_rows.append(w)               # Series indexada por ativo
        prev_w = w

    rets = pd.Series(strat_rets).sort_index()
    cash = pd.Series(cash_hist).sort_index()
    wdf = pd.DataFrame(weight_rows, index=list(strat_rets.keys())).fillna(0.0)
    wdf = wdf.sort_index()
    return {"returns": rets, "weights": wdf, "cash": cash}


def benchmarks(pred: pd.DataFrame, panel: pd.DataFrame) -> pd.DataFrame:
    """
    Carteiras de comparação, alinhadas às mesmas datas da estratégia:
      - IBOV (buy & hold)
      - Equal Weight (todos os ativos investíveis igualmente)
      - CDI/Selic (100% caixa)
      - 60/40 (60% IBOV, 40% IMAB)
    """
    dates = np.sort(pred.index.get_level_values("date").unique())
    out = {}
    fwd = pred["fwd_ret"].unstack("asset").reindex(dates)
    rf = pred.groupby(level="date")["fwd_rf"].first().reindex(dates)

    out["IBOV"] = fwd["IBOV"]
    out["Pesos iguais"] = fwd.mean(axis=1)
    out["CDI"] = rf
    out["60/40"] = 0.6 * fwd["IBOV"] + 0.4 * fwd["IMAB"]
    return pd.DataFrame(out)
