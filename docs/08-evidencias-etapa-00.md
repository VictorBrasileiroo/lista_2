# Evidências reais — Etapa 00 (30/10/2026)

**Estado: PARCIAL, pronta para revisão do escopo; integração Q12 BLOQUEADA.**
Nenhuma questão completa ou aprovada. Branch de trabalho: `etapa-00-spikes`.

## Cobertura do prompt 00

- [x] Estrutura inspecionada e verificador executado; sem necessidade de mudar scaffold.
- [x] Instruções Windows/PowerShell, Python 3.11+, Java/HermiT/Protégé e Ollama configurável.
- [x] Spike Q9: três classes, um indivíduo, OWL local, HermiT real, consistência e novo tipo inferido; controle negativo inconsistente.
- [x] Spike Q12: POST real `/api/chat`, formato JSON, verificação determinística e falha explícita; teste reproduzível pronto.
- [x] Testes mínimos, revisão de `.gitignore`, diário e riscos atualizados.
- [ ] Resposta de modelo Ollama obtida e validada: **BLOQUEADO**, conexão recusada.
- [ ] Conferência com enunciado original: **NÃO EXECUTADO**, não localizado localmente.

## Comandos executados e resultados

Todos os comandos de teste abaixo usam `./.venv/Scripts/python.exe` na raiz.
[comandos.json](evidencias/etapa-00/comandos.json) registra argumentos e códigos de saída.
Arquivos `.txt` contêm stdout/stderr capturados de execuções reais por `subprocess.run`;
somente os prefixos do repositório/perfil foram substituídos por `<REPO>`/`<USERPROFILE>`.
Temporários Java identificam execuções específicas. Não são outputs simulados.

| Argumentos | Saída observada | Exit | Evidência |
|---|---|---|---|
| `scripts/verificar_estrutura.py` | 15 pastas presentes; validação apenas estrutural | 0 | [estrutura](evidencias/etapa-00/estrutura.txt) |
| `-m unittest discover -s tests -v` | 4 testes passaram; fixtures artificiais, sem rede/LLM | 0 | [contrato](evidencias/etapa-00/contrato-json.txt) |
| `questoes/q09/spike_reasoner.py --output _tmp/q09` | consistente; antes `[Recurso]`, depois `[RecursoBasico]` | 0 | [HermiT](evidencias/etapa-00/q09.txt) |
| `questoes/q09/spike_reasoner.py --inconsistent --output _tmp/q09-inconsistent` | inconsistência rejeitada pelo HermiT | 0 | [controle](evidencias/etapa-00/q09-inconsistente.txt) |
| `questoes/q12/spike_ollama.py --model qwen2.5:3b --timeout 5` | WinError 10061, conexão recusada em 127.0.0.1:11434 | 2 | [chamada real](evidencias/etapa-00/q12.txt) |
| `questoes/q12/spike_ollama.py` | modelo não configurado; erro explícito antes de HTTP | 2 | [sem modelo](evidencias/etapa-00/q12-sem-modelo.txt) |
| `-m pip check` | No broken requirements found. | 0 | [dependências](evidencias/etapa-00/pip-check.txt) |

Preparação efetivamente executada:

- Leitura integral de `AGENTS.md`, prompt 00 e sete documentos/READMEs exigidos; inventário com `rg --files --hidden -g '!.git/**'`. Original ausente nesse inventário.
- `git status --short`, `git remote -v`, `git branch --show-current`, `git log -1 --oneline`: checkout limpo inicialmente em `main`, base `9923e0e`, remoto `VictorBrasileiroo/lista_2`.
- Git no sandbox exigiu exceção de ownership. Usado `git -c safe.directory=C:/Users/victo/Desktop/FACULDADE/IA/lista_2 ...` por comando, sem alterar configuração global. `git switch -c etapa-00-spikes` precisou execução elevada pela restrição de escrita em `.git` e então funcionou.
- `python --version` / `py -3.12 --version`: alias da Store falhou no sandbox. Caminho convencional `C:/Users/victo/AppData/Local/Programs/Python/Python312/python.exe --version`: 3.12.4, funcional. Esse executável criou `.venv` com `-m venv .venv`.
- `java -version`: OpenJDK Microsoft 21.0.9 LTS. `java -cp .venv/Lib/site-packages/owlready2/hermit/HermiT.jar org.semanticweb.HermiT.cli.CommandLine --version`: 1.3.8.1099.
- `./.venv/Scripts/python.exe -m pip install -r questoes/q09/requirements-spike.txt`: falhou inicialmente por rede restrita, WinError 10013. Repetido com permissão de rede e `--retries 0 --timeout 30`: instalou Owlready2 0.48, código 0. Nenhuma dependência global instalada.
- `Test-NetConnection 127.0.0.1 -Port 11434`: TcpTestSucceeded=False; o POST posterior confirmou recusa. Não demonstra ausência do Ollama na máquina do estudante.
- `git diff --check`: sem erros de whitespace (avisos locais de conversão LF/CRLF).
- Inspeção independente dos OWLs com `xml.etree.ElementTree` em Python (`python -`, script inline): confirmou três classes nomeadas, um indivíduo e diferença exata de tipos `{#RecursoBasico}` entre antes/depois; código 0.

## Artefatos e inspeção independente

O [asserted.owl](evidencias/etapa-00/asserted.owl) e o
[inferred.owl](evidencias/etapa-00/inferred.owl) são cópias dos arquivos gerados
pela execução consistente. Compare o indivíduo `exemplo`: a assertiva
`rdf:type RecursoBasico` existe somente depois. O log do processo Java contém
`Type( <https://example.org/etapa00.owl#exemplo> <https://example.org/etapa00.owl#RecursoBasico> )`.
O código não acrescenta esse tipo manualmente. O controle negativo exige rejeição
da combinação com `RecursoAvancado`, disjunto da classe inferida.

## Arquivos alterados e justificativas

- `README.md`: estado atual e links para reprodução/evidências; corrigida observação histórica sobre remoto inexistente.
- `docs/04-pendencias-e-riscos.md`, `docs/05-diario-de-decisoes.md`: pressupostos, testes planejados antes do código, descobertas e bloqueios reais.
- `docs/07-ambiente-etapa-00.md`, este relatório e `docs/evidencias/etapa-00/`: instalação, reprodução e evidências verificáveis.
- `questoes/q09/README.md`, `spike_reasoner.py`, `requirements-spike.txt`: isolar prova real OWL e fixar dependência.
- `questoes/q12/README.md`, `spike_ollama.py`: isolar integração real e contrato JSON sem assistente completo.
- `tests/test_spike_ollama.py`: casos artificiais independentes de contrato, incluindo duração booleana, intenção errada e estrutura inválida.

## Pendências e reprodução limpa

Seguir [07-ambiente-etapa-00.md](07-ambiente-etapa-00.md) em novo checkout e venv.
Executar estrutura, unittest e ambos os comandos Q9. Para Q12, configurar um
servidor efetivamente acessível e modelo instalado, repetir o POST e preservar
stdout/stderr, exit code, modelo e versão de Ollama. Versão do Ollama, modelo
instalado e inferência LLM: **NÃO VERIFICADOS** nesta execução.
Protégé e questões completas: **NÃO EXECUTADOS**. Não há planejador, interface
natural completa, recomendações, apresentação ou solução de outras questões.
Revisão independente e conferência das 11 páginas permanecem pendentes.
