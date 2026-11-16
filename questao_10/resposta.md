# Questão 10: Planejamento de rotas com algoritmos de busca

## 1. Introdução e formulação do problema

A empresa precisa determinar uma rota entre o centro de distribuição A e o destino I. O mapa contém nove localidades e custos de deslocamento em minutos. O problema de busca é definido pelos seguintes elementos:

| Elemento | Definição |
|---|---|
| Estados | Localidades A, B, C, D, E, F, G, H e I |
| Estado inicial | A |
| Teste de objetivo | A localidade atual é I |
| Ações | Deslocar-se para uma localidade adjacente |
| Transição | Passar do vértice atual ao vértice conectado pela aresta escolhida |
| Custo de uma ação | Peso da aresta percorrida, em minutos |
| Custo da solução | Soma dos pesos das arestas da rota |

O grafo é não direcionado: cada trecho pode ser percorrido nos dois sentidos, com o mesmo custo. Todos os pesos são positivos. Não há custos adicionais associados às localidades.

## 2. Representação do grafo

A implementação em [buscas.py](./buscas.py) utiliza um dicionário de adjacência. Cada localidade possui um dicionário com seus vizinhos e os respectivos custos. As 12 arestas são:

| Trecho | Custo (min) | Trecho | Custo (min) |
|---|---:|---|---:|
| A–B | 4 | A–D | 3 |
| B–C | 5 | B–E | 2 |
| C–F | 2 | D–E | 4 |
| D–G | 6 | E–F | 3 |
| E–H | 5 | F–I | 4 |
| G–H | 3 | H–I | 2 |

Não foram incluídas outras conexões. Cada aresta aparece duas vezes na estrutura de adjacência, uma em cada sentido, totalizando 24 entradas.

### Convenções de execução

Todos os algoritmos examinam os vizinhos em ordem alfabética crescente. A busca termina quando o objetivo é selecionado para processamento, antes de gerar seus sucessores.

Um estado é descoberto quando entra pela primeira vez na fronteira. Na DFS recursiva, isso corresponde à entrada na chamada da função. Um estado é processado quando é retirado validamente da fronteira, ou quando sua chamada começa na DFS. Um estado é expandido somente quando seus sucessores são gerados. Assim, I aparece na ordem de processamento, mas não é contado como expansão no problema original.

DFS marca o vértice como visitado ao entrar na chamada e mantém essa marca mesmo após um retrocesso. BFS marca o vértice como descoberto ao inseri-lo na fila. UCS e A* mantêm o melhor custo conhecido: apenas uma melhoria estrita altera o predecessor e insere uma nova entrada no heap. Entradas cujo custo ficou desatualizado são descartadas e não contam como processamento ou expansão. O núcleo permite reabrir um estado caso surja um custo menor.

O heap utiliza a tupla `(prioridade, estado, g)`. Em UCS, a prioridade é g; em A*, é g + h. Empates de prioridade são resolvidos pela ordem lexicográfica dos estados. Se dois caminhos alcançam o mesmo estado com custo igual, o primeiro predecessor é preservado.

## 3. Busca em profundidade e busca em largura

O enunciado utiliza a expressão “Busca em Profundidade (BFS)”. Há uma ambiguidade nessa indicação: DFS corresponde à busca em profundidade, enquanto BFS corresponde à busca em largura. Foram implementadas ambas as interpretações.

### Busca em profundidade (DFS)

DFS segue um ramo até encontrar o objetivo ou precisar retroceder. Os pesos não influenciam a escolha dos próximos vértices. Com visitação alfabética e marcação na entrada da chamada, a execução produziu:

| Informação | Resultado |
|---|---|
| Ordem de processamento e descoberta | A → B → C → F → E → D → G → H → I |
| Vértices expandidos | A → B → C → F → E → D → G → H |
| Quantidade de expansões | 8 |
| Rota encontrada | A → B → C → F → E → D → G → H → I |
| Custo | 4 + 5 + 2 + 3 + 4 + 6 + 3 + 2 = 29 minutos |

Neste caso, a rota coincide com a ordem de processamento porque o objetivo é encontrado sem retrocesso. Essa coincidência não é uma propriedade geral da DFS.

### Busca em largura (BFS)

BFS utiliza uma fila FIFO e processa os vértices por profundidade. A marcação na inserção impede que um mesmo vértice seja descoberto repetidamente.

| Informação | Resultado |
|---|---|
| Ordem de processamento e descoberta | A → B → D → C → E → G → F → H → I |
| Vértices expandidos | A → B → D → C → E → G → F → H |
| Quantidade de expansões | 8 |
| Rota encontrada | A → B → C → F → I |
| Custo | 4 + 5 + 2 + 4 = 15 minutos |

A solução utiliza quatro arestas, o menor número necessário para alcançar I a partir de A. Entretanto, BFS não considera os pesos: minimizar a quantidade de arestas não garante minimizar o tempo quando os custos variam. A rota encontrada custa dois minutos a mais que a ótima.

## 4. Busca de custo uniforme (UCS)

UCS seleciona o estado com o menor custo acumulado g. O resultado foi:

| Seleção | Estado | g (min) | Predecessor |
|---:|---|---:|---|
| 1 | A | 0 | nenhum |
| 2 | D | 3 | A |
| 3 | B | 4 | A |
| 4 | E | 6 | B |
| 5 | C | 9 | B |
| 6 | F | 9 | E |
| 7 | G | 9 | D |
| 8 | H | 11 | E |
| 9 | I | 13 | F |

Ao expandir D, E é inicialmente inserido com custo 7. A expansão posterior de B melhora esse custo para 6 e troca seu predecessor para B. A entrada antiga de E é descartada quando retirada do heap. C, F e G empatam em g = 9 e são processados em ordem alfabética.

A ordem de descoberta foi A → B → D → E → G → C → F → H → I. Todos os vértices foram descobertos e nove foram processados. Houve oito expansões, correspondentes a A, D, B, E, C, F, G e H.

A rota retornada foi A → B → E → F → I, com custo 4 + 2 + 3 + 4 = 13 minutos. Como o grafo é finito e todos os custos são positivos, UCS é completa e encontra uma solução de custo mínimo.

## 5. Busca A*

A* prioriza os estados por f(n) = g(n) + h(n), em que g é o custo acumulado desde A e h é a estimativa do custo restante até I. A heurística fornecida foi mantida integralmente:

| Estado | A | B | C | D | E | F | G | H | I |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| h(n) | 10 | 8 | 6 | 9 | 6 | 4 | 5 | 2 | 0 |

### Execução

Cada linha corresponde a uma seleção válida da fronteira. As atualizações indicam os novos custos g e os predecessores atribuídos ao expandir o estado da linha.

| Estado selecionado | Predecessor | g | h | f | Atualizações da fronteira |
|---|---|---:|---:|---:|---|
| A | nenhum | 0 | 10 | 10 | B: g = 4, pai A; D: g = 3, pai A |
| B | A | 4 | 8 | 12 | C: g = 9, pai B; E: g = 6, pai B |
| D | A | 3 | 9 | 12 | G: g = 9, pai D |
| E | B | 6 | 6 | 12 | F: g = 9, pai E; H: g = 11, pai E |
| F | E | 9 | 4 | 13 | I: g = 13, pai F |
| H | E | 11 | 2 | 13 | Nenhuma melhoria |
| I | F | 13 | 0 | 13 | Parada, sem expansão |

A ordem de processamento foi A → B → D → E → F → H → I. Os seis vértices expandidos foram A, B, D, E, F e H. A ordem de descoberta foi A → B → D → C → E → G → F → H → I, totalizando nove vértices descobertos. C e G permanecem na fronteira quando a busca termina, com f = 15 e f = 14, respectivamente.

B é selecionado antes de D no empate em f = 12. Depois, F e H são selecionados antes de I nos empates em f = 13. F descobre I com g = 13; H oferece outro caminho de mesmo custo, que não substitui o predecessor já registrado. Portanto, a solução retornada é A → B → E → F → I, com 13 minutos. A alternativa A → B → E → H → I também custa 4 + 2 + 5 + 2 = 13 minutos.

### Admissibilidade

A heurística é admissível se nunca supera o custo mínimo real restante. As distâncias exatas até I foram calculadas por Bellman-Ford, independentemente das buscas com heap:

| Estado | h(n) | Distância mínima até I | Verificação |
|---|---:|---:|---|
| A | 10 | 13 | 10 ≤ 13 |
| B | 8 | 9 | 8 ≤ 9 |
| C | 6 | 6 | 6 ≤ 6 |
| D | 9 | 11 | 9 ≤ 11 |
| E | 6 | 7 | 6 ≤ 7 |
| F | 4 | 4 | 4 ≤ 4 |
| G | 5 | 5 | 5 ≤ 5 |
| H | 2 | 2 | 2 ≤ 2 |
| I | 0 | 0 | 0 ≤ 0 |

Todos os valores são não negativos, h(I) = 0 e h(n) ≤ distância mínima para cada vértice. Logo, a heurística é admissível neste grafo.

### Consistência

A consistência exige h(u) ≤ c(u,v) + h(v) para toda transição. Como as arestas são não direcionadas, foram verificadas as duas direções de cada trecho:

| Trecho (u,v) | Direção u → v | Direção v → u |
|---|---|---|
| A–B | 10 ≤ 4 + 8 = 12 | 8 ≤ 4 + 10 = 14 |
| A–D | 10 ≤ 3 + 9 = 12 | 9 ≤ 3 + 10 = 13 |
| B–C | 8 ≤ 5 + 6 = 11 | 6 ≤ 5 + 8 = 13 |
| B–E | 8 ≤ 2 + 6 = 8 | 6 ≤ 2 + 8 = 10 |
| C–F | 6 ≤ 2 + 4 = 6 | 4 ≤ 2 + 6 = 8 |
| D–E | 9 ≤ 4 + 6 = 10 | 6 ≤ 4 + 9 = 13 |
| D–G | 9 ≤ 6 + 5 = 11 | 5 ≤ 6 + 9 = 15 |
| E–F | 6 ≤ 3 + 4 = 7 | 4 ≤ 3 + 6 = 9 |
| E–H | 6 ≤ 5 + 2 = 7 | 2 ≤ 5 + 6 = 11 |
| F–I | 4 ≤ 4 + 0 = 4 | 0 ≤ 4 + 4 = 8 |
| G–H | 5 ≤ 3 + 2 = 5 | 2 ≤ 3 + 5 = 8 |
| H–I | 2 ≤ 2 + 0 = 2 | 0 ≤ 2 + 2 = 4 |

As 24 desigualdades são satisfeitas. Com custos positivos, grafo finito, h(I) = 0 e essa heurística consistente, a seleção do objetivo em A* garante uma solução ótima. Nenhum estado precisou ser reaberto nesta execução.

## 6. Comparação dos algoritmos

A coluna de expansões considera somente a geração de sucessores. As propriedades abaixo referem-se a este grafo finito, às implementações com controle de repetição e aos custos e à heurística utilizados.

| Algoritmo | Rota encontrada | Custo (min) | Nós expandidos | Completude | Otimalidade em custo |
|---|---|---:|---:|---|---|
| DFS | A → B → C → F → E → D → G → H → I | 29 | 8 | Sim, grafo finito e visitados | Não garante |
| BFS | A → B → C → F → I | 15 | 8 | Sim, grafo finito e fila FIFO | Não garante com pesos distintos |
| UCS | A → B → E → F → I | 13 | 8 | Sim, grafo finito e custos positivos | Sim |
| A* | A → B → E → F → I | 13 | 6 | Sim, nas condições verificadas | Sim, heurística admissível e consistente |

DFS encontrou a rota mais cara entre as retornadas. BFS reduziu o número de arestas, mas não atingiu o custo mínimo. UCS encontrou o ótimo usando apenas os custos acumulados. A* atingiu o mesmo custo com duas expansões a menos, uma redução de 25% em relação a UCS nesta execução. Isso não permite concluir que qualquer heurística ou grafo produzirá a mesma redução.

## 7. Visitas obrigatórias a D e F

Para exigir a passagem pelas duas localidades, o estado passou a ser `(localidade_atual, visitou_D, visitou_F)`. O estado inicial é `(A, False, False)` e o objetivo é `(I, True, True)`. As visitas podem acontecer em qualquer ordem.

Ao atravessar uma aresta, o custo original é preservado. O marcador de D torna-se verdadeiro ao chegar a D, e o de F torna-se verdadeiro ao chegar a F. Marcadores verdadeiros permanecem verdadeiros. Existem no máximo 9 × 2 × 2 = 36 combinações de estado, embora algumas sejam inalcançáveis.

Chegar a E sem ter visitado D é diferente de chegar a E após essa visita. Um controle de visitados baseado apenas na localidade eliminaria caminhos que ainda precisam ser considerados. Por isso, os custos e predecessores são associados à tupla completa.

A UCS sobre os estados estendidos calculou automaticamente:

```text
(A, False, False)
  → (D, True, False)
  → (E, True, False)
  → (F, True, True)
  → (I, True, True)
```

A rota é A → D → E → F → I e custa 3 + 4 + 3 + 4 = 14 minutos. D e F aparecem antes da chegada final a I. A execução descobriu 29 estados, processou 24 e expandiu 23. Apenas o objetivo completo não foi expandido entre os estados processados.

O teste de objetivo não aceita I com marcadores incompletos. Tais estados podem ser processados e gerar sucessores, pois alcançar I não encerra a busca sem as visitas exigidas. Isso acontece nesta execução com `(I, False, False)`, `(I, False, True)` e `(I, True, False)`. A solução ótima retornada não passa antecipadamente por I. A formulação segue o teste de objetivo solicitado, sem impor uma proibição adicional de transitar por I.

A otimalidade decorre da aplicação de UCS a um espaço finito com custos positivos. Como conferência independente, Bellman-Ford foi executado sobre as 36 combinações e suas transições, construídas separadamente. A distância de `(A, False, False)` a `(I, True, True)` foi 14. Assim, o custo da rota coincide com o mínimo calculado por outro algoritmo.

## 8. Execução e validação

O programa utiliza somente a biblioteca padrão do Python. A demonstração pode ser executada dentro desta pasta com:

```text
python buscas.py
```

A execução de validação foi realizada com Python 3.13.12, utilizando o ambiente virtual existente do repositório e este comando, dentro de `questao_10`:

```powershell
& '../.venv/Scripts/python.exe' -B buscas.py
```

A opção `-B` evita gerar arquivos de bytecode. A saída é configurada explicitamente em UTF-8, para que as setas das rotas sejam exibidas também em consoles e redirecionamentos do Windows. O comando terminou com código de saída 0, após executar as verificações internas, sem instalar dependências. Também foi consultado o diagnóstico do editor para o arquivo Python, que não apresentou erros.

As verificações efetivamente executadas foram:

1. Presença exata dos nove vértices e das 12 arestas, correspondência dos pesos com a especificação, simetria e positividade.
2. Validade das arestas das rotas e igualdade entre custos retornados e somas recalculadas.
3. Correspondência da rota e da ordem de processamento de DFS e BFS com as convenções alfabéticas definidas.
4. Reexecução de todas as cinco buscas e comparação dos resultados completos, incluindo ordens, descobertas, expansões e registros da fronteira.
5. Custos 13 para UCS e A*, comparados com a distância de referência de Bellman-Ford.
6. Admissibilidade em todos os nove estados e consistência nos 24 sentidos de transição.
7. Coerência dos marcadores ao longo da rota estendida e presença de D e F antes do objetivo final.
8. Custo 14 da rota obrigatória, comparado com Bellman-Ford no espaço estendido.
9. Conferência das tabelas e contagens deste relatório com a saída real da demonstração.

As verificações estão incluídas em [buscas.py](./buscas.py) por meio de asserções e são executadas antes da apresentação dos resultados. Não se deve usar a opção `-O` na validação, pois ela desativa asserções. A conferência independente usa relaxações de Bellman-Ford, sem reutilizar a fila de prioridade ou a reconstrução de caminhos das buscas principais.

A validação cobre os dados fixos do exercício e a repetibilidade das execuções. Não constitui uma bateria de testes para grafos arbitrários, e nenhuma medição de tempo ou memória foi realizada. O ganho de A* relatado é exclusivamente a diferença na quantidade de expansões observada.

## 9. Referências

RUSSELL, Stuart; NORVIG, Peter. Artificial Intelligence: A Modern Approach. 4. ed. Pearson, 2021. Capítulo 3: Solving Problems by Searching.
