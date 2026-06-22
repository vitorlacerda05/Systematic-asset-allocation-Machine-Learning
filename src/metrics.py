"""
Métricas de avaliação de performance (mensais -> anualizadas).

Inclui as métricas citadas em aula (taxa de acerto, payoff) e as padrão de
mercado (CAGR, vol, Sharpe, max drawdown), todas calculadas sobre a série de
retornos mensais da carteira.
"""
import numpy as np
import pandas as pd

from config import ANNUALIZATION, RISK_FREE


def equity_curve(returns: pd.Series) -> pd.Series:
    """Curva de patrimônio (base 1.0) a partir de retornos mensais."""
    return (1.0 + returns.fillna(0)).cumprod()


def max_drawdown(returns: pd.Series) -> float:
    eq = equity_curve(returns)
    dd = eq / eq.cummax() - 1.0
    return dd.min()


def perf_metrics(returns: pd.Series, rf: pd.Series | None = None) -> dict:
    r = returns.dropna()
    n = len(r)
    if n == 0:
        return {}
    ann = ANNUALIZATION
    cagr = (1 + r).prod() ** (ann / n) - 1
    vol = r.std() * np.sqrt(ann)

    if rf is not None:
        excess = (r - rf.reindex(r.index)).dropna()
        sharpe = (excess.mean() * ann) / (excess.std() * np.sqrt(ann)) \
            if excess.std() > 0 else np.nan
    else:
        sharpe = (r.mean() * ann) / vol if vol > 0 else np.nan

    wins = r[r > 0]
    losses = r[r < 0]
    hit = len(wins) / n
    payoff = (wins.mean() / abs(losses.mean())) if len(losses) else np.nan

    return {
        "CAGR": cagr,
        "Vol": vol,
        "Sharpe": sharpe,
        "MaxDD": max_drawdown(r),
        "HitRate": hit,
        "Payoff": payoff,
        "TotalReturn": (1 + r).prod() - 1,
    }


def metrics_table(strat_rets: pd.Series, bench: pd.DataFrame,
                  rf: pd.Series) -> pd.DataFrame:
    rows = {"Estrategia_ML": perf_metrics(strat_rets, rf)}
    for col in bench.columns:
        rows[col] = perf_metrics(bench[col], rf)
    tab = pd.DataFrame(rows).T
    return tab[["CAGR", "Vol", "Sharpe", "MaxDD", "HitRate", "Payoff", "TotalReturn"]]
