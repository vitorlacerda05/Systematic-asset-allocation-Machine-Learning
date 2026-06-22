"""
Modelos de aprendizado supervisionado (classificação).

Comparamos os algoritmos vistos na aula de Aprendizado de Máquina:
  - Logistic Regression  -> baseline linear interpretável
  - Random Forest        -> ensemble de árvores (aula: árvores + random forests)
  - Gradient Boosting    -> boosting de árvores
  - MLP                  -> Rede Neural (aula: RNA / Perceptron multicamadas)

MLP e Logistic exigem padronização das features (StandardScaler); árvores não,
mas usar Pipeline uniformiza a interface.
"""
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from config import RANDOM_STATE


def make_models() -> dict:
    """Retorna {nome: estimador sklearn} com hiperparâmetros conservadores
    (anti-overfitting: profundidade/limites controlados)."""
    rs = RANDOM_STATE
    return {
        "Logistic": Pipeline([
            ("scaler", StandardScaler()),
            ("clf", LogisticRegression(max_iter=1000, C=0.5,
                                       class_weight="balanced", random_state=rs)),
        ]),
        "RandomForest": RandomForestClassifier(
            n_estimators=300, max_depth=5, min_samples_leaf=30,
            max_features="sqrt", class_weight="balanced_subsample",
            random_state=rs, n_jobs=-1),
        "GradientBoosting": GradientBoostingClassifier(
            n_estimators=200, max_depth=3, learning_rate=0.03,
            subsample=0.8, random_state=rs),
        "MLP": Pipeline([
            ("scaler", StandardScaler()),
            ("clf", MLPClassifier(hidden_layer_sizes=(32, 16), alpha=1e-2,
                                  max_iter=500, early_stopping=True,
                                  random_state=rs)),
        ]),
    }
