"""
Configuração central da estratégia de alocação sistemática.

Mantemos todos os "parâmetros de projeto" num só lugar para que o
experimento seja reprodutível e fácil de ajustar (boa prática para
evitar números mágicos espalhados pelo código).
"""
from pathlib import Path

# ----------------------------------------------------------------------
# Caminhos
# ----------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "context" / "v6-DB-Indices.xlsx"
SHEET = "IDIV"
OUTPUT_DIR = ROOT / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

# ----------------------------------------------------------------------
# Universo investível (classes de ativos)
# Cada chave é uma COLUNA de nível (preço/índice) no Excel; calculamos
# o retorno mensal a partir dela.
# ----------------------------------------------------------------------
RISK_FREE = "SELIC-ACC"            # índice acumulado da Selic = "caixa"/CDI

# Classes de ativos sobre as quais o modelo decide alocar.
# Incluímos setores de ações BR (IDIV/UTIL/IFNC) para AUMENTAR a "largura"
# de apostas independentes (Lei Fundamental da Gestão Ativa: IR = IC*sqrt(BR)).
INVESTABLE = [
    "IBOV",      # Ações Brasil (amplo)
    "SP500BR",   # Ações EUA em R$ (embute câmbio)
    "OURO",      # Ouro (proteção / descorrelação)
    "IMAB",      # Renda fixa atrelada à inflação (NTN-B longas)
    "IMAB5",     # Renda fixa inflação (duration curta)
    "IDIV",      # Ações BR - dividendos
    "UTIL",      # Ações BR - utilities (defensivo)
    "IFNC",      # Ações BR - financeiro (cíclico)
]

# Séries macro usadas SÓ como features (não são investíveis)
MACRO = ["USD", "IPCA", "IGPM", "SELIC-META", "SP500USD"]

# ----------------------------------------------------------------------
# Parâmetros de features
# ----------------------------------------------------------------------
MOMENTUM_WINDOWS = [1, 3, 6, 12]   # horizontes de momentum (meses)
VOL_WINDOWS = [3, 6, 12]           # janelas de volatilidade
MA_WINDOWS = [6, 12]               # médias para "distância da média" (reversão)

# ----------------------------------------------------------------------
# Parâmetros de modelo / validação
# ----------------------------------------------------------------------
MIN_TRAIN_MONTHS = 60      # mínimo de histórico antes da 1a previsão (5 anos)
RANDOM_STATE = 42

# ----------------------------------------------------------------------
# Parâmetros de alocação (gestão de risco) e custos
# ----------------------------------------------------------------------
PROB_THRESHOLD = 0.50      # só aloca em ativo com P(bater caixa) acima disso
MAX_WEIGHT = 0.35          # teto por ativo (diversificação)
COST_PER_TURNOVER = 0.0010 # 0,10% sobre o giro (corretagem+slippage+impostos)
ANNUALIZATION = 12         # dados mensais
