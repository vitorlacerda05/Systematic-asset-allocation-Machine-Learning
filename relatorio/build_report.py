# -*- coding: utf-8 -*-
"""
Gera o relatório científico em HTML (com figuras embutidas em base64) e o
converte para PDF usando o Microsoft Edge em modo headless.
"""
import base64
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
HERE = Path(__file__).resolve().parent
HTML_PATH = HERE / "relatorio.html"
PDF_PATH = HERE / "relatorio.pdf"


def b64(name):
    data = (OUT / name).read_bytes()
    return "data:image/png;base64," + base64.b64encode(data).decode()


IMG_EQUITY = b64("equity_curve.png")
IMG_DD = b64("drawdown.png")
IMG_WEIGHTS = b64("weights.png")
IMG_IMP = b64("feature_importance.png")

HTML = r"""<!DOCTYPE html>
<html lang="pt-br">
<head>
<meta charset="utf-8">
<title>Alocação Sistemática em Classes de Ativos com Aprendizado Supervisionado</title>
<style>
  @page { size: A4; margin: 2.5cm 2.3cm; }
  * { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  html { font-family: "Segoe UI", Arial, Helvetica, sans-serif; color: #1a1a1a; }
  body { font-size: 11pt; line-height: 1.6; }
  p { text-align: justify; margin: 0 0 11px 0; text-indent: 1.1cm; }
  h2 { font-size: 14pt; margin: 28px 0 12px 0; color: #1a1a1a; }
  h3 { font-size: 12pt; margin: 20px 0 8px 0; color: #1a1a1a; }
  .first { page-break-after: always; }
  .cover { height: 24.5cm; display: flex; flex-direction: column;
           align-items: center; text-align: center; }
  .cover .top { margin-top: 0.4cm; }
  .cover h1u { font-size: 16pt; font-weight: bold; letter-spacing: .5px; }
  .cover .inst { font-size: 12pt; font-weight: bold; margin-top: 6px; }
  .cover .disc { margin-top: 3.4cm; font-size: 12pt; font-weight: bold; }
  .cover .prof { font-size: 11pt; margin-top: 4px; }
  .cover .title { margin-top: 3.6cm; font-size: 15pt; font-weight: bold;
                  line-height: 1.4; max-width: 16cm; }
  .cover .authors { margin-top: 3.8cm; font-size: 11.5pt; line-height: 1.9; }
  .cover .place { margin-top: auto; font-size: 11pt; line-height: 1.8; }
  figure { margin: 22px 0; text-align: center; page-break-inside: avoid; }
  figure img { max-width: 100%; border: 1px solid #ddd; }
  .cap { font-size: 9.5pt; color: #333; text-align: center; text-indent: 0;
         margin: 0 auto 6px auto; max-width: 15cm; line-height: 1.4; }
  .cap b { color: #1a1a1a; }
  .keep { break-inside: avoid; page-break-inside: avoid; margin: 22px 0; }
  table { border-collapse: collapse; width: 100%; margin: 6px 0 4px 0;
          font-size: 10pt; page-break-inside: avoid; }
  th { background: #1f3b66; color: #fff; text-align: left; padding: 7px 9px;
       font-weight: 600; }
  td { padding: 6px 9px; border-bottom: 1px solid #e3e3e3; }
  tbody tr:nth-child(even) { background: #f4f7fb; }
  .num td:not(:first-child) { text-align: center; }
  .hi { font-weight: 700; }
  .cards { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px;
           margin: 20px 0; page-break-inside: avoid; }
  .card { background: #f4f7fb; border: 1px solid #e0e6ef; border-radius: 8px;
          text-align: center; padding: 14px 8px; }
  .card .v { font-size: 17pt; font-weight: 700; color: #1f7a3d; }
  .card .v.red { color: #b3261e; }
  .card .v.blue { color: #1f3b66; }
  .card .l { font-size: 9pt; color: #555; margin-top: 3px; }
  .refs p { text-indent: -22px; padding-left: 22px; font-size: 10pt;
            text-align: left; }
</style>
</head>
<body>

<div class="cover first">
  <div class="top">
    <div class="hu" style="font-size:16pt;font-weight:bold;">UNIVERSIDADE DE SÃO PAULO</div>
    <div class="inst">Instituto de Ciências Matemáticas e de Computação</div>
  </div>
  <div class="disc">SSC0964 - Introdução à Computação no Mercado Financeiro</div>
  <div class="prof">Prof. Dr. Denis Fernando Wolf</div>
  <div class="title">Alocação Sistemática em Classes de Ativos por Aprendizado Supervisionado</div>
  <div class="authors">
    Bruno Garcia de Oliveira Breda &nbsp; Nº USP 11212702<br>
    Vitor Antonio de Almeida Lacerda &nbsp; Nº USP 12544761
  </div>
  <div class="place">
    São Carlos - SP<br>
    1º Semestre de 2026
  </div>
</div>

<!-- ====================== 1. INTRODUÇÃO ====================== -->
<h2>1. Introdução</h2>

<p>A decisão sobre como distribuir o capital entre diferentes classes de ativos
é reconhecida como o principal determinante do desempenho de uma carteira no
longo prazo, respondendo por uma parcela do resultado bem maior do que a escolha
de papéis individuais dentro de cada classe. Em um país como o Brasil, no qual a
taxa básica de juros é historicamente elevada, essa decisão ganha um contorno
ainda mais delicado, pois o custo de oportunidade de qualquer aplicação é o
próprio CDI, que entrega retornos altos com risco praticamente nulo. Alocar de
forma sistemática significa, portanto, definir regras objetivas e replicáveis que
indiquem, a cada período, quanto destinar a ações, renda fixa, ouro, moeda
estrangeira ou caixa, sem depender de opiniões pontuais ou da intuição do gestor.</p>

<p>As abordagens clássicas para esse problema vão da otimização de média e
variância proposta por Markowitz até as regras técnicas aplicadas a uma única
série de preços, como o cruzamento de médias móveis e as Bandas de Bollinger,
estudadas em aula. Tais regras costumam observar apenas o histórico de preços de
um ativo isolado e tomar decisões binárias de compra e venda. Foi adotada neste
trabalho uma estratégia diferente, que trata a alocação como um problema de
aprendizado supervisionado e que combina, num mesmo modelo, informações de
diversas classes de ativos com variáveis macroeconômicas do ambiente brasileiro.</p>

<p>A originalidade da proposta está em dois pontos centrais. O primeiro é a
variável de saída do modelo. Em vez de tentar prever se o preço de um ativo vai
subir ou cair, o que é notoriamente difícil e instável, foi definido um alvo mais
útil para a decisão de alocação, que é a probabilidade de cada classe de ativo
superar o CDI no mês seguinte. Essa probabilidade é interpretada como um grau de
convicção e usada diretamente para dimensionar o tamanho de cada posição. O
segundo ponto é a escolha das variáveis de entrada, que reúnem sinais técnicos
calculados para cada ativo, como momentum, volatilidade e distância da média, com
um conjunto de indicadores macroeconômicos compartilhados, como o juro real, a
variação recente da Selic, o ritmo da inflação medida pelo IPCA e pelo IGP-M, a
inclinação implícita da curva de juros e a tendência do dólar e das bolsas
internacionais.</p>

<p>O objetivo do trabalho foi construir e avaliar, de ponta a ponta, um sistema
de alocação que aprende com o histórico a reconhecer em quais regimes cada classe
de ativo tende a remunerar acima do caixa, e que converte esse conhecimento em uma
carteira diversificada e com risco controlado. Foram comparados quatro algoritmos
de aprendizado supervisionado vistos na disciplina, a saber, regressão logística,
floresta aleatória, gradient boosting e rede neural do tipo perceptron
multicamadas, todos avaliados de maneira honesta fora da amostra, sobre dados
mensais que cobrem de dezembro de 1999 a maio de 2026.</p>

<!-- ====================== 2. METODOLOGIA ====================== -->
<h2>2. Metodologia</h2>

<h3>2.1. Base de dados e universo de ativos</h3>

<p>Foi utilizada a base de índices fornecida na disciplina, com observações
mensais que se estendem de dezembro de 1999 a maio de 2026, totalizando 318 meses
sem dados faltantes. A partir dos níveis de cada índice foram calculados os
retornos mensais simples, que constituem a matéria-prima de todas as etapas
seguintes. O universo de decisão foi composto por oito classes de ativos
investíveis, e a taxa Selic acumulada foi adotada como representação do caixa, ou
seja, do ativo livre de risco contra o qual todas as demais classes são comparadas.
Além das séries investíveis, um grupo de variáveis macroeconômicas foi reservado
exclusivamente para a geração de atributos, sem nunca compor a carteira. A Tabela 1
resume essa organização.</p>

<div class="keep">
<p class="cap"><b>Tabela 1</b> - Universo de ativos e variáveis utilizadas.
Fonte: Elaborado pelos autores.</p>
<table class="num">
  <thead><tr><th>Papel na estratégia</th><th>Séries</th><th>Descrição</th></tr></thead>
  <tbody>
    <tr><td>Ações Brasil</td><td>IBOV, IDIV, UTIL, IFNC</td><td>Índice amplo e setores de dividendos, utilidades e financeiro</td></tr>
    <tr><td>Ações exterior</td><td>SP500BR</td><td>S&amp;P 500 convertido para reais, que embute o câmbio</td></tr>
    <tr><td>Proteção</td><td>OURO</td><td>Ouro, ativo descorrelacionado e defensivo</td></tr>
    <tr><td>Renda fixa</td><td>IMAB, IMAB5</td><td>Títulos públicos atrelados à inflação, duration longa e curta</td></tr>
    <tr><td>Caixa (livre de risco)</td><td>SELIC-ACC</td><td>Selic acumulada, usada como referência e como posição de proteção</td></tr>
    <tr><td>Macro (apenas atributos)</td><td>USD, IPCA, IGP-M, SELIC-META, SP500USD</td><td>Câmbio, inflação, juro de política e bolsa global</td></tr>
  </tbody>
</table>
</div>

<p>A inclusão dos setores de ações brasileiras, e não apenas do índice amplo,
foi uma decisão deliberada. Ela amplia o número de apostas independentes que a
estratégia pode realizar a cada mês, o que se conecta diretamente à Lei
Fundamental da Gestão Ativa apresentada em aula, segundo a qual o desempenho de um
gestor cresce com a sua capacidade de previsão e com a raiz quadrada do número de
oportunidades distintas que ele explora.</p>

<h3>2.2. Definição do problema e variável-alvo</h3>

<p>O problema foi formulado como uma classificação binária aplicada a cada par
formado por um mês e uma classe de ativo. Para cada par, o rótulo recebe o valor um
quando o retorno do ativo no mês seguinte supera o retorno do caixa no mesmo mês, e
recebe o valor zero caso contrário. Em outras palavras, o modelo não responde se o
ativo vai subir, e sim se vale a pena estar nele em vez de permanecer no CDI. Essa
formulação é mais aderente à decisão de alocação e tende a ser mais estável do que
a previsão direta de retornos, que é fortemente contaminada por ruído.</p>

<p>Um cuidado essencial foi o tratamento do tempo, de modo a impedir qualquer
uso indevido de informação futura. Os atributos de um determinado mês são
construídos apenas com dados disponíveis até o fechamento daquele mês, ao passo que
o rótulo observa o desempenho que se realiza somente no mês seguinte. Assim, a
previsão é genuinamente feita um passo à frente, replicando a situação de um gestor
que decide hoje sem conhecer o amanhã.</p>

<h3>2.3. Engenharia de atributos</h3>

<p>O conjunto de atributos foi projetado para combinar duas fontes de
informação complementares. A primeira é técnica e específica de cada ativo,
capturando o comportamento recente da própria série. A segunda é macroeconômica e
compartilhada por todos os ativos em um mesmo mês, descrevendo o regime de mercado
no qual a decisão é tomada. Foi essa fusão, somada à identidade de cada classe
representada por variáveis indicadoras, que produziu um total de 34 atributos por
observação. A Tabela 2 organiza esses atributos em grupos e explica a intuição por
trás de cada um.</p>

<div class="keep">
<p class="cap"><b>Tabela 2</b> - Grupos de atributos de entrada do modelo.
Fonte: Elaborado pelos autores.</p>
<table>
  <thead><tr><th>Grupo</th><th>Atributos</th><th>Intuição</th></tr></thead>
  <tbody>
    <tr><td>Momentum</td><td>Retornos de 1, 3, 6 e 12 meses</td><td>Captura a continuidade de tendências, um efeito amplamente documentado</td></tr>
    <tr><td>Momentum em excesso</td><td>Retornos acima do caixa em 1, 3, 6 e 12 meses</td><td>Mede a tendência líquida do custo de oportunidade</td></tr>
    <tr><td>Volatilidade</td><td>Desvio padrão dos retornos em 3, 6 e 12 meses</td><td>Indica o regime de risco e alimenta a gestão de risco</td></tr>
    <tr><td>Reversão à média</td><td>Distância padronizada da média móvel de 6 e 12 meses</td><td>Versão estatística da ideia das Bandas de Bollinger</td></tr>
    <tr><td>Aceleração</td><td>Variação do momentum de 3 meses</td><td>Detecta perda ou ganho de força do movimento</td></tr>
    <tr><td>Macro de juros</td><td>Juro real, Selic meta, variação da Selic em 3 meses</td><td>Resume o regime monetário, que move renda fixa e ações</td></tr>
    <tr><td>Macro de inflação</td><td>IPCA e IGP-M em 12 meses</td><td>Ambiente inflacionário, relevante para títulos atrelados ao IPCA</td></tr>
    <tr><td>Curva e câmbio</td><td>Inclinação IMA-B menos IMA-B 5, tendência do dólar em 1, 3 e 6 meses</td><td>Aversão a risco e expectativas de juros longos</td></tr>
    <tr><td>Bolsa global</td><td>Tendência do S&amp;P 500 em dólar em 3 e 6 meses</td><td>Beta global e apetite internacional por risco</td></tr>
    <tr><td>Identidade do ativo</td><td>Variáveis indicadoras por classe</td><td>Permite ao modelo aprender prêmios de risco distintos</td></tr>
  </tbody>
</table>
</div>

<p>Vale destacar que o atributo de distância da média foi calculado como um
escore padronizado, ou seja, a diferença entre o preço e a sua média móvel dividida
pelo desvio padrão do período. Essa transformação cumpre o mesmo papel das Bandas
de Bollinger discutidas em aula, porém de forma contínua e comparável entre ativos
de escalas diferentes, o que é mais adequado para um modelo estatístico.</p>

<h3>2.4. Modelos de aprendizado supervisionado</h3>

<p>Foram treinados e comparados quatro algoritmos de classificação, todos
apresentados na aula de Aprendizado de Máquina. A regressão logística serviu como
referência linear e interpretável. A floresta aleatória e o gradient boosting
representam os métodos baseados em conjuntos de árvores de decisão, que combinam
muitas árvores simples para obter robustez e capacidade de capturar relações não
lineares. A rede neural do tipo perceptron multicamadas representa a abordagem
conexionista. Foi avaliado ainda um comitê, formado pela média das probabilidades
dos três modelos de aprendizado de máquina, com o intuito de verificar se a
combinação traria ganho de estabilidade.</p>

<p>Para reduzir o risco de superajuste, que foi enfatizado em aula como uma das
principais armadilhas do aprendizado de máquina, os hiperparâmetros foram mantidos
conservadores. As árvores tiveram profundidade limitada e um número mínimo de
amostras por folha relativamente alto, a rede neural recebeu regularização e parada
antecipada, e as variáveis foram padronizadas antes de alimentar os modelos
sensíveis à escala. O objetivo foi privilegiar a capacidade de generalização em vez
do ajuste perfeito ao passado.</p>

<h3>2.5. Validação walk-forward</h3>

<p>A avaliação foi conduzida por um procedimento de validação com janela
expansível, conhecido como walk-forward. A cada mês de decisão, o modelo é treinado
exclusivamente com observações cujo resultado já se realizou, e em seguida gera as
probabilidades para o mês corrente. No mês seguinte, a janela de treino é ampliada
para incorporar o novo dado observado, e o processo se repete. Foi exigido um
histórico mínimo de cinco anos antes da primeira previsão, de modo que o período
efetivamente avaliado fora da amostra vai de janeiro de 2005 a maio de 2026, o que
corresponde a 258 meses de decisões independentes.</p>

<p>A qualidade preditiva foi medida pela acurácia, pela área sob a curva ROC e
pelo coeficiente de informação, definido como a correlação entre a probabilidade
prevista e o excesso de retorno efetivamente realizado em relação ao caixa. Esse
último indicador é particularmente informativo, pois mede se a convicção do modelo
de fato se traduz em retorno.</p>

<h3>2.6. Estratégia de alocação e gestão de risco</h3>

<p>As probabilidades previstas foram convertidas em pesos de carteira por meio
de uma regra que une convicção e controle de risco. Para cada ativo, a convicção
foi definida como o quanto a probabilidade prevista excede o limiar de cinquenta
por cento, de forma que apenas ativos considerados atraentes recebem alocação. Essa
convicção foi então ponderada pelo inverso da volatilidade recente do ativo, o que
faz com que classes mais arriscadas entrem com peso menor para uma mesma convicção.
Os pesos resultantes foram normalizados, limitados a um teto de trinta e cinco por
cento por ativo para garantir diversificação, e a fração não alocada foi
direcionada ao caixa remunerado pela Selic.</p>

<p>Essa construção reúne os três princípios de gestão de risco discutidos em
aula. A ponderação pelo inverso da volatilidade é uma forma de orçamento de risco,
na qual cada posição contribui de maneira mais equilibrada para o risco total. O
teto por ativo funciona como um limite de exposição por posição. E o uso do caixa
como destino padrão atua como um mecanismo de proteção de capital, já que a
estratégia recolhe naturalmente aos títulos públicos pós-fixados sempre que o
modelo não identifica oportunidades convincentes.</p>

<h3>2.7. Custos de transação e benchmarks</h3>

<p>Para aproximar o resultado de condições reais, foi aplicado um custo de
transação de dez centésimos por cento sobre o giro mensal da carteira, calculado
como a soma das variações absolutas dos pesos entre dois meses consecutivos. Esse
custo procura refletir corretagem, impostos e escorregamento de preço, conforme o
modelo de custos apresentado na disciplina. O desempenho da estratégia foi comparado
a quatro referências, a saber, o Ibovespa comprado e mantido, uma carteira de pesos
iguais entre todos os ativos investíveis, a aplicação integral no CDI e a clássica
carteira sessenta por cento em ações e quarenta por cento em renda fixa. As métricas
de avaliação incluíram o retorno anualizado, a volatilidade anualizada, o índice de
Sharpe calculado sobre o excesso em relação ao CDI, o drawdown máximo, a taxa de
acerto mensal e o payoff, este último na forma da razão entre o ganho médio e a
perda média.</p>

<!-- ====================== 3. RESULTADOS ====================== -->
<h2>3. Resultados e Discussões</h2>

<h3>3.1. Qualidade preditiva dos modelos</h3>

<p>A Tabela 3 apresenta as métricas de previsão fora da amostra para os quatro
algoritmos e para o comitê. O primeiro ponto que merece atenção é a taxa de base,
que indica que, no período avaliado, as classes de ativos superaram o caixa em
apenas cerca de cinquenta e três por cento dos meses. Esse número confirma que
bater o CDI no Brasil é uma tarefa difícil e estabelece um patamar exigente para
qualquer modelo.</p>

<div class="keep">
<p class="cap"><b>Tabela 3</b> - Qualidade preditiva fora da amostra,
janeiro de 2005 a maio de 2026. Fonte: Elaborado pelos autores.</p>
<table class="num">
  <thead><tr><th>Modelo</th><th>Acurácia</th><th>AUC</th><th>Coef. de informação</th></tr></thead>
  <tbody>
    <tr class="hi"><td>Floresta aleatória</td><td>0,543</td><td>0,552</td><td>0,052</td></tr>
    <tr><td>Gradient boosting</td><td>0,534</td><td>0,548</td><td>0,058</td></tr>
    <tr><td>Comitê (média)</td><td>0,538</td><td>0,548</td><td>0,053</td></tr>
    <tr><td>Regressão logística</td><td>0,513</td><td>0,524</td><td>0,054</td></tr>
    <tr><td>Rede neural (MLP)</td><td>0,521</td><td>0,514</td><td>0,016</td></tr>
  </tbody>
</table>
</div>

<p>Todos os modelos baseados em árvores superaram a taxa de base, com destaque
para a floresta aleatória, que atingiu acurácia de aproximadamente cinquenta e
quatro por cento e a maior área sob a curva ROC. Os coeficientes de informação
positivos, na casa de cinco a seis centésimos, indicam que a convicção dos modelos
guarda relação real com o retorno futuro. Embora esses valores possam parecer
modestos, eles estão em linha com o que se observa na prática de mercado, e cabe
lembrar a comparação feita em aula, na qual foi mencionado que o renomado fundo
Medallion apresentou taxa de acerto próxima de cinquenta e um por cento. O que torna
uma vantagem pequena lucrativa é a sua aplicação consistente sobre muitas apostas
independentes, exatamente o que a estratégia faz ao decidir mês a mês sobre oito
classes simultaneamente. A rede neural foi o modelo mais fraco, com coeficiente de
informação próximo de zero, o que sugere maior dificuldade de generalização nesse
conjunto de dados.</p>

<h3>3.2. Desempenho da carteira</h3>

<p>Traduzida a previsão em alocação, a floresta aleatória foi a estratégia de
melhor desempenho ajustado ao risco, e seus principais números estão sintetizados a
seguir. O resultado é expressivo, pois combina um retorno anualizado superior ao do
Ibovespa com uma volatilidade muito menor e um drawdown máximo notavelmente
contido.</p>

<div class="cards">
  <div class="card"><div class="v">13,8%</div><div class="l">Retorno anualizado</div></div>
  <div class="card"><div class="v blue">7,0%</div><div class="l">Volatilidade anualizada</div></div>
  <div class="card"><div class="v">0,43</div><div class="l">Índice de Sharpe</div></div>
  <div class="card"><div class="v red">-7,7%</div><div class="l">Drawdown máximo</div></div>
  <div class="card"><div class="v">80,5%</div><div class="l">Taxa de acerto mensal</div></div>
  <div class="card"><div class="v blue">1.497,8%</div><div class="l">Retorno acumulado</div></div>
</div>

<p>A Tabela 4 posiciona todas as estratégias frente aos benchmarks. A leitura
conjunta revela um padrão claro. As estratégias baseadas em aprendizado supervisionado
entregaram retornos próximos ou superiores ao do Ibovespa, mas com uma fração da sua
volatilidade e, sobretudo, com drawdowns muito menores. A floresta aleatória se
destacou por unir o melhor índice de Sharpe, igual a 0,43, ao menor drawdown máximo
entre todas as carteiras, de apenas sete vírgula sete por cento negativos, contra
quase cinquenta por cento negativos do Ibovespa no mesmo período.</p>

<div class="keep">
<p class="cap"><b>Tabela 4</b> - Desempenho das estratégias e dos benchmarks,
janeiro de 2005 a maio de 2026, líquido de custos. Fonte: Elaborado pelos autores.</p>
<table class="num">
  <thead><tr><th>Carteira</th><th>Ret. a.a.</th><th>Vol. a.a.</th><th>Sharpe</th><th>Drawdown</th><th>Taxa acerto</th><th>Ret. acum.</th></tr></thead>
  <tbody>
    <tr class="hi"><td>Floresta aleatória</td><td>13,8%</td><td>7,0%</td><td>0,43</td><td>-7,7%</td><td>80,5%</td><td>1.497,8%</td></tr>
    <tr><td>Rede neural (MLP)</td><td>13,9%</td><td>9,3%</td><td>0,36</td><td>-20,0%</td><td>70,8%</td><td>1.528,1%</td></tr>
    <tr><td>Regressão logística</td><td>13,0%</td><td>8,3%</td><td>0,29</td><td>-10,8%</td><td>75,1%</td><td>1.261,5%</td></tr>
    <tr><td>Gradient boosting</td><td>12,6%</td><td>7,9%</td><td>0,25</td><td>-27,0%</td><td>79,0%</td><td>1.167,5%</td></tr>
    <tr><td>Comitê (média)</td><td>12,7%</td><td>8,7%</td><td>0,25</td><td>-29,8%</td><td>77,8%</td><td>1.187,3%</td></tr>
    <tr><td>Carteira de pesos iguais</td><td>14,3%</td><td>10,8%</td><td>0,36</td><td>-21,9%</td><td>65,8%</td><td>1.657,5%</td></tr>
    <tr><td>CDI (caixa)</td><td>10,7%</td><td>1,0%</td><td>&mdash;</td><td>0,0%</td><td>100%</td><td>779,3%</td></tr>
    <tr><td>Carteira 60/40</td><td>11,0%</td><td>14,8%</td><td>0,09</td><td>-33,3%</td><td>58,8%</td><td>831,9%</td></tr>
    <tr><td>Ibovespa</td><td>9,3%</td><td>22,1%</td><td>0,06</td><td>-49,6%</td><td>57,2%</td><td>576,8%</td></tr>
  </tbody>
</table>
</div>

<p>A carteira de pesos iguais alcançou retorno anualizado um pouco maior, de
quatorze vírgula três por cento, mas o fez assumindo volatilidade e drawdown bem
mais altos, o que se reflete em um índice de Sharpe inferior ao da floresta
aleatória. Isso evidencia que o ganho do modelo não está apenas em obter retorno,
e sim em obter retorno com risco controlado. A taxa de acerto mensal elevada, de
oitenta vírgula cinco por cento, é coerente com o comportamento esperado de uma
estratégia que recolhe ao caixa em momentos de incerteza, perfil que a aula associa
aos sistemas de reversão à média, marcados por acertos frequentes de pequena
magnitude.</p>

<p>A Figura 1 mostra a evolução do patrimônio em escala logarítmica. A linha da
estratégia cresce de forma consistente e com poucas interrupções, acompanhando de
perto a carteira de pesos iguais, porém com trajetória visivelmente mais suave, e
mantendo-se sempre acima do CDI e do Ibovespa ao longo de quase todo o período.</p>

<figure>
  <p class="cap"><b>Figura 1</b> - Curva de patrimônio em escala logarítmica da
  estratégia frente aos benchmarks, base igual a um. Fonte: Elaborado pelos autores.</p>
  <img src="%%IMG_EQUITY%%" alt="Curva de patrimônio">
</figure>

<p>A vantagem mais marcante da estratégia aparece na Figura 2, que compara o
drawdown ao longo do tempo. Enquanto o Ibovespa sofreu quedas profundas, chegando a
cerca de cinquenta por cento negativos na crise de 2008, a quarenta e quatro por
cento negativos em 2015 e a trinta e sete por cento negativos no choque de 2020, a
estratégia raramente ultrapassou oito por cento negativos. Essa diferença é
decisiva para um investidor real, pois quedas dessa magnitude no benchmark exigem
anos de recuperação e costumam levar à desistência no pior momento.</p>

<figure>
  <p class="cap"><b>Figura 2</b> - Drawdown da estratégia comparado ao Ibovespa e
  ao CDI ao longo do período avaliado. Fonte: Elaborado pelos autores.</p>
  <img src="%%IMG_DD%%" alt="Drawdown">
</figure>

<h3>3.3. Comportamento da alocação ao longo do tempo</h3>

<p>A Figura 3 ilustra como a carteira se reorganiza mês a mês. Observa-se uma
rotação clara entre as classes de ativos conforme o regime de mercado muda, e
nota-se que a posição em caixa cresce de forma expressiva em períodos de maior
estresse, quando poucas classes apresentam probabilidade de superar a Selic. Esse
comportamento dinâmico, no qual a própria ausência de alocação é uma decisão
ativa, é justamente o que explica os drawdowns reduzidos observados na figura
anterior.</p>

<figure>
  <p class="cap"><b>Figura 3</b> - Composição da carteira ao longo do tempo, com a
  parcela em caixa destacada. Fonte: Elaborado pelos autores.</p>
  <img src="%%IMG_WEIGHTS%%" alt="Alocação ao longo do tempo">
</figure>

<h3>3.4. Importância dos atributos</h3>

<p>A Figura 4 apresenta a importância relativa dos atributos segundo a floresta
aleatória. O resultado é revelador e reforça a aposta de originalidade do trabalho.
Os atributos mais determinantes não foram os sinais técnicos tradicionais, e sim as
variáveis macroeconômicas. A tendência do dólar em diferentes horizontes, a variação
recente da Selic, o ritmo da inflação medido pelo IPCA e pelo IGP-M, o juro real e a
tendência da bolsa global despontaram como os fatores mais influentes na decisão de
superar ou não o caixa.</p>

<figure>
  <p class="cap"><b>Figura 4</b> - Importância dos atributos estimada pela floresta
  aleatória ajustada ao histórico completo. Fonte: Elaborado pelos autores.</p>
  <img src="%%IMG_IMP%%" alt="Importância das features">
</figure>

<p>Essa constatação faz sentido econômico. Em uma economia sensível a juros e
câmbio como a brasileira, o regime macroeconômico condiciona fortemente qual classe
de ativo remunera melhor em cada momento. Quando o juro real está alto, por exemplo,
torna-se mais difícil para ativos de risco superarem o caixa, e o modelo aprende a
reconhecer essas situações. O fato de o modelo ter atribuído mais peso ao contexto
macro do que aos indicadores técnicos de cada série confirma que a combinação de
dados proposta agregou informação genuína, e não apenas repetiu os sinais já
explorados pelas regras técnicas vistas em aula.</p>

<!-- ====================== 4. CONCLUSÃO ====================== -->
<h2>4. Conclusão</h2>

<p>Foi desenvolvida uma estratégia de alocação sistemática entre classes de
ativos fundamentada em aprendizado supervisionado, na qual o modelo estima, a cada
mês e para cada classe, a probabilidade de superar o CDI, e essa probabilidade é
convertida em peso de carteira por meio de uma regra de gestão de risco que combina
convicção, orçamento por volatilidade, limite de exposição e proteção em caixa. A
proposta se diferencia das regras técnicas de série única estudadas na disciplina
tanto pela escolha original da variável de saída quanto pela combinação de sinais
técnicos com um amplo conjunto de indicadores macroeconômicos na entrada.</p>

<p>Os resultados fora da amostra, obtidos por validação walk-forward ao longo
de mais de vinte anos, mostraram que a estratégia atingiu seu objetivo. A versão
baseada em floresta aleatória entregou retorno anualizado de treze vírgula oito por
cento, superior ao do Ibovespa, com volatilidade de apenas sete por cento e
drawdown máximo de sete vírgula sete por cento negativos, o que representa um perfil
de risco muito mais favorável do que o de qualquer dos benchmarks. Em termos
simples, foi obtido um retorno comparável ao das ações com um risco semelhante ao da
renda fixa, e o melhor índice de Sharpe de todas as carteiras analisadas.</p>

<p>A análise da importância dos atributos trouxe a conclusão mais interessante
do trabalho. Foi o contexto macroeconômico, e não os indicadores técnicos isolados,
que mais contribuiu para as decisões do modelo, o que está alinhado à realidade de
uma economia sensível a juros e câmbio. Esse achado valida a hipótese central de que
combinar diferentes naturezas de dados, técnicos e macroeconômicos, sobre várias
classes de ativos ao mesmo tempo, gera uma vantagem informacional que se traduz em
desempenho superior e mais estável.</p>

<p>Cabe registrar algumas limitações que delimitam o alcance das conclusões. O
Ibovespa é um índice de preço, ao passo que parte das demais séries incorpora
retorno total, o que introduz uma assimetria nas comparações entre classes. O custo
de transação adotado é uma aproximação razoável, porém o impacto de mercado real
depende do volume efetivamente negociado. Por fim, todo backtest reflete o passado,
e desempenho histórico não constitui garantia de resultado futuro. Ainda assim, o
trabalho evidencia que o aprendizado supervisionado, quando aplicado com disciplina
metodológica e validação honesta, é uma ferramenta poderosa para a alocação
sistemática entre classes de ativos, sobretudo no contexto brasileiro.</p>

<h2>Referências</h2>
<div class="refs">
<p>BREIMAN, L. Random Forests. <i>Machine Learning</i>, v. 45, p. 5 a 32, 2001.</p>
<p>FAMA, E. F.; FRENCH, K. R. Common risk factors in the returns on stocks and
bonds. <i>Journal of Financial Economics</i>, v. 33, 1993.</p>
<p>GRINOLD, R. C. The fundamental law of active management. <i>The Journal of
Portfolio Management</i>, 1989.</p>
<p>KELLY, J. L. A new interpretation of information rate. <i>Bell System Technical
Journal</i>, 1956.</p>
<p>MARKOWITZ, H. Portfolio selection. <i>The Journal of Finance</i>, v. 7, 1952.</p>
<p>PEDREGOSA, F. et al. Scikit-learn: Machine Learning in Python. <i>Journal of
Machine Learning Research</i>, v. 12, 2011.</p>
<p>WOLF, D. F. Notas de aula da disciplina SSC0964, Introdução à Computação no
Mercado Financeiro. ICMC USP, 2026.</p>
</div>

</body>
</html>
"""

HTML = HTML.replace("%%IMG_EQUITY%%", IMG_EQUITY)
HTML = HTML.replace("%%IMG_DD%%", IMG_DD)
HTML = HTML.replace("%%IMG_WEIGHTS%%", IMG_WEIGHTS)
HTML = HTML.replace("%%IMG_IMP%%", IMG_IMP)

HTML_PATH.write_text(HTML, encoding="utf-8")
print("HTML escrito em", HTML_PATH)

# Converte para PDF com o Edge headless
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
import tempfile
_profile = tempfile.mkdtemp(prefix="edge_pdf_")
cmd = [EDGE, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
       f"--user-data-dir={_profile}", "--disable-cache",
       f"--print-to-pdf={PDF_PATH}", HTML_PATH.as_uri()]
print("Convertendo para PDF...")
subprocess.run(cmd, check=True, timeout=120)
print("PDF gerado em", PDF_PATH)
