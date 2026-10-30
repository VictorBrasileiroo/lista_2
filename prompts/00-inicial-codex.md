# Prompt 00 — bootstrap e prova de viabilidade (enviar primeiro)

Você está no repositório `lista-2-inteligencia-artificial`, destinado à Lista 2 de IA (15 questões, prazo 17/11/2026). Você é o **executor**; o usuário e o ChatGPT revisam e aprovam.

Leia antes de agir: `AGENTS.md`, `docs/00-visao-geral.md`, `docs/01-matriz-de-requisitos.md`, `docs/03-validacao.md`, `docs/04-pendencias-e-riscos.md`, `docs/05-diario-de-decisoes.md` e os `README.md` de Q9 e Q12. Se o enunciado original não estiver acessível localmente, considere a matriz uma transcrição operacional parcial e sinalize pontos para conferência posterior, sem inventar requisitos.

## Escopo estrito desta execução

**Não implemente ainda sistemas completos nem outras questões.** Faça apenas:

1. Conferir/ajustar a estrutura existente sem apagar conteúdo útil.
2. Criar documentação prática mínima de ambiente Windows/PowerShell + Python 3.11+, explicando dependências específicas de Q9 (Java + Owlready2/HermiT/Protégé) e Q12 (Ollama + modelo configurável).
3. Criar **dois spikes isolados e pequenos**:
   - `questoes/q09/spike_reasoner.py`: construir uma ontologia OWL **mínima** local (2–3 classes e 1 indivíduo), criar uma condição para classe inferida, executar **um reasoner OWL real** e evidenciar o novo tipo inferido; salvar OWL e reportar versão/execução. Se Java/reasoner não estiver disponível, falhar explicitamente (não imitar inferência em Python puro).
   - `questoes/q12/spike_ollama.py`: chamar **de verdade** a API local configurável do Ollama (`/api/chat`) com saída em JSON, validar estrutura da resposta e registrar conexão/modelo. Caso não haja servidor ou modelo, retornar erro claro, não usar resposta simulada.
4. Testes/validações mínimas desses spikes, quando o ambiente permitir. Adicionar `.gitignore` ou ajustes necessários, sem commitar segredos e dados privados.
5. Atualizar o `docs/04-pendencias-e-riscos.md` e `docs/05-diario-de-decisoes.md` com descobertas **reais**.

## Critérios de aceite

- `python scripts/verificar_estrutura.py` funciona.
- Os spikes são executáveis por comandos documentados e mantidos isolados das implementações finais.
- Em caso de indisponibilidade local (Java, Owlready2, Ollama), estado marcado como **NÃO EXECUTADO / BLOQUEADO** com mensagens, e não como sucesso.
- Nenhum conteúdo das outras 13 questões alterado, exceto correções justificadas de estrutura.
- Relatório final: arquivos alterados, comandos rodados, saídas reais, resultados comprovados e bloqueios.

## Parar ao concluir

Não prossiga sozinho para Q9/Q12 completos. Entregue diff e evidências para revisão independente. Prefira progresso pequeno, reproduzível e auditável.
