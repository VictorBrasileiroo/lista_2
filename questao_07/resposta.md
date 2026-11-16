# Questão 7: Sistema de Apoio ao Diagnóstico Médico Baseado em Casos

Lista 2 de Inteligência Artificial, 2026.2. Professor Evandro Costa.

## 1. Introdução

O protótipo recebe sintomas, compara a consulta com uma base artificial e apresenta uma hipótese educacional acompanhada de uma orientação ilustrativa. Um operador pode confirmar, corrigir ou rejeitar essa hipótese antes de decidir se deseja armazenar um novo caso.

O Raciocínio Baseado em Casos (RBC) utiliza experiências registradas para apoiar a solução de novos problemas. O ciclo envolve recuperar experiências semelhantes, reutilizar uma solução, revisar o resultado e reter a experiência pertinente. A organização adotada segue essas quatro etapas, discutidas por [Aamodt e Plaza (1994)](https://www.iiia.csic.es/~enric/AICom_ToC.html). Neste trabalho, as experiências são inteiramente fictícias e a revisão é uma ação didática do operador.

O programa foi implementado em Python 3, usando somente a biblioteca padrão e uma interface de terminal. Não utiliza dados de pacientes, serviços externos ou validação clínica.

## 2. Base de conhecimento

A base inicial em [casos.json](./casos.json) contém 15 registros, distribuídos igualmente entre cinco condições.

| Condição | Identificador textual | IDs | Quantidade |
| --- | --- | --- | --- |
| Resfriado comum | `resfriado_comum` | 1, 2 e 3 | 3 |
| Gripe | `gripe` | 4, 5 e 6 | 3 |
| Rinite alérgica | `rinite_alergica` | 7, 8 e 9 | 3 |
| Gastroenterite | `gastroenterite` | 10, 11 e 12 | 3 |
| Enxaqueca | `enxaqueca` | 13, 14 e 15 | 3 |

Cada caso contém um ID inteiro positivo, uma lista de sintomas, um diagnóstico textual e uma orientação no campo `tratamento`. As listas são convertidas em conjuntos para calcular similaridade. O JSON utiliza listas porque esse formato não possui um tipo nativo para conjuntos.

Exemplo real da base:

```json
{
  "id": 4,
  "sintomas": ["febre", "tosse", "dor_no_corpo", "fadiga"],
  "diagnostico": "gripe",
  "tratamento": "Orientação fictícia: descanso e hidratação geral; buscar avaliação profissional para acompanhar o quadro."
}
```

Os registros possuem quatro sintomas cada, com combinações distintas. O vocabulário é compartilhado entre as condições e usa um único termo por conceito, como `dor_de_cabeca`. Não há conjuntos de sintomas idênticos na base inicial. Uma mesma condição mantém uma orientação geral consistente entre seus três casos, sem medicamentos ou dosagens.

A base foi construída artificialmente para demonstrar recuperação e ambiguidade. A seleção de sintomas não foi obtida de prontuários ou avaliada por profissionais de saúde.

## 3. Método de similaridade

Para os conjuntos A, da consulta, e B, de um caso, utiliza-se:

```text
J(A, B) = |A ∩ B| / |A ∪ B|
```

A interseção conta os sintomas compartilhados, enquanto a união conta todos os sintomas distintos presentes em pelo menos um dos conjuntos. O resultado fica entre 0 e 1. A função retorna 0 quando ambos os conjuntos são vazios; a interface rejeita consultas vazias antes dessa etapa.

Por exemplo, para A = {febre, tosse, fadiga} e B = {febre, tosse, dor_no_corpo}, a interseção contém dois elementos e a união contém quatro. Portanto, J(A, B) = 2/4 = 0,50.

Jaccard foi escolhido por operar diretamente sobre conjuntos, dispensar treinamento e permitir explicar o resultado pela sobreposição dos sintomas. A posição de um sintoma na entrada e suas repetições não alteram o cálculo.

Todos os sintomas têm o mesmo peso. O programa não considera intensidade, duração, idade, histórico ou ausência explícita de um sintoma. A pontuação e sua apresentação percentual expressam sobreposição, nunca probabilidade de diagnóstico correto.

## 4. Implementação do ciclo RBC

O código está em [sistema_rbc.py](./sistema_rbc.py).

### 4.1 Recuperação

A função `interpretar_sintomas` separa a entrada por vírgulas, remove espaços excedentes, converte letras para minúsculas, remove acentos e padroniza separadores. Assim, `Náusea` torna-se `nausea` e `dor no corpo` torna-se `dor_no_corpo`. Repetições são eliminadas pela representação em conjunto.

Entradas vazias e itens vazios entre vírgulas são rejeitados. Termos desconhecidos interrompem a consulta e podem receber uma sugestão ortográfica calculada com `difflib`. A correção não é aplicada automaticamente e nenhum sintoma desconhecido é descartado silenciosamente. O terminal mostra o vocabulário disponível.

A função `recuperar` calcula Jaccard para todos os casos e ordena por pontuação decrescente e ID crescente. A exibição mostra os três primeiros registros, incluindo sintomas, diagnóstico e pontuação. Com a base entregue, há sempre casos suficientes para exibir três posições. Pontuações nulas podem aparecer entre os vizinhos, sem representar evidência favorável.

### 4.2 Reutilização

A função `reutilizar` seleciona o primeiro caso ordenado como origem da hipótese e de sua orientação. A saída também mostra os sintomas compartilhados. Se a maior pontuação for zero, nenhuma hipótese é produzida e a interface volta à entrada de sintomas.

Os diagnósticos de todos os casos empatados na maior pontuação são examinados, inclusive os que estejam além das três posições exibidas. Se houver condições diferentes, a ambiguidade é anunciada. O desempate por ID apenas garante uma execução determinística.

### 4.3 Revisão

O operador escolhe entre confirmar, corrigir e rejeitar ou cancelar. Opções inválidas são solicitadas novamente. Na correção, são oferecidas as outras condições existentes na base. O diagnóstico e a orientação passam a ser obtidos de um caso da condição escolhida, usando o menor ID dessa condição. Isso impede que a orientação da sugestão anterior seja mantida indevidamente.

A função `revisar` retorna o par diagnóstico e orientação, marcado como revisado, ou retorna `None` após cancelamento. Uma confirmação digitada representa somente a decisão do operador durante a demonstração.

### 4.4 Retenção

Após uma revisão concluída, o programa pergunta separadamente se o operador deseja salvar. A função `reter` rejeita revisão ausente ou cancelada e verifica se diagnóstico e orientação correspondem a um caso da base. Ela relê o JSON, calcula `max(id) + 1` e salva os sintomas consultados com o resultado revisado.

A leitura verifica a estrutura dos registros, os tipos dos campos, os sintomas normalizados e os IDs positivos e únicos. Base ausente, JSON inválido ou registros malformados produzem uma mensagem de erro, sem recriação automática do arquivo.

## 5. Experimentos

Os três cenários foram executados em 6 de novembro de 2026, com Python 3.12, pelo comando `py -3 -B questao_07\sistema_rbc.py --demo`, a partir da raiz do repositório. A opção `-B` impede a criação de cache de bytecode. Os números abaixo correspondem à saída calculada pelo programa.

### 5.1 Cenário A: caso semelhante

Consulta: `{febre, tosse, dor_no_corpo, fadiga}`.

| Posição | ID | Diagnóstico | Jaccard | Sobreposição percentual |
| --- | --- | --- | --- | --- |
| 1 | 4 | Gripe | 1,0000 | 100,00% |
| 2 | 6 | Gripe | 0,6000 | 60,00% |
| 3 | 3 | Resfriado comum | 0,3333 | 33,33% |

A hipótese educacional foi gripe, com a orientação do caso 4. Os quatro sintomas da consulta coincidem com esse caso. O valor 1,00 indica igualdade entre conjuntos, sem demonstrar acerto clínico. Não houve revisão nem retenção neste cenário.

### 5.2 Cenário B: caso ambíguo

Consulta: `{coriza, espirros}`.

| Posição | ID | Diagnóstico | Jaccard | Sobreposição percentual |
| --- | --- | --- | --- | --- |
| 1 | 1 | Resfriado comum | 0,5000 | 50,00% |
| 2 | 7 | Rinite alérgica | 0,5000 | 50,00% |
| 3 | 9 | Rinite alérgica | 0,5000 | 50,00% |

Os três casos compartilham os dois sintomas da consulta e possuem quatro sintomas no total. O programa informou explicitamente a ambiguidade entre resfriado comum e rinite alérgica. A hipótese exibida foi resfriado comum porque o caso 1 tem o menor ID, acompanhada da orientação desse registro.

O resultado mostra que o critério de ordenação não permite decidir qual condição corresponde ao problema real. Não houve revisão nem retenção neste cenário.

### 5.3 Cenário C: revisão e retenção

Consulta: `{febre, tosse, fadiga}`.

| Momento | Posição | ID | Diagnóstico | Jaccard |
| --- | --- | --- | --- | --- |
| Antes da retenção | 1 | 4 | Gripe | 0,7500 |
| Antes da retenção | 2 | 3 | Resfriado comum | 0,4000 |
| Antes da retenção | 3 | 5 | Gripe | 0,4000 |
| Após a retenção | 1 | 16 | Gripe | 1,0000 |
| Após a retenção | 2 | 4 | Gripe | 0,7500 |
| Após a retenção | 3 | 3 | Resfriado comum | 0,4000 |

A hipótese inicial foi gripe, com a orientação do caso 4. O operador simulado confirmou essa hipótese. O sistema reteve o caso 16 com os três sintomas consultados e a mesma orientação. Após reler a cópia do JSON, a base passou a conter 16 casos e o registro novo ocupou a primeira posição.

A demonstração utilizou uma pasta temporária dentro desta questão, removida ao final. A igualdade byte a byte entre a base original antes e depois foi conferida pelo programa. Os 15 registros entregues foram preservados.

### 5.4 Validações complementares

Foram executados 14 grupos de verificações com `unittest` e `unittest.mock`, por código enviado diretamente ao interpretador, sem criar arquivos de teste adicionais. Foram conferidos:

| Verificação | Resultado observado |
| --- | --- |
| Quantidade e distribuição | 15 casos, cinco condições, três casos por condição |
| Diversidade inicial | 15 conjuntos de sintomas distintos |
| Jaccard | Exemplo 2/4 correto e pontuações entre 0 e 1 para consultas de um a três termos do vocabulário |
| Recuperação e desempate | Ordenação correta e três casos exibidos |
| Ambiguidade | Empate entre resfriado e rinite identificado |
| Ausência de sobreposição | Consulta sintética na função de recuperação não gerou hipótese |
| Normalização e erros de entrada | Acentos, espaços e repetições tratados; entradas vazias e termos inválidos rejeitados |
| Revisão | Confirmação, correção, cancelamento e opções inválidas verificados |
| Compatibilidade da orientação | Correção simulada para rinite substituiu a orientação anterior |
| Bloqueio de retenção | Revisão ausente ou cancelada não alterou o JSON |
| Persistência | Outro processo Python leu 16 casos e recuperou o ID 16 com Jaccard 1,00 |
| Unicidade após nova retenção | O registro seguinte recebeu ID 17 na cópia de teste |
| Integridade da base | JSON ausente, sintaxe inválida, estrutura incorreta, campos inválidos e IDs repetidos rejeitados |
| Fluxos de terminal | Entradas simuladas cobriram confirmação, correção, cancelamento e recusa de armazenamento |
| Preservação | Demonstração e verificações mantiveram a base original intacta |

Os 14 grupos foram concluídos com sucesso.

A persistência após reinício foi verificada com um novo processo Python, independente da memória do processo que salvou o registro. A demonstração automática faz uma releitura do arquivo no mesmo processo. Os fluxos interativos foram exercitados com entradas simuladas; não foi realizado um estudo com usuários ou uma avaliação clínica.

## 6. Análise dos resultados

A recuperação funcionou conforme a sobreposição esperada: uma consulta igual a um registro recebeu pontuação máxima, enquanto correspondências parciais receberam valores menores. O caso semelhante apresentou uma origem identificável para a hipótese e sua orientação.

A consulta ambígua evidenciou a insuficiência dos sintomas compartilhados para distinguir condições. Com pesos iguais, dois sintomas comuns a várias condições podem produzir pontuações idênticas. O sistema não dispõe de informações adicionais que resolvam essa situação.

O tamanho e a composição da base influenciam diretamente a saída. Quinze casos artificiais não representam a diversidade de apresentações possíveis. A validação do vocabulário evita que erros de escrita sejam ignorados, mas também impede consultar sintomas que ainda não aparecem na base.

A retenção aumentou a pontuação da consulta do cenário C de 0,75 para 1,00 porque criou um registro com exatamente aqueles sintomas. Esse efeito demonstra memória de casos, sem estabelecer melhora de desempenho clínico. Decisões incorretas do operador também podem ser retidas e influenciar consultas posteriores.

O algoritmo utiliza o primeiro vizinho para a hipótese. Não há votação entre diagnósticos nem ponderação dos sintomas. Considerando n casos e conjuntos de tamanho até m, a comparação de todos os registros tem custo aproximado O(nm), seguido de ordenação O(n log n), adequado à pequena base proposta.

## 7. Limitações e cuidados

Todos os casos são fictícios e não possuem validação clínica. A similaridade não é uma probabilidade médica. Sintomas semelhantes podem ocorrer em condições distintas, inclusive condições ausentes da base.

O protótipo não substitui avaliação profissional. As orientações são textos ilustrativos, sem prescrição de medicamentos ou dosagens. A decisão de um operador durante a revisão não equivale a uma confirmação médica.

Não são representados intensidade, duração, histórico ou exames. Também não existe um limiar clínico de aceitação: qualquer sobreposição positiva pode produzir uma hipótese educacional, cuja pontuação permanece visível. Essa regra serve apenas à demonstração do ciclo.

A persistência usa um arquivo JSON local e foi projetada para um operador por vez. Há validação básica de estrutura e unicidade de IDs, sem mecanismos de concorrência ou recuperação contra interrupção durante a escrita. Casos idênticos podem ser retidos por decisão do operador; seus IDs permanecem distintos.

As verificações realizadas avaliam o comportamento computacional especificado. Não medem sensibilidade, especificidade, acurácia médica ou utilidade para atendimento real. Nenhum vídeo foi produzido; a demonstração executável é a forma de apresentação entregue.

## 8. Instruções de execução

É necessário Python 3. Não é preciso instalar bibliotecas. A partir da raiz do repositório, execute:

```text
python questao_07/sistema_rbc.py
```

Para a demonstração automática:

```text
python questao_07/sistema_rbc.py --demo
```

No Windows, também é possível substituir `python` por `py -3`. Se o terminal já estiver nesta pasta, use `python sistema_rbc.py` ou `python sistema_rbc.py --demo`. O caminho da base é resolvido a partir da localização do programa, independentemente do diretório de execução.

Na interface, digite sintomas separados por vírgulas. Para encerrar na entrada de uma consulta, digite `sair`. As opções de revisão são `1` para confirmar, `2` para corrigir e `3` para cancelar. Na correção, escolha o número mostrado para outra condição ou `0` para cancelar. Depois de confirmar ou corrigir, responda `s` ou `n` à pergunta de armazenamento. `Ctrl+C` também encerra a execução.

### Roteiro de apresentação interativa

1. Inicie o programa e informe `febre, tosse, dor no corpo, fadiga`. Observe os IDs 4, 6 e 3 e a hipótese de gripe. Digite `3` para cancelar a revisão.
2. Informe `coriza, espirros`. Observe os IDs 1, 7 e 9 com pontuação 0,50 e a mensagem de ambiguidade. Digite `3` para cancelar.
3. Informe `febre, tosse, fadiga`. Observe a hipótese inicial de gripe, com pontuação 0,75. Digite `1` para confirmar e `s` para salvar.
4. Digite `sair`, inicie o programa novamente e repita a consulta anterior. Na base inicial, o novo ID será 16 e terá pontuação 1,00. Se outros casos já tiverem sido retidos, seu ID será o próximo inteiro disponível.
5. Para apresentar a correção, repita uma consulta e escolha `2`. Selecione outra condição pela numeração exibida, confira a nova orientação e responda `n` para não salvar essa alteração simulada.

O passo 3 modifica a base no modo interativo. Para preservar os 15 registros ao gravar uma apresentação, execute o roteiro sobre uma cópia de trabalho do programa e do JSON ou utilize `--demo`, que já prepara e remove sua própria cópia temporária. Não é necessário produzir arquivos adicionais para a demonstração automática.

## 9. Referências

AAMODT, Agnar; PLAZA, Enric. Case-Based Reasoning: Foundational Issues, Methodological Variations, and System Approaches. AI Communications, v. 7, n. 1, p. 39-59, 1994. [Resumo e estrutura do artigo no site do IIIA-CSIC](https://www.iiia.csic.es/~enric/AICom_ToC.html). Consulta em: 6 nov. 2026. Utilizado como referência para a organização conceitual do RBC.

Enunciado da Questão 7 da Lista 2 de Inteligência Artificial, 2026.2, professor Evandro Costa. Utilizado para identificar os requisitos e o escopo da atividade. A similaridade de Jaccard foi adotada como decisão de modelagem deste trabalho.
