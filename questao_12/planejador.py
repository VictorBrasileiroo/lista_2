"""Planejamento e verificação independentes do LLM. Somente biblioteca padrão."""

from dataclasses import dataclass
import re


MAX_ATIVIDADES = 10
PRIORIDADES = ("alta", "media", "baixa")
PRAZOS = ("hoje", "amanha", "proxima_semana", "sem_prazo")


class DadosInvalidos(ValueError):
    """Dados incompatíveis com o contrato de entrada ou com as restrições."""

    def __init__(self, mensagens):
        self.mensagens = tuple(mensagens)
        super().__init__("; ".join(self.mensagens))


class EsclarecimentoNecessario(DadosInvalidos):
    """A entrada está incompleta ou ambígua e não pode ser planejada."""


class RecursoNaoSuportado(DadosInvalidos):
    """Pedido fora das capacidades do MVP."""


@dataclass(frozen=True)
class Atividade:
    id: str
    nome: str
    duracao_minutos: int
    prioridade: str
    prazo: str
    inicio_fixo: int | None = None
    fim_fixo: int | None = None


@dataclass(frozen=True)
class Problema:
    inicio: int
    fim: int
    atividades: tuple[Atividade, ...]


@dataclass(frozen=True)
class Intervalo:
    id: str
    inicio: int
    fim: int


@dataclass(frozen=True)
class Pendencia:
    id: str
    motivo: str


@dataclass(frozen=True)
class Plano:
    agenda: tuple[Intervalo, ...]
    pendentes: tuple[Pendencia, ...]


def minutos(horario):
    """Converte HH:MM estrito em minutos desde 00:00, sem mudança de dia."""
    if not isinstance(horario, str) or not re.fullmatch(r"(?:[01][0-9]|2[0-3]):[0-5][0-9]", horario):
        raise ValueError("Horário deve estar entre 00:00 e 23:59, no formato HH:MM.")
    hora, minuto = map(int, horario.split(":"))
    return hora * 60 + minuto


def horario(valor):
    return f"{valor // 60:02d}:{valor % 60:02d}"


def _objeto(valor, chaves, local):
    if not isinstance(valor, dict) or set(valor) != set(chaves):
        raise DadosInvalidos([f"{local}: estrutura incorreta; campos esperados: {', '.join(chaves)}."])


def _lista_textos(valor, local):
    if not isinstance(valor, list) or any(not isinstance(s, str) or not s.strip() for s in valor):
        raise DadosInvalidos([f"{local} deve ser uma lista de textos não vazios."])


def validar_dados(dados):
    """Valida o JSON interpretado, inclusive regras não expressas no schema.

    Null indica informação ausente. Nenhum valor essencial é estimado aqui.
    Chaves desconhecidas e tipos incorretos são rejeitados, sem coerção.
    """
    _objeto(dados, ("janela", "atividades", "esclarecimentos", "recursos_nao_suportados"), "Solicitação")
    _objeto(dados["janela"], ("inicio", "fim"), "Janela")
    _lista_textos(dados["esclarecimentos"], "Esclarecimentos")
    _lista_textos(dados["recursos_nao_suportados"], "Recursos não suportados")
    if dados["recursos_nao_suportados"]:
        raise RecursoNaoSuportado([
            "Este MVP aceita uma janela no mesmo dia e atividades indivisíveis. "
            "Divisão de tarefas e múltiplos dias/janelas não estão implementados.",
            *dados["recursos_nao_suportados"],
        ])
    erros, perguntas = [], list(dados["esclarecimentos"])
    janela = []
    for campo in ("inicio", "fim"):
        valor = dados["janela"][campo]
        if valor is None:
            perguntas.append(f"Informe o {campo} da janela disponível (HH:MM).")
            janela.append(None)
        else:
            try:
                janela.append(minutos(valor))
            except ValueError as exc:
                erros.append(f"Janela, {campo}: {exc}")
                janela.append(None)
    itens = dados["atividades"]
    if not isinstance(itens, list):
        raise DadosInvalidos(["Atividades deve ser uma lista."])
    if not itens:
        perguntas.append("Informe pelo menos uma atividade acadêmica.")
    if len(itens) > MAX_ATIVIDADES:
        erros.append(f"São permitidas no máximo {MAX_ATIVIDADES} atividades por solicitação.")
    atividades, ids = [], set()
    campos = ("id", "nome", "duracao_minutos", "prioridade", "prazo", "inicio_fixo", "fim_fixo")
    for indice, item in enumerate(itens, 1):
        _objeto(item, campos, f"Atividade {indice}")
        identificador, nome = item["id"], item["nome"]
        if not isinstance(identificador, str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,24}", identificador):
            erros.append(f"Atividade {indice}: ID inválido.")
        elif identificador in ids:
            erros.append(f"ID repetido: {identificador}.")
        else:
            ids.add(identificador)
        if not isinstance(nome, str) or not nome.strip():
            erros.append(f"Atividade {indice}: nome vazio ou inválido.")
        for campo, dominio in (("prioridade", PRIORIDADES), ("prazo", PRAZOS)):
            valor = item[campo]
            if valor is None:
                perguntas.append(f"Informe {campo} de {identificador}: {', '.join(dominio)}.")
            elif valor not in dominio:
                erros.append(f"{identificador}: {campo} inválido.")
        duracao = item["duracao_minutos"]
        if duracao is None:
            perguntas.append(f"Qual a duração, em minutos, de {identificador} ({nome})?")
        elif type(duracao) is not int or duracao <= 0:
            erros.append(f"{identificador}: duração deve ser um inteiro positivo.")
        fixos = []
        for campo in ("inicio_fixo", "fim_fixo"):
            valor = item[campo]
            if valor is None:
                fixos.append(None)
            else:
                try:
                    fixos.append(minutos(valor))
                except ValueError as exc:
                    erros.append(f"{identificador}, {campo}: {exc}")
                    fixos.append(None)
        if (item["inicio_fixo"] is None) != (item["fim_fixo"] is None):
            perguntas.append(f"Informe início e fim do compromisso fixo {identificador}.")
        atividades.append(Atividade(identificador, nome, duracao, item["prioridade"], item["prazo"], *fixos))
    if erros:
        raise DadosInvalidos(erros)
    if perguntas:
        raise EsclarecimentoNecessario(dict.fromkeys(perguntas))
    problema = Problema(*janela, tuple(atividades))
    verificar_problema(problema)
    return problema


def verificar_problema(problema):
    """Também protege chamadas diretas ao planejador sem passar pelo JSON."""
    erros = []
    if type(problema.inicio) is not int or type(problema.fim) is not int:
        raise DadosInvalidos(["Limites da janela devem ser minutos inteiros."])
    if not 0 <= problema.inicio < problema.fim < 24 * 60:
        erros.append("A janela deve ter início anterior ao fim, no mesmo dia (00:00 a 23:59).")
    if not 1 <= len(problema.atividades) <= MAX_ATIVIDADES:
        erros.append(f"Informe de 1 a {MAX_ATIVIDADES} atividades.")
    ids = set()
    fixos = []
    for atividade in problema.atividades:
        if not isinstance(atividade.id, str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,24}", atividade.id):
            erros.append("ID inválido.")
        elif atividade.id in ids:
            erros.append(f"ID repetido: {atividade.id}.")
        else:
            ids.add(atividade.id)
        if not isinstance(atividade.nome, str) or not atividade.nome.strip():
            erros.append(f"{atividade.id}: nome inválido.")
        if type(atividade.duracao_minutos) is not int or atividade.duracao_minutos <= 0:
            erros.append(f"{atividade.id}: duração deve ser um inteiro positivo.")
        if atividade.prioridade not in PRIORIDADES or atividade.prazo not in PRAZOS:
            erros.append(f"{atividade.id}: prioridade ou prazo inválido.")
        inicio, fim = atividade.inicio_fixo, atividade.fim_fixo
        if inicio is None and fim is None:
            continue
        if type(inicio) is not int or type(fim) is not int:
            erros.append(f"{atividade.id}: horário fixo incompleto ou inválido.")
            continue
        if not problema.inicio <= inicio < fim <= problema.fim:
            erros.append(f"{atividade.id}: horário fixo fora da janela ou invertido.")
        if fim - inicio != atividade.duracao_minutos:
            erros.append(f"{atividade.id}: duração incompatível com o horário fixo.")
        fixos.append(Intervalo(atividade.id, inicio, fim))
    fixos.sort(key=lambda x: (x.inicio, x.fim, x.id))
    for anterior, atual in zip(fixos, fixos[1:]):
        if atual.inicio < anterior.fim:
            erros.append(f"Compromissos fixos {anterior.id} e {atual.id} se sobrepõem.")
    if erros:
        raise DadosInvalidos(erros)


def intervalos_livres(problema, agenda):
    """Complemento de uma agenda já validada dentro da janela."""
    livres, cursor = [], problema.inicio
    for intervalo in sorted(agenda, key=lambda x: (x.inicio, x.fim, x.id)):
        if cursor < intervalo.inicio:
            livres.append((cursor, intervalo.inicio))
        cursor = intervalo.fim
    if cursor < problema.fim:
        livres.append((cursor, problema.fim))
    return tuple(livres)


def _pontuacao(mascara, atividades):
    """Vetor lexicográfico: contagens por prazo/prioridade, minutos, IDs."""
    escolhidas = [a for i, a in enumerate(atividades) if mascara & (1 << i)]
    contagens = tuple(sum(a.prazo == p and a.prioridade == q for a in escolhidas)
                      for p in PRAZOS for q in PRIORIDADES)
    return (*contagens, sum(a.duracao_minutos for a in escolhidas),
            *(int(bool(mascara & (1 << i))) for i in range(len(atividades))))


def planejar(problema):
    """Busca exata por subconjuntos, com dominância do menor fim.

    Para cada subconjunto guarda a sequência cujo término é mais cedo.
    Um término mais cedo nunca reduz as possibilidades de continuação,
    pois não há datas de liberação, precedências ou prazos intradiários.
    Empates no término usam a sequência lexicográfica de IDs.
    """
    verificar_problema(problema)
    fixos = tuple(sorted((Intervalo(a.id, a.inicio_fixo, a.fim_fixo)
                          for a in problema.atividades if a.inicio_fixo is not None),
                         key=lambda x: (x.inicio, x.fim, x.id)))
    livres = intervalos_livres(problema, fixos)
    flexiveis = sorted((a for a in problema.atividades if a.inicio_fixo is None), key=lambda a: a.id)
    # máscara -> (menor término, sequência de IDs, intervalos correspondentes)
    estados = {0: (problema.inicio, (), ())}
    for mascara in range(1 << len(flexiveis)):
        if mascara not in estados:
            continue
        cursor, sequencia, agenda = estados[mascara]
        for indice, atividade in enumerate(flexiveis):
            if mascara & (1 << indice):
                continue
            for inicio, fim in livres:
                posicao = max(cursor, inicio)
                termino = posicao + atividade.duracao_minutos
                if termino <= fim:
                    novo = mascara | (1 << indice)
                    candidato = (termino, sequencia + (atividade.id,),
                                 agenda + (Intervalo(atividade.id, posicao, termino),))
                    if novo not in estados or candidato[:2] < estados[novo][:2]:
                        estados[novo] = candidato
                    break
    melhor = max(estados, key=lambda m: _pontuacao(m, flexiveis))
    agenda = tuple(sorted(fixos + estados[melhor][2], key=lambda x: (x.inicio, x.fim, x.id)))
    restantes = intervalos_livres(problema, agenda)
    maior_livre = max((fim - inicio for inicio, fim in restantes), default=0)
    total_livre = sum(fim - inicio for inicio, fim in restantes)
    maior_original = max((fim - inicio for inicio, fim in livres), default=0)
    pendentes = []
    for indice, atividade in enumerate(flexiveis):
        if melhor & (1 << indice):
            continue
        if atividade.duracao_minutos > problema.fim - problema.inicio:
            motivo = "A duração excede toda a janela disponível."
        elif atividade.duracao_minutos > maior_original:
            motivo = ("Após reservar os compromissos fixos, nenhum intervalo contínuo "
                      f"comporta {atividade.duracao_minutos} min (maior: {maior_original} min).")
        else:
            motivo = ("A seleção seguiu as contagens por prazo e prioridade e os desempates definidos. "
                      f"Após as atividades selecionadas, restam {total_livre} min livres; "
                      f"o maior intervalo contínuo é de {maior_livre} min, "
                      f"insuficiente para os {atividade.duracao_minutos} min indivisíveis desta tarefa.")
        pendentes.append(Pendencia(atividade.id, motivo + " Nenhum horário futuro foi criado."))
    plano = Plano(agenda, tuple(pendentes))
    erros = validar_agenda(problema, plano)
    if erros:
        raise DadosInvalidos(["Falha na validação do plano: " + erro for erro in erros])
    return plano


def validar_agenda(problema, plano):
    """Validador independente da busca. Lista vazia significa agenda viável.

    Verifica viabilidade e cobertura, não prova a melhor pontuação do plano.
    Identificadores são comparados com a entrada estruturada, não com o texto.
    """
    try:
        verificar_problema(problema)
    except DadosInvalidos as exc:
        return list(exc.mensagens)
    originais = {a.id: a for a in problema.atividades}
    erros, vistos, pendentes = [], set(), set()
    intervalos_validos = []
    for item in plano.agenda:
        if not isinstance(item.id, str) or item.id not in originais:
            erros.append(f"Atividade inventada ou ID inválido na agenda: {item.id}.")
            continue
        if item.id in vistos:
            erros.append(f"{item.id}: ID agendado mais de uma vez; atividade deve ser indivisível.")
        vistos.add(item.id)
        tarefa = originais[item.id]
        if type(item.inicio) is not int or type(item.fim) is not int:
            erros.append(f"{item.id}: início e fim devem ser minutos inteiros.")
            continue
        if not problema.inicio <= item.inicio < item.fim <= problema.fim:
            erros.append(f"{item.id}: intervalo fora da janela ou início/fim inválidos.")
        if item.fim - item.inicio != tarefa.duracao_minutos:
            erros.append(f"{item.id}: duração incorreta ou atividade dividida.")
        if tarefa.inicio_fixo is not None and (item.inicio, item.fim) != (tarefa.inicio_fixo, tarefa.fim_fixo):
            erros.append(f"{item.id}: compromisso fixo foi deslocado.")
        intervalos_validos.append(item)
    intervalos_validos.sort(key=lambda x: (x.inicio, x.fim, x.id))
    for anterior, atual in zip(intervalos_validos, intervalos_validos[1:]):
        if atual.inicio < anterior.fim:
            erros.append(f"Sobreposição entre {anterior.id} e {atual.id}.")
    for item in plano.pendentes:
        if not isinstance(item.id, str) or item.id not in originais:
            erros.append(f"Atividade inventada ou ID inválido nas pendências: {item.id}.")
            continue
        if item.id in pendentes:
            erros.append(f"Pendência repetida: {item.id}.")
        pendentes.add(item.id)
        if not isinstance(item.motivo, str) or not item.motivo.strip():
            erros.append(f"{item.id}: pendência sem justificativa.")
    for identificador in sorted(vistos & pendentes):
        erros.append(f"{identificador}: atividade está agendada e pendente simultaneamente.")
    for identificador in sorted(set(originais) - vistos - pendentes):
        erros.append(f"{identificador}: atividade ausente da agenda e das pendências.")
    for tarefa in problema.atividades:
        if tarefa.inicio_fixo is not None and tarefa.id not in vistos:
            erros.append(f"{tarefa.id}: compromisso fixo não foi reservado.")
    return erros
