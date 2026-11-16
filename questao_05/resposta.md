# Questão 5: Inferência em LLMs: do prompt à geração da resposta

## 1. Introdução

A inferência em modelos de linguagem de grande porte, ou LLMs, é o processo de executar um modelo já treinado para produzir uma saída a partir de uma nova entrada. Em um assistente de conversação, ela ocorre quando o usuário envia uma mensagem e o sistema utiliza os parâmetros do modelo para gerar uma resposta. Embora a interação pareça simples, seu funcionamento envolve preparação dos dados, gerenciamento de recursos computacionais e geração sequencial de tokens.

A principal diferença entre treinamento e inferência está na finalidade dessas etapas. No treinamento, os parâmetros do modelo são ajustados a partir de dados. Na inferência, esses parâmetros são utilizados para calcular a saída, sem que cada interação implique uma atualização dos pesos. Isso não significa que o treinamento aconteça uma única vez durante toda a vida do modelo: ele pode passar por novas etapas de treinamento e ajustes antes de outras versões serem disponibilizadas.

Essa distinção também ajuda a entender os custos de operação. O treinamento pode exigir muitos recursos, mas a inferência se repete a cada requisição. Em aplicações com grande volume de uso, seu custo acumulado pode superar o de treinamento. Essa relação depende da escala, do modelo e da infraestrutura utilizada. Por isso, atender às requisições com eficiência é parte central da disponibilização de LLMs em chatbots e assistentes de código.


## 2. Motores de inferência

O motor de inferência é o software responsável por executar o modelo e organizar o uso dos recursos disponíveis. Entre os exemplos apresentados no material estão vLLM, Ollama e llama.cpp. Suas capacidades variam, mas envolvem tarefas como carregar o modelo, administrar memória e coordenar o processamento das entradas.

Em um serviço que atende vários usuários, esse gerenciamento envolve decidir quando cada requisição será executada e quais podem compartilhar uma etapa de processamento. A memória disponível, o tamanho dos prompts e a quantidade de pedidos em andamento influenciam essas decisões. Assim, o desempenho depende tanto do modelo quanto da organização de sua execução.

A integração com a aplicação ocorre por uma interface de programação, ou API. Ela define como enviar entradas e receber resultados sem exigir que o aplicativo controle diretamente as operações na GPU. Algumas ferramentas oferecem interfaces compatíveis com a API da OpenAI, o que pode facilitar a troca de modelos ou servidores. Essa compatibilidade não é universal nem garante equivalência entre todos os recursos: cada implementação pode apresentar diferenças de suporte e comportamento.

## 3. Processamento de uma requisição

Quando o usuário envia um prompt, a aplicação encaminha uma requisição ao serviço de inferência. Antes da execução pelo modelo, o sistema precisa preparar a entrada, verificar a autorização de acesso e direcionar o trabalho aos recursos disponíveis. A ordem exata desses procedimentos depende da arquitetura do serviço, e a tokenização pode ocorrer no próprio servidor.

A tokenização divide o texto em unidades chamadas tokens, que podem corresponder a palavras, partes de palavras ou sinais de pontuação. Cada token recebe um identificador numérico utilizado na entrada do modelo. Portanto, a quantidade de palavras não corresponde necessariamente à quantidade de tokens. A segmentação depende do tokenizador e de seu vocabulário, além das características do texto. Um vocabulário maior não garante, isoladamente, uma redução no número de tokens em qualquer entrada.

Essa representação tem consequências práticas. A quantidade de tokens influencia o trabalho necessário para processar o prompt e, nos serviços cobrados por token, o custo de uso. O histórico de uma conversa também pode fazer parte da entrada, aumentando o contexto que precisa ser processado.

A autenticação verifica se a requisição possui credenciais válidas, como uma chave de API. Depois, o roteamento direciona o pedido a uma instância capaz de atendê-lo. Essa escolha pode considerar disponibilidade, modelo solicitado, extensão da entrada e políticas do serviço. Não há uma regra única segundo a qual todo sistema selecione o hardware com base no conteúdo do prompt.

Após o encaminhamento, o agendador organiza a execução. Uma técnica importante é o batching, que reúne múltiplas requisições em um lote para aproveitar melhor o processamento paralelo. Como as respostas têm comprimentos diferentes, um lote fixo pode perder eficiência quando algumas requisições terminam antes das demais. No continuous batching, a composição do lote pode ser atualizada durante a execução, permitindo incorporar novos pedidos conforme surgem recursos disponíveis. Isso tende a reduzir a ociosidade e aumentar a vazão, embora não garanta utilização máxima da GPU em todas as situações.

## 4. Prefill, KV cache e decode

O processamento de uma requisição pode ser compreendido em duas fases principais: prefill e decode. A primeira processa o contexto de entrada; a segunda produz sua continuação. Começar uma resposta e continuar sua geração apresentam, portanto, exigências diferentes para o hardware.

### 4.1 Processamento do prompt no prefill

No prefill, o modelo processa os tokens do prompt. Como esses tokens já estão disponíveis, muitas operações sobre suas posições podem ser realizadas em paralelo, respeitando as dependências do mecanismo de atenção. Essa característica permite realizar operações matriciais amplas, aproveitando o paralelismo da GPU.

Durante esse processamento, o modelo calcula representações utilizadas pelas camadas de atenção e constrói o KV cache. Ao final do prefill, também estão disponíveis os resultados necessários para selecionar o primeiro token de saída. Por isso, essa fase participa diretamente do tempo que o usuário espera até a resposta começar a aparecer.

O prefill costuma ser mais intensivo em computação, especialmente quando há muitos tokens de entrada. Seu desempenho está associado à capacidade de realizar os cálculos exigidos pelo modelo, mas o tamanho do lote, a extensão do contexto e as características do hardware também afetam o gargalo observado.

### 4.2 Finalidade do KV cache

O KV cache armazena tensores de chaves e valores calculados nas camadas de atenção para os tokens já processados. Essas estruturas permitem que o modelo utilize informações das posições anteriores ao calcular a continuação da sequência. Trata-se de um estado numérico da execução, e não de um armazenamento textual da compreensão completa da conversa.

Seu papel é evitar o recálculo de chaves e valores dos tokens anteriores a cada novo passo. Depois de processar uma pergunta inteira, por exemplo, o modelo reutiliza essas estruturas enquanto gera a resposta. Recalcular todo o prefixo a cada passo repetiria trabalho e aumentaria o custo de geração, sem que isso implique crescimento necessariamente exponencial do tempo.

A economia de cálculo exige espaço de memória. Conforme a sequência cresce, o cache também aumenta, pois precisa incorporar informações dos novos tokens. Ao atender várias requisições simultaneamente, o motor administra os caches correspondentes a cada uma. Portanto, o KV cache contribui para acelerar a geração, mas também influencia a quantidade de requisições e o tamanho dos contextos que cabem na memória disponível.

### 4.3 Geração autoregressiva no decode

Depois do processamento inicial, a resposta é construída de forma autoregressiva: cada token gerado passa a compor o contexto utilizado para produzir o próximo. O modelo calcula uma distribuição de probabilidades sobre o vocabulário, e uma estratégia de seleção determina o token que será acrescentado à sequência. A saída, portanto, não é necessariamente formada pela escolha do token de maior probabilidade em todos os passos.

Após a seleção do primeiro token, os passos seguintes processam o token recém-incorporado, consultam as chaves e os valores anteriores e atualizam o KV cache. Esse ciclo continua até uma condição de parada, como a emissão de um token de término ou o alcance do limite de geração. Os tokens produzidos são convertidos novamente em texto e podem ser enviados gradualmente ao usuário.

A dependência entre os passos limita o paralelismo dentro de uma mesma resposta. Ainda assim, o motor pode executar passos de diferentes requisições em conjunto, aproveitando melhor o hardware durante a geração.

O decode frequentemente encontra um gargalo na largura de banda da memória. Cada passo exige acessar pesos do modelo e dados do cache, enquanto há menos tokens novos para processar por requisição do que no prefill. Nessa situação, a rapidez de movimentação dos dados pode limitar o desempenho, e aumentar apenas a capacidade de cálculo pode produzir ganhos limitados. O gargalo efetivo depende das condições de execução.

## 5. Métricas de desempenho

O tempo para o primeiro token, ou TTFT, mede o intervalo entre o envio da requisição e o recebimento do primeiro token de resposta. Ele representa a espera inicial percebida pelo usuário. O prefill contribui para esse intervalo, mas a métrica também pode incluir comunicação, preparação da entrada, roteamento e espera na fila. Assim, um TTFT elevado não permite atribuir o problema exclusivamente ao processamento do prompt.

A latência entre tokens, ou ITL, corresponde ao intervalo entre tokens consecutivos. Ela ajuda a avaliar a velocidade com que a resposta continua aparecendo depois de iniciada. Quando medida no recebimento pelo cliente, também pode refletir efeitos da transmissão e do agrupamento de dados para envio. Um serviço pode apresentar TTFT baixo e geração posterior lenta, ou uma espera inicial maior seguida de entrega rápida dos demais tokens.

Para uma saída com N tokens, considerando a ITL média entre tokens consecutivos, uma aproximação do tempo até o recebimento do último token é:

Tempo total ≈ TTFT + (N − 1) × ITL média.

O fator N − 1 aparece porque o primeiro token já está incluído no TTFT. A expressão ajuda a relacionar a espera inicial ao comprimento da resposta, embora uma média não descreva todas as variações que podem ocorrer durante a entrega.

Também é necessário distinguir latência de throughput, ou vazão. A latência descreve o tempo de uma requisição ou de uma etapa da resposta. O throughput expressa a quantidade de trabalho realizada por unidade de tempo, como tokens gerados por segundo pelo serviço. Ele não corresponde simplesmente ao número de usuários simultâneos. Um lote maior pode elevar a produção total de tokens sem reduzir o tempo de cada pedido. Por isso, avaliar a infraestrutura exige observar tanto a capacidade de atendimento quanto os tempos percebidos por quem a utiliza.

## 6. Considerações finais

A geração de respostas depende da coordenação entre representação da entrada, agendamento e execução do modelo. O prefill aproveita a disponibilidade do prompt para processar seu contexto, enquanto o KV cache permite reutilizar parte desse trabalho durante o decode. A geração sequencial, por sua vez, torna o acesso à memória e a organização de requisições simultâneas decisivos para o desempenho.

Essa relação mostra por que melhorar um serviço de inferência exige identificar onde o tempo e os recursos estão sendo consumidos. Uma espera inicial alta pode envolver filas ou processamento da entrada; uma resposta que avança lentamente pode revelar limitações nos passos de geração. TTFT, ITL e throughput ajudam a diferenciar essas situações e a avaliar se o uso da infraestrutura atende às necessidades da aplicação.

## 7. Referências

IBM TECHNOLOGY. What Is LLM Inference? How AI Models Generate Responses. YouTube. Disponível em: https://www.youtube.com/watch?v=615-yWyS1n0.