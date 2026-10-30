# Q09 — Recomendador por ontologia OWL 2

**Fonte:** Lista 2 IA, 2026.2, pp. 7–8.  
**Status na etapa 0:** `PENDENTE` (planejamento, não implementação).  
**Bloco:** B1.

## Spike da Etapa 00 (isolado)

`spike_reasoner.py` e `requirements-spike.txt` verificam apenas Java/HermiT,
consistência e um tipo inferido em ontologia mínima (três classes/um indivíduo).
Não atendem às contagens nem implementam o recomendador final.
Ver [ambiente e comandos](../../docs/07-ambiente-etapa-00.md) e
[resultados observados](../../docs/08-evidencias-etapa-00.md).
O checklist abaixo continua pendente para a questão completa.

## O que exige o enunciado

Domínio proposto: recursos de aprendizagem; OWL 2 com >=10 classes, >=15 propriedades, hierarquia, restrições, axiomas, indivíduos, consulta semântica, reasoner, recomendações justificadas e evidências de raciocínio.

## Evidências esperadas

.owl, código, relatório (domínio, modelagem, exemplos, mecanismo, crítica), apresentação ou vídeo.

## Critérios de aceite / testes

Contar classes/propriedades, razão automática realmente executada, classificação inferida, relação implícita e consistência (não apenas consultas manuais).

## Dependências e riscos

Protégé + HermiT; Python Owlready2/RDFLib; requer Java configurado.

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
- **Bloqueios:** Protégé + HermiT; Python Owlready2/RDFLib; requer Java configurado.
- **Parecer final:** pendente.
