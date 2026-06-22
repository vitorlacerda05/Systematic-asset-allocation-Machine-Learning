"""
Pipeline completo: dados -> features -> rótulos -> walk-forward (4 modelos)
-> alocação/backtest -> métricas -> gráficos.

Estratégia: alocação sistemática entre classes de ativos via classificação
supervisionada de "bater o CDI", com pesos por convicção x inverso da vol.

Uso:  python main.py
Saídas em outputs/: tabelas CSV e gráficos PNG.
"""
import pickle
import sys
import numpy as np
import pandas as pd

from config import OUTPUT_DIR, RISK_FREE, MIN_TRAIN_MONTHS, RANDOM_STATE
from labels import build_labeled_panel
from model import make_models
from walkforward import run_walkforward, classification_report
from allocation import backtest, benchmarks
from metrics import metrics_table
import plots


def main():
    pd.set_option("display.width", 200)
    print("=" * 70)
    print("ALOCAÇÃO SISTEMÁTICA EM CLASSES DE ATIVOS — Aprendizado Supervisionado")
    print("=" * 70)

    print("\n[1/5] Montando painel de features + rótulos...")
    panel, feat_cols = build_labeled_panel()
    print(f"      {panel.shape[0]} linhas (mês x ativo), {len(feat_cols)} features.")

    print("\n[2/5] Validação walk-forward out-of-sample (4 modelos)...")
    cache = OUTPUT_DIR / "preds_cache.pkl"
    use_cache = "--cache" in sys.argv and cache.exists()
    models = make_models()
    preds, clf_rows = {}, {}
    if use_cache:
        print("      (usando previsões em cache: outputs/preds_cache.pkl)")
        preds = pickle.load(open(cache, "rb"))
        for name in list(models) + ["Ensemble"]:
            if name in preds:
                clf_rows[name] = classification_report(preds[name])
    else:
        for name, mdl in models.items():
            print(f"      treinando {name} ...", flush=True)
            p = run_walkforward(panel, feat_cols, mdl)
            preds[name] = p
            clf_rows[name] = classification_report(p)

    # Ensemble: média das probabilidades dos 3 modelos de ML (bônus, robusto)
    if not use_cache:
        ml_names = ["RandomForest", "GradientBoosting", "MLP"]
        ens = preds["RandomForest"][["target", "fwd_ret", "fwd_rf"]].copy()
        ens["proba"] = np.mean([preds[n]["proba"].reindex(ens.index)
                                for n in ml_names], axis=0)
        preds["Ensemble"] = ens
        clf_rows["Ensemble"] = classification_report(ens)
        pickle.dump(preds, open(cache, "wb"))

    clf_tab = pd.DataFrame(clf_rows).T
    print("\n--- Qualidade preditiva (out-of-sample) ---")
    print(clf_tab.round(3).to_string())
    clf_tab.to_csv(OUTPUT_DIR / "classification_metrics.csv")

    print("\n[3/5] Backtest da alocação (com custos) para cada modelo...")
    bench = benchmarks(preds["RandomForest"], panel)
    rf_series = preds["RandomForest"].groupby(level="date")["fwd_rf"].first()

    perf_rows, bt_cache = {}, {}
    from metrics import perf_metrics
    for name, p in preds.items():
        bt = backtest(p, panel)
        bt_cache[name] = bt
        perf_rows[name] = perf_metrics(bt["returns"], rf_series)

    perf_strat = pd.DataFrame(perf_rows).T
    perf_bench = pd.DataFrame({c: perf_metrics(bench[c], rf_series)
                               for c in bench.columns}).T
    perf_all = pd.concat([perf_strat, perf_bench])
    cols = ["CAGR", "Vol", "Sharpe", "MaxDD", "HitRate", "Payoff", "TotalReturn"]
    perf_all = perf_all[cols]

    print("\n--- Performance (estratégias por modelo + benchmarks) ---")
    show = perf_all.copy()
    for c in ["CAGR", "Vol", "MaxDD", "HitRate", "TotalReturn"]:
        show[c] = (show[c] * 100).round(1)
    show["Sharpe"] = show["Sharpe"].round(2)
    show["Payoff"] = show["Payoff"].round(2)
    print(show.to_string())
    perf_all.to_csv(OUTPUT_DIR / "performance_metrics.csv")

    print("\n[4/5] Selecionando melhor estratégia (por Sharpe) e gerando gráficos...")
    best = perf_strat["Sharpe"].idxmax()
    print(f"      Melhor modelo: {best}")
    bt = bt_cache[best]
    plots.plot_equity(bt["returns"], bench)
    plots.plot_drawdown(bt["returns"], bench)
    plots.plot_weights(bt["weights"], bt["cash"])

    print("\n[5/5] Importância das features (Random Forest no histórico completo)...")
    from sklearn.ensemble import RandomForestClassifier
    full = panel.dropna(subset=["target"] + feat_cols)
    rf_imp = RandomForestClassifier(n_estimators=300, max_depth=5,
                                    min_samples_leaf=30, max_features="sqrt",
                                    class_weight="balanced_subsample",
                                    random_state=RANDOM_STATE, n_jobs=-1)
    rf_imp.fit(full[feat_cols].values, full["target"].astype(int).values)
    imp = pd.Series(rf_imp.feature_importances_, index=feat_cols)
    plots.plot_feature_importance(imp)
    imp.sort_values(ascending=False).to_csv(OUTPUT_DIR / "feature_importance.csv")

    print("\nConcluído. Saídas em:", OUTPUT_DIR)
    print("Top 8 features:")
    print(imp.sort_values(ascending=False).head(8).round(4).to_string())


if __name__ == "__main__":
    main()
