# Lista 2 — Inteligência Artificial

Resoluções teóricas e implementações da Lista 2 de Inteligência Artificial, período **2026.2**. O repositório reúne 15 questões sobre representação do conhecimento, agentes inteligentes, aprendizagem, inferência e planejamento.

**Alunos:** Victor André Lopes Brasileiro, José Riquelme Teixeira da Silva e Erasmo da Silva Sá Junior.

- [Enunciado da lista (PDF)](docs/Lista%202_IA_Grad_2026_2%20%281%29.pdf)
- [Todas as respostas, com sumário](respostas_consolidadas.md)

## Questões

Cada link da primeira coluna abre o relatório `resposta.md`, com a fundamentação, os resultados e as referências da questão.

| Questão | Tema | Implementação |
| --- | --- | --- |
| [01](questao_01/resposta.md) | Ontologias e grafos de conhecimento | Discussão e exemplo de catálogo de livros |
| [02](questao_02/resposta.md) | K-vizinhos mais próximos (KNN) | `knn.py`: K = 3, distância de Hamming e avaliação Leave-One-Out sobre `dados.csv` |
| [03](questao_03/resposta.md) | ELIZA, PARRY e AIML/ALICE | Análise dos sistemas de conversação |
| [04](questao_04/resposta.md) | Categorias de agentes inteligentes e PEAS | Comparação de arquiteturas e aplicações |
| [05](questao_05/resposta.md) | Inferência em LLMs | Do processamento do prompt à geração da resposta |
| [06](questao_06/resposta.md) | Inferência fuzzy de Mamdani | `sistema_fuzzy.py`: controle de ventilação por temperatura e umidade |
| [07](questao_07/resposta.md) | Raciocínio baseado em casos (RBC) | `sistema_rbc.py`: recuperação por Jaccard, revisão e retenção em `casos.json` |
| [08](questao_08/resposta.md) | Redes bayesianas | `rede_bayesiana.py`: inferência por eliminação de variáveis, exportação BIF e grafo PNG |
| [09](questao_09/resposta.md) | Recomendação de livros com OWL 2 | `recomendador.py`: ontologia, consultas SPARQL e inferência com HermiT |
| [10](questao_10/resposta.md) | Planejamento de rotas | `buscas.py`: DFS, BFS, custo uniforme (UCS), A* e visitas obrigatórias |
| [11](questao_11/resposta.md) | Agentes clássicos e agentes baseados em LLMs | Comparação aplicada ao planejamento acadêmico |
| [12](questao_12/resposta.md) | Agente de planejamento acadêmico com LLM | `agente.py` e `planejador.py`: extração via Gemini, planejamento e validação locais |
| [13](questao_13/resposta.md) | Arquitetura Transformer | Ensaio sobre os componentes e o funcionamento da arquitetura |
| [14](questao_14/resposta.md) | Knowledge Graphs | Representação, inferência e aprendizagem |
| [15](questao_15/resposta.md) | Ontologia OWL 2 com inferência automática | `ontologia.py`: classificação, transitividade e teste de inconsistência com HermiT |

## Organização das pastas

```text
lista_2/
├── docs/                       # Enunciado em PDF
├── questao_01/ ... questao_15/  # Relatórios e arquivos de cada questão
├── respostas_consolidadas.md   # Respostas reunidas em um documento
└── README.md
```

As pastas com implementação incluem os scripts e seus dados. As questões 6, 8, 9 e 15 possuem dependências Python externas, listadas nos respectivos `requirements.txt`. O `requirements.txt` da questão 12 apenas documenta os requisitos, pois o código usa a biblioteca padrão.

As questões 8 e 9 também possuem apresentações HTML: [rede bayesiana](questao_08/apresentacao.html) e [recomendação de livros](questao_09/apresentacao.html). Abra os arquivos em um navegador para visualizá-las.

## Preparação do ambiente

Para consultar os relatórios, basta um leitor de Markdown. Para executar o código, use Python; a questão 12 exige **Python 3.10 ou superior**. Os relatórios das questões 8, 9, 12 e 15 registram validações com Python 3.13.12.

Os comandos abaixo partem da **raiz do repositório**, com o ambiente virtual ativado. Instale somente as dependências das questões que pretende executar.

No Windows, com PowerShell:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

No Linux ou macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Se a ativação estiver bloqueada no PowerShell, use `.\.venv\Scripts\python.exe` no lugar de `python` nos comandos seguintes.

As questões 9 e 15 também precisam de Java para executar o HermiT incluído no Owlready2. A questão 12 precisa de internet e de uma chave da API Gemini para usar o agente.

## Execução

### Questões 2, 7 e 10 — biblioteca padrão

```bash
python questao_02/knn.py
python questao_07/sistema_rbc.py --demo
python questao_10/buscas.py
```

Para abrir o RBC em modo interativo, execute `python questao_07/sistema_rbc.py`. Nesse modo, a confirmação de retenção grava novos casos em `questao_07/casos.json`; a demonstração com `--demo` usa uma cópia temporária e preserva a base original.

### Questão 6 — sistema fuzzy

```bash
python -m pip install -r questao_06/requirements.txt
python questao_06/sistema_fuzzy.py --exemplos
python questao_06/sistema_fuzzy.py --temperatura 30 --umidade 65
```

As entradas aceitas são temperatura de 0 a 40 °C e umidade relativa de 0 a 100%. A saída é a velocidade recomendada do ventilador, em porcentagem.

### Questão 8 — rede bayesiana

```bash
python -m pip install -r questao_08/requirements.txt
python questao_08/rede_bayesiana.py --demo
python questao_08/rede_bayesiana.py --evidencias "Febre=Sim,Tosse=Sim"
```

A demonstração valida o modelo e os resultados, além de gerar novamente `questao_08/modelo.bif` e `questao_08/rede.png`. Sem argumentos, o programa apresenta a probabilidade a priori.

### Questões 9 e 15 — ontologias e HermiT

Com Java disponível no `PATH`:

```bash
java -version
python -m pip install -r questao_09/requirements.txt
python -m pip install -r questao_15/requirements.txt
python questao_09/recomendador.py --demo
python questao_09/recomendador.py --tema ia --nivel basico --formato digital
python questao_15/ontologia.py --demo
python questao_15/ontologia.py --teste-inconsistencia
```

Se o Java estiver fora do `PATH`, defina `JAVA_EXE` com o caminho completo do executável. No PowerShell, por exemplo, substitua o caminho abaixo pelo da sua instalação:

```powershell
$env:JAVA_EXE = "C:\caminho\do\jdk\bin\java.exe"
```

Os arquivos `ontologia.owl` já estão no repositório. Para reconstruí-los a partir do código, execute os comandos abaixo; eles sobrescrevem o OWL da respectiva questão:

```bash
python questao_09/recomendador.py --construir
python questao_15/ontologia.py --construir
```

O teste de inconsistência da questão 15 introduz estados disjuntos somente em memória. O resultado esperado é a detecção da inconsistência pelo HermiT, mantendo o arquivo OWL original intacto.

### Questão 12 — agente acadêmico com Gemini

Crie `questao_12/.env` com sua chave. O arquivo é ignorado pelo Git:

```dotenv
GEMINI_API_KEY=SUA_CHAVE_AQUI
GEMINI_MODEL=gemini-3.1-flash-lite
```

`GEMINI_MODEL` é opcional; o valor mostrado é o padrão definido no código. Também é possível configurar as variáveis no ambiente. Valores preenchidos no `.env` têm preferência sobre variáveis de mesmo nome no terminal.

```bash
python questao_12/agente.py --diagnostico
python questao_12/agente.py --demo
python questao_12/agente.py
```

`--diagnostico` consulta os metadados do modelo, sem gerar uma agenda. `--demo` usa a API para interpretar o cenário da questão 11; sem argumentos, o agente abre uma interface interativa no terminal.

O Gemini extrai os dados do pedido; o planejamento e a verificação das restrições ocorrem localmente. O planejador aceita até 10 atividades indivisíveis em uma única janela do mesmo dia, com prioridades, prazos e horários fixos. Os detalhes e as limitações estão no [relatório da questão 12](questao_12/resposta.md).

## Testes e validações

Execute os testes da questão 12 a partir da raiz, sem chave de API ou acesso à internet:

```bash
python -m unittest discover -s questao_12 -p test_planejador.py -v
```

A suíte contém 69 testes de planejamento, validação, configuração e integração simulada. A integração real com Gemini é exercitada separadamente por `python questao_12/agente.py --demo`.

As demais implementações incluem verificações nos próprios scripts ou modos de demonstração. Os relatórios individuais descrevem os cenários, os resultados observados e as limitações de cada solução.
