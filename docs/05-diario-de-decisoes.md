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

### 30/10/2026 — Etapa 00: pressupostos e testes definidos antes do código

- Escopo: somente dois spikes descartáveis de integração; nenhuma questão completa.
- Enunciado original ausente no inventário local; matriz usada como transcrição operacional parcial, a conferir posteriormente com as 11 páginas.
- Q9: três classes, um indivíduo e restrição de valor literal. Caso conhecido: recurso com nível `basico` deve ser classificado em `RecursoBasico` por HermiT; tipo ausente antes do reasoner. Controle negativo: ontologia deliberadamente inconsistente deve ser rejeitada pelo mesmo reasoner real. Salvar OWL antes/depois e registrar versões.
- Q12: biblioteca padrão HTTP, URL/modelo configuráveis, POST real `/api/chat`, JSON sem streaming. Verificador determinístico exige intenção `estudar` e duração inteira positiva. Testes unitários usam entradas explicitamente artificiais somente para o contrato JSON, nunca como evidência de LLM.
- Testes planejados: verificador estrutural, unittest do contrato Q12, integração Q9 com inferência e inconsistência, tentativa real Q12 com erro explícito se indisponível.
- Descobertas iniciais: Java OpenJDK 21.0.9 acessível; alias Python da Store falha na conta sandbox. Python 3.12.4 convencional localizado; execução com conta elevada confirmou também Python 3.12.10 via alias. Git exigiu `safe.directory` apenas por comando e execução elevada para criar `etapa-00-spikes`; não alterada configuração global.

### 30/10/2026 — Resultados e limites da Etapa 00

- Ambiente isolado `.venv` com Python 3.12.4; Owlready2 fixado em 0.48, instalado de fato após repetição com rede autorizada. Instalação inicial bloqueada por WinError 10013 não foi tratada como pacote inexistente.
- HermiT empacotado reporta 1.3.8.1099. Executou classificação consistente e controle negativo inconsistente, ambos com verificação esperada (código 0); OWL antes/depois preservado como evidência.
- Quatro testes unittest de contrato JSON passaram; não constituem chamada LLM. POST real Q12 falhou com conexão recusada (código 2). Não iniciar serviço, baixar modelo ou alterar rede do estudante; deixar teste pronto para repetição no servidor acessível.
- `.gitignore` existente já cobre `.venv`, `_tmp`, caches e `.env`; sem ajuste necessário. Logs selecionados sem dados privados em `docs/evidencias/etapa-00/*.txt`; caminhos locais variáveis substituídos por marcadores, com resultados inalterados. OWL local de exemplo é original deste spike.
- Q9/Q12 completas e demais 13 questões não implementadas; nenhuma aprovação atribuída pelo executor. Revisão independente e acesso ao original continuam necessários.

Acrescentar uma linha por decisão importante. Registrar problema, opções, justificativa, risco e como saber se funcionou. O Codex não deve mudar decisões silenciosamente.
