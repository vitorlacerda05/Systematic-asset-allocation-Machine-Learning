"""
Carregamento e limpeza da base de índices (aba IDIV).

A coluna 'Data' vem como rótulo em português ("Dez-1999", "Jan-2000"...),
então precisamos converter para um índice temporal de verdade (pandas
DatetimeIndex) para conseguir ordenar, fatiar e reamostrar corretamente.
"""
import pandas as pd

from config import DATA_FILE, SHEET, INVESTABLE, MACRO, RISK_FREE

# Abreviações de mês em português -> número
_MESES = {
    "jan": 1, "fev": 2, "mar": 3, "abr": 4, "mai": 5, "jun": 6,
    "jul": 7, "ago": 8, "set": 9, "out": 10, "nov": 11, "dez": 12,
}


def _parse_data_ptbr(s: str) -> pd.Timestamp:
    """Converte 'Dez-1999' -> Timestamp no último dia do mês."""
    mes, ano = str(s).strip().lower().split("-")
    ts = pd.Timestamp(year=int(ano), month=_MESES[mes[:3]], day=1)
    return ts + pd.offsets.MonthEnd(0)


def load_levels() -> pd.DataFrame:
    """
    Retorna um DataFrame de NÍVEIS (preços/índices) indexado por data,
    contendo apenas as colunas que vamos usar.
    """
    raw = pd.read_excel(DATA_FILE, sheet_name=SHEET, header=0)
    raw["Data"] = raw["Data"].map(_parse_data_ptbr)
    raw = raw.set_index("Data").sort_index()

    cols = INVESTABLE + MACRO + [RISK_FREE]
    cols = [c for c in cols if c in raw.columns]
    levels = raw[cols].astype(float)
    return levels


def monthly_returns(levels: pd.DataFrame) -> pd.DataFrame:
    """Retorno simples mês a mês a partir dos níveis."""
    return levels.pct_change()


if __name__ == "__main__":
    lv = load_levels()
    print("Período:", lv.index.min().date(), "->", lv.index.max().date())
    print("Meses:", len(lv))
    print("Colunas:", list(lv.columns))
    rets = monthly_returns(lv)[INVESTABLE]
    print("\nRetorno mensal médio (anualizado, %):")
    print((rets.mean() * 12 * 100).round(2).to_string())
    print("\nVolatilidade anualizada (%):")
    print((rets.std() * (12 ** 0.5) * 100).round(2).to_string())
