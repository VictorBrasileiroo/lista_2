# Protocolo de validação independente

O Codex **pode** gerar código e testes, mas não aprova a própria entrega. Revisão final feita por usuário + ChatGPT com base nos arquivos de um commit identificado, outputs e enunciado.

## Estado por questão

- `PENDENTE`: ainda sem execução.
- `EM_EXECUCAO`: Codex está implementando.
- `PRONTA_PARA_REVISAO`: entrega com comandos e arquivos revisáveis.
- `CORRECAO`: falhas de requisitos, resultado ou documentação.
- `APROVADA`: checklist completo e validação independente realizada.
- `BLOQUEADA`: dados ou ferramenta necessária indisponível, com justificativa.

## Critérios transversais (todos exigidos antes de aprovar)

1. **Requisitos:** comparar literalmente cada item do enunciado com evidência no repo; itens não cobertos explícitos.
2. **Correção:** rodar experimento/teste significativo; pelo menos 1 caso controlado com resposta conhecida calculada independentemente quando for sistema/algoritmo.
3. **Explicação:** entender a relação entrada → inferência/cálculo → saída e limitações reais.
4. **Reprodução:** instruções para instalar, executar e gerar o resultado em ambiente limpo; sem credenciais, rotas absolutas, seeds não declaradas.
5. **Entrega:** relatórios, scripts, `.owl`, diagramas, slides ou vídeos exigidos; saída de teste não substitui apresentação.
6. **Fontes:** citações rastreáveis em textos e algoritmos; nada de URLs inventadas, transcrições simuladas ou referências de segunda mão apresentadas como primárias.
7. **Escopo:** sem alterações colaterais em outras questões; estado e changelog atualizados.

## Testes de alto risco por questão

- **Q2:** 30 linhas reais; um exemplo de distância e previsão de KNN calculado à mão; conferir escolhas de `k` e tratamento de empate.
- **Q3:** uma regra/resposta do ELIZA explicada por cada sentença do diálogo. Não inventar regra original.
- **Q4:** contagem 5 categorias × 2 aplicações = 10 PEAS completos.
- **Q5:** resumo não excede seis páginas **renderizadas**; argumentos aderem ao vídeo real.
- **Q6:** verificação do domínio numérico e de funções de pertinência, regras disparadas e defuzzificação explicada.
- **Q7:** teste da recuperação por similaridade, correção por humano, retenção persistente e 15 casos/5 doenças.
- **Q8:** cada coluna da CPT soma 1; prior/posterior para pelo menos 3 cenários; checagem por enumeração independente para uma evidência.
- **Q9:** contagem > =10 classes e >=15 propriedades; executar reasoner; inferência ausente nos axiomas assertivos; consistência demonstrada.
- **Q10:** rodar algoritmos com ordem de vizinhos/tie-break fixos; UCS/A* e busca no estado aumentado D/F conferidos por referência.
- **Q11:** agenda 14–18h, reunião fixa 16–17h, sem sobreposição ou divisão indevida, e comparação correta com LLM.
- **Q12:** chamada real ao LLM, verificador rejeita horários sobrepostos mesmo quando proposta do LLM é inválida; saída explicável.
- **Q13:** checar o exemplo numérico/conceitual, termos e natureza original do vídeo e paper.
- **Q14:** ao menos uma inferência explicitamente *derivada*, não somente recuperada por consulta.
- **Q15:** mostrar assertivas, inferidas, consistência e ferramenta de raciocínio utilizada.

## Modelo para solicitação de revisão no ChatGPT

> Revise o commit `<SHA>` do repositório `<URL>` para as questões QXX e QYY. Compare os arquivos `questoes/qXX/README.md`, o enunciado e a matriz `docs/01-matriz-de-requisitos.md`. Não aceite alegações sem evidência. Verifique execução/testes, casos conhecidos, artefatos e riscos. Responda com APROVADA/PARCIAL/CORRECAO, achados priorizados e um prompt de correção pronto para o Codex.

**Importante:** o ChatGPT só verá o conteúdo efetivamente acessível do repositório/commit, e não atualizações que estejam apenas na máquina local.
