# Ambiente e reprodução — Etapa 00

Somente provas de integração isoladas; não são as soluções de Q9/Q12.
Execute da raiz do repositório em Windows/PowerShell com Python 3.11+.
Não é necessário ativar o virtualenv nem mudar a ExecutionPolicy.

## Instalação

```powershell
python --version
python -m venv .venv
./.venv/Scripts/python.exe -m pip install -r questoes/q09/requirements-spike.txt
./.venv/Scripts/python.exe scripts/verificar_estrutura.py
./.venv/Scripts/python.exe -m unittest discover -s tests -v
```

Se `python` apontar para um alias da Store que não abre, use `py -3.12`
ou o caminho completo de uma instalação convencional no comando que cria a venv.
Q12 e seus testes usam somente a biblioteca padrão; não exigem Owlready2.
A instalação de Owlready2 pelo código-fonte pode precisar de ferramentas de build;
não considerar instalação concluída sem retorno zero do pip.

## Q9: Java, Owlready2 e HermiT

Instale um JDK (Java 17 ou 21 é uma opção de ambiente; esta execução usa 21).
Owlready2 0.48 traz o HermiT; não é necessário baixar outro reasoner.
Protégé Desktop é opcional para inspecionar o OWL neste spike; sua execução
e evidências de interface não estão concluídas por este experimento.

```powershell
java -version
# Somente se java não estiver no PATH:
# $env:JAVA_EXE = 'C:/caminho/jdk/bin/java.exe'
./.venv/Scripts/python.exe questoes/q09/spike_reasoner.py --output _tmp/q09
./.venv/Scripts/python.exe questoes/q09/spike_reasoner.py --inconsistent --output _tmp/q09-inconsistent
```

Referência lógica independente: `RecursoBasico ≡ Recurso ∩ (nivel value "basico")`.
O único indivíduo é assertado como `Recurso`, com nível `basico`; o tipo
`RecursoBasico` deve surgir somente após HermiT. No controle negativo, também
é assertado `RecursoAvancado`, disjunto de `RecursoBasico`: HermiT deve rejeitar
a inconsistência. O controle retorna zero somente se essa rejeição ocorrer.
Cada diretório recebe `asserted.owl`; somente a execução consistente recebe
`inferred.owl`. Use diretórios distintos para não confundir artefatos.
Stdout informa versões e tipos; stderr mostra o comando/saída real do HermiT.
Saída 0 = verificação comprovada; 2 = dependência bloqueada; 1 = falha do reasoner
ou do caso conhecido. Não há inferência alternativa em Python.

## Q12: Ollama acessível a partir do executor

O Ollama instalado no computador do estudante pode não estar acessível ao Codex.
Não modificar firewall, publicar portas nem assumir que localhost é a mesma
máquina. No terminal da máquina que hospedará o servidor:

```powershell
ollama --version
ollama serve  # somente se o serviço ainda não estiver rodando
# Em outro terminal: escolher um modelo compatível com memória/disco disponíveis.
ollama pull qwen2.5:3b
ollama list
```

O modelo acima é apenas exemplo configurável, não requisito nem modelo observado.
No ambiente que executa o spike, configure a origem realmente alcançável:

```powershell
$env:OLLAMA_URL = 'http://127.0.0.1:11434'
$env:OLLAMA_MODEL = 'qwen2.5:3b' # substituir pelo nome de ollama list
./.venv/Scripts/python.exe questoes/q12/spike_ollama.py --timeout 60
# Alternativa sem variáveis de ambiente:
./.venv/Scripts/python.exe questoes/q12/spike_ollama.py --url http://127.0.0.1:11434 --model qwen2.5:3b --timeout 60
$LASTEXITCODE
```

POST `/api/chat` usa `format=json`, `stream=false`, temperatura 0 e seed 42.
Esses parâmetros não garantem resultados idênticos entre modelos/versões/hardware.
O pedido fixo é estudar por meia hora. O contrato exige envelope final de
assistant, nome do modelo e conteúdo com apenas `intencao="estudar"` e
`duracao_minutos=30` (inteiro, não booleano). Saída 0 só ocorre após HTTP real
e validação; 2 indica conexão/modelo indisponível; 1 indica resposta inválida.
O script não baixa modelos, não inicia serviços e não possui fallback simulado.
O teste unitário valida fixtures artificiais do contrato, sem alegar execução LLM.
Planejador de agenda e verificador de sobreposições ficam para a questão completa.

## Fontes técnicas consultadas em 30/10/2026

- [Owlready2: reasoning](https://owlready2.readthedocs.io/en/latest/reasoning.html): execução Java/HermiT, gravação de inferências e erro de inconsistência.
- [Ollama: chat](https://docs.ollama.com/api/chat): POST, parâmetros de formato/streaming e envelope da resposta.

Evidências e limitações desta execução: [08-evidencias-etapa-00.md](08-evidencias-etapa-00.md).
