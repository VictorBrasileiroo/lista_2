# Lista 2 — Inteligência Artificial (planejamento e execução)

**Prazo oficial informado pelo estudante:** 17/11/2026, 23h59 (horário local).  
**Meta interna:** conteúdo e implementações congelados até 13/11; auditoria de 14 a 16/11.  
**Estado:** Etapa 00 com dois spikes isolados para revisão; **nenhuma das 15 questões foi implementada integralmente ou aprovada**. Ambiente e reprodução em [`docs/07-ambiente-etapa-00.md`](docs/07-ambiente-etapa-00.md); resultados reais em [`docs/08-evidencias-etapa-00.md`](docs/08-evidencias-etapa-00.md).

## Comece aqui

1. Leia [`docs/00-visao-geral.md`](docs/00-visao-geral.md), [`docs/01-matriz-de-requisitos.md`](docs/01-matriz-de-requisitos.md) e [`AGENTS.md`](AGENTS.md).
2. Confira decisões pendentes em [`docs/04-pendencias-e-riscos.md`](docs/04-pendencias-e-riscos.md).
3. Envie o texto de [`prompts/00-inicial-codex.md`](prompts/00-inicial-codex.md) ao Codex no repositório.
4. Revise o diff do Codex; use a matriz de requisitos e [`docs/03-validacao.md`](docs/03-validacao.md) para aprovar ou pedir correções.
5. Execute os prompts de lotes na ordem da prioridade técnica (não necessariamente na ordem numérica).

## Estrutura

- `questoes/q01...q15/`: fonte da verdade para cada questão, progresso e futura implementação.
- `docs/`: requisitos, arquitetura, cronograma, decisões, riscos e validação.
- `prompts/`: prompts prontos ou modelos de delegação para Codex.
- `entrega/`: lista de arquivos finais e orientação para empacotamento.
- `scripts/`: validações de estrutura (não substituem testes das implementações).

## Regras de honestidade

- Não afirmar que código, experimentos, razão OWL, vídeos ou fontes foram validados antes da execução.
- Questão 2 depende das **30 instâncias reais da Lista 1**; não as inventar.
- A Q10 tem contradição entre "Profundidade" e "BFS"; documentar ambas as interpretações.
- Exemplos médicos são fictícios e educacionais, nunca orientação clínica.
- O enunciado original não está versionado aqui para evitar redistribuição sem autorização. Manter cópia privada e transcrever somente requisitos necessários.

## Como publicar no GitHub (Windows PowerShell)

Se o GitHub CLI (`gh`) estiver instalado e autenticado, abra esta pasta e execute:

```powershell
git init
git add .
git commit -m "docs: estrutura e planejamento da lista 2 de IA"
gh repo create lista-2-inteligencia-artificial --public --source . --remote origin --push
```

Alternativa: crie o repositório público no site do GitHub, sem README/.gitignore automático, e faça `git remote add origin <URL>` + `git push -u origin main` (configure o nome da branch antes, se necessário).

**Observação:** os comandos acima são instruções históricas do pacote inicial. Nesta execução foi encontrado o remoto `https://github.com/VictorBrasileiroo/lista_2.git`; não execute `git init`/`gh repo create` novamente neste checkout.
