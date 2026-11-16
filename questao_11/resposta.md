# Questão 11: Agentes inteligentes clássicos e agentes baseados em LLMs

## 1. Introdução e apresentação do problema

Um professor precisa organizar atividades acadêmicas entre 14h e 18h. A janela oferece 240 minutos, enquanto as tarefas somam 330 minutos. Portanto, o problema exige selecionar atividades e justificar as pendências, além de distribuir horários.

| Atividade | Duração | Prioridade | Prazo ou horário |
| --- | --- | --- | --- |
| A. Preparar aula de IA | 90 minutos | Alta | Hoje |
| B. Corrigir trabalhos | 120 minutos | Média | Amanhã |
| C. Reunião de pesquisa | 60 minutos | Alta | Hoje, obrigatoriamente das 16h às 17h |
| D. Revisar artigo | 60 minutos | Baixa | Próxima semana |

As atividades não podem se sobrepor e são indivisíveis, salvo autorização explícita. As urgentes devem ser priorizadas, e qualquer tarefa não realizada precisa de justificativa. Não há informação sobre disponibilidade em outros dias.

Segundo Russell e Norvig (2021, cap. 2), um agente percebe seu ambiente e atua sobre ele. Sua racionalidade é avaliada em relação a uma medida de desempenho, às informações disponíveis e às ações possíveis. Nesse cenário, tanto uma arquitetura clássica quanto uma baseada em grandes modelos de linguagem (LLMs) podem buscar uma agenda adequada. A diferença está principalmente em como interpretam o pedido, representam o problema e articulam planejamento e verificação. Os exemplos a seguir são conceituais, sem execução de agente, LLM ou ferramenta de calendário.

## 2. Formulação do planejamento

O estado contém as atividades concluídas ou pendentes e os intervalos ocupados. Durante a construção do plano, também registra as tarefas já alocadas, que só serão consideradas concluídas após sua execução. Uma ação de planejamento consiste em selecionar uma atividade e atribuir a ela um intervalo de duração suficiente.

O objetivo é produzir uma agenda viável que respeite as exigências obrigatórias e priorize atividades relevantes. As restrições rígidas incluem a janela de 14h a 18h, as durações, a reunião fixa, a ausência de sobreposição e a indivisibilidade. A e C precisam ser atendidas hoje. Já o prazo de B amanhã não permite considerá-la atrasada apenas porque ficou pendente hoje, mas exige acompanhamento antes do vencimento.

Prioridades e proximidade dos prazos orientam a escolha entre planos viáveis. A exigência de priorizar atividades urgentes pode ser operacionalizada atendendo primeiro A e C, ambas de prioridade alta e prazo hoje. Isso não significa que uma tarefa de menor prioridade esteja proibida de ocupar um espaço no qual outra, mais prioritária, não caiba integralmente.

O recurso explicitamente limitado é o tempo de um único professor. Não foram informadas dependências de precedência entre tarefas, como a necessidade de concluir A antes de D, nem outros recursos escassos. Se existissem, precisariam ser incluídos no modelo, sem presumir relações ausentes no enunciado.

Uma função de utilidade poderia diferenciar agendas válidas, mas seus pesos e critérios teriam de ser definidos. Como o problema não fornece valores numéricos para as prioridades, a solução apresentada será justificada por viabilidade e urgência, sem alegar maximização matemática de utilidade.

## 3. Solução pela abordagem clássica

Uma arquitetura clássica baseada em objetivos pode representar cada tarefa por identificador, duração, prioridade, prazo e, quando necessário, horário fixo. Um modelo da agenda mantém os intervalos ocupados e permite avaliar as consequências de inserir uma atividade.

O agente aplica regras explícitas para descartar alocações incompatíveis. A busca ou o planejador explora combinações de tarefas e horários, verifica as restrições e compara as alternativas restantes segundo critérios declarados. Uma formulação como problema de satisfação de restrições também é possível: as variáveis representam alocações e as restrições delimitam quais combinações são admissíveis.

Neste caso, uma estratégia é reservar primeiro C, que possui horário obrigatório, e buscar uma posição para A, que também vence hoje. Depois, o agente examina quais tarefas cabem nos espaços restantes. O procedimento pode ser descrito pelo seguinte pseudocódigo conceitual:

```text
Representar tarefas, janela disponível e restrições.
Reservar C no intervalo obrigatório de 16h a 17h.
Buscar alocações completas para as demais tarefas, admitindo pendências.
Descartar planos com conflitos ou que deixem de atender A e C hoje.
Comparar os planos válidos por prioridades, prazos e critérios declarados.
Verificar o plano escolhido e registrar as justificativas das pendências.
```

Uma função de utilidade previamente definida poderia substituir ou complementar a comparação qualitativa. A característica central permanece o uso explícito de estados, ações, objetivos e restrições. O capítulo 2 de Russell e Norvig fundamenta essa caracterização do agente; a formulação concreta da agenda é uma aplicação desses conceitos ao enunciado.

O agente também pode consultar um calendário e registrar compromissos por meio de interfaces de software. A explicação das decisões pode ser produzida a partir das regras aplicadas e dos motivos de descarte. Contudo, a confiabilidade depende da correção do modelo: uma restrição importante que não tenha sido representada não será automaticamente respeitada.

## 4. Solução conceitual baseada em LLM

Em uma arquitetura hipotética com LLM, o professor descreve suas necessidades em linguagem natural. O modelo identifica tarefas, durações, prioridades, prazos e horários obrigatórios e converte essas informações em registros estruturados. Ambiguidades relevantes, como a possibilidade de dividir B, devem ser esclarecidas antes de alterar a regra de indivisibilidade.

A partir desses registros, o LLM pode propor uma agenda ou solicitar uma solução a um planejador. Quando há ferramentas disponíveis, a arquitetura encaminha a proposta a um validador e consulta o calendário para conferir compromissos conhecidos. O retorno pode indicar conflitos, durações insuficientes ou tarefas omitidas. O modelo usa esse feedback para revisar a proposta e explicar as decisões ao professor.

Por exemplo, se o LLM sugerisse B das 15h30 às 16h00 como tarefa concluída, um validador informaria que foram reservados somente 30 dos 120 minutos exigidos. A arquitetura precisaria corrigir o plano e manter B pendente. Esse fluxo é uma demonstração conceitual, não o relato de uma execução.

Gerar uma proposta é diferente de comprovar sua validade. Uma resposta linguisticamente convincente pode conter erros de cálculo ou ignorar uma restrição. Um calendário pode detectar sobreposições, mas não necessariamente verificar todas as regras acadêmicas ou a indivisibilidade; a ferramenta precisa oferecer as verificações pertinentes.

O trabalho ReAct, de Yao et al. (2023), contextualiza a combinação de raciocínio em linguagem e ações em ambientes com ferramentas. Ele não estabelece, por si só, garantias de correção ou de otimalidade para este problema de agenda. Uma arquitetura com LLM pode incorporar busca, planejamento e validação clássicos, usando o modelo como componente de interpretação e interação.

## 5. Exemplo de agenda e análise de viabilidade

### 5.1. Plano com tarefas indivisíveis

| Horário | Atividade | Duração |
| --- | --- | --- |
| 14h00 a 15h30 | A. Preparar aula de IA | 90 minutos |
| 15h30 a 16h00 | Intervalo disponível | 30 minutos |
| 16h00 a 17h00 | C. Reunião de pesquisa | 60 minutos |
| 17h00 a 18h00 | D. Revisar artigo | 60 minutos |

A e C recebem suas durações completas, atendendo às prioridades altas e aos prazos de hoje. C ocupa exatamente o horário obrigatório, todas as atividades ficam dentro da janela e não há sobreposições. Os intervalos são considerados com início incluído e fim excluído, permitindo que uma tarefa comece no instante em que outra termina.

B permanece pendente. Depois de reservar A e C, sobram 90 minutos no total, distribuídos em intervalos de 30 e 60 minutos. Isso é insuficiente para os 120 minutos de B e também não oferece um bloco contínuo adequado. D cabe integralmente das 17h às 18h. Sua inclusão aproveita um espaço disponível sem impedir a execução completa de B, que já não seria possível nessas condições.

O plano ocupa 210 minutos e deixa 30 livres. É uma solução viável, sem afirmação de que seja única ou de maior utilidade. A correção dos trabalhos deverá ser planejada antes do prazo de amanhã, mas não se pode garantir um horário em outro dia sem conhecer a disponibilidade do professor.

### 5.2. Alternativa com divisão autorizada de B

Se o professor permitir dividir B, os intervalos menores passam a comportar partes dessa tarefa:

| Horário | Atividade | Duração |
| --- | --- | --- |
| 14h00 a 15h30 | A. Preparar aula de IA | 90 minutos |
| 15h30 a 16h00 | B. Corrigir trabalhos, primeira parte | 30 minutos |
| 16h00 a 17h00 | C. Reunião de pesquisa | 60 minutos |
| 17h00 a 18h00 | B. Corrigir trabalhos, segunda parte | 60 minutos |

Nesse cenário, A e C continuam integralmente atendidas. B recebe 90 dos 120 minutos necessários e permanece parcialmente pendente, com 30 minutos restantes. D também fica pendente, pois seu prazo mais distante justifica ceder o intervalo final ao avanço de B. Nenhum horário futuro é presumido.

Essa alternativa só é admissível mediante autorização para dividir B. A mudança de restrição amplia as alocações possíveis, mas não transforma execução parcial em conclusão.

### 5.3. Verificação determinística

Um verificador pode conferir os horários por aritmética de intervalos e regras explícitas. Ele deve verificar se cada tarefa declarada completa recebeu sua duração, se todas as alocações estão entre 14h e 18h, se não há interseções e se C ocorre das 16h às 17h. Também deve conferir a indivisibilidade e produzir uma relação consistente das tarefas completas, parciais e pendentes.

Os prazos conhecidos precisam ser avaliados conforme o alcance das informações: A e C são atendidas hoje; B continua com vencimento amanhã; D mantém seu prazo na próxima semana. A pendência de B não prova atraso, mas tampouco garante atendimento futuro. Se um prazo informado apenas como dia exigisse precisão de horário, esse dado precisaria ser esclarecido.

Como exemplo hipotético de plano inválido, alocar B das 15h às 17h e manter C das 16h às 17h viola a ausência de sobreposição. Já marcar B como concluída após executá-la somente das 17h às 18h viola sua duração e, no cenário original, a indivisibilidade. Ferramentas estruturadas complementam o LLM ao detectar esses erros de forma reproduzível. Essa validação comprova apenas as propriedades verificadas sobre os dados fornecidos, não a execução real das tarefas.

## 6. Comparação entre as abordagens

| Aspecto | Agente clássico | Agente baseado em LLM |
| --- | --- | --- |
| Formato das entradas | Tipicamente registros estruturados; pode incluir um módulo de linguagem natural. | Recebe pedidos em linguagem natural e pode convertê-los em dados estruturados. |
| Representação do conhecimento | Estados, regras, relações, objetivos e modelos explícitos. | Conhecimento aprendido nos parâmetros, contexto textual e, conforme a arquitetura, memória e modelos externos. |
| Interpretação de linguagem natural | Depende dos recursos de interpretação incorporados. | Oferece flexibilidade para interpretar formulações variadas, com possibilidade de ambiguidades e erros. |
| Planejamento | Busca ou planejamento sobre estados, ações e critérios definidos. | Pode propor sequências e revisar planos, além de acionar planejadores externos. |
| Tratamento de restrições | Regras formalizadas permitem rejeitar violações durante a busca ou validação. | Restrições descritas no contexto podem ser ignoradas; componentes explícitos aumentam a confiabilidade. |
| Interação com ferramentas | Integrações programadas permitem consultar e alterar sistemas externos. | Pode selecionar ferramentas e gerar argumentos, dentro das interfaces e permissões implementadas. |
| Explicabilidade | Pode apresentar regras aplicadas e motivos registrados para suas escolhas. | Produz explicações acessíveis, que precisam corresponder aos dados e às verificações efetivas. |
| Verificabilidade | Modelos explícitos favorecem checagens e, quando cabível, garantias formais. | O texto gerado não comprova validade; propostas estruturadas podem ser verificadas externamente. |
| Limitações principais | Exige modelagem e manutenção; entradas imprevistas podem demandar novas regras. | Pode inventar informações, errar cálculos ou produzir planos inconsistentes com explicações plausíveis. |

Essa comparação descreve características típicas. Agentes clássicos podem interpretar linguagem natural, e agentes com LLM podem planejar. As capacidades dependem dos componentes da arquitetura, das informações disponíveis e dos mecanismos de controle.

## 7. Vantagens dos agentes com LLM e necessidade de mecanismos explícitos

### Quando agentes baseados em LLM oferecem vantagens?

Eles oferecem vantagens quando o professor apresenta solicitações abertas ou ambíguas, descreve tarefas em textos não estruturados ou modifica o pedido durante uma conversa. O modelo pode extrair informações, adaptar-se a diferentes formas de expressão e solicitar esclarecimentos, como confirmar se a correção dos trabalhos admite interrupções.

Também facilita a comunicação dos motivos de uma escolha e a integração flexível com ferramentas, quando as interfaces são adequadamente implementadas. Por exemplo, pode explicar por que D foi incluída apesar de B ter maior prioridade: D cabe no intervalo disponível, enquanto B exige um bloco maior. Essas vantagens são especialmente úteis na passagem entre a intenção humana e um problema estruturado.

### O que ainda depende de mecanismos explícitos?

Verificar restrições rígidas, calcular horários e durações com precisão e garantir ausência de conflitos exige mecanismos cujas operações possam ser conferidas. A busca de uma solução ótima requer ainda critérios definidos e um método adequado, com condições de completude e otimalidade quando essas garantias forem exigidas.

O controle do estado e da execução também precisa ser explícito: uma tarefa planejada não equivale a uma tarefa realizada. Alterações no calendário devem depender de ações efetivamente executadas e de seus retornos. Da mesma forma, pendências e cumprimento de prazos precisam ser atualizados com base em informações confirmadas.

Assim, uma arquitetura híbrida pode combinar a flexibilidade linguística do LLM com planejamento e validação determinísticos. Isso não torna todo agente híbrido superior. Para uma agenda pequena e já estruturada, uma solução clássica pode ser suficiente; pedidos variados e interação frequente podem justificar a inclusão de um LLM.

## 8. Considerações finais

O cenário mostra que organizar uma agenda envolve interpretar objetivos e respeitar limites que não podem ser resolvidos apenas pela qualidade da explicação. Com tarefas indivisíveis, a agenda proposta conclui A, C e D, mantendo B pendente com justificativa. Se a divisão de B for autorizada, torna-se possível avançar 90 minutos nessa atividade, sem considerá-la concluída.

Agentes clássicos tornam explícita a estrutura do planejamento, enquanto LLMs podem facilitar a interpretação e a interação com o professor. A escolha da arquitetura deve acompanhar os requisitos do problema. Quando há exigência de validade verificável, propostas e explicações precisam estar vinculadas a restrições, dados e verificações efetivas.

## 9. Referências

RUSSELL, Stuart; NORVIG, Peter. Artificial Intelligence: A Modern Approach. 4. ed. Pearson, 2021. Capítulo 2: Intelligent Agents. Página oficial: <https://aima.cs.berkeley.edu/>.

YAO, Shunyu et al. ReAct: Synergizing Reasoning and Acting in Language Models. In: International Conference on Learning Representations (ICLR), 2023. Disponível em: <https://arxiv.org/abs/2210.03629>.
