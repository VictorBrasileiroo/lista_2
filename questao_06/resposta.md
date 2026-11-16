# Questão 6: Sistema de inferência fuzzy com Mamdani

## 1. Introdução e descrição da aplicação

O sistema desenvolvido recomenda a velocidade de um ventilador a partir da temperatura ambiente e da umidade relativa do ar. A saída é um percentual da capacidade máxima do equipamento. A aplicação é didática e executada por linha de comando, sem conexão com sensores ou com um ventilador físico.

A modelagem considera que ambientes quentes exigem ventilação alta e que, em temperaturas amenas, a umidade pode influenciar a recomendação. Essas relações foram escolhidas para estudar a inferência fuzzy e não constituem regras cientificamente validadas de conforto térmico. O ventilador movimenta o ar, mas não remove sua umidade.

## 2. Variáveis e universos de discurso

| Variável | Papel | Universo | Conjuntos linguísticos |
|---|---|---|---|
| Temperatura ambiente | Entrada | [0, 40] °C | Fria, amena e quente |
| Umidade relativa | Entrada | [0, 100]% | Baixa, média e alta |
| Velocidade do ventilador | Saída | [0, 100]% | Baixa, média e alta |

No código, as entradas são objetos `Antecedent` e a saída é um `Consequent`. Os universos são representados por amostras com passo 1, incluindo os extremos. Entradas decimais também são aceitas: a biblioteca interpola os graus de pertinência entre as amostras. Como os vértices das funções estão na malha, os segmentos lineares das funções de entrada são preservados por essa interpolação.

## 3. Funções de pertinência e fuzzificação

Foram mantidos os parâmetros propostos. Os conjuntos centrais são triangulares, definidos por `trimf([a, b, c])`, e os conjuntos extremos são trapezoidais, definidos por `trapmf([a, b, c, d])`.

Na função triangular, a pertinência vale zero fora de [a, c], cresce linearmente até 1 em b e decresce até zero em c. Na trapezoidal, a pertinência cresce de a até b, permanece em 1 entre b e c e decresce até zero em d. Vértices repetidos nas extremidades representam ombros: por exemplo, [0, 0, 15, 22] possui pertinência 1 desde 0 até 15.

| Variável | Conjunto | Função | Parâmetros |
|---|---|---|---|
| Temperatura | Fria | Trapezoidal | [0, 0, 15, 22] |
| Temperatura | Amena | Triangular | [18, 25, 32] |
| Temperatura | Quente | Trapezoidal | [28, 34, 40, 40] |
| Umidade | Baixa | Trapezoidal | [0, 0, 30, 50] |
| Umidade | Média | Triangular | [35, 55, 75] |
| Umidade | Alta | Trapezoidal | [60, 80, 100, 100] |
| Velocidade | Baixa | Trapezoidal | [0, 0, 20, 40] |
| Velocidade | Média | Triangular | [30, 50, 70] |
| Velocidade | Alta | Trapezoidal | [60, 80, 100, 100] |

Os patamares dos trapézios representam faixas de pertinência plena para as categorias extremas. Os triângulos representam valores centrais de referência, como 25 °C para temperatura amena e 55% para umidade média. As sobreposições permitem que uma entrada pertença simultaneamente a categorias vizinhas, evitando uma troca abrupta de categoria.

Na temperatura, há sobreposição entre fria e amena no intervalo (18, 22) e entre amena e quente em (28, 32). Na umidade, as sobreposições ocorrem em (35, 50) e (60, 75). Na velocidade, ocorrem em (30, 40) e (60, 70). Os ombros garantem pertinência plena de pelo menos um conjunto nos extremos de cada universo. Portanto, nenhum valor dos universos fica com pertinência zero em todos os conjuntos da respectiva variável. Não é necessário que a soma das pertinências seja igual a 1.

A fuzzificação converte cada entrada numérica em seus graus de pertinência. Esses graus indicam compatibilidade com os conjuntos linguísticos, e não probabilidades.

## 4. Base de regras fuzzy

Cada célula da tabela corresponde a uma regra com conjunção E entre temperatura e umidade, totalizando nove regras.

| Temperatura / Umidade | Baixa | Média | Alta |
|---|---|---|---|
| Fria | Velocidade baixa | Velocidade baixa | Velocidade baixa |
| Amena | Velocidade baixa | Velocidade média | Velocidade alta |
| Quente | Velocidade alta | Velocidade alta | Velocidade alta |

Por exemplo: SE temperatura é amena E umidade é alta, ENTÃO velocidade é alta. Todas as regras têm peso 1. A implementação percorre as três linhas e as três colunas da tabela para construir os nove objetos `Rule`, reunidos em um `ControlSystem`.

## 5. Funcionamento da inferência de Mamdani

A inferência é executada pela API `skfuzzy.control`, por meio de `ControlSystemSimulation`. Não foi implementado um motor fuzzy próprio. Para uma regra r com conjuntos de entrada A e B e consequente C, as etapas são:

1. Fuzzificação: obter μ_A(T) e μ_B(U) para a temperatura T e a umidade U informadas.
2. Conjunção E: calcular a ativação α_r = min(μ_A(T), μ_B(U)). No código, o operador é explicitamente definido como `np.fmin`.
3. Implicação: truncar o conjunto de saída pela ativação, de modo que μ_r(v) = min(α_r, μ_C(v)). Essa operação é realizada pela biblioteca.
4. Agregação: reunir as contribuições por μ_agregada(v) = max_r μ_r(v). A acumulação de regras com o mesmo consequente foi configurada com `np.fmax`, e a biblioteca combina os conjuntos de saída também pelo máximo.

As regras são avaliadas em conjunto. Quando várias delas apontam para o mesmo conjunto de saída, prevalece sua maior ativação, sem somar graus de pertinência. Regras que apontam para conjuntos diferentes também contribuem para a curva agregada.

Como há cobertura dos dois universos de entrada e uma regra para cada combinação de conjuntos, sempre existe pelo menos uma regra com ativação positiva para entradas válidas. Seu consequente possui área positiva, permitindo calcular o centroide.

## 6. Defuzzificação pelo centroide

A saída numérica é o centro de área da função agregada:

$$
v^* = \frac{\int_0^{100} v\,\mu_{\mathrm{agregada}}(v)\,dv}
{\int_0^{100} \mu_{\mathrm{agregada}}(v)\,dv}.
$$

O método foi definido explicitamente por `defuzzify_method="centroid"`. A biblioteca acrescenta à malha os pontos necessários ao truncamento e calcula o centroide da representação linear por partes. A defuzzificação considera a distribuição de área da saída agregada, em vez de escolher apenas o conjunto com maior ativação.

## 7. Exemplos de execução e análise dos resultados

### 7.1. Exemplo passo a passo: 25 °C e 55%

As entradas coincidem com os picos de temperatura amena e umidade média. Os graus obtidos na implementação foram:

| Entrada | Conjunto | Pertinência |
|---|---|---|
| Temperatura de 25 °C | Fria | 0 |
| Temperatura de 25 °C | Amena | 1 |
| Temperatura de 25 °C | Quente | 0 |
| Umidade de 55% | Baixa | 0 |
| Umidade de 55% | Média | 1 |
| Umidade de 55% | Alta | 0 |

Apenas a regra SE temperatura é amena E umidade é média, ENTÃO velocidade é média possui ativação positiva. Sua ativação é min(1, 1) = 1. As outras oito regras têm ativação zero, pois pelo menos uma de suas condições possui pertinência zero.

O truncamento da velocidade média em 1 preserva o triângulo [30, 50, 70] inteiro. As ativações acumuladas dos conjuntos baixa, média e alta são, respectivamente, 0, 1 e 0. A agregação pelo máximo resulta, portanto, no próprio triângulo médio. Sua área é (70 − 30)/2 = 20, e seu primeiro momento é 1000. Logo, o centroide é 1000/20 = 50%. A simulação confirmou a velocidade de 50,00%.

### 7.2. Cenários demonstrativos

Os valores abaixo foram obtidos com `python sistema_fuzzy.py --exemplos`. A coluna final usa vírgula decimal para apresentação; a linha de comando imprime ponto decimal.

| Cenário | Temperatura (°C) | Umidade (%) | Velocidade (%) |
|---|---|---|---|
| Ambiente frio | 15 | 40 | 17,62 |
| Ambiente ameno | 25 | 50 | 50,00 |
| Ambiente quente e úmido | 34 | 85 | 84,44 |
| Picos amena e média | 25 | 55 | 50,00 |
| Transição entre conjuntos | 30 | 65 | 67,70 |
| Limites mínimos | 0 | 0 | 15,56 |
| Frio e umidade máxima | 0 | 100 | 15,56 |
| Quente e umidade mínima | 40 | 0 | 84,44 |
| Limites máximos | 40 | 100 | 84,44 |

No ambiente frio, a temperatura pertence plenamente ao conjunto fria. Para umidade de 40%, as pertinências baixa e média são 0,50 e 0,25. Duas regras contribuem para velocidade baixa, cuja ativação acumulada é max(0,50; 0,25) = 0,50. O centroide do trapézio truncado resulta em 17,62%.

No cenário ameno de 25 °C e 50%, apenas a regra amena com umidade média é ativada, com grau 0,75. O triângulo de saída é truncado nessa altura, mas permanece simétrico em torno de 50%, mantendo o centroide nesse valor. No cenário de 34 °C e 85%, quente e alta têm pertinência 1. A velocidade alta é preservada integralmente e seu centroide resulta em 84,44%.

### 7.3. Transição com múltiplas regras

Para 30 °C, as pertinências amena e quente são 2/7 ≈ 0,285714 e 1/3 ≈ 0,333333. Para 65% de umidade, média e alta têm pertinências 0,50 e 0,25. Fria e umidade baixa possuem pertinência zero. As quatro regras com ativação positiva, verificadas na simulação, são:

| Regra | Consequente | Ativação pelo mínimo |
|---|---|---|
| Amena E média | Média | 0,285714 |
| Amena E alta | Alta | 0,250000 |
| Quente E média | Alta | 0,333333 |
| Quente E alta | Alta | 0,250000 |

A ativação acumulada da saída média é 2/7, e a da saída alta é 1/3. Assim, a função agregada é:

$$
\mu_{\mathrm{agregada}}(v) = \max\left\{
\min\left(\frac{2}{7}, \mu_{\mathrm{média}}(v)\right),
\min\left(\frac{1}{3}, \mu_{\mathrm{alta}}(v)\right)
\right\}.
$$

O centroide calculado pela biblioteca foi 67,70%. Esse caso mostra que uma entrada pode ativar vários antecedentes e combinar regiões diferentes da saída.

Mantendo a umidade em 65%, as temperaturas 28, 29, 30, 31 e 32 °C produziram, respectivamente, 61,85%, 62,69%, 67,70%, 75,31% e 82,38%. A sequência ilustra a transição nessa faixa específica, sem demonstrar monotonicidade em todo o domínio.

### 7.4. Verificações adicionais

As verificações foram executadas diretamente com Python, sem adicionar arquivos de teste ao diretório da questão. Elas incluíram:

- Conferência das nove regras e da configuração `centroid`.
- Cobertura em 10.001 pontos de cada universo, sempre com pelo menos uma pertinência positiva.
- Simulação das 4.141 combinações inteiras de temperatura de 0 a 40 °C e umidade de 0 a 100%, incluindo as fronteiras. Todas produziram saídas finitas entre 0% e 100%, com mínimo observado de 15,56% e máximo de 84,44%.
- Consulta com valores decimais, para 20,5 °C e 42,5% de umidade, com saída de 33,23%.
- Rejeição de oito pares inválidos pela função de cálculo: temperatura −1, 41, `NaN` ou infinito, e umidade −1, 101, `NaN` ou infinito negativo, mantendo a outra entrada válida.
- Validação de 14 casos pela linha de comando: consulta individual, ajuda e 12 erros envolvendo argumentos ausentes, uso conjunto de `--exemplos` com uma entrada, texto não numérico e os oito pares inválidos. As falhas retornaram código 2 com mensagem de erro, sem rastreamento de exceção.

A grade finita complementa a análise de cobertura, mas não constitui uma enumeração de todas as entradas reais possíveis. Esses testes avaliam a implementação e não validam o modelo como controlador de conforto térmico.

O ambiente utilizado nos testes foi Python 3.12.4, Scikit-Fuzzy 0.5.0, NumPy 2.5.4, SciPy 1.18.1, NetworkX 3.7 e Matplotlib 3.11.2. As dependências foram instaladas em uma pasta temporária, fora dos arquivos entregues.

## 8. Limitações do sistema

As funções de pertinência e as regras são escolhas didáticas, sem calibração experimental. Os testes verificam a execução da inferência e a validade numérica das saídas; não medem precisão científica ou conforto térmico.

O modelo não considera ocupação, circulação de ar, radiação solar, preferências individuais ou características do ventilador. Também não possui memória temporal, realimentação ou tratamento do ruído de sensores. Assim, mudanças sucessivas nas entradas podem alterar a recomendação sem qualquer mecanismo de estabilização temporal.

Embora o universo de saída seja [0, 100]%, o centroide dos conjuntos definidos não precisa atingir os extremos. A categoria baixa não representa necessariamente ventilador desligado, e a categoria alta não equivale necessariamente a 100% de potência. Uma aplicação física exigiria outra etapa de modelagem e validação.

## 9. Instruções básicas de execução

Com Python 3 instalado, executar a partir da raiz do repositório:

```bash
cd questao_06
python -m pip install -r requirements.txt
python sistema_fuzzy.py --temperatura 25 --umidade 50
python sistema_fuzzy.py --exemplos
```

O modo `--exemplos` executa os três cenários solicitados, o exemplo dos picos, uma transição e os quatro cantos dos universos de entrada. Para uma consulta individual, os dois argumentos são obrigatórios. Valores fora dos intervalos, `NaN` e infinito são rejeitados com uma mensagem de erro, sem serem ajustados automaticamente aos limites. Valores decimais devem ser escritos com ponto, como `--temperatura 29.5`.

O arquivo de dependências inclui Scikit-Fuzzy, NumPy, SciPy, NetworkX e Matplotlib, utilizados pela biblioteca e por sua API de controle. Não é necessário abrir gráficos para executar o programa.

## 10. Referências

- SCIKIT-FUZZY. [Fuzzy Control Systems: The Tipping Problem](https://scikit-fuzzy.github.io/scikit-fuzzy/auto_examples/plot_tipping_problem_newapi.html). Exemplo oficial de construção e simulação com a API de controle.
- SCIKIT-FUZZY. [Módulo skfuzzy.control](https://scikit-fuzzy.readthedocs.io/en/latest/api/skfuzzy.control.html). Documentação dos objetos de controle e da simulação de Mamdani.
- SCIKIT-FUZZY. [Código-fonte de controlsystem](https://scikit-fuzzy.readthedocs.io/en/latest/_modules/skfuzzy/control/controlsystem.html). Detalhamento da inferência, do truncamento e da agregação implementados pela biblioteca.
- SCIKIT-FUZZY. [Repositório oficial](https://github.com/scikit-fuzzy/scikit-fuzzy). Dependências e instruções de instalação.
