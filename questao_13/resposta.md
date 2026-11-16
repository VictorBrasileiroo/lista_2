# Questão 13: Ensaio sobre a arquitetura Transformer

## 1. Introdução

No processamento de linguagem natural, interpretar uma sequência exige relacionar seus elementos. O significado de uma palavra depende do contexto, e uma relação entre sujeito e verbo pode envolver posições distantes. Portanto, representar palavras isoladamente é insuficiente para tarefas como tradução, classificação e geração de texto.

Redes neurais recorrentes, incluindo LSTMs, processam sequências atualizando um estado a partir do estado anterior e da entrada atual. Essa dependência limita a paralelização entre posições de uma mesma sequência. Além disso, informações de posições distantes precisam atravessar sucessivas etapas, o que pode dificultar a aprendizagem dessas relações, mesmo com mecanismos que atenuam o problema.

Proposto por [Vaswani et al. (2017)](https://arxiv.org/abs/1706.03762), o Transformer utiliza atenção como mecanismo central para relacionar posições, dispensando a recorrência. A atenção já aparecia em modelos anteriores; a contribuição foi organizar a arquitetura em torno dela. Isso amplia a paralelização e encurta o caminho de comunicação entre tokens, sem eliminar todos os desafios do processamento de sequências.

## 2. Representação da entrada

O processamento começa pela tokenização, que divide o texto em unidades chamadas tokens. Dependendo do tokenizador, um token pode corresponder a uma palavra, parte dela ou um sinal de pontuação. Cada unidade recebe um identificador em um vocabulário, o conjunto de tokens reconhecidos pelo modelo. Neste ensaio, a sequência “Gato dorme” será simplificada para dois tokens, “gato” e “dorme”, desconsiderando a inicial maiúscula. Um tokenizador real não precisa produzir essa mesma divisão.

Os identificadores permitem consultar uma tabela de embeddings, representações vetoriais aprendidas durante o treinamento. Cada token passa a ser um vetor de números reais, cujas coordenadas participam dos cálculos seguintes. Essas coordenadas não precisam corresponder a propriedades linguísticas interpretáveis individualmente. O embedding inicial identifica o token; os blocos posteriores modificam sua representação conforme o contexto.

A atenção sem informação posicional não distingue, por si só, a ordem dos elementos. As frases “O gato perseguiu o cão” e “O cão perseguiu o gato” contêm as mesmas palavras, mas descrevem situações diferentes. No Transformer original, vetores de codificação posicional, ou *positional encoding*, calculados com senos e cossenos de diferentes frequências, são somados aos embeddings. Assim, a entrada combina identidade e posição. Variantes posteriores podem empregar embeddings posicionais aprendidos ou outras estratégias para representar posições e distâncias; a codificação senoidal não é uma exigência de todo Transformer.

## 3. Mecanismo de self-attention

A autoatenção, ou *self-attention*, transforma a representação de cada posição combinando informações da própria sequência. Para isso, produz três projeções: *query* (consulta), que participa da busca por informações relevantes; *key* (chave), usada na comparação com a consulta; e *value* (valor), que contém o conteúdo a ser combinado. São papéis matemáticos, aprendidos conforme a tarefa, sem significados linguísticos fixos.

Se a matriz $X$ reúne os vetores de entrada em suas linhas, essas projeções são $Q=XW_Q$, $K=XW_K$ e $V=XW_V$. As matrizes $W_Q$, $W_K$ e $W_V$ são parâmetros aprendidos. Portanto, queries, keys e values não são fornecidos manualmente em um modelo treinado. Na self-attention, os três conjuntos derivam da mesma sequência, embora resultem de projeções diferentes. A exposição de [Alammar (2018)](https://jalammar.github.io/illustrated-transformer/) ajuda a acompanhar essa passagem dos vetores de entrada às representações contextualizadas.

A atenção por produto escalar escalonado é expressa por:

$$
\operatorname{Attention}(Q,K,V)
=\operatorname{softmax}\left(\frac{QK^{\mathsf T}}{\sqrt{d_k}}\right)V.
$$

Primeiro, $QK^{\mathsf T}$ calcula os produtos escalares entre cada query e todas as keys. A entrada da linha $i$ e coluna $j$ mede a compatibilidade entre a consulta da posição $i$ e a chave da posição $j$. A divisão por $\sqrt{d_k}$, sendo $d_k$ a dimensão das queries e keys, controla a escala desses resultados: dimensões maiores podem produzir magnitudes elevadas e levar a softmax a regiões com gradientes muito pequenos.

Em seguida, a softmax é aplicada separadamente em cada linha. Ela exponencia cada pontuação e divide pelo total das exponenciais daquela linha, produzindo pesos positivos cuja soma é um. Esses pesos determinam a participação de cada value na combinação. A multiplicação final por $V$ calcula as somas ponderadas e produz um vetor por posição. Assim, a representação de um token passa a incorporar conteúdo de outros tokens, inclusive distantes, conforme os pesos calculados para aquela consulta.

## 4. Exemplo de funcionamento

Considere a atenção para “dorme” na sequência “Gato dorme”. Para tornar o cálculo reproduzível, adotam-se os seguintes vetores fictícios, escolhidos apenas para fins didáticos:

$$
\begin{aligned}
q_{\text{dorme}}&=(1,0),\\
k_{\text{gato}}&=(1,0), & k_{\text{dorme}}&=(0,1),\\
v_{\text{gato}}&=(2,0), & v_{\text{dorme}}&=(0,2),\\
d_k&=2.
\end{aligned}
$$

Os produtos escalares da query de “dorme” com as duas keys são:

$$
q\cdot k_{\text{gato}}=1\times1+0\times0=1,
\qquad
q\cdot k_{\text{dorme}}=1\times0+0\times1=0.
$$

Dividindo por $\sqrt{2}$, obtêm-se as pontuações $1/\sqrt{2}\approx0{,}7071$ e $0/\sqrt{2}=0$. A softmax transforma essas pontuações nos pesos:

$$
\alpha_{\text{gato}}=
\frac{e^{1/\sqrt{2}}}{e^{1/\sqrt{2}}+e^0}
\approx0{,}6698,
\qquad
\alpha_{\text{dorme}}=
\frac{e^0}{e^{1/\sqrt{2}}+e^0}
\approx0{,}3302.
$$

A saída da atenção nessa posição é a soma ponderada dos values:

$$
z_{\text{dorme}}
=\alpha_{\text{gato}}(2,0)+\alpha_{\text{dorme}}(0,2)
\approx(1{,}3395;\;0{,}6605).
$$

Em termos dos pesos arredondados, a operação é $0{,}6698\times(2,0)+0{,}3302\times(0,2)$. O resultado apresentado usa os pesos sem arredondamento intermediário, aproximadamente $0{,}6697615493$ e $0{,}3302384507$. Multiplicar somente os pesos de quatro casas produziria $(1{,}3396;\;0{,}6604)$, uma pequena diferença de arredondamento.

O vetor resultante incorpora informações das duas posições, com maior participação do value de “gato”. Isso mostra como “dorme” pode receber conteúdo de outro token. Entretanto, os vetores e pesos não vieram de um modelo treinado e não demonstram uma relação linguística aprendida. Foi calculada apenas a saída de uma operação de atenção para uma posição, sem as demais operações de um Transformer. O vetor obtido também não é uma palavra prevista diretamente.

Mesmo em modelos treinados, pesos de atenção não devem ser interpretados automaticamente como uma explicação causal da decisão final. Eles descrevem uma combinação interna de representações; a saída depende também dos values e das operações posteriores. A cautela é consistente com a investigação de [Jain e Wallace (2019)](https://aclanthology.org/N19-1357/) sobre os limites de tratar atenção como explicação.

## 5. Multi-head attention e demais componentes

A atenção com múltiplas cabeças, ou *multi-head attention*, executa operações como a anterior com diferentes conjuntos de projeções aprendidas. Cada cabeça trabalha em um subespaço de representação e pode atribuir pesos diferentes às posições. Suas saídas são concatenadas e passam por uma projeção linear que combina as informações. Isso permite representar diferentes relações simultaneamente, sem exigir que cada cabeça corresponda a uma função linguística específica ou facilmente interpretável.

Depois da atenção, uma rede *feed-forward*, de propagação direta, transforma o vetor de cada posição separadamente. No modelo original, são duas transformações lineares com uma ativação ReLU entre elas. Os parâmetros dessa rede são compartilhados entre posições de um mesmo bloco. Enquanto a atenção mistura informações entre posições, a feed-forward transforma as características presentes em cada vetor contextualizado.

Conexões residuais somam a entrada de uma subcamada à sua saída, facilitando a circulação de informações e gradientes. A normalização de camadas, ou *layer normalization*, normaliza as características de cada vetor e aplica ajustes aprendidos, contribuindo para a estabilidade do treinamento. No Transformer original, a normalização ocorre após a soma residual. Ao empilhar blocos com parâmetros próprios, a arquitetura refina sucessivamente as representações. Portanto, a saída de atenção do exemplo ainda passaria por combinações e transformações antes de chegar à saída do modelo.

## 6. Encoder e decoder

A arquitetura original possui um codificador, ou *encoder*, e um decodificador, ou *decoder*, cada um com seis blocos. O encoder recebe os embeddings com informação posicional e aplica repetidamente self-attention e feed-forward, com conexões residuais e normalização. Sua saída mantém uma representação contextualizada por posição da entrada; ela não precisa ser reduzida a um único vetor.

O decoder recebe os tokens anteriores da sequência de saída, também representados por embeddings e posições. Primeiro, aplica self-attention com máscara causal, que impede acesso a posições futuras. As pontuações dessas posições recebem $-\infty$ antes da softmax, tornando seus pesos zero. Como as entradas de saída são deslocadas uma posição, a previsão de um token depende apenas dos tokens anteriores, sem consultar a resposta que deve prever.

Depois, o decoder aplica atenção cruzada, ou *cross-attention*: as queries vêm das representações do próprio decoder, e as keys e values são projeções da saída do encoder. Diferentemente da self-attention, que relaciona posições de uma mesma sequência, a atenção cruzada relaciona a saída em construção com a entrada. Após a feed-forward e os demais blocos, uma projeção linear converte o vetor do decoder em pontuações, chamadas logits, para os tokens do vocabulário. Outra softmax produz uma distribuição de probabilidades sobre o próximo token.

Uma tradução conceitual de “Gato dorme” para “The cat sleeps” ilustra esse fluxo. Supondo um token por palavra, o encoder processa toda a entrada. A partir de um símbolo de início e das representações do encoder, o decoder poderia gerar “The”; depois, usando esse token, gerar “cat”; em seguida, “sleeps” e um símbolo de término. A escolha pode usar, por exemplo, o token mais provável. Essa é uma trajetória ilustrativa, sem probabilidades obtidas de um modelo real. Não é necessário haver correspondência de um para um entre tokens de entrada e saída.

No treinamento, a tradução correta já está disponível. O decoder recebe seus tokens deslocados e calcula previsões para várias posições em paralelo, mantendo a máscara causal. Uma função de perda compara essas previsões aos tokens esperados, e a retropropagação ajusta os parâmetros, incluindo embeddings e projeções de atenção. Na geração autoregressiva, os próximos tokens ainda são desconhecidos: cada novo passo depende do que foi gerado anteriormente. A paralelização no treinamento, portanto, não significa produzir toda a tradução de uma vez.

Modelos posteriores não precisam conservar o arranjo completo. Variantes apenas encoder produzem representações úteis para compreensão e classificação; variantes apenas decoder são utilizadas na geração autoregressiva; modelos encoder-decoder mantêm a separação entre entrada e saída. A atenção permanece central, mas sua organização depende da tarefa.

## 7. Vantagens, limitações e aplicações

A possibilidade de calcular projeções e atenção para várias posições simultaneamente favorece o treinamento em hardware paralelo. Além disso, uma camada de atenção densa permite relacionar diretamente posições distantes, reduzindo a dependência de uma cadeia de estados recorrentes. Essas características sustentam aplicações em tradução, classificação e geração de texto. Na classificação, por exemplo, representações do encoder podem alimentar uma camada que estima a categoria do texto; na geração, o decoder estima tokens sucessivos.

Essa comunicação tem custo. Para uma sequência de comprimento $n$, a self-attention densa padrão calcula uma matriz com $n\times n$ pontuações por cabeça. Mantendo a dimensão fixa, o cálculo dessa matriz cresce quadraticamente com $n$; explicitando a dimensão das keys, o custo de $QK^{\mathsf T}$ é $O(n^2d_k)$. Materializar a matriz também exige memória quadrática. Isso dificulta o processamento de sequências longas, mas não significa que todos os custos de qualquer variante Transformer sejam quadráticos. Outras camadas, estratégias de atenção e formas de execução apresentam características próprias.

O desempenho também depende dos dados, do treinamento e dos recursos computacionais, especialmente em modelos de grande escala. A arquitetura não garante superioridade sobre redes recorrentes em toda tarefa. Da mesma forma, uma saída provável pode ser incorreta, reproduzir vieses dos dados ou apresentar informações inventadas. A distribuição sobre tokens estima continuações conforme o aprendizado do modelo; ela não constitui uma verificação da verdade do conteúdo produzido.

## 8. Considerações finais

O Transformer converte tokens e posições em vetores que são contextualizados por atenção e refinados por blocos sucessivos. Nos modelos gerativos, essas representações alimentam a previsão do próximo token, repetida até encerrar a saída. O exemplo mostrou o núcleo desse processo: comparar queries e keys para combinar values. A arquitetura original organiza esse mecanismo em encoder e decoder, enquanto aplicações posteriores adaptam seus componentes a diferentes tarefas, preservando vantagens e limitações que dependem da configuração e do treinamento.

## 9. Referências

Vídeo recomendado no enunciado da questão como ponto de partida para o funcionamento da arquitetura. YouTube. Disponível em: [youtu.be/bVVm68KTD2M](https://youtu.be/bVVm68KTD2M).

VASWANI, Ashish et al. Attention Is All You Need. In: Advances in Neural Information Processing Systems, v. 30, 2017. Disponível em: [artigo no arXiv](https://arxiv.org/abs/1706.03762). Acesso em: 12 nov. 2026.

ALAMMAR, Jay. The Illustrated Transformer. 27 jun. 2018. Disponível em: [publicação do autor](https://jalammar.github.io/illustrated-transformer/). Acesso em: 12 nov. 2026.

JAIN, Sarthak; WALLACE, Byron C. Attention is not Explanation. In: Proceedings of the 2019 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies, v. 1. Minneapolis: Association for Computational Linguistics, 2019. p. 3543 a 3556. Disponível em: [ACL Anthology](https://aclanthology.org/N19-1357/). Acesso em: 12 nov. 2026.

