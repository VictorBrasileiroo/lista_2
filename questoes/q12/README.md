# Q12 — Agente LLM com explicabilidade

**Fonte:** Lista 2 IA, 2026.2, p. 11.  
**Status na etapa 0:** `PENDENTE` (planejamento, não implementação).  
**Bloco:** B1.

## Spike da Etapa 00 (isolado)

`spike_ollama.py` verifica somente chamada HTTP real e contrato JSON de um pedido
fixo. Não implementa assistente, planejador ou validação de conflitos de agenda.
Ver [ambiente e comandos](../../docs/07-ambiente-etapa-00.md) e
[resultados observados](../../docs/08-evidencias-etapa-00.md).
Execução LLM depende de servidor/modelo acessíveis; testes unitários artificiais
do contrato não demonstram integração. Checklist da questão completa pendente.

## O que exige o enunciado

Implementar assistente acadêmico com interface em linguagem natural, uso efetivo de LLM, inferência/planejamento de ações e explicações; modelo local opcional via Ollama.

## Evidências esperadas

Aplicação executável, arquitetura e exemplos de interação, logs de validação e explicações; demo.

## Critérios de aceite / testes

Sem choque de agenda, restrições garantidas por verificador explícito, LLM real não simulado, falha controlada se indisponível.

## Dependências e riscos

Ollama e modelo local a confirmar; pode reusar baseline da Q11.

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
- **Bloqueios:** Ollama e modelo local a confirmar; pode reusar baseline da Q11.
- **Parecer final:** pendente.
