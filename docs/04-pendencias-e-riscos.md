# Pendências, riscos e contingências

| Item | Impacto | Ação / mitigação | Estado inicial |
|---|---|---|---|
| **Q2: 30 instâncias da Lista 1** | Sem os dados originais, resultado seria fabricado | Localizar/fornecer arquivo da Lista 1, atributo-alvo e convenções; deixar execução bloqueada | BLOQUEADO |
| **Q10: Profundidade (BFS)** | Ambiguidade altera ordem de expansão e comparação | Implementar BFS (largura) e DFS (profundidade), nomear e comparar ambos; pedir esclarecimento ao professor se viável | ABERTO |
| **Q5/Q13 vídeos** | Risco de resumo inventado por inacessibilidade de transcrição | Coletar vídeo/transcrição confiável e notas com timestamps, citar precisamente; se não disponível, sinalizar bloqueio | ABERTO |
| **Q9/Q15 reasoner OWL** | Necessita Java/Protégé ou reasoner funcional; RDFLib sozinho não faz inferência OWL DL | Prova mínima de inferência no 1º marco; se API Java falhar, usar Protégé + HermiT e evidenciar resultado | ABERTO |
| **Q12 LLM local** | Dependência de Ollama/modelo e formato da saída do modelo | Configurar modelo por variável de ambiente e teste real; planner/verificador separado, fallback com erro explícito | ABERTO |
| **Q7/Q8 diagnóstico fictício** | Conteúdo pode sugerir orientação clínica, dados sintéticos confundidos com evidência | Disclaimer educacional, rótulo sintético, sem pacientes reais/conduta clínica individual | ABERTO |
| **Q7–Q9 apresentação/demo** | Não bastam códigos e roteiros | Q7: demonstração executável ou vídeo. Q8/Q9: slides exportados em PDF ou vídeo efetivo | ABERTO |
| **Escopo excessivo para 15 itens** | Retrabalho, consumo alto, prazo | Em cada prompt limitar a no máximo 1–3 questões; impedir UI sofisticada sem necessidade | ABERTO |
| **Repo público** | Exposição inadvertida de segredos e material protegido | Não versionar PDF original, dados privados, chaves, logs sensíveis, transcrição integral de vídeos | ABERTO |
| **Formato de submissão não explicitado** | Falta de artefatos finais aceitos pelo professor | Conferir plataforma de entrega/instruções adicionais; pacote final conter README e arquivos reproduzíveis | ABERTO |

## Decisão de contingência

Se um requisito técnico ameaçar 13/11, reduzir apresentação/UI, não remover a inferência real nem o artefato formal. Se dependência for externa (Lista 1 ou vídeo), explicitar bloqueio e trabalhar em outra questão, sem produzir evidência sintética indevida.
