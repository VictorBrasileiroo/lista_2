# Questão 14: Knowledge Graphs, representação, inferência e aprendizagem

Lista 2 de Inteligência Artificial, 2026.2. Professor Evandro Costa.

## 1. Introdução

Um Knowledge Graph (KG), ou grafo de conhecimento, representa entidades de um domínio, suas características e os relacionamentos que possuem significado nesse domínio. Em uma aplicação financeira, contas, clientes, dispositivos e transações podem ser conectados para permitir a análise conjunta de informações antes dispersas.

O diferencial está em tornar essas relações explícitas, consultáveis e reutilizáveis, com identificadores e um vocabulário coerente. Assim, armazenar objetos conectados não basta para caracterizar qualquer grafo como KG: é necessário considerar o significado do conhecimento representado. Este relatório examina essa representação, os mecanismos de inferência e aprendizagem e sua aplicação à investigação de possíveis fraudes.

## 2. Representação do conhecimento

Entidades precisam de identificadores estáveis para distinguir, por exemplo, duas contas de um mesmo cliente. Os nós representam essas entidades; as relações expressam conexões tipadas e orientadas. Considere:

```text
Conta_01 --UTILIZA--> Dispositivo_A
Conta_02 --UTILIZA--> Dispositivo_A
Conta_01 --REALIZA--> Transacao_10
```

As duas primeiras afirmações indicam o uso do mesmo dispositivo por contas diferentes. A terceira identifica a conta que realiza a transação. Os tipos `Conta`, `Dispositivo` e `Transacao` classificam entidades, enquanto `UTILIZA` e `REALIZA` distinguem os significados das conexões.

No grafo de propriedades utilizado pelo Neo4j, nós possuem rótulos e relações possuem um tipo. Ambos podem ter propriedades na forma de pares chave-valor. Uma transação pode registrar `valor` e `instante`; uma relação `UTILIZA` pode registrar quando ocorreu o acesso. Essa estrutura é descrita em [Graph database concepts, da Neo4j](https://neo4j.com/docs/getting-started/appendix/graphdb-concepts/).

RDF representa afirmações como triplas sujeito-predicado-objeto. Na tripla `Conta_01 utiliza Dispositivo_A`, a conta é o sujeito, `utiliza` é o predicado e o dispositivo é o objeto. Em RDF 1.1, IRIs identificam recursos e propriedades; objetos também podem ser literais, como valores numéricos. Existem ainda nós em branco para recursos sem uma IRI explícita. Esses elementos são definidos em [RDF 1.1 Concepts and Abstract Syntax, do W3C](https://www.w3.org/TR/rdf11-concepts/).

Vocabulários estabelecem os termos utilizados; esquemas organizam tipos e propriedades; ontologias formalizam conceitos e axiomas do domínio. RDFS descreve classes e hierarquias, enquanto OWL oferece construções mais expressivas, como propriedades transitivas. RDF é o modelo de afirmações, e RDFS/OWL permitem acrescentar semântica para raciocínio. Portanto, grafos de propriedades e RDF são modelos distintos, e armazenar dados no Neo4j não ativa automaticamente inferência RDFS ou OWL. É necessário um mecanismo de raciocínio ou regras implementadas para essa finalidade. Ver [RDF Schema 1.1](https://www.w3.org/TR/rdf-schema/) e [OWL 2 Primer](https://www.w3.org/TR/owl2-primer/).

## 3. Inferência em Knowledge Graphs

Inferir significa obter conclusões a partir de fatos conhecidos e regras ou axiomas definidos. No encadeamento de regras, uma conclusão intermediária pode tornar-se premissa de outra regra. A validade lógica depende das premissas e da semântica adotada; ela não garante que os dados correspondam à realidade.

Um exemplo de hierarquia de classes é:

```text
Pesquisador rdfs:subClassOf Pessoa.
Ana rdf:type Pesquisador.
Conclusão: Ana rdf:type Pessoa.
```

A conclusão decorre da semântica de `rdfs:subClassOf`: instâncias da subclasse também pertencem à superclasse. Com `rdfs:subPropertyOf`, uma afirmação feita por uma subpropriedade também vale para sua superpropriedade. Domínio e alcance permitem inferir tipos: se `utiliza` tem domínio `Conta` e alcance `Dispositivo`, `A utiliza X` permite concluir esses tipos para A e X. Essas declarações não funcionam simplesmente como restrições de validação de entrada. Ver [RDF Schema 1.1](https://www.w3.org/TR/rdf-schema/).

Outra possibilidade é a transitividade. Se `ancestralDe` for declarada transitiva em OWL, `A ancestralDe B` e `B ancestralDe C` implicam `A ancestralDe C`. Essa propriedade precisa ser semanticamente estabelecida: não se pode estender a transitividade a qualquer relacionamento. Ver [OWL 2 Primer](https://www.w3.org/TR/owl2-primer/).

A descoberta de relações implícitas também pode resultar de caminhos, como duas contas ligadas ao mesmo dispositivo. Uma consulta identifica esse padrão nas relações existentes; uma regra de negócio pode então determinar um encaminhamento. Isso difere tanto da inferência semântica por axiomas quanto da inferência estatística de um modelo. É preciso distinguir o fato armazenado, o fato logicamente inferido, o resultado de consulta, a sinalização de negócio e a predição aprendida. A seção 6 aplica essa distinção.

## 4. Aprendizagem em Knowledge Graphs

A estrutura do grafo fornece características para aprendizagem de máquina. Embeddings representam nós por vetores de dimensão reduzida, utilizados em tarefas posteriores. A biblioteca Neo4j Graph Data Science (GDS) inclui FastRP e Node2Vec entre seus algoritmos de embeddings. Dependendo do método, os vetores capturam aspectos da vizinhança e da semelhança estrutural entre entidades. Semelhança vetorial, entretanto, não demonstra identidade nem participação em fraude. Ver [Node embeddings, da Neo4j](https://neo4j.com/docs/graph-data-science/current/machine-learning/node-embeddings/).

A classificação de nós atribui categorias a entidades a partir de características e exemplos rotulados. A predição de relacionamentos estima ligações possivelmente ausentes entre pares de nós. Já a identificação de comunidades agrupa entidades conectadas e pode fornecer características para modelos, sem depender necessariamente de rótulos. O exemplo publicado com IEEE-CIS utiliza comunidades, centralidades e embeddings para enriquecer um classificador, conforme [A Graph-Based Approach to Financial Fraud Detection](https://neo4j.com/developer/industry-use-cases/finserv/retail-banking/ieee-cis-fraud-graphs/). A documentação [Getting started do GDS](https://neo4j.com/docs/graph-data-science/current/getting-started/) apresenta o uso de algoritmos e pipelines de aprendizagem, incluindo classificação de nós.

Um fluxo conceitual seria:

```text
Grafo com relações conhecidas
    -> Extração de características ou embeddings
    -> Conjuntos de treino e avaliação
    -> Modelo de aprendizagem
    -> Predição de relações ou risco
    -> Validação das predições
```

Essa sequência exige cuidado: as características devem ser calculadas somente com informações permitidas em cada etapa. A documentação [Link prediction pipelines](https://neo4j.com/docs/graph-data-science/current/machine-learning/linkprediction-pipelines/link-prediction/) separa relações usadas para características, treinamento e teste. Em fraude, uma divisão temporal também ajuda a evitar que dados futuros contaminem previsões sobre o passado. Modelos supervisionados exigem rótulos confiáveis; casos não investigados não devem ser automaticamente rotulados como legítimos.

A mesma documentação utiliza pares não adjacentes para amostrar exemplos negativos. Isso é uma convenção de treinamento, pois ausência de ligação não prova falsidade: o grafo pode estar incompleto. Devem-se avaliar falsos positivos, que encaminham casos legítimos, e falsos negativos, que deixam fraudes passar. Uma relação prevista estatisticamente permanece uma hipótese, sem a garantia dedutiva de uma conclusão obtida de axiomas. A aprendizagem é discutida conceitualmente; a demonstração da seção 6 se concentra em inferência por uma regra explícita.

## 5. Aplicação: identificação de possíveis fraudes financeiras

O material [A Graph-Based Approach to Financial Fraud Detection, da Neo4j](https://neo4j.com/developer/industry-use-cases/finserv/retail-banking/ieee-cis-fraud-graphs/) demonstra a construção de um grafo com o conjunto IEEE-CIS, conectando transações, cartões, dispositivos e outras entidades. O objetivo é explorar conexões e gerar características para aprendizagem. O guia [Account Takeover Fraud](https://neo4j.com/developer/industry-use-cases/finserv/retail-banking/account-takeover-fraud/) apresenta dados demonstrativos e consultas para investigar padrões como um dispositivo usado para acessar contas de diferentes clientes e sequências de alterações cadastrais.

São exemplos publicados de aplicação e demonstração técnica. Esses materiais não são tratados aqui como comprovação de implantação em produção por uma instituição identificada, nem como evidência de eficácia universal. A demonstração abaixo é fictícia, com modelo simplificado próprio.

Nesse modelo, `Conta` representa a conta financeira, `Dispositivo` o meio de acesso e `Transacao` uma movimentação. `UTILIZA` liga conta a dispositivo; `REALIZA` liga conta à transação de origem; `DESTINA_A` liga transação à conta destinatária. Um nó `Cliente` pode representar o titular e ligar-se à conta por `TITULAR_DE`.

Analisar apenas valor e horário de uma transação pode deixar de revelar seu vínculo com outra conta por um dispositivo compartilhado. O grafo permite investigar esse contexto e os caminhos até registros de fraude confirmada. As conexões orientam a investigação, mas seu significado depende da qualidade dos registros e da regra utilizada.

## 6. Demonstração de inferência

### Passo 1: conhecimento explícito

Considere somente os seguintes fatos do exemplo:

```text
F1: Conta_A UTILIZA Dispositivo_X.
F2: Conta_B UTILIZA Dispositivo_X.
F3: Conta_A possui uma fraude previamente confirmada.
F4: Não há fraude confirmada registrada para Conta_B nos dados disponíveis.
```

F1 e F2 são relações armazenadas entre dois nós `Conta` e um nó `Dispositivo`. F3 é representado pela propriedade `status = 'fraude_confirmada'` da Conta_A. Esse status é uma premissa assumida, não uma descoberta desta demonstração. F4 descreve a ausência de confirmação para Conta_B e não comprova que ela seja legítima ou fraudulenta. Os identificadores `id` são `Conta_A`, `Conta_B` e `Dispositivo_X`.

### Passo 2: relação derivada

F1 e F2 satisfazem o caminho:

```text
Conta_A --UTILIZA--> Dispositivo_X <--UTILIZA-- Conta_B
```

Portanto, Conta_A e Conta_B compartilham o Dispositivo_X. O compartilhamento é uma relação derivada do padrão, sem exigir uma aresta direta entre as contas. Formalmente, para contas distintas x e y, define-se `Compartilha(x,y)` quando existe um dispositivo d tal que `Utiliza(x,d)` e `Utiliza(y,d)`.

### Passo 3: regra de negócio

Adota-se a seguinte regra ilustrativa R1:

```text
SE uma conta compartilha dispositivo com outra conta
E essa outra conta possui fraude confirmada
ENTÃO a primeira conta deve ser sinalizada para análise.
```

Como `Compartilha(Conta_B,Conta_A)` e F3 são satisfeitos, R1 produz:

```text
Conta_B -> REQUER_ANALISE
Motivo -> Compartilha Dispositivo_X com Conta_A.
```

A conclusão é um encaminhamento para investigação adicional, não uma prova de fraude. Familiares ou usuários de um equipamento coletivo podem compartilhar dispositivos legitimamente. A sinalização decorre de R1, uma regra da aplicação, e não de uma consequência automática de RDF/OWL ou de uma probabilidade calculada por aprendizagem de máquina.

### Passo 4: consulta ilustrativa em Cypher

A consulta abaixo expressa o padrão e a condição da conta de referência:

```cypher
MATCH (suspeita:Conta)-[:UTILIZA]->(d:Dispositivo)
      <-[:UTILIZA]-(referencia:Conta)
WHERE suspeita <> referencia
  AND referencia.status = 'fraude_confirmada'
RETURN DISTINCT suspeita.id AS conta_para_analise,
                d.id AS dispositivo_compartilhado,
                referencia.id AS conta_de_referencia
```

`MATCH` procura relações existentes, `WHERE` exige contas distintas e confirmação na referência, e `RETURN DISTINCT` apresenta combinações distintas. Esse uso de padrões corresponde à documentação [MATCH, do manual Cypher](https://neo4j.com/docs/cypher-manual/current/clauses/match/).

Nesta consulta ilustrativa, a análise dos fatos estipulados leva à linha esperada `Conta_B | Dispositivo_X | Conta_A`. O padrão seleciona candidatos à aplicação de R1; a consulta apenas lê os dados, sem criar arestas ou executar um reasoner OWL. Persistir `REQUER_ANALISE` exigiria uma operação adicional, segundo a política da aplicação.

### Passo 5: explicabilidade

A justificativa pode preservar toda a sequência:

```text
Origem: fatos fictícios F1, F2 e F3 definidos neste exemplo.
Conta_B usa Dispositivo_X (F2).
Conta_A também usa Dispositivo_X (F1).
Conta_A tem fraude confirmada (F3).
Regra R1: compartilhar dispositivo com uma conta com fraude
confirmada implica encaminhamento para análise.
Conclusão: Conta_B requer investigação adicional.
```

Em uma aplicação real, a justificativa também deveria identificar os registros de acesso, a confirmação anterior e a versão da regra. Isso permite revisar tanto a origem dos fatos quanto a política que produziu o alerta.

## 7. Diferença entre inferência e aprendizagem no exemplo

| Mecanismo | Operação | Resultado e interpretação |
| --- | --- | --- |
| Regras explícitas | Aplicar R1 aos fatos e ao compartilhamento derivado. | Encaminhar Conta_B para análise conforme a política definida. |
| Consulta a padrões | Encontrar duas contas ligadas ao mesmo dispositivo. | Retornar contas e caminhos existentes que satisfazem condições. |
| Inferência semântica por axiomas | Aplicar, por exemplo, a hierarquia Pesquisador/Pessoa. | Concluir um tipo logicamente implicado pelos axiomas e fatos. |
| Aprendizagem sobre grafos | Aprender padrões usando características ou embeddings. | Estimar uma categoria, ligação ou risco, sujeito a erro estatístico. |

Uma versão mais avançada poderia combinar embeddings de contas com características como quantidade de dispositivos e conexões com casos confirmados, alimentando um classificador. O modelo estimaria risco a partir de exemplos históricos; não converteria essa estimativa em fraude comprovada. Regras e modelos podem apoiar uma mesma decisão, mas ambos precisam ser avaliados quanto aos erros, à qualidade dos dados e à utilidade para a investigação. Não se atribuem aqui probabilidades ou resultados de classificação.

## 8. Vantagens e limitações

O KG permite reunir fontes de informação sob identificadores e conceitos comuns, revelar relacionamentos indiretos e investigar caminhos. Na aplicação proposta, a sequência entre duas contas e um dispositivo oferece uma justificativa compreensível. Comunidades e outros padrões estruturais ampliam as possibilidades de análise além de atributos isolados.

Essas vantagens dependem de dados confiáveis: identificar incorretamente um dispositivo pode associar pessoas sem vínculo real, enquanto relações ausentes podem ocultar conexões relevantes. Grafos grandes exigem recursos para armazenamento, atualização e processamento; não se presume superioridade de desempenho em relação a bancos relacionais. Falsos positivos demandam revisão, sobretudo quando o compartilhamento tem explicação legítima.

Como cuidados de projeto, dados pessoais e registros de acesso devem ser limitados ao necessário, protegidos por controles de acesso e tratados com critérios de retenção. A explicabilidade do caminho ajuda a revisão, mas não elimina os riscos de qualidade, privacidade ou interpretação indevida.

## 9. Considerações finais

Knowledge Graphs organizam entidades e relações com significado explícito, apoiando integração, consultas e análise. A inferência pode acrescentar conclusões por regras e axiomas, enquanto a aprendizagem utiliza a estrutura para reconhecer padrões estatísticos e prever relações ou categorias.

Na aplicação financeira, o exemplo demonstra como fatos de uso de dispositivos, combinados com uma confirmação anterior e uma regra explícita, levam ao encaminhamento da Conta_B. A combinação de representação, inferência e aprendizagem pode orientar a investigação, desde que se preserve a diferença entre informação confirmada, alerta de análise e hipótese estatística.

## 10. Referências

- W3C. [RDF 1.1 Concepts and Abstract Syntax](https://www.w3.org/TR/rdf11-concepts/).
- W3C. [RDF Schema 1.1](https://www.w3.org/TR/rdf-schema/).
- W3C. [OWL 2 Web Ontology Language Primer (Second Edition)](https://www.w3.org/TR/owl2-primer/).
- Neo4j. [Graph database concepts](https://neo4j.com/docs/getting-started/appendix/graphdb-concepts/). Getting Started.
- Neo4j. [A Graph-Based Approach to Financial Fraud Detection](https://neo4j.com/developer/industry-use-cases/finserv/retail-banking/ieee-cis-fraud-graphs/). Industry Use Cases.
- Neo4j. [Account Takeover Fraud](https://neo4j.com/developer/industry-use-cases/finserv/retail-banking/account-takeover-fraud/). Industry Use Cases.
- Neo4j. [Node embeddings](https://neo4j.com/docs/graph-data-science/current/machine-learning/node-embeddings/). Graph Data Science.
- Neo4j. [Link prediction pipelines](https://neo4j.com/docs/graph-data-science/current/machine-learning/linkprediction-pipelines/link-prediction/). Graph Data Science.
- Neo4j. [Getting started](https://neo4j.com/docs/graph-data-science/current/getting-started/). Graph Data Science.
- Neo4j. [MATCH](https://neo4j.com/docs/cypher-manual/current/clauses/match/). Cypher Manual.
