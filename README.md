# Alocação Sistemática em Classes de Ativos com Aprendizado Supervisionado

**SSC0964 — Introdução à Computação no Mercado Financeiro — Trabalho 2**

Estratégia de alocação sistemática entre classes de ativos que usa
classificação supervisionada para decidir, mês a mês, quanto alocar em cada
classe versus o caixa (CDI/Selic).

---

## 1. Ideia central (e o que a torna original)

Em vez de aplicar uma regra técnica sobre uma única série (cruzamento de médias,
Bandas de Bollinger etc., vistas em aula), tratamos a alocação como um problema
**cross-sectional** de aprendizado supervisionado:

- **Saída (rótulo) — original:** para cada classe de ativo e cada mês, prever a
  **probabilidade de o ativo superar o CDI no mês seguinte**
  (`retorno_ativo(t+1) > retorno_Selic(t+1)`). Não prevemos "sobe/desce", e sim
  *"vale a pena estar neste ativo em vez de ficar no caixa?"*. A probabilidade
  vira **tamanho da posição**.
- **Entrada (features) — original:** combinamos sinais **técnicos** de cada ativo
  (momentum multi-horizonte, volatilidade, distância da média / reversão,
  momentum em excesso ao caixa, aceleração) com um **contexto macro**
  compartilhado (juro real Selic−IPCA, variação da Selic, momentum de inflação
  IPCA/IGP-M, inclinação implícita da curva via IMA-B vs IMA-B 5, tendência do
  dólar e do S&P global). É a fusão técnico + macro, sobre várias classes ao
  mesmo tempo, que difere das estratégias de série única vistas em aula.

A decisão por classe aumenta a **largura de apostas independentes** — alinhado à
*Lei Fundamental da Gestão Ativa* (`IR = IC · √BR`): mais apostas razoáveis
elevam o information ratio.

## 2. Dados

Arquivo `context/v6-DB-Indices.xlsx` (aba `IDIV`): série **mensal**,
Dez/1999 → Mai/2026 (318 meses).

- **Classes investíveis:** IBOV, SP500BR (ações EUA em R$), OURO, IMA-B, IMA-B 5,
  IDIV, UTIL, IFNC.
- **Caixa / risk-free:** SELIC-ACC (índice acumulado da Selic).
- **Macro (apenas features):** USD, IPCA, IGP-M, SELIC-META, SP500USD.

## 3. Pipeline (módulos em `src/`)

| Módulo | Papel |
|---|---|
| `config.py` | Parâmetros centrais (universo, janelas, custos, limites). |
| `data.py` | Carrega o Excel, converte datas PT-BR, calcula retornos. |
| `features.py` | Engenharia de features (técnicas + macro) → painel longo. |
| `labels.py` | Cria o rótulo "bater o CDI" (1 passo à frente, sem lookahead). |
| `model.py` | Modelos: Logistic, **Random Forest**, **Gradient Boosting**, **MLP**. |
| `walkforward.py` | Validação out-of-sample com janela expansível. |
| `allocation.py` | Converte probabilidades em pesos (gestão de risco) + custos. |
| `metrics.py` | CAGR, vol, Sharpe, max drawdown, taxa de acerto, payoff. |
| `plots.py` | Gráficos (curva de patrimônio, drawdown, pesos, importâncias). |
| `main.py` | Orquestra tudo e salva resultados em `outputs/`. |

## 4. Modelagem supervisionada

Comparamos quatro algoritmos vistos na aula de Aprendizado de Máquina:
regressão logística (baseline), **Random Forest**, **Gradient Boosting** e
**Rede Neural MLP**, além de um **ensemble** (média das probabilidades dos três
de ML). Hiperparâmetros são conservadores (profundidade/regularização limitadas)
para conter **overfitting**.

**Validação walk-forward (expansível):** a cada mês *d*, o modelo é treinado só
com dados cujo resultado já se realizou (`date < d`) e prevê as classes em *d*.
Não há vazamento de informação futura — é o análogo honesto de rodar a
estratégia ao vivo.

## 5. Alocação e gestão de risco

Para cada mês, a partir das probabilidades `P_i`:

```
convicção_i = max(P_i − 0,5; 0)              # só ativos atraentes
peso_bruto_i = convicção_i × (1 / vol_i)     # risk budgeting (inverso da vol)
pesos = normaliza(peso_bruto), teto de 35% por ativo
caixa = 1 − Σ pesos                          # piso de proteção em Selic
```

Aplica-se **custo de transação de 0,10% sobre o giro** (corretagem + slippage +
impostos, conforme o modelo de custos da aula).

## 6. Avaliação

Métricas (aula + mercado): **Sharpe**, CAGR, volatilidade, **máximo drawdown**,
**taxa de acerto**, **payoff**, retorno total; e métricas preditivas
(acurácia, AUC, **IC** = correlação entre convicção e excesso realizado).
Benchmarks: **IBOV** (buy & hold), **Equal Weight**, **CDI** (100% caixa) e
**60/40** (IBOV/IMA-B).

## 7. Como executar

```bash
pip install -r requirements.txt
cd src
python main.py
```

Resultados (tabelas `.csv` e gráficos `.png`) são gravados em `outputs/`.

## 8. Resultados (out-of-sample, jan/2005 → mai/2026)

**Qualidade preditiva** (acima do acaso de 52,6%):

| Modelo | Acurácia | AUC | IC |
|---|---|---|---|
| Random Forest | 0,543 | 0,552 | 0,052 |
| Gradient Boosting | 0,534 | 0,548 | 0,058 |
| Logistic | 0,513 | 0,524 | 0,054 |
| MLP | 0,521 | 0,514 | 0,016 |

**Performance da carteira** (Sharpe = excesso sobre o CDI):

| Carteira | CAGR | Vol | Sharpe | Max DD | Taxa acerto |
|---|---|---|---|---|---|
| **Estratégia ML (Random Forest)** | **13,8%** | **7,0%** | **0,43** | **−7,7%** | 80,5% |
| Equal Weight | 14,3% | 10,8% | 0,36 | −21,9% | 65,8% |
| 60/40 | 11,0% | 14,8% | 0,09 | −33,3% | 58,8% |
| CDI (caixa) | 10,7% | 1,0% | — | 0,0% | 100% |
| IBOV (buy & hold) | 9,3% | 22,1% | 0,06 | −49,6% | 57,2% |

**Leitura:** a estratégia entrega retorno **maior que o IBOV** com **um terço da
volatilidade** e drawdown máximo de apenas −7,7% (vs. −49,6% do IBOV). O melhor
modelo foi o **Random Forest** (melhor Sharpe e menor drawdown).

**Features mais importantes** (Random Forest): momentum do dólar (6/3/1m),
variação da Selic em 3m, IPCA 12m, IGP-M 12m, juro real e momentum do S&P
global. Ou seja, o modelo aprendeu que o **regime macro** (câmbio, política
monetária, inflação) é o que mais determina se uma classe de ativo bate o caixa
— exatamente a aposta de originalidade da estratégia.

Gráficos em `outputs/`: `equity_curve.png`, `drawdown.png`, `weights.png`,
`feature_importance.png`.

## 9. Limitações e cuidados

- IBOV é índice de preço (sem dividendos); IDIV/UTIL/IFNC e IMA-B são de retorno
  total — comparações entre classes têm essa assimetria.
- Custos são uma aproximação; impacto de mercado real depende do volume.
- Resultados são *backtest*; desempenho passado não garante futuro.
