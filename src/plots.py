"""Gráficos para o relatório (salvos em outputs/)."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from config import OUTPUT_DIR
from metrics import equity_curve


def plot_equity(strat_rets, bench, fname="equity_curve.png"):
    fig, ax = plt.subplots(figsize=(11, 6))
    equity_curve(strat_rets).plot(ax=ax, lw=2.5, color="black",
                                  label="Estratégia ML")
    for col in bench.columns:
        equity_curve(bench[col]).plot(ax=ax, lw=1.2, alpha=0.8, label=col)
    ax.set_yscale("log")
    ax.set_title("Curva de patrimônio (escala logarítmica)")
    ax.set_ylabel("Patrimônio (base 1,0)")
    ax.set_xlabel("")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / fname, dpi=130)
    plt.close(fig)


def plot_drawdown(strat_rets, bench, fname="drawdown.png"):
    fig, ax = plt.subplots(figsize=(11, 4.5))
    for name, r in [("Estratégia ML", strat_rets), ("IBOV", bench["IBOV"]),
                    ("CDI", bench["CDI"])]:
        eq = equity_curve(r)
        dd = eq / eq.cummax() - 1.0
        dd.plot(ax=ax, label=name, lw=1.5)
    ax.set_title("Drawdown (queda a partir do topo)")
    ax.set_ylabel("Queda do topo")
    ax.set_xlabel("")
    ax.legend(); ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / fname, dpi=130)
    plt.close(fig)


def plot_weights(weights, cash, fname="weights.png"):
    fig, ax = plt.subplots(figsize=(11, 6))
    w = weights.copy()
    w["CAIXA"] = cash.reindex(w.index).values
    w = w.clip(lower=0)
    ax.stackplot(w.index, *[w[c].values for c in w.columns], labels=w.columns)
    ax.set_title("Alocação ao longo do tempo")
    ax.set_ylabel("Peso")
    ax.set_xlabel("")
    ax.set_ylim(0, 1)
    ax.legend(loc="upper left", ncol=5, fontsize=8)
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / fname, dpi=130)
    plt.close(fig)


def plot_feature_importance(importances: pd.Series, fname="feature_importance.png"):
    fig, ax = plt.subplots(figsize=(9, 7))
    importances.sort_values().tail(20).plot.barh(ax=ax, color="steelblue")
    ax.set_title("Importância dos atributos (floresta aleatória)")
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / fname, dpi=130)
    plt.close(fig)
