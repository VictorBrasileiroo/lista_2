# Questão 3: ELIZA, PARRY e AIML/ALICE

## 1. Introdução e funcionalidades do ELIZA

Joseph Weizenbaum desenvolveu ELIZA no MIT e apresentou o programa em 1966, em artigo publicado na Communications of the ACM. Sua contribuição foi mostrar como procedimentos de manipulação textual, combinados com regras editáveis, podiam sustentar uma conversa aparentemente significativa com um computador.

É necessário distinguir ELIZA de DOCTOR. ELIZA é o mecanismo geral que interpreta um roteiro de conversação. DOCTOR é o roteiro que o faz assumir uma postura semelhante à de um psicoterapeuta rogeriano, devolvendo perguntas e reformulações ao interlocutor. Esse papel favorecia respostas que retomavam as próprias palavras do usuário, sem exigir que o programa demonstrasse conhecimento sobre os assuntos mencionados (Weizenbaum, 1966, p. 36-37).

O mecanismo reconhece palavras-chave, decompõe a entrada segundo padrões e remonta uma resposta com fragmentos selecionados. Substituições como `I → YOU` e `MY → YOUR` ajustam a perspectiva dos trechos reutilizados. Diferentes respostas associadas ao mesmo padrão, uma memória restrita e respostas genéricas ajudam a prolongar a interação. Essas funcionalidades produzem aparência de compreensão, mas não constituem interpretação semântica ou compreensão clínica.

## 2. Regras e funcionamento do algoritmo

### 2.1. Da entrada à resposta

O processamento descrito no artigo pode ser organizado nas etapas abaixo. Trata-se de uma explicação do algoritmo, sem implementação.

| Etapa | Operação realizada |
| --- | --- |
| Recebimento e processamento | O programa recebe o texto e percorre suas palavras. Vírgulas e pontos delimitam trechos: se já encontrou uma palavra-chave, conserva o trecho relevante anterior ao delimitador; caso contrário, descarta o trecho inicial e continua a busca. |
| Identificação de palavras-chave | Consulta o dicionário do roteiro. Durante a varredura, também aplica substituições lexicais previstas, inclusive de pronomes. Nem toda palavra que admite substituição ativa regras de resposta. |
| Seleção por prioridade | Compara os valores de prioridade e coloca a palavra de maior valor no topo da estrutura de candidatas, chamada keystack. A ausência de valor explícito corresponde a prioridade zero. As candidatas restantes não são necessariamente mantidas em ordenação completa. |
| Decomposição | Testa, na ordem do roteiro, os padrões associados à palavra selecionada, até encontrar correspondência. O padrão divide o texto em componentes numerados. |
| Transformações e substituições | Trabalha sobre o texto já submetido às substituições da varredura. Algumas regras também preveem transformação preliminar, indicada por `PRE`, ou encaminhamento para outro conjunto de regras. |
| Seleção da remontagem | Escolhe a próxima alternativa associada ao padrão que correspondeu. As alternativas comuns são percorridas ciclicamente, evitando repetição imediata. |
| Construção da resposta | Combina texto fixo e componentes capturados, referidos por números na regra de remontagem. Exibe o resultado e devolve o turno ao usuário. |
| Ausência de correspondência adequada | `NEWKEY` permite tentar outra candidata. Esgotadas as candidatas, o programa pode recuperar uma transformação da memória, nas condições previstas, ou recorrer às respostas genéricas de `NONE`. |

Essa descrição acompanha Weizenbaum (1966, p. 37-41). O reconhecimento de padrões determina quais partes da entrada serão reutilizadas; ele não equivale a uma análise sintática e semântica completa.

### 2.2. Notação das regras e memória

Na decomposição, `0` corresponde a uma sequência de tamanho variável, inclusive vazia. Um inteiro positivo indica uma quantidade fixa de palavras. Na remontagem, um número identifica a posição de um componente capturado. Portanto, o número tem funções diferentes conforme o tipo de regra.

A notação `(* WANT NEED)` aceita uma das palavras enumeradas. Já `(/FAMILY)` identifica uma palavra previamente marcada como pertencente à classe de família. São agrupamentos definidos pelo autor do roteiro. Um encaminhamento como `(=WHAT)` reutiliza regras de outra entrada do dicionário, sem duplicá-las.

A memória de DOCTOR está vinculada a `MY`. Quando essa palavra é a candidata de maior prioridade, uma transformação específica de memória pode ser selecionada aleatoriamente e armazenada. Posteriormente, diante de uma entrada sem palavras-chave, uma condição de contagem permite recuperar a transformação mais antiga, retirando-a da fila. Isso difere da alternância cíclica das respostas comuns e não corresponde a armazenar uma representação dos fatos narrados (Weizenbaum, 1966, p. 41).

## 3. Diálogo demonstrativo e análise técnica

### 3.1. Critério da demonstração

O diálogo abaixo é uma simulação didática própria, obtida por aplicação manual de regras verificáveis do DOCTOR. Não é uma transcrição histórica nem o resultado de uma execução real de ELIZA. As regras foram conferidas na transcrição do apêndice de 1966 realizada por Anthony C. Hay, que documenta correções de duplicações tipográficas e de um parêntese do texto impresso.

Adota-se o estado inicial dos ciclos: a primeira correspondência de cada padrão usa sua primeira remontagem; a segunda usa a próxima. A memória começa vazia. Nenhuma entrada contém `MY`, de modo que esta sequência não a alimenta. As maiúsculas das respostas acompanham a apresentação histórica, e não acrescentam significado ao processamento.

| Interação | Usuário | ELIZA, por aplicação manual |
| --- | --- | --- |
| 1 | I need more time. | WHAT WOULD IT MEAN TO YOU IF YOU GOT MORE TIME |
| 2 | If I fail the exam. | DO YOU THINK ITS LIKELY THAT YOU FAIL THE EXAM |
| 3 | I need a computer. | DO COMPUTERS WORRY YOU |
| 4 | It works well. | I AM NOT SURE I UNDERSTAND YOU FULLY |
| 5 | It helps with the exam. | PLEASE GO ON |
| 6 | I need some rest. | WHY DO YOU WANT SOME REST |

### 3.2. Interação 1: decomposição e reutilização

A palavra-chave é `I`, de prioridade zero, cuja substituição produz `YOU NEED MORE TIME`. O padrão `(0 YOU (* WANT NEED) 0)` captura os componentes: 1 vazio, 2 `YOU`, 3 `NEED` e 4 `MORE TIME`. A primeira remontagem é `(WHAT WOULD IT MEAN TO YOU IF YOU GOT 4)`, que incorpora o componente 4.

A resposta retoma adequadamente o objeto da necessidade. Entretanto, a questão sobre obter mais tempo não resulta de compreender a situação: o mesmo procedimento funcionaria para qualquer complemento compatível com o padrão.

### 3.3. Interação 2: prioridade e transformação de pronome

`IF`, com prioridade 3, prevalece sobre `I`, de prioridade zero. A substituição `I → YOU` gera `IF YOU FAIL THE EXAM`. O padrão `(0 IF 0)` produz: 1 vazio, 2 `IF` e 3 `YOU FAIL THE EXAM`. A remontagem `(DO YOU THINK ITS LIKELY THAT 3)` acrescenta o componente 3 ao texto fixo. A forma `ITS`, sem apóstrofo, pertence à regra consultada.

A mudança de pronome faz a pergunta dirigir-se ao usuário. Contudo, o programa não avalia a possibilidade de reprovação nem relaciona esse receio à falta de tempo da interação anterior.

### 3.4. Interação 3: palavra-chave que desvia a conversa

`COMPUTER`, de prioridade 50, supera `I`. Embora a entrada também admita o padrão de necessidade utilizado na interação 1, esse padrão não é selecionado. A decomposição de `COMPUTER` é `(0)`, que captura o texto inteiro em um único componente. Sua primeira remontagem é `(DO COMPUTERS WORRY YOU)`, sem referência numérica a fragmentos.

A prioridade funciona conforme o roteiro, mas a resposta introduz uma preocupação que o usuário não declarou. Reconhecer o assunto “computador” não permite distinguir precisar de um equipamento de sentir receio dele. O ciclo do padrão da interação 1 também não avança neste turno.

### 3.5. Interação 4: resposta genérica e referência não resolvida

`IT WORKS WELL` não contém palavra-chave que acione uma resposta no roteiro consultado. Como a memória está vazia, aplica-se `NONE`. Seu padrão `(0)` aceita a entrada inteira; a primeira remontagem é `(I AM NOT SURE I UNDERSTAND YOU FULLY)`. Nenhum fragmento capturado aparece na saída.

A resposta permite continuar a interação, mas não resolve a referência de `It` ao computador. Para um leitor humano, há uma conexão com o turno anterior; o mecanismo apresentado não a recupera como uma relação entre entidades.

### 3.6. Interação 5: alternância sem avanço no conteúdo

`IT HELPS WITH THE EXAM` também não encontra palavra-chave acionadora. Reaplica-se a decomposição `(0)` de `NONE`. Como esse padrão já foi usado no turno anterior, a próxima remontagem é `(PLEASE GO ON)`, novamente sem inserir componentes da entrada.

A alternância evita repetir exatamente a mesma frase. Porém, o programa continua sem relacionar o equipamento, a prova e a necessidade de tempo. A variedade superficial das respostas não representa continuidade semântica.

### 3.7. Interação 6: retorno ao padrão anterior

`I`, de prioridade zero, volta a ser selecionada. Após `I → YOU`, o texto é `YOU NEED SOME REST`. O padrão `(0 YOU (* WANT NEED) 0)` captura: 1 vazio, 2 `YOU`, 3 `NEED` e 4 `SOME REST`. Como esse padrão correspondeu na interação 1, utiliza-se agora sua segunda remontagem: `(WHY DO YOU WANT 4)`.

A resposta preserva o complemento e mostra que o estado do ciclo pertence ao padrão, mesmo com outros turnos entre as duas utilizações. Ao mesmo tempo, troca uma necessidade por um desejo. Essa diferença de sentido é perdida porque `WANT` e `NEED` compartilham o mesmo conjunto de remontagens.

## 4. Limitações observadas

As falhas identificadas decorrem do mecanismo, e não de erros de execução. Uma palavra de alta prioridade pode desviar a resposta, como ocorre com `COMPUTER`. Um padrão pode neutralizar diferenças de sentido, como a distinção entre precisar e desejar. Respostas de `NONE` mantêm a troca de turnos, mas não resolvem referências ou estabelecem relações entre informações anteriores.

O programa conserva algum estado, como os ciclos das respostas e a fila de memória. Portanto, seria incorreto descrevê-lo como totalmente sem memória. Esse estado, porém, não basta para acompanhar a situação do usuário. A adequação de uma pergunta isolada pode levar o interlocutor a atribuir ao sistema uma compreensão que suas operações não demonstram.

## 5. Evolução histórica: PARRY e AIML/ALICE

### 5.1. PARRY e a modelagem de estados

PARRY foi desenvolvido em Stanford por Kenneth Mark Colby e colaboradores para simular comportamento verbal associado à paranoia, assumindo o papel de paciente. O marco de 1972 corresponde ao artigo de avaliação indicado no enunciado. A formulação do modelo já havia sido publicada em Artificial Paranoia, em 1971.

O modelo combina crenças persecutórias, temas sensíveis e variáveis de medo, raiva e desconfiança. Reconhecer uma ameaça pode alterar esses valores e favorecer respostas de confronto, esquiva ou retraimento. Assim, uma entrada pode repercutir em respostas posteriores por meio do estado interno, além da identificação de termos na mensagem atual (Colby, Weber e Hilf, 1971).

Os autores reconhecem limitações do processamento linguístico e restringem o modelo a um caso hipotético em situação de entrevista. O resumo do artigo de 1972 descreve avaliações de paranoia e tentativas de distinguir entrevistas com pacientes de entrevistas com a simulação. Isso não demonstra compreensão clínica geral. Nesta consulta, foram verificados o registro bibliográfico e os trechos do resumo de 1972 disponibilizados pela editora na indexação; o texto integral não ficou acessível. Por isso, não são apresentados percentuais ou conclusões experimentais detalhadas desse estudo.

### 5.2. AIML e ALICE

ALICE, desenvolvido por Richard S. Wallace a partir de 1995, é um chatbot. AIML, Artificial Intelligence Markup Language, é a linguagem baseada em XML utilizada para definir suas regras. Wallace (2009) apresenta a trajetória de ambos desde 1995. O documento AIML 1.0.1 consultado é um Working Draft de 8 de agosto de 2005, não um documento de 1995.

Em AIML, cada `category` contém um `pattern` de reconhecimento e um `template` de resposta. Curingas capturam trechos, recuperáveis por `star`. A categoria didática abaixo ilustra essa relação; não é apresentada como regra original de ALICE.

```xml
<category>
  <pattern>I STUDY *</pattern>
  <template>What interests you about <star/>?</template>
</category>
```

Para a entrada normalizada `I STUDY COMPUTING`, o curinga captura `COMPUTING`; a resposta seria `What interests you about COMPUTING?`. A categoria exemplifica reconhecimento textual, sem inferir conhecimento sobre computação.

AIML também permite organizar categorias por `topic`, condicionar correspondências à resposta anterior por `that` e reutilizar regras com `srai`, que reenvia texto ao mecanismo de correspondência. `set` e `get` armazenam e consultam valores associados à conversa; `condition` e `random` permitem selecionar alternativas. Esses recursos ampliam a organização e o controle das regras, mas sua presença não garante compreensão semântica (A.L.I.C.E. AI Foundation, 2005).

### 5.3. Comparação técnica

| Aspecto | ELIZA com DOCTOR, 1966 | PARRY, marco de avaliação em 1972 | ALICE e AIML, desde a década de 1990 |
| --- | --- | --- | --- |
| Papel conversacional | Postura semelhante à de um terapeuta rogeriano. | Paciente hipotético com comportamento paranoide. | Personagem conversacional para assuntos variados. |
| Mecanismo central | Palavras-chave, prioridades, decomposição e remontagem. | Reconhecimento de temas combinado com crenças e estados afetivos simulados. | Correspondência entre categorias e avaliação de templates. |
| Continuidade | Ciclos de respostas e memória textual restrita. | Estados internos influenciam a estratégia ao longo da entrevista. | Contexto e valores explicitamente organizados pelas regras. |
| Contribuição | Separação entre mecanismo geral e roteiro editável. | Modelagem comportamental além da transformação textual isolada. | Linguagem estruturada para organizar e reutilizar regras. |
| Limite | Pouca continuidade semântica. | Modelo restrito e dependente de reconhecimento linguístico limitado. | Dependência da cobertura e da qualidade das categorias. |

PARRY e ALICE são sistemas distintos, não atualizações diretas de ELIZA. Eles representam caminhos relacionados: simular estados e estratégias de um personagem ou ampliar a estrutura e a reutilização de regras conversacionais.

## 6. Referências

WEIZENBAUM, Joseph. ELIZA: A Computer Program for the Study of Natural Language Communication Between Man and Machine. Communications of the ACM, v. 9, n. 1, p. 36-45, 1966. [DOI](https://doi.org/10.1145/365153.365168). [Cópia indicada na Stanford](https://web.stanford.edu/class/cs124/p36-weizenabaum.pdf). [Cópia integral consultada na University at Buffalo](https://cse.buffalo.edu/~rapaport/572/S02/weizenbaum.eliza.1966.pdf).

HAY, Anthony C. Transcrição do roteiro do apêndice de Weizenbaum (1966). Dezembro de 2020. Repositório ELIZAGEN, organizado por Jeff Shrager. Fonte técnica auxiliar, com correções editoriais declaradas. [Texto e notas da transcrição](https://github.com/jeffshrager/elizagen.org/blob/master/1965_Weizenbaum_MAD-SLIP/1966_01_CACM_article_Eliza_script.txt).

COLBY, Kenneth Mark; WEBER, Sylvia; HILF, Franklin Dennis. Artificial Paranoia. Artificial Intelligence, v. 2, n. 1, p. 1-25, 1971. [DOI](https://doi.org/10.1016/0004-3702(71)90002-6). [Texto integral consultado na UMBC](https://courses.cs.umbc.edu/471/papers/colby_71.pdf).

COLBY, Kenneth Mark; HILF, Franklin Dennis; WEBER, Sylvia; KRAEMER, Helena C. Turing-like indistinguishability tests for the validation of a computer simulation of paranoid processes. Artificial Intelligence, v. 3, p. 199-221, 1972. [DOI](https://doi.org/10.1016/0004-3702(72)90049-5). [Registro da editora](https://www.sciencedirect.com/science/article/pii/0004370272900495). Consulta limitada ao registro e aos trechos indexados do resumo.

A.L.I.C.E. AI FOUNDATION. Artificial Intelligence Markup Language (AIML), Version 1.0.1. Working Draft, revisão 008, 8 ago. 2005. [Documento consultado no repositório da fundação](https://github.com/AIML-Foundation/AIML-1.0.1).

WALLACE, Richard S. The Anatomy of A.L.I.C.E. In: EPSTEIN, Robert; ROBERTS, Gary; BEBER, Grace (org.). Parsing the Turing Test. Dordrecht: Springer, 2009. p. 181-210. [DOI](https://doi.org/10.1007/978-1-4020-6710-5_13). Consulta ao resumo e aos dados bibliográficos da editora.
