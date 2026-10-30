# Diário de decisões arquiteturais (ADR simplificado)

| Data | Decisão | Motivo | Trade-off / validar |
|---|---|---|---|
| 30/10 | Repositório único com pastas `q01`–`q15` | Revisão, reuso, entrega rastreável | Separar dependências por questão |
| 30/10 | Python + CLI primeiro | Baixo atrito e fácil teste | Interface mais simples; Q12 mantém linguagem natural |
| 30/10 | Q9/Q15 usar domínio de recursos de aprendizagem | Reaproveita OWL e KG em Q1/Q14 | Exige classes/propriedades com significado, não inflar contagens |
| 30/10 | Q7/Q8 usar domínio respiratório **sintético** | Compartilha vocabulário sem confundir métodos | Não alegar probabilidades epidemiológicas reais |
| 30/10 | Q11/Q12 usar agenda acadêmica | Mesmo cenário descrito no PDF | LLM deve ser validado por planner determinístico |
| 30/10 | Mamdani Q6: priorização de tarefas acadêmicas | Domínio de fácil interpretação | Evitar confundir fuzzy com agendamento otimizado |
| 30/10 | Q10 documentar BFS e DFS | PDF contradiz sigla/termo | Pode produzir análise extra curta |
| 30/10 | Q2 não fabricar 30 exemplos | Depende da Lista 1 não disponibilizada | Necessita dados reais |

## Novas decisões

Acrescentar uma linha por decisão importante. Registrar problema, opções, justificativa, risco e como saber se funcionou. O Codex não deve mudar decisões silenciosamente.
