"""
Validação walk-forward (janela expansível, out-of-sample).

A cada mês de decisão d (a partir de MIN_TRAIN_MONTHS):
  1. treina o modelo com TODAS as linhas cujo rótulo já se realizou (date < d)
  2. prevê P(bater o caixa) para cada ativo na data d
  3. essa probabilidade será usada para alocar no mês d->d+1

Isso evita lookahead: nenhuma informação futura entra no treino. É o análogo
honesto de rodar a estratégia ao vivo, mês a mês.
"""
import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.metrics import accuracy_score, roc_auc_score

from config import MIN_TRAIN_MONTHS
from labels import build_labeled_panel


def run_walkforward(panel, feat_cols, model, retrain_every: int = 1):
    """
    Retorna DataFrame com índice (date, asset) e colunas:
      proba   -> P(bater caixa) previsto out-of-sample
      target  -> rótulo realizado (0/1)
      fwd_ret -> retorno realizado d->d+1 do ativo
      fwd_rf  -> retorno realizado d->d+1 do caixa
    """
    dates = np.sort(panel.index.get_level_values("date").unique())
    decision_dates = dates[MIN_TRAIN_MONTHS:]

    rows = []
    fitted = None
    for i, d in enumerate(decision_dates):
        train = panel[panel.index.get_level_values("date") < d].dropna(
            subset=["target"] + feat_cols)
        test = panel[panel.index.get_level_values("date") == d].dropna(
            subset=feat_cols)
        if train.empty or test.empty:
            continue

        if fitted is None or i % retrain_every == 0:
            fitted = clone(model)
            fitted.fit(train[feat_cols].values, train["target"].astype(int).values)

        proba = fitted.predict_proba(test[feat_cols].values)[:, 1]
        res = test[["target", "fwd_ret", "fwd_rf"]].copy()
        res["proba"] = proba
        rows.append(res)

    return pd.concat(rows)


def classification_report(pred: pd.DataFrame) -> dict:
    """Métricas out-of-sample agregadas."""
    valid = pred.dropna(subset=["target", "proba"])
    y = valid["target"].astype(int).values
    p = valid["proba"].values
    yhat = (p > 0.5).astype(int)

    # IC (Information Coefficient): correlação entre convicção e excesso realizado
    xs = (valid["fwd_ret"] - valid["fwd_rf"]).values
    ic = np.corrcoef(p, xs)[0, 1]

    return {
        "n": len(valid),
        "accuracy": accuracy_score(y, yhat),
        "auc": roc_auc_score(y, p) if len(np.unique(y)) > 1 else float("nan"),
        "base_rate": y.mean(),
        "IC": ic,
    }


if __name__ == "__main__":
    from model import make_models
    panel, feat_cols = build_labeled_panel()
    print(f"Rodando walk-forward (treino expansível, mínimo "
          f"{MIN_TRAIN_MONTHS} meses)...\n")
    print(f"{'Modelo':<18}{'N':>7}{'Acc':>8}{'AUC':>8}{'Base':>8}{'IC':>8}")
    for name, mdl in make_models().items():
        pred = run_walkforward(panel, feat_cols, mdl)
        r = classification_report(pred)
        print(f"{name:<18}{r['n']:>7}{r['accuracy']:>8.3f}{r['auc']:>8.3f}"
              f"{r['base_rate']:>8.3f}{r['IC']:>8.3f}")
