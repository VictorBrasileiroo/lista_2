# Etapa 0 — visão geral

**Documento-base:** Lista 2, IA PPGI, 2026.2, Prof. Evandro Costa (11 páginas, 15 questões).  
**Prazo:** terça-feira, 17/11/2026, 23h59.  
**Planejamento criado em:** 30/10/2026.

## Estratégia aprovada

Discussão (usuário + ChatGPT) → prompt com critérios de aceite → execução (Codex) → validação independente (usuário + ChatGPT) → correção. Commits pequenos e auditáveis; avançar por blocos de afinidade.

**Modelo de esforço:** reservar inicialmente 4 sessões por semana de 60–90 min mais uma janela eventual maior para revisão/demo. Estimativa sujeita a ajuste, sobretudo na OWL/Java, rede Bayesiana e LLM local. Não tratar qualquer prazo de subatividade como garantia.

## Mapa de blocos

| Bloco | Questões | Conexão principal | Ordem de prioridade |
|---|---|---|---|
| B1 — riscos de integração | Q9, Q12 | Reasoner OWL 2 e LLM operacional | Primeiro (provas de viabilidade) |
| B2 — conhecimento semântico | Q1, Q14, Q15 | Reusar ontologia da Q9 e KG derivado | Após a prova de reasoner |
| B3 — sistemas e agentes | Q6, Q7, Q8, Q4, Q11 | Fuzzy/prioridades, casos/redes médicas, planejamento | Em paralelo às pesquisas |
| B4 — algoritmos e história | Q2, Q3, Q10 | Dataset da Lista 1, ELIZA, rotas | Conforme dados e revisão |
| B5 — textos baseados em vídeos | Q5, Q13 | Conferir conteúdo em fontes reais | Iniciar coleta cedo, fechar ao final |

## Arquitetura proposta, não requisito do professor

- Base: Python 3.11+, CLI e relatórios Markdown + exportações PDF/HTML onde necessário.
- Q6: scikit-fuzzy, Mamdani, centroide; exemplo sugerido: priorização acadêmica.
- Q7: casos fictícios em JSON/CSV e similaridade Jaccard ponderada (ajustável após análise), persistência local explícita.
- Q8: pgmpy, rede discreta, VariableElimination, diagrama e 3 inferências, CPTs **ilustrativas**.
- Q9/Q15: OWL 2; Protégé + HermiT para inspeção, Owlready2 + HermiT para integração Python; RDFLib para consultas.
- Q10: Python puro com BFS, DFS, UCS e A* e estados expandidos para D/F.
- Q11: baseline determinístico para planejamento; comparação com agente Q12.
- Q12: Ollama local (modelo configurável) para interpretar intenção, agenda determinística para garantir restrições, resposta explicada.
- Q1/Q14: mesmo domínio da Q9; distinguir ontologia, KG, consultas e inferências; Neo4j opcional, não obrigatório.
- Q2: biblioteca ou implementação transparente; **dados reais da Lista 1 são indispensáveis**.

## Definição de pronto

Uma questão só passa a "APROVADA" quando cobrir requisitos, executar (quando aplicável), ter casos de controle e documentos/demo e receber revisão externa ao Codex. Ver `docs/03-validacao.md`.
