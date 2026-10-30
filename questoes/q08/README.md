# Q08 — Diagnóstico fictício com rede bayesiana

**Fonte:** Lista 2 IA, 2026.2, pp. 4–6.  
**Status na etapa 0:** `PENDENTE` (planejamento, não implementação).  
**Bloco:** B3.

## O que exige o enunciado

Rede com >=1 doença principal, >=5 variáveis, >=3 sintomas, dependências e CPTs justificadas, hipóteses e independências; >=3 cenários prior/post e interpretação.

## Evidências esperadas

Diagrama, artefato do modelo, código, CPTs, relatório (inferência/limitações), apresentação ou vídeo.

## Critérios de aceite / testes

CPTs normalizadas; 3 experimentos; posterior recontável por enumeração em rede pequena; dados ilustrativos.

## Dependências e riscos

pgmpy; reutiliza vocabulário de sintomas da Q7, NÃO seus valores como priors.

## Tarefas rastreáveis

- [ ] Conferir texto completo do enunciado e definir solução mínima.
- [ ] Gerar prompt de execução específico (baseado em `prompts/_modelo-ciclo.md`).
- [ ] Implementar ou redigir artefatos exigidos; documentar escolhas.
- [ ] Executar experimento, validação de fonte ou caso conhecido.
- [ ] Produzir relatórios, diagramas e apresentação/demo, se exigidos.
- [ ] Obter revisão externa ao Codex e registrar commit aprovado.

## Validação independente

- **Commit:** não definido.
- **Comandos efetivamente rodados:** nenhum.
- **Resultados observados:** nenhum.
- **Bloqueios:** pgmpy; reutiliza vocabulário de sintomas da Q7, NÃO seus valores como priors.
- **Parecer final:** pendente.
