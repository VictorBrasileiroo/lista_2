# Questão 15: ontologia OWL 2 com inferência automática

Lista 2 de Inteligência Artificial, 2026.2. Professor Evandro Costa.

## 1. Introdução

Uma ontologia descreve conceitos de um domínio, suas relações e as condições que restringem sua interpretação. OWL 2 permite expressar esse conhecimento com semântica formal, tornando possível verificar sua consistência e obter consequências lógicas. Neste trabalho, a linguagem representa participações em projetos universitários e permite reconhecer estudantes pesquisadores a partir dos fatos registrados. A fundamentação segue o [OWL 2 Primer do W3C](https://www.w3.org/TR/owl2-primer/).

## 2. Aplicação escolhida

O cenário contém três estudantes, um professor, três projetos e três áreas de conhecimento. Todos os nomes e projetos são fictícios, sem associação com pessoas reais.

Ana participa de um projeto de pesquisa em inteligência artificial. Bruno participa de um projeto de pesquisa em redes universitárias, associado à computação. Clara participa de um projeto de extensão sobre inclusão digital. Alex orienta os três projetos. O objetivo é obter as classificações de pesquisadores a partir dessas participações, sem preenchê-las manualmente.

## 3. Representação do conhecimento

A ontologia possui 13 classes, quatro propriedades de objeto, duas propriedades de dados e dez indivíduos. Sua IRI é `https://example.org/ia/2026.2/projetos.owl#`. Essa IRI identifica o vocabulário; a execução carrega o arquivo local e não depende de acessar esse endereço.

```text
Thing
├── Pessoa
│   ├── Estudante
│   │   └── EstudantePesquisador
│   │       └── EstudantePesquisadorIA
│   └── Professor
├── Projeto
│   ├── ProjetoPesquisa
│   ├── ProjetoExtensao
│   ├── ProjetoAtivo
│   └── ProjetoEncerrado
└── AreaConhecimento
    └── AreaComputacao
        └── AreaIA
```

As propriedades de objeto registram relações entre indivíduos:

| Propriedade | Domínio | Alcance | Característica |
|---|---|---|---|
| `participaDe` | `Estudante` | `Projeto` | Participação acadêmica |
| `temArea` | `Projeto` | `AreaConhecimento` | Área do projeto |
| `orientadoPor` | `Projeto` | `Professor` | Orientação do projeto |
| `subAreaDe` | `AreaConhecimento` | `AreaConhecimento` | Transitiva |

`nome` associa pessoas ou áreas a textos, e `titulo` associa projetos a textos. O domínio de `nome` é uma união, `Pessoa or AreaConhecimento`, para permitir seu uso nas duas categorias.

Os fatos principais são:

| Indivíduo | Classe declarada | Relações declaradas |
|---|---|---|
| `estudante_ana` | `Estudante` | `participaDe projeto_ia` |
| `estudante_bruno` | `Estudante` | `participaDe projeto_redes` |
| `estudante_clara` | `Estudante` | `participaDe projeto_extensao` |
| `professor_alex` | `Professor` | Referenciado como orientador dos três projetos |
| `projeto_ia` | `ProjetoPesquisa`, `ProjetoAtivo` | `temArea ia`, `orientadoPor professor_alex` |
| `projeto_redes` | `ProjetoPesquisa`, `ProjetoAtivo` | `temArea computacao`, `orientadoPor professor_alex` |
| `projeto_extensao` | `ProjetoExtensao`, `ProjetoAtivo` | `temArea computacao`, `orientadoPor professor_alex` |
| `computacao` | `AreaComputacao` | Sem superárea declarada |
| `ia` | `AreaIA` | `subAreaDe computacao` |
| `pln` | `AreaIA` | `subAreaDe ia` |

As classes de pesquisadores são definidas por equivalência. Em notação Manchester simplificada:

```text
EstudantePesquisador EquivalentTo:
    Estudante and (participaDe some ProjetoPesquisa)

EstudantePesquisadorIA EquivalentTo:
    Estudante and
    (participaDe some (ProjetoPesquisa and (temArea some AreaIA)))

DisjointClasses: ProjetoAtivo, ProjetoEncerrado
Transitive: subAreaDe
```

A primeira definição fornece condições necessárias e suficientes para reconhecer um estudante pesquisador. A segunda exige participação em um mesmo projeto que seja de pesquisa e tenha alguma área pertencente a `AreaIA`. Isso evita combinar indevidamente a participação em um projeto de pesquisa com a área de outro projeto.

`ProjetoPesquisa` e `ProjetoExtensao` não são disjuntas: a modelagem permite que um projeto combine essas atividades. Já `ProjetoAtivo` e `ProjetoEncerrado` são mutuamente exclusivas no instante de referência deste exemplo.

A hierarquia entre classes e a relação entre áreas têm funções diferentes. `AreaIA` é subclasse de `AreaComputacao`; `ia` e `pln` são indivíduos de `AreaIA`. A relação transitiva liga esses indivíduos, sem transformar `pln` em uma classe.

## 4. Ferramentas

O Python constrói a ontologia, organiza os comandos e consulta os resultados. O Owlready2 fornece a representação OWL, a persistência em RDF/XML e a integração com HermiT. O HermiT é o mecanismo que executa o raciocínio, em um processo Java. A chamada utilizada é:

```python
owl.sync_reasoner([onto], infer_property_values=True, debug=1)
```

O parâmetro `infer_property_values=True` solicita também a obtenção de valores inferidos de propriedades de objeto. O modo de depuração imprime o comando Java executado. As inferências ficam no grafo de inferências em memória, separado da ontologia declarada, conforme o funcionamento descrito na [documentação de raciocínio do Owlready2](https://owlready2.readthedocs.io/en/latest/reasoning.html).

Cada execução carrega um `World()` independente. Os modos de demonstração e de inconsistência não salvam a ontologia. O arquivo `ontologia.owl` contém somente o modelo e os fatos declarados e pode ser aberto em ferramentas compatíveis com RDF/XML e OWL 2, como o Protégé. Não foi realizada uma inspeção pela interface do Protégé.

## 5. Demonstração das inferências

Os resultados abaixo foram verificados com execução real do HermiT em 16/11/2026. O programa consulta as mesmas condições antes e depois do raciocínio e encerra com erro se uma conclusão esperada não aparecer.

| Informação | Antes do HermiT | Depois do HermiT |
|---|---|---|
| Ana é `EstudantePesquisador` | Não declarada | Inferida |
| Ana é `EstudantePesquisadorIA` | Não declarada | Inferida |
| Bruno é `EstudantePesquisador` | Não declarada | Inferida |
| PLN `subAreaDe` Computacao | Não declarada | Inferida |

Ana e Bruno são declarados estudantes e participam, respectivamente, de `projeto_ia` e `projeto_redes`. Ambos os projetos pertencem a `ProjetoPesquisa`. Esses fatos satisfazem a definição de `EstudantePesquisador`.

Além disso, `projeto_ia temArea ia` e `ia` pertence a `AreaIA`. Ana satisfaz, portanto, a definição mais específica de `EstudantePesquisadorIA`. O Owlready2 registrou esse tipo mais específico para Ana. A consulta de pertinência considera também a hierarquia `rdfs:subClassOf`, de modo que sua condição de `EstudantePesquisador` é reconhecida. Essa consulta não avalia as restrições existenciais para classificar indivíduos.

A transitividade de `subAreaDe`, combinada com `pln subAreaDe ia` e `ia subAreaDe computacao`, permite concluir `pln subAreaDe computacao`. Sua verificação consulta a tripla diretamente, sem usar caminhos transitivos em SPARQL nem calcular o fecho em Python. A tripla estava ausente antes do HermiT e apareceu após sua execução.

O registro de execução incluiu:

```text
* Owlready2 * Running HermiT...
org.semanticweb.HermiT.cli.CommandLine -c -O -D -I file:///... -Y
* Owlready * Reparenting projetos.estudante_bruno:
  {projetos.Estudante} => {projetos.EstudantePesquisador}
* Owlready * Reparenting projetos.estudante_ana:
  {projetos.Estudante} => {projetos.EstudantePesquisadorIA}
* Owlready * Adding relation projetos.pln subAreaDe projetos.computacao
```

O caminho temporário foi abreviado no trecho acima. O comando completo aparece no terminal durante a reprodução. Bruno não recebeu a classificação de pesquisador de IA, e Clara não recebeu a classificação de pesquisadora. Esses resultados indicam ausência das respectivas inferências nesta base, sem provar suas negações.

## 6. Teste de consistência

O teste negativo recarrega o arquivo original em outro `World()` e primeiro confirma sua consistência com HermiT. Em seguida, acrescenta somente em memória a classificação `ProjetoEncerrado` a `projeto_ia`, que já pertence a `ProjetoAtivo`.

Como essas classes são disjuntas, um indivíduo não pode pertencer às duas simultaneamente. A nova execução do HermiT lançou `OwlReadyInconsistentOntologyError`. O programa capturou especificamente essa exceção e tratou a inconsistência como o resultado esperado. Se o reasoner aceitasse a base alterada, o comando terminaria com erro.

Os comandos de demonstração e de teste negativo terminaram com código de saída zero. Após cada execução, o SHA-256 de `ontologia.owl` permaneceu igual e o arquivo foi recarregado, com nova verificação dos fatos declarados. O teste negativo não contaminou a ontologia principal.

## 7. Discussão

O conhecimento explícito consiste nas declarações do arquivo, como a participação de Ana em `projeto_ia`. O conhecimento inferido corresponde às consequências verificadas pelo HermiT, como sua classificação de pesquisadora de IA.

As equivalências, restrições existenciais, disjunções e transitividade são axiomas OWL 2. Embora suas consequências possam ser explicadas como implicações, não foram implementadas como regras procedurais em Python ou regras SWRL. O código Python prepara os dados e verifica a saída do reasoner.

A verificação de consistência determina se os fatos e axiomas admitem uma interpretação conjunta. O teste negativo demonstra uma contradição decorrente dos estados disjuntos. A validade lógica das conclusões depende do conhecimento representado, sem garantir que os fatos descrevam corretamente uma realidade externa.

Sob a hipótese de mundo aberto, informação ausente pode ser desconhecida. Assim, a falta de classificação de Bruno como pesquisador de IA não implica que ele pertença ao complemento dessa classe. Essa distinção segue a semântica apresentada no [OWL 2 Primer](https://www.w3.org/TR/owl2-primer/).

O exemplo realiza dedução lógica a partir de axiomas e fatos. Não envolve treinamento de modelos de linguagem, aprendizagem estatística ou estimativas de probabilidade.

## 8. Limitações

A base é pequena e simplifica a organização universitária. Não representa bolsas, carga horária, vínculos institucionais ou histórico de participações. Os estados dos projetos pressupõem um mesmo instante e não incluem informações temporais completas. Em uma aplicação real, seria necessário representar mudanças de estado ao longo do tempo.

A ausência de disjunção entre pesquisa e extensão permite projetos híbridos, mas também impede usar o tipo de extensão como prova de que Clara não participa de pesquisa. As conclusões dependem da qualidade dos fatos e axiomas, da biblioteca instalada e da execução bem-sucedida do Java e do HermiT.

## 9. Reprodução

No PowerShell, partindo da raiz do repositório:

```powershell
cd questao_15
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
java -version
.\.venv\Scripts\python.exe ontologia.py --construir
.\.venv\Scripts\python.exe ontologia.py --demo
.\.venv\Scripts\python.exe ontologia.py --teste-inconsistencia
```

Se o comando `python` não estiver disponível, utilize `py -3` ou o caminho de uma instalação Python 3 funcional para criar o ambiente. Não é necessário ativá-lo. Se o Java não estiver no `PATH`, indique o executável, ajustando o caminho à instalação local:

```powershell
$env:JAVA_EXE = 'C:\Program Files\Microsoft\jdk-21.0.9.10-hotspot\bin\java.exe'
```

Os caminhos de leitura e gravação são relativos ao próprio script. Por exemplo, a partir da raiz do repositório, também é possível executar:

```powershell
.\questao_15\.venv\Scripts\python.exe -O .\questao_15\ontologia.py --demo
.\questao_15\.venv\Scripts\python.exe -O .\questao_15\ontologia.py --teste-inconsistencia
```

As verificações utilizam exceções explícitas, sem `assert`, e permanecem ativas com `-O`. A aplicação não substitui falhas do HermiT por classificações programadas em Python.

Ambiente efetivamente utilizado:

| Componente | Versão verificada |
|---|---|
| Python | 3.13.12 |
| Owlready2 | 0.51, fixada em `requirements.txt` |
| Java | Microsoft OpenJDK 21.0.9 LTS, build 21.0.9+10 |
| HermiT incluído no Owlready2 | `Implementation-Version: 1.3.8.1099`, conforme manifesto do JAR |

Foram executados a criação do ambiente local, a instalação do Owlready2, `pip check`, `java -version` e os três modos da CLI. O Python encontrado inicialmente no `PATH` era um atalho WindowsApps que falhou neste ambiente; por isso, o ambiente da questão foi criado usando o Python 3.13.12 disponível em `..\.venv\Scripts\python.exe`. A primeira tentativa de instalação foi bloqueada pela restrição de rede do sandbox, e a repetição com a autorização de execução do ambiente concluiu a instalação. Não houve falha do HermiT nos testes positivos ou negativos.

A demonstração e o teste negativo também foram executados com `-O`, a partir da raiz do repositório, com sucesso. Em uma verificação adicional do tratamento de falhas, a chamada ao reasoner foi substituída por uma função vazia apenas naquele processo de teste. A demonstração retornou código 1 por ausência das inferências esperadas, mesmo com `-O`. Esse teste controlado verifica a rejeição de resultados ausentes; as conclusões da tabela foram obtidas nas execuções reais do HermiT.

## 10. Referências

1. W3C. [OWL 2 Web Ontology Language Primer, Second Edition](https://www.w3.org/TR/owl2-primer/). Recomendação de 11 de dezembro de 2012.
2. Owlready2. [Documentação oficial](https://owlready2.readthedocs.io/en/latest/).
3. Owlready2. [Reasoning](https://owlready2.readthedocs.io/en/latest/reasoning.html).

Documentação consultada em 16/11/2026. A documentação online consultada identifica a versão 0.52; a implementação foi executada e validada com a versão 0.51 indicada acima.
