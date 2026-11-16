# Questão 2: K-vizinhos mais próximos (KNN)

## 1. Funcionamento do KNN

O KNN classifica uma instância a partir das classes das K instâncias mais próximas de um conjunto de referência. Para isso, calcula as distâncias, seleciona os vizinhos e realiza uma votação. Não ajusta previamente uma função de classificação: mantém os exemplos disponíveis para comparação no momento da previsão.

Nesta implementação, cada instância recebe a classe mais votada entre três vizinhos, com critérios de desempate definidos a seguir. O código utiliza apenas a biblioteca padrão do Python.

## 2. Base de dados

A base contém exatamente as 30 instâncias da Lista 1, identificadas de E1 a E30. Cada instância descreve um caso de classificação de risco de crédito por seis atributos categóricos: historia_credito, divida, garantia, renda, emprego e comprometimento. A coluna risco contém a classe real.

| Classe de risco | Quantidade |
| --- | ---: |
| Alto | 10 |
| Moderado | 10 |
| Baixo | 10 |
| Total | 30 |

O arquivo dados.csv preserva os dados fornecidos. O identificador permite reconhecer cada instância e desempatar a seleção de vizinhos. A classe real é usada na votação dos exemplos de referência e na avaliação das previsões. Nenhuma dessas duas colunas participa do cálculo das distâncias.

## 3. Distância, valor de K e desempates

Foi adotado K = 3. A distância de Hamming não normalizada conta quantos dos seis atributos diferem entre duas instâncias. Cada atributo contribui com zero quando os valores são iguais e com um quando são diferentes. Assim, a distância varia de 0 a 6, e atributos idênticos produzem distância zero.

Todos os atributos têm o mesmo peso. As faixas de renda são tratadas como categorias: qualquer diferença entre faixas conta como uma diferença, sem considerar uma distância numérica entre elas. O mesmo critério vale para os demais atributos.

Os candidatos são ordenados pela distância crescente. Quando dois candidatos têm a mesma distância, a ordem é definida pelo número do identificador, de modo que E2 precede E10. Apenas os três primeiros são selecionados, mesmo que outros candidatos tenham distância igual à do terceiro.

Na votação, vence a classe com mais votos. Havendo empate entre classes, vence aquela com a menor soma das distâncias de seus próprios votos. Se o empate persistir, aplica-se a ordem alfabética dos nomes: Alto, Baixo e Moderado. Classes sem votos não participam desse desempate.

## 4. Demonstração da classificação de E1

E1 possui historia_credito = Ruim, divida = Alta, garantia = Nenhuma, renda = 0-15k, emprego = Instavel e comprometimento = Alto. Sua classe real é Alto. Para classificá-la, E1 é excluída dos candidatos e são calculadas as distâncias às outras 29 instâncias.

| Instância candidata | Distância até E1 |
| --- | ---: |
| E2 | 4 |
| E3 | 5 |
| E4 | 2 |
| E5 | 5 |
| E6 | 6 |
| E7 | 3 |
| E8 | 4 |
| E9 | 5 |
| E10 | 4 |
| E11 | 2 |
| E12 | 3 |
| E13 | 4 |
| E14 | 2 |
| E15 | 6 |
| E16 | 4 |
| E17 | 4 |
| E18 | 3 |
| E19 | 5 |
| E20 | 4 |
| E21 | 4 |
| E22 | 1 |
| E23 | 3 |
| E24 | 4 |
| E25 | 2 |
| E26 | 6 |
| E27 | 5 |
| E28 | 3 |
| E29 | 5 |
| E30 | 4 |

E22 é a instância mais próxima, com distância 1. E4, E11, E14 e E25 têm distância 2. Pelo desempate numérico, E4 e E11 ocupam as duas vagas restantes.

| Vizinho selecionado | Atributos diferentes em relação a E1 | Distância | Classe |
| --- | --- | ---: | --- |
| E22 | garantia | 1 | Alto |
| E4 | historia_credito e divida | 2 | Alto |
| E11 | historia_credito e emprego | 2 | Alto |

Por exemplo, E22 tem garantia Adequada e E1 tem garantia Nenhuma. Os outros cinco atributos são iguais, o que resulta em distância 1.

| Classe | Votos | Soma das distâncias |
| --- | ---: | ---: |
| Alto | 3 | 5 |
| Moderado | 0 | 0 |
| Baixo | 0 | 0 |

Os três votos são para Alto, sem necessidade de desempate entre classes. A previsão para E1 é Alto e coincide com sua classe real.

## 5. Resultados do Leave-One-Out

No Leave-One-Out, cada uma das 30 instâncias é classificada uma vez, usando as outras 29 como referência. A própria instância é excluída antes da seleção dos vizinhos. O valor de K, a distância e os desempates permanecem iguais em todas as rodadas.

A execução de knn.py produziu os seguintes resultados:

| Medida | Resultado |
| --- | ---: |
| Instâncias avaliadas | 30 |
| Acertos | 11 |
| Erros | 19 |
| Acurácia | 36,67% |

A acurácia corresponde a 11 acertos divididos por 30 avaliações, multiplicados por 100. As 19 classificações incorretas foram:

| Instância | Classe real | Classe prevista |
| --- | --- | --- |
| E2 | Alto | Moderado |
| E3 | Moderado | Alto |
| E6 | Baixo | Moderado |
| E7 | Alto | Moderado |
| E8 | Moderado | Baixo |
| E11 | Alto | Moderado |
| E12 | Moderado | Alto |
| E15 | Moderado | Baixo |
| E16 | Moderado | Baixo |
| E17 | Moderado | Alto |
| E18 | Moderado | Baixo |
| E19 | Moderado | Baixo |
| E20 | Moderado | Baixo |
| E21 | Moderado | Alto |
| E25 | Alto | Moderado |
| E27 | Baixo | Moderado |
| E28 | Baixo | Moderado |
| E29 | Baixo | Moderado |
| E30 | Baixo | Moderado |

A validação confirmou a quantidade de instâncias e sua distribuição por classe, a distância zero para atributos idênticos e a exclusão do alvo em todas as rodadas. Uma conferência independente verificou os 900 pares de distâncias, incluindo os pares de uma instância consigo mesma, além dos vizinhos selecionados e da votação nas 30 classificações.

## 6. Discussão dos resultados e limitações

Embora E1 tenha sido classificada corretamente, o Leave-One-Out apresentou mais erros do que acertos. Nesta configuração, instâncias próximas pelos atributos nem sempre possuem a mesma classe. E3, por exemplo, tem E2, E17 e E5 como vizinhos, com classes Alto, Moderado e Baixo e distâncias 1, 1 e 2. Cada classe recebe um voto; Alto e Moderado empatam também na soma das distâncias. A ordem alfabética define a previsão Alto, diferente da classe real Moderado.

Há poucos valores possíveis para a distância, o que favorece empates. O desempate pelo número da instância torna a seleção reproduzível, mas esse número não expressa semelhança entre os casos. Além disso, a distância adotada atribui o mesmo peso a todos os atributos e desconsidera a ordem das faixas de renda e dos níveis de comprometimento. K = 3 foi fixado previamente, por ser um valor ímpar pequeno, sem buscar um valor que maximize os acertos.

A base é pequena e foi construída para fins didáticos. A acurácia de 36,67% descreve somente as previsões obtidas nessas 30 instâncias com as regras adotadas. Ela não deve ser tratada como uma medida confiável do desempenho em casos reais de risco de crédito.
