# Questão 4: Categorias de agentes inteligentes e PEAS

## 1. Introdução

Um agente percebe seu ambiente por sensores e atua sobre ele por atuadores. No Capítulo 2 de Artificial Intelligence: A Modern Approach, Russell e Norvig discutem arquiteturas que diferem nas informações utilizadas para selecionar ações: percepção atual, estado interno, objetivos e utilidade. A aprendizagem permite aperfeiçoar o comportamento a partir da experiência. As cinco categorias solicitadas são apresentadas a seguir com aplicações ilustrativas, sem implementação ou teste.

A descrição PEAS especifica a tarefa por quatro componentes: Performance, medidas de desempenho; Environment, ambiente de atuação; Actuators, ações disponíveis; e Sensors, informações percebidas. A medida de desempenho avalia o comportamento do agente e não deve ser confundida com uma função de utilidade usada internamente para decidir.

As propriedades do ambiente dependem do cenário assumido, não da arquitetura escolhida. Observabilidade indica o acesso ao estado relevante; determinismo, a previsibilidade das transições; e a distinção episódico/sequencial, a dependência entre decisões. Um ambiente dinâmico pode mudar enquanto o agente decide. A classificação discreto/contínuo considera estados, percepções, ações e tempo. A distinção agente único/multiagente depende da presença de outros agentes relevantes para a tarefa. Finalmente, conhecido/desconhecido diz respeito ao conhecimento das regras de funcionamento, não à observação completa do estado.

## 2. Agentes reativos simples

Um agente reativo simples seleciona ações por regras condição-ação aplicadas à percepção atual. Não mantém uma representação histórica do ambiente, nem projeta consequências para escolher ações. Seu funcionamento é adequado quando a informação presente basta para aplicar a regra, embora isso não torne o ambiente necessariamente totalmente observável.

### 2.1. Termostato automático

Considera-se um aquecedor residencial controlado pela temperatura medida no instante atual. Uma regra liga o aquecedor quando a leitura está abaixo do valor de referência e o desliga nos demais casos. Não há aprendizagem, previsão térmica ou memória para implementar histerese.

| Componente PEAS | Descrição |
| --- | --- |
| Performance | Desvio da temperatura em relação à referência, consumo elétrico e quantidade de acionamentos. |
| Environment | Cômodo aquecido, sujeito à temperatura externa, à abertura de portas e a perdas de calor. |
| Actuators | Ligar ou desligar o aquecedor. |
| Sensors | Temperatura local atual e valor de referência configurado. |

| Observabilidade | Transições | Dependência | Mudança | Representação | Agentes | Conhecimento |
| --- | --- | --- | --- | --- | --- | --- |
| Parcial | Estocásticas | Sequencial | Dinâmico | Misto | Único | Parcialmente conhecido |

A leitura local não revela toda a distribuição térmica nem perturbações futuras. As ações influenciam temperaturas posteriores, enquanto trocas de calor continuam durante a decisão. Temperatura e tempo são contínuos, mas o comando é binário. O efeito geral do aquecimento é conhecido; as perturbações são incertas. Os moradores são tratados como fontes externas de perturbação, sem modelagem de decisões de outros agentes.

### 2.2. Sistema de iluminação com sensor de presença

Considera-se um corredor com sensor que fornece um sinal atual de presença, sem temporizador ou memória no controlador. A regra acende a lâmpada quando há presença detectada e a apaga quando não há. O cenário admite falhas de detecção e movimentos de pessoas fora do alcance do sensor.

| Componente PEAS | Descrição |
| --- | --- |
| Performance | Tempo de iluminação durante a ocupação, tempo de luz acesa sem ocupantes e consumo elétrico. |
| Environment | Corredor, luminária e circulação de pessoas na área monitorada. |
| Actuators | Acender ou apagar a luminária. |
| Sensors | Sinal binário atual de presença. |

| Observabilidade | Transições | Dependência | Mudança | Representação | Agentes | Conhecimento |
| --- | --- | --- | --- | --- | --- | --- |
| Parcial | Estocásticas | Sequencial | Dinâmico | Misto | Único | Parcialmente conhecido |

O sensor não informa perfeitamente a ocupação real. Pessoas podem entrar ou sair durante a decisão, e a duração de cada acionamento afeta o consumo e a iluminação ao longo do tempo. Sinais e comandos são discretos, mas tempo e deslocamentos são contínuos. A regra elétrica de acionamento é conhecida, enquanto ocupação e detecções futuras são incertas. Considera-se apenas o controlador como agente da tarefa, sem interação estratégica com os ocupantes.

## 3. Agentes baseados em modelo, com estado

Esses agentes atualizam um estado interno a partir das percepções, das ações anteriores e de um modelo de como o ambiente evolui. Assim, representam aspectos que não estão diretamente visíveis no momento. Diferem dos reativos simples pelo uso dessa memória estruturada; manter um modelo, por si só, não exige planejar por objetivos ou comparar utilidades.

### 3.1. Robô aspirador com mapa e registro das áreas visitadas

Considera-se um apartamento vazio, com obstáculos imóveis, representado por uma grade. Para isolar o papel do estado interno, movimentos e sensores são idealizados como exatos. O robô constrói um mapa, registra células já limpas e aplica regras fixas para seguir para células adjacentes ainda não visitadas ou retornar por passagens registradas.

| Componente PEAS | Descrição |
| --- | --- |
| Performance | Proporção de células limpas, número de revisitas desnecessárias e energia consumida. |
| Environment | Cômodos, passagens, obstáculos fixos e sujeira inicialmente distribuída no piso. |
| Actuators | Avançar uma célula, girar e acionar a aspiração. |
| Sensors | Obstáculos próximos, sujeira na célula atual e deslocamento realizado. |

| Observabilidade | Transições | Dependência | Mudança | Representação | Agentes | Conhecimento |
| --- | --- | --- | --- | --- | --- | --- |
| Parcial | Determinísticas | Sequencial | Estático | Discreto | Único | Conhecido |

Os sensores locais não mostram todo o apartamento, o que justifica o mapa interno. Limpar ou deslocar-se altera as condições das próximas decisões. O ambiente não muda por conta própria durante a deliberação, e movimentos e limpeza têm efeitos exatos no cenário idealizado. A grade e os ciclos de ação são discretos. As regras de transição são conhecidas, embora a disposição inicial dos obstáculos precise ser descoberta.

### 3.2. Semáforo inteligente com estado do trânsito

Considera-se um cruzamento em que detectores cobrem apenas parte das aproximações. O controlador guarda a fase atual, o tempo decorrido e estimativas de filas atualizadas pelas contagens de veículos. Regras fixas permitem prolongar uma fase quando a fila estimada supera um limiar, respeitando limites de duração e intervalos de segurança.

| Componente PEAS | Descrição |
| --- | --- |
| Performance | Tempo médio de espera, extensão das filas, vazão e ausência de fases conflitantes. |
| Environment | Cruzamento, faixas de aproximação e motoristas que escolhem trajetórias e velocidades. |
| Actuators | Manter a fase atual ou iniciar uma troca com amarelo e intervalo de segurança. |
| Sensors | Contagens de passagem, ocupação nos detectores e relógio do controlador. |

| Observabilidade | Transições | Dependência | Mudança | Representação | Agentes | Conhecimento |
| --- | --- | --- | --- | --- | --- | --- |
| Parcial | Estocásticas | Sequencial | Dinâmico | Misto | Multiagente | Parcialmente conhecido |

As filas fora da cobertura precisam ser estimadas pelo histórico. Cada fase afeta filas futuras, enquanto veículos continuam chegando durante a decisão. Fases e contagens são discretas; tempo, posições e velocidades são contínuos. Motoristas são outros agentes cujas decisões afetam o controle. As regras do semáforo são conhecidas, mas o comportamento do tráfego é apenas parcialmente modelado. As medidas de desempenho avaliam o controlador, sem que ele necessariamente calcule uma utilidade.

## 4. Agentes baseados em objetivo

Agentes baseados em objetivo selecionam ações considerando estados desejados e as consequências das alternativas. Podem realizar busca ou planejamento para encontrar uma sequência que alcance o objetivo. Diferem dos agentes apenas baseados em modelo porque usam explicitamente um resultado desejado para orientar a escolha, sem necessariamente ordenar por preferência todas as soluções válidas.

### 4.1. Planejador de rotas

Considera-se o planejamento offline em um mapa fixo, sem informações de trânsito ou mudanças de vias. O objetivo é produzir uma sequência de trechos permitidos que conecte uma origem a um destino. Qualquer caminho válido satisfaz a tarefa; não se exige escolher o mais rápido ou o mais confortável.

| Componente PEAS | Descrição |
| --- | --- |
| Performance | Proporção de consultas com rota válida, respeito às restrições viárias e tempo de cálculo. |
| Environment | Grafo fixo de cruzamentos e vias, com sentidos e proibições conhecidos. |
| Actuators | Apresentar uma sequência de vias ou informar ausência de caminho. |
| Sensors | Origem, destino e base cartográfica com conexões e restrições. |

| Observabilidade | Transições | Dependência | Mudança | Representação | Agentes | Conhecimento |
| --- | --- | --- | --- | --- | --- | --- |
| Total | Determinísticas | Sequencial | Estático | Discreto | Único | Conhecido |

Todos os dados relevantes do grafo estão disponíveis, e percorrer uma aresta leva ao vértice previsto. A escolha de um trecho condiciona as próximas possibilidades da rota, tornando o problema sequencial. O mapa não muda durante a busca, e a representação usa vértices e arestas discretos. Não há outros agentes no problema offline. O destino orienta a expansão de caminhos até que um deles o alcance.

### 4.2. Agendador de reuniões

Considera-se uma cópia fixa e completa das disponibilidades de participantes e salas para a próxima semana, dividida em intervalos de 30 minutos. O objetivo é atribuir horários a um conjunto de reuniões, respeitando duração, participantes obrigatórios e ausência de sobreposições. Não há negociação ou atualização das agendas durante o cálculo.

| Componente PEAS | Descrição |
| --- | --- |
| Performance | Quantidade de reuniões alocadas conforme os requisitos, ausência de conflitos e tempo para encontrar a agenda. |
| Environment | Disponibilidades registradas, salas, intervalos semanais e requisitos das reuniões. |
| Actuators | Propor horários e salas para as reuniões ou indicar inviabilidade. |
| Sensors | Agendas fornecidas, duração, participantes obrigatórios e capacidade das salas. |

| Observabilidade | Transições | Dependência | Mudança | Representação | Agentes | Conhecimento |
| --- | --- | --- | --- | --- | --- | --- |
| Total | Determinísticas | Sequencial | Estático | Discreto | Único | Conhecido |

Os dados e as restrições estão integralmente disponíveis e permanecem fixos. Alocar uma reunião retira opções das seguintes, exigindo considerar a sequência de atribuições. Os horários são discretizados em blocos, e os participantes aparecem como restrições já informadas, não como agentes negociadores. O objetivo orienta a busca e o eventual retrocesso até obter uma atribuição que satisfaça as exigências; não há preferência entre agendas igualmente válidas.

## 5. Agentes baseados em utilidade

Agentes baseados em utilidade comparam alternativas por uma função que expressa a preferência entre resultados. Quando há incerteza, podem escolher a ação de maior utilidade esperada. Diferem dos agentes baseados apenas em objetivo porque distinguem a qualidade de soluções que alcançam o mesmo resultado, conciliando critérios conflitantes.

### 5.1. Robô de entregas que considera tempo, custo e risco

Considera-se um robô que entrega encomendas em calçadas compartilhadas com pedestres e outros robôs. Ele estima duração, gasto de bateria e risco dos trajetos. Sua função de utilidade penaliza atrasos, custos e riscos com pesos definidos para a tarefa, mantendo restrições obrigatórias de segurança.

| Componente PEAS | Descrição |
| --- | --- |
| Performance | Entregas concluídas no prazo, custo por entrega, consumo de bateria e número de incidentes. |
| Environment | Calçadas, travessias, pontos de entrega, pedestres, outros robôs e condições meteorológicas. |
| Actuators | Mover-se, reduzir velocidade, parar, mudar de trajeto e liberar a encomenda no destino. |
| Sensors | Câmeras, lidar, localização, nível de bateria e dados do pedido. |

| Observabilidade | Transições | Dependência | Mudança | Representação | Agentes | Conhecimento |
| --- | --- | --- | --- | --- | --- | --- |
| Parcial | Estocásticas | Sequencial | Dinâmico | Misto | Multiagente | Parcialmente conhecido |

Oclusões e intenções desconhecidas dos pedestres limitam a observação. Movimentos afetam posição e bateria futuras, e outros agentes continuam se deslocando durante o cálculo. Destinos e escolhas de trajeto são discretos; velocidade, posição e tempo são contínuos. O robô conhece seu modelo de movimento, mas estima as reações alheias e os efeitos do clima.

Por exemplo, um trajeto de 12 minutos pode ter menor gasto energético, mas mais travessias movimentadas que uma alternativa de 18 minutos. Se ambos respeitam os limites de segurança, a utilidade permite escolher a segunda opção quando a redução do risco compensa o tempo e o custo adicionais. O objetivo de entregar, isoladamente, não expressa essa preferência.

### 5.2. Gerenciador inteligente de energia residencial

Considera-se uma residência com painéis solares, bateria, climatização e aparelhos cujo funcionamento pode ser adiado. O agente conhece tarifas anunciadas, mas estima geração solar, consumo e ocupação futura. Uma função de utilidade combina economia, conforto e desgaste da bateria, sujeita a limites técnicos e prazos de uso dos aparelhos.

| Componente PEAS | Descrição |
| --- | --- |
| Performance | Custo da eletricidade, tempo fora da faixa de conforto, cumprimento dos prazos e degradação da bateria. |
| Environment | Instalação elétrica residencial, rede de distribuição, clima e demanda dos moradores. |
| Actuators | Programar aparelhos, ajustar a climatização e comandar carga ou descarga da bateria. |
| Sensors | Medidores de consumo e geração, carga da bateria, temperatura interna, tarifas e preferências informadas. |

| Observabilidade | Transições | Dependência | Mudança | Representação | Agentes | Conhecimento |
| --- | --- | --- | --- | --- | --- | --- |
| Parcial | Estocásticas | Sequencial | Dinâmico | Misto | Único | Parcialmente conhecido |

Consumo futuro e condições térmicas completas não são diretamente observáveis. Decisões presentes alteram a energia armazenada e o conforto posterior, enquanto clima e demanda mudam durante a operação. Ligar aparelhos é discreto; potência, temperatura e carga são contínuas. Assume-se um único controlador, com tarifas externas e moradores representados por demandas e preferências, sem negociação entre agentes. Modelos dos equipamentos são conhecidos, mas as perturbações são incertas.

Por exemplo, adiar uma lavagem para um horário de menor tarifa reduz o custo, mas pode descumprir a preferência por roupas prontas cedo. Da mesma forma, reduzir a climatização economiza energia e diminui o conforto. A utilidade pondera essas consequências para escolher entre alternativas tecnicamente viáveis, em vez de considerar apenas a meta de fornecer energia.

## 6. Agentes adaptativos, ou agentes que aprendem

Um agente adaptativo modifica seu comportamento a partir da experiência por mecanismos de aprendizagem. Na arquitetura discutida por Russell e Norvig, o elemento de aprendizagem melhora o elemento de desempenho, com avaliação fornecida por um crítico e possível exploração orientada por um gerador de problemas. A diferença central em relação a regras fixas é a atualização efetiva do comportamento com base nos resultados observados.

### 6.1. Filtro de spam que aprende com correções dos usuários

Considera-se um filtro que calcula a probabilidade de uma mensagem ser spam e a encaminha para a caixa de entrada ou quarentena. Quando o usuário corrige uma classificação, o sistema usa esse exemplo rotulado para atualizar os parâmetros do classificador. Remetentes maliciosos podem modificar suas mensagens para tentar escapar da filtragem.

| Componente PEAS | Descrição |
| --- | --- |
| Performance | Precisão na detecção de spam, proporção de mensagens legítimas bloqueadas e tempo de classificação. |
| Environment | Fluxo de e-mails, caixa postal, usuário que fornece correções e remetentes, inclusive adversários. |
| Actuators | Encaminhar mensagens à entrada ou quarentena e reclassificá-las após correções. |
| Sensors | Texto, cabeçalhos, endereço do remetente, características de links e marcações do usuário. |

| Observabilidade | Transições | Dependência | Mudança | Representação | Agentes | Conhecimento |
| --- | --- | --- | --- | --- | --- | --- |
| Parcial | Estocásticas | Sequencial | Dinâmico | Misto | Multiagente | Desconhecido |

A intenção real do remetente não é diretamente observável, e a distribuição das mensagens muda com o tempo. O cenário inclui a aprendizagem contínua: uma correção altera classificações futuras, por isso é sequencial, embora a classificação isolada de mensagens com modelo congelado possa ser tratada como episódica. Textos, rótulos e ações são discretos, enquanto escores de probabilidade são contínuos. Remetentes adversários são outros agentes. A relação entre conteúdo, legitimidade e estratégias futuras precisa ser aprendida.

### 6.2. Sistema de recomendação de filmes que aprende preferências

Considera-se uma plataforma que atualiza um modelo de preferências a partir de avaliações, escolhas, abandonos e tempo assistido. O sistema usa essas experiências para alterar a ordem dos filmes recomendados. O catálogo permanece fixo durante cada sessão, mas interesses e interações podem mudar.

| Componente PEAS | Descrição |
| --- | --- |
| Performance | Satisfação declarada, proporção de recomendações bem avaliadas, diversidade relevante e redução de abandonos precoces. |
| Environment | Catálogo de filmes, interface da plataforma, sessões e usuário que escolhe o que assistir. |
| Actuators | Selecionar e ordenar filmes exibidos e solicitar avaliações opcionais. |
| Sensors | Avaliações, cliques, histórico de exibição, tempo assistido e interrupções. |

| Observabilidade | Transições | Dependência | Mudança | Representação | Agentes | Conhecimento |
| --- | --- | --- | --- | --- | --- | --- |
| Parcial | Estocásticas | Sequencial | Dinâmico | Misto | Multiagente | Desconhecido |

Preferências e contexto do usuário são apenas inferidos por sinais incompletos. Recomendações afetam o que será visto e quais dados alimentarão o modelo, ligando decisões sucessivas. O usuário toma decisões próprias e pode mudar de interesse enquanto o sistema opera. Filmes e posições da lista são discretos; tempo assistido e escores de preferência são contínuos. O efeito de cada recomendação sobre satisfação e resposta do usuário não é previamente conhecido, sendo estimado pela aprendizagem.

## 7. Comparação final

O reativo simples usa a percepção atual; o baseado em modelo acrescenta uma representação interna; o baseado em objetivo avalia se as ações conduzem ao resultado desejado; e o baseado em utilidade compara a preferência entre resultados. O adaptativo acrescenta a capacidade de melhorar com a experiência. Essas categorias não são necessariamente excludentes: um recomendador que aprende pode ordenar filmes por utilidade estimada, e um robô pode combinar modelo, objetivo, utilidade e aprendizagem. O enquadramento dos exemplos destaca o mecanismo decisório assumido em cada cenário.

## 8. Referências

Russell, Stuart; Norvig, Peter. Artificial Intelligence: A Modern Approach. 4ª edição. Pearson, 2021. Capítulo 2: Intelligent Agents.

Página oficial da obra: <https://aima.cs.berkeley.edu/>.
