# Questão 9: Recomendação educacional de livros com OWL 2

## 1. Aplicação e objetivo

O sistema recomenda livros a partir de três preferências: tema, nível e formato. A seleção usa uma ontologia OWL 2, classificação automática pelo HermiT e consultas SPARQL executadas pelo mecanismo nativo do Owlready2. O objetivo é mostrar como fatos bibliográficos e axiomas produzem conhecimento que passa a participar da recomendação.

A base inteira é fictícia, incluindo títulos, autores, editoras e perfis de leitores. Os valores `FICT-001` a `FICT-008`, armazenados em `isbn`, são identificadores ilustrativos, não ISBN válidos nem referências a publicações reais. A aplicação é executada no terminal. A apresentação HTML é apenas material de exposição, sem interface de recomendação.

## 2. Modelagem conceitual

A ontologia distribuída em [ontologia.owl](ontologia.owl) é serializada em RDF/XML e possui a IRI estável `https://example.org/ia/2026.2/livros.owl#`. O endereço identifica o vocabulário; não precisa estar publicado nem ser acessado pela aplicação. O carregamento lê um arquivo local em um novo `World`, sem depender das classes Python usadas na construção.

As quantidades verificadas após carregar o arquivo foram:

| Elemento nomeado do domínio | Quantidade |
| --- | ---: |
| Classes | 24 |
| Propriedades de objeto | 11 |
| Propriedades de dados | 7 |
| Total de propriedades | 18 |
| Indivíduos | 26 |
| Livros, incluídos nos indivíduos | 8 |

As contagens excluem construções anônimas, como interseções e restrições existenciais, e o vocabulário padrão OWL.

### Classes e hierarquia

```text
Thing
├── Publicacao
│   └── Livro
│       ├── LivroTecnico
│       │   └── LivroIA
│       │       └── LivroIntrodutorioIA
│       ├── LivroFiccao
│       ├── LivroIntrodutorio
│       │   └── LivroIntrodutorioIA (herança múltipla)
│       ├── LivroAvancado
│       ├── LivroDigital
│       └── LivroFisico
├── Autor
├── Leitor
├── Tema
│   ├── TemaComputacao
│   │   ├── TemaIA
│   │   └── TemaProgramacao
│   └── TemaLiteratura
├── Nivel
│   ├── NivelBasico
│   └── NivelAvancado
├── Formato
│   ├── FormatoDigital
│   └── FormatoFisico
└── Editora
```

`LivroFisico` foi incluída para que ambos os formatos possam ser consultados por classes inferidas. Cada classe tem função na classificação, na tipagem das propriedades ou na consistência.

Classes de tema e indivíduos de tema cumprem papéis diferentes. `TemaIA` é uma classe; `inteligencia_artificial`, `aprendizado_maquina` e `pln` são indivíduos dessa classe. A inclusão de `TemaIA` em `TemaComputacao` representa uma hierarquia de categorias. Já `subTemaDe` organiza os assuntos concretos usados nos livros.

### Propriedades

| Propriedade de objeto | Domínio | Alcance | Uso |
| --- | --- | --- | --- |
| temAutor | Livro | Autor | Autoria |
| autorDe | Autor | Livro | Inversa de temAutor |
| abordaTema | Livro | Tema | Assunto abordado |
| temNivel | Livro | Nivel | Dificuldade |
| temFormato | Livro | Formato | Forma de acesso |
| publicadoPor | Publicacao | Editora | Editora responsável |
| prefereTema | Leitor | Tema | Interesse do perfil |
| prefereNivel | Leitor | Nivel | Dificuldade preferida |
| prefereFormato | Leitor | Formato | Formato preferido |
| subTemaDe | Tema | Tema | Hierarquia transitiva de assuntos |
| relacionadoA | Tema | Tema | Associação simétrica entre IA e programação |

| Propriedade de dados | Domínio | Alcance | Uso |
| --- | --- | --- | --- |
| titulo | Publicacao | string | Apresentação e ordenação |
| nome | União de Autor, Leitor, Tema, Nivel, Formato e Editora | string | Nomes legíveis |
| anoPublicacao | Publicacao | integer | Ano ilustrativo |
| idioma | Publicacao | string | Idioma da obra |
| numeroPaginas | Livro | integer | Extensão |
| isbn | Livro | string | Código bibliográfico fictício |
| descricao | Publicacao | string | Descrição do assunto |

As 18 propriedades têm relações efetivas na base, verificadas pela demonstração. Nem todos os dados bibliográficos são filtros de recomendação. Ano, idioma, páginas, editora e descrição registram informações relevantes para uma possível ampliação do catálogo. As preferências dos dois leitores ilustram a representação de perfis; a CLI recebe as preferências diretamente, sem exigir a seleção de um perfil.

O domínio de `nome` é uma união. Declarar seis classes separadamente na lista de domínios significaria interseção, fazendo cada entidade com nome pertencer simultaneamente a categorias disjuntas. Domínios e alcances em OWL produzem consequências lógicas e não são validações de formulário.

## 3. Axiomas e restrições

As definições equivalentes abaixo fornecem condições necessárias e suficientes. A notação `∃ propriedade.Classe` indica a existência de pelo menos um valor da propriedade pertencente à classe.

```text
LivroTecnico ≡ Livro ⊓ ∃ abordaTema.TemaComputacao
LivroFiccao ≡ Livro ⊓ ∃ abordaTema.TemaLiteratura
LivroIntrodutorio ≡ Livro ⊓ ∃ temNivel.NivelBasico
LivroAvancado ≡ Livro ⊓ ∃ temNivel.NivelAvancado
LivroDigital ≡ Livro ⊓ ∃ temFormato.FormatoDigital
LivroFisico ≡ Livro ⊓ ∃ temFormato.FormatoFisico
LivroIA ≡ Livro ⊓ ∃ abordaTema.TemaIA
LivroIntrodutorioIA ≡ LivroIA ⊓ LivroIntrodutorio
```

No Owlready2, uma definição usa, por exemplo, `Livro & temNivel.some(NivelBasico)` em `equivalent_to`. Uma simples declaração de subclasse com uma restrição não seria suficiente para classificar todo livro que apresenta aquela propriedade.

Além das equivalências, todo `Livro` possui restrições existenciais para autor, tema, nível, formato e editora. Essas restrições expressam compromissos conceituais; não obrigam que todos os valores sejam explicitamente nomeados no arquivo, devido à hipótese de mundo aberto.

Foram declaradas disjunções entre as categorias principais `Publicacao`, `Autor`, `Leitor`, `Tema`, `Nivel`, `Formato` e `Editora`; entre `TemaComputacao` e `TemaLiteratura`; entre os dois níveis; entre os dois formatos; e entre `LivroTecnico` e `LivroFiccao`.

A última disjunção segue uma convenção deste catálogo: obras técnicas e de ficção são categorias exclusivas. Isso limita a representação de obras híbridas. Não há disjunção entre `LivroDigital` e `LivroFisico`, pois um livro poderia existir nos dois formatos. Também não há disjunção entre livros introdutórios e avançados: a base atual atribui um nível por livro, mas o modelo não proíbe obras que atendam aos dois níveis.

Não foram usadas propriedades funcionais, chaves nem cardinalidades máximas. Assim, adicionar um segundo autor, tema ou formato não força identificações entre indivíduos.

## 4. Base de indivíduos

Os 26 indivíduos são oito livros, quatro autores, duas editoras, seis temas, dois níveis, dois formatos e dois leitores. Os leitores são `leitora_ana`, interessada em IA básica digital, e `leitor_caio`, interessado em programação avançada física.

| ID | Título fictício | Autor | Tema | Nível | Formato |
| --- | --- | --- | --- | --- | --- |
| livro_1 | Primeiros passos em inteligência artificial | Ana Prado | IA | Básico | Digital |
| livro_2 | Linguagem natural para iniciantes | Bruno Reis | PLN | Básico | Digital |
| livro_3 | Aprendizado de máquina em profundidade | Clara Luz | Aprendizado de máquina | Avançado | Digital |
| livro_4 | Inteligência artificial no papel | Davi Melo | IA | Básico | Físico |
| livro_5 | Programação desde o começo | Ana Prado | Programação | Básico | Digital |
| livro_6 | Algoritmos e programação avançada | Bruno Reis | Programação | Avançado | Físico |
| livro_7 | Contos da biblioteca azul | Clara Luz | Literatura | Básico | Físico |
| livro_8 | Narrativas e labirintos | Davi Melo | Literatura | Avançado | Digital |

Todos os livros são inicialmente declarados apenas como `Livro`. Os tipos especializados não são gravados antecipadamente no arquivo de origem.

## 5. Execução do HermiT e inferências obtidas

A validação foi executada em Windows, com Python 3.13.12, Owlready2 0.51 e Microsoft OpenJDK 21.0.9. A documentação oficial consultada estava na versão 0.52; as APIs foram conferidas pela execução efetiva na versão fixada 0.51. Em 16/11/2026, a demonstração foi reexecutada com Python 3.14.7 e Microsoft OpenJDK 21.0.13, com os mesmos resultados.

O programa configura o executável Java a partir de `JAVA_EXE` ou do `PATH` e chama:

```python
ow.sync_reasoner([onto], infer_property_values=True, debug=1)
```

`sync_reasoner` executa o HermiT incluído no Owlready2. O terminal mostra o processo Java, a classe `org.semanticweb.HermiT.cli.CommandLine` e a opção `-Y` para valores de propriedades. Não há substituição por regras Python. As inferências ficam em um grafo separado, `http://inferrences/`, consultável no mesmo `World`, sem salvar novamente o arquivo principal.

### Classificação automática

Os tipos RDF novos apresentados pela demonstração foram:

| Indivíduo | Tipo de domínio antes | Novos tipos RDF após HermiT |
| --- | --- | --- |
| livro_1 | Livro | LivroDigital, LivroIntrodutorioIA |
| livro_2 | Livro | LivroDigital, LivroIntrodutorioIA |
| livro_3 | Livro | LivroAvancado, LivroDigital, LivroIA |
| livro_4 | Livro | LivroFisico, LivroIntrodutorioIA |
| livro_5 | Livro | LivroDigital, LivroIntrodutorio, LivroTecnico |
| livro_6 | Livro | LivroAvancado, LivroFisico, LivroTecnico |
| livro_7 | Livro | LivroFiccao, LivroFisico, LivroIntrodutorio |
| livro_8 | Livro | LivroAvancado, LivroDigital, LivroFiccao |

O reasoner pode materializar os tipos mais específicos, sem repetir todas as superclasses como triplas de tipo. Por isso as consultas de pertinência usam `a/rdfs:subClassOf*`. Pertencer a `LivroIntrodutorioIA` também implica pertencer a `LivroIA`, `LivroIntrodutorio`, `LivroTecnico`, `Livro` e `Publicacao` pela hierarquia.

Para `livro_1`, o tema é um indivíduo de `TemaIA`, o nível é de `NivelBasico` e o formato é de `FormatoDigital`. As equivalências permitem concluir `LivroIA`, `LivroIntrodutorio` e `LivroDigital`. A interseção das duas primeiras produz `LivroIntrodutorioIA`. O mesmo ocorre com `livro_2`, cujo tema PLN foi explicitamente categorizado em `TemaIA`.

### Relacionamento implícito

Os seguintes fatos foram declarados:

```text
pln subTemaDe aprendizado_maquina
aprendizado_maquina subTemaDe inteligencia_artificial
inteligencia_artificial subTemaDe computacao
```

Antes do HermiT, a consulta da tripla direta `pln subTemaDe inteligencia_artificial` não encontrou resultado. Depois da execução, a mesma consulta encontrou a relação. O HermiT também acrescentou `pln subTemaDe computacao` e `aprendizado_maquina subTemaDe computacao`.

Essa comparação usa a propriedade direta, sem caminho transitivo SPARQL, para comprovar que a relação foi materializada pelo reasoner. Nas buscas de temas, o caminho `subTemaDe*` permite incluir tanto o próprio assunto quanto seus descendentes. Esse caminho SPARQL já pode percorrer os fatos declarados antes do HermiT; portanto, sua presença isolada não comprova uma inferência pelo reasoner.

As propriedades inversas `temAutor`/`autorDe` são úteis para navegação, mas o Owlready2 pode disponibilizar a inversa automaticamente. Elas não são usadas como evidência exclusiva de raciocínio pelo HermiT. Da mesma forma, a classificação de PLN como assunto de IA é declarada, e não é apresentada como consequência da transitividade.

## 6. Consistência e mundo aberto

O HermiT terminou normalmente na ontologia principal, confirmando sua consistência. A lista de classes insatisfatíveis também ficou vazia. Consistência da ontologia e satisfatibilidade de todas as classes são verificações diferentes: uma classe impossível, mas sem instâncias, não implica necessariamente uma ontologia inconsistente.

O teste negativo carrega o mesmo OWL em outro `World` e acrescenta, somente em memória, os tipos `LivroTecnico` e `LivroFiccao` ao `livro_1`. Como essas classes são disjuntas, a existência desse indivíduo contradiz o axioma. O HermiT lançou `OwlReadyInconsistentOntologyError`, e somente a captura dessa exceção aprova o teste. Não receber a exceção faz a demonstração falhar.

O SHA-256 do OWL foi comparado antes e depois da demonstração e permaneceu:

```text
2895f8ad9bba3bf245dac9e1e23b6e0cd244b6908b1a2ed8d59e3654ba7f009f
```

A hipótese de mundo aberto significa que a falta de uma informação não equivale à sua negação. Um livro sem formato conhecido não pode ser considerado automaticamente físico ou não digital. Também não receber recomendação significa apenas que a base não demonstrou a compatibilidade pedida. Não é uma prova de que o livro seja inadequado no mundo real.

## 7. Consultas semânticas

Todas as consultas são executadas por `world.sparql`, sem RDFlib ou serviço externo. `SELECT DISTINCT` evita duplicatas decorrentes de múltiplas classificações e caminhos de superclasses. Os exemplos abaixo usam o prefixo:

```sparql
PREFIX q: <https://example.org/ia/2026.2/livros.owl#>
```

### Livros e autores

```sparql
SELECT DISTINCT ?titulo ?nome {
  ?l a/rdfs:subClassOf* q:Livro ; q:titulo ?titulo ; q:temAutor ?a .
  ?a q:nome ?nome .
} ORDER BY ?titulo
```

Resultado: oito pares de títulos e autores, correspondentes à tabela da base.

### Livros de um tema

```sparql
SELECT DISTINCT ?titulo {
  ?l q:titulo ?titulo ; q:abordaTema ?tema .
  ?tema q:subTemaDe* q:inteligencia_artificial .
} ORDER BY ?titulo
```

Resultado: Aprendizado de máquina em profundidade; Inteligência artificial no papel; Linguagem natural para iniciantes; Primeiros passos em inteligência artificial.

### Livros de uma classe inferida

```sparql
SELECT DISTINCT ?titulo {
  ?l a/rdfs:subClassOf* q:LivroIntrodutorioIA ; q:titulo ?titulo .
} ORDER BY ?titulo
```

Resultado após o HermiT: Inteligência artificial no papel; Linguagem natural para iniciantes; Primeiros passos em inteligência artificial. Nenhum desses livros foi originalmente declarado nessa classe.

### Recomendação e fatos usados na justificativa

Na implementação, os parâmetros `??1` a `??5` são entidades OWL passadas à API, sem interpolar texto fornecido pelo usuário na consulta:

```sparql
SELECT DISTINCT ?livro ?titulo ?tema ?nomeTema ?nomeNivel ?nomeFormato ?autor
WHERE {
  ?livro a/rdfs:subClassOf* ??1 ; a/rdfs:subClassOf* ??2 ;
         q:titulo ?titulo ; q:abordaTema ?tema ;
         q:temNivel ??3 ; q:temFormato ??4 ; q:temAutor ?a .
  ?tema q:subTemaDe* ??5 ; q:nome ?nomeTema .
  ??3 q:nome ?nomeNivel . ??4 q:nome ?nomeFormato . ?a q:nome ?autor .
} ORDER BY ?titulo ?autor
```

Para IA básica digital, os parâmetros são `LivroIntrodutorio`, `LivroDigital`, `basico`, `digital` e `inteligencia_artificial`. Os fatos retornados pelo SPARQL abastecem as justificativas, e uma consulta complementar recupera os novos tipos. Python interpreta argumentos e formata a saída, mas não decide a compatibilidade por comparação de strings nem por pontuação.

## 8. Recomendações e dependência do raciocínio

A mesma consulta para IA básica digital retornou zero linhas antes e duas após o HermiT. Antes, os livros só possuíam o tipo `Livro`; depois, passaram a atender aos filtros de classe da consulta. Isso comprova que o raciocínio influencia a seleção.

| Preferências | Resultados verificados |
| --- | --- |
| ia, basico, digital | Linguagem natural para iniciantes; Primeiros passos em inteligência artificial |
| programacao, avancado, fisico | Algoritmos e programação avançada |
| literatura, basico, digital | Nenhum livro compatível encontrado |

No primeiro cenário, Linguagem natural para iniciantes atende ao nível básico e ao formato digital. Seu assunto PLN está abaixo de IA na hierarquia, e o livro recebeu as classes `LivroIntrodutorioIA` e `LivroDigital`. Primeiros passos em inteligência artificial tem IA como assunto direto e recebeu as mesmas classes.

No segundo cenário, Algoritmos e programação avançada tem tema programação, nível avançado e formato físico. O HermiT produziu as classes `LivroAvancado` e `LivroFisico`, exigidas pela consulta. No terceiro, a obra de literatura básica da base é física, e a digital é avançada. A consulta não produz resultados nem substituições aproximadas.

Os resultados são ordenados pelo título e pelo autor. As justificativas são explicações construídas a partir dos fatos consultados e dos axiomas conhecidos, não provas mínimas de explicação extraídas automaticamente do HermiT.

## 9. Reprodução e validação

Os cinco arquivos da solução são [recomendador.py](recomendador.py), [ontologia.owl](ontologia.owl), [requirements.txt](requirements.txt), este [relatório](resposta.md) e [apresentacao.html](apresentacao.html). Não são necessários banco externo, servidor web, framework ou modelo de aprendizagem.

Com Python 3 e Java instalados, abra o terminal nesta pasta:

```console
python -m pip install -r requirements.txt
python recomendador.py --demo
python recomendador.py --tema ia --nivel basico --formato digital
python recomendador.py --tema programacao --nivel avancado --formato fisico
python recomendador.py --tema literatura --nivel basico --formato digital
```

Os temas aceitos são `ia`, `computacao`, `programacao`, `literatura`, `aprendizado_maquina` e `pln`; os níveis são `basico` e `avancado`; os formatos são `digital` e `fisico`. Argumentos inválidos ou incompletos produzem erro de uso com código 2. Falhas na execução do reasoner ou nas verificações retornam código 1. Ausência de recomendação é um resultado válido, com código 0.

O OWL já está incluído. Para reconstruí-lo com os fatos declarados:

```console
python recomendador.py --construir
python recomendador.py --demo
```

`--construir` substitui somente a ontologia de origem. A demonstração não a altera. O caminho do OWL é resolvido em relação ao script, permitindo executar a CLI também de outra pasta.

Se o Java estiver fora do PATH, no PowerShell configure seu caminho real, por exemplo:

```powershell
$env:JAVA_EXE = 'C:\Program Files\Microsoft\jdk-21.0.9.10-hotspot\bin\java.exe'
python recomendador.py --demo
```

Em algumas instalações Windows, o empacotamento do Owlready2 pode esbarrar no limite de caminhos longos. Nesse caso, extraia o pacote oficial em um caminho curto e execute `python -m pip install CAMINHO_DA_PASTA_EXTRAIDA`. A leitura do OWL usa `fileobj` para evitar o problema de conversão de URI local observado no Owlready2 0.51 no Windows.

### Verificações efetivamente executadas

| Verificação | Natureza | Resultado |
| --- | --- | --- |
| 24 classes, 18 propriedades, 26 indivíduos, oito livros | Estrutural | Aprovada |
| Todas as propriedades com relações na base | Estrutural | Aprovada |
| Carregamento do RDF/XML em novo World | Leitura do arquivo | Aprovada |
| Oito livros com tipo original apenas Livro | Estrutural | Aprovada |
| Execução Java/HermiT e classificação dos oito livros | Reasoner real | Aprovada |
| Relação PLN → IA ausente antes e presente depois | Reasoner e SPARQL direto | Aprovada |
| Consistência principal e nenhuma classe insatisfatível | Reasoner real | Aprovada |
| Contradição detectada em World isolado | Reasoner real | Aprovada |
| Consultas de autores, tema, classe e justificativas | SPARQL nativo | Aprovada |
| Consulta de IA básica digital: zero antes, duas depois | Comparação semântica | Aprovada |
| Cenários alternativo e vazio | CLI e SPARQL | Aprovada |
| SHA-256 preservado | Integridade do OWL | Aprovada |
| Nova demo e três consultas em processos Python separados | Reprodutibilidade | Aprovada |
| Argumentos inválidos e preferências incompletas | CLI, código 2 | Aprovada |
| Cinco slides locais, navegação por botões e teclado | Navegador, 1280 × 900 e 390 × 844 | Aprovada, sem transbordamento horizontal |

A apresentação pode ser aberta diretamente no navegador, sem servidor. Os botões e as teclas de seta, Page Up, Page Down, Home e End controlam a navegação. O HTML não faz requisições a recursos externos. Em telas pequenas, o conteúdo pode exigir rolagem vertical.

## 10. Vantagens e limitações

A ontologia torna explícitos os critérios de classificação e permite reutilizar o mesmo vocabulário em consultas diferentes. Novos livros podem receber as classificações existentes apenas pelo preenchimento de propriedades, sem adicionar uma regra procedural para cada título. A hierarquia de temas permite aproveitar assuntos mais específicos em buscas amplas.

A qualidade dos resultados depende da correção e da cobertura dos fatos e axiomas. O catálogo exige manutenção manual, não aprende com cliques, avaliações ou mudanças de interesse e não faz busca aproximada ou ranking de relevância. A convenção exclusiva entre técnica e ficção precisaria ser revista para um catálogo mais amplo. Assuntos de IA são explicitamente tipados em `TemaIA`; a relação `subTemaDe` não determina, por si só, essa categoria de classe.

As restrições existenciais e o mundo aberto não substituem uma validação de completude de dados. A execução depende de Java e do HermiT, e seu custo pode aumentar em ontologias maiores. A validação realizada comprova os cenários desta base pequena no ambiente informado, sem demonstrar desempenho ou portabilidade em todos os sistemas operacionais.

## 11. Referências

1. Owlready2. Documentação oficial. <https://owlready2.readthedocs.io/en/latest/>. Consulta em 9 de novembro de 2026.
2. Owlready2. Reasoning. <https://owlready2.readthedocs.io/en/latest/reasoning.html>. Consulta em 9 de novembro de 2026.
3. Owlready2. SPARQL queries. <https://owlready2.readthedocs.io/en/latest/sparql.html>. Consulta em 9 de novembro de 2026.
4. W3C. OWL 2 Web Ontology Language Primer, Second Edition. Recomendação de 11 de dezembro de 2012. <https://www.w3.org/TR/owl-primer/>. Consulta em 9 de novembro de 2026.
