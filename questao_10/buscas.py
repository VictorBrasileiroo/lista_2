"""Questão 10: buscas em grafo, usando somente a biblioteca padrão.

Processamento: retirada válida da fronteira (ou entrada na chamada da DFS).
Expansão: geração dos sucessores. O objetivo é processado, mas não expandido.
Empates no heap: prioridade, estado em ordem lexicográfica, custo acumulado.
Uma melhoria estrita substitui o predecessor; custos iguais não o substituem.
"""

from collections import deque
from dataclasses import dataclass, field
import heapq
from math import inf


ARESTAS = (
    ("A", "B", 4), ("A", "D", 3), ("B", "C", 5), ("B", "E", 2),
    ("C", "F", 2), ("D", "E", 4), ("D", "G", 6), ("E", "F", 3),
    ("E", "H", 5), ("F", "I", 4), ("G", "H", 3), ("H", "I", 2),
)
HEURISTICA = dict(zip("ABCDEFGHI", (10, 8, 6, 9, 6, 4, 5, 2, 0)))


@dataclass
class Resultado:
    rota: list
    custo: int
    processamento: list
    expandidos: list
    descobertos: list
    tabela: list = field(default_factory=list)


def construir_grafo():
    grafo = {v: {} for v in "ABCDEFGHI"}
    for u, v, custo in ARESTAS:
        if v in grafo[u] or custo <= 0:
            raise ValueError("Aresta duplicada ou custo não positivo.")
        grafo[u][v] = custo
        grafo[v][u] = custo
    validar_grafo(grafo)
    return grafo


def validar_grafo(grafo):
    assert set(grafo) == set("ABCDEFGHI")
    assert sum(map(len, grafo.values())) == 24
    esperadas = {(u, v): c for u, v, c in ARESTAS}
    obtidas = {(u, v): c for u in grafo for v, c in grafo[u].items() if u < v}
    assert obtidas == esperadas and len(obtidas) == 12
    assert all(c > 0 and grafo[v][u] == c
               for u in grafo for v, c in grafo[u].items())


def custo_rota(grafo, rota):
    return sum(grafo[u][v] for u, v in zip(rota, rota[1:]))


def reconstruir(pais, estado):
    rota = []
    while estado is not None:
        rota.append(estado)
        estado = pais[estado]
    return rota[::-1]


def dfs(grafo, inicio="A", objetivo="I"):
    """Marca visitado ao entrar na chamada, antes de testar o objetivo."""
    visitados, ordem, expandidos, caminho = set(), [], [], []

    def visitar(u):
        visitados.add(u)
        ordem.append(u)
        caminho.append(u)
        if u == objetivo:
            return True
        expandidos.append(u)
        for v in sorted(grafo[u]):
            if v not in visitados and visitar(v):
                return True
        caminho.pop()
        return False

    if not visitar(inicio):
        raise ValueError("Objetivo inalcançável.")
    return Resultado(caminho, custo_rota(grafo, caminho), ordem, expandidos, ordem[:])


def bfs(grafo, inicio="A", objetivo="I"):
    """Marca descoberto na inserção na fila FIFO, uma vez por vértice."""
    fila, pais = deque([inicio]), {inicio: None}
    ordem, expandidos, descobertos = [], [], [inicio]
    while fila:
        u = fila.popleft()
        ordem.append(u)
        if u == objetivo:
            rota = reconstruir(pais, u)
            return Resultado(rota, custo_rota(grafo, rota), ordem, expandidos, descobertos)
        expandidos.append(u)
        for v in sorted(grafo[u]):
            if v not in pais:
                pais[v] = u
                descobertos.append(v)
                fila.append(v)
    raise ValueError("Objetivo inalcançável.")


def busca_prioridade(inicio, eh_objetivo, sucessores, heuristica):
    """Núcleo de UCS/A*: descarta entradas antigas e permite reabertura.

    Cada estado é descoberto na primeira inserção. Melhorias estritas geram
    novas inserções; a comparação com melhor_g descarta as entradas antigas.
    Não há conjunto fechado que impeça reexpandir um estado com custo melhor.
    """
    fila = [(heuristica(inicio), inicio, 0)]
    melhor_g, pais = {inicio: 0}, {inicio: None}
    ordem, expandidos, descobertos, tabela = [], [], [inicio], []
    while fila:
        f, u, g = heapq.heappop(fila)
        if g != melhor_g[u]:
            continue
        ordem.append(u)
        linha = {"estado": u, "pai": pais[u], "g": g,
                 "h": heuristica(u), "f": f, "atualizacoes": []}
        tabela.append(linha)
        if eh_objetivo(u):
            return Resultado(reconstruir(pais, u), g, ordem, expandidos,
                             descobertos, tabela)
        expandidos.append(u)
        for v, custo in sucessores(u):
            novo_g = g + custo
            anterior = melhor_g.get(v, inf)
            if novo_g < anterior:
                if anterior == inf:
                    descobertos.append(v)
                melhor_g[v], pais[v] = novo_g, u
                heapq.heappush(fila, (novo_g + heuristica(v), v, novo_g))
                linha["atualizacoes"].append((v, anterior, novo_g))
    raise ValueError("Objetivo inalcançável.")


def ucs(grafo, inicio="A", objetivo="I"):
    return busca_prioridade(inicio, lambda u: u == objetivo,
                            lambda u: sorted(grafo[u].items()), lambda u: 0)


def a_estrela(grafo, inicio="A", objetivo="I", heuristica=None):
    h = HEURISTICA if heuristica is None else heuristica
    return busca_prioridade(inicio, lambda u: u == objetivo,
                            lambda u: sorted(grafo[u].items()), h.__getitem__)


def sucessores_estendidos(grafo, estado):
    u, visitou_d, visitou_f = estado
    return [((v, visitou_d or v == "D", visitou_f or v == "F"), grafo[u][v])
            for v in sorted(grafo[u])]


def ucs_obrigatoria(grafo):
    # I com marcadores incompletos não é objetivo e pode gerar sucessores.
    return busca_prioridade(("A", False, False),
                            lambda s: s == ("I", True, True),
                            lambda s: sucessores_estendidos(grafo, s), lambda s: 0)


def referencia_bellman_ford(estados, arestas, inicio):
    """Referência independente: relaxação exaustiva, sem heap ou predecessores."""
    distancias = dict.fromkeys(estados, inf)
    distancias[inicio] = 0
    for _ in range(len(estados) - 1):
        mudou = False
        for u, v, custo in arestas:
            if distancias[u] + custo < distancias[v]:
                distancias[v] = distancias[u] + custo
                mudou = True
        if not mudou:
            break
    return distancias


def verificar_heuristica(grafo):
    arestas = [(u, v, c) for u in grafo for v, c in grafo[u].items()]
    distancias = referencia_bellman_ford(list(grafo), arestas, "I")
    admissivel = all(0 <= HEURISTICA[u] <= distancias[u] for u in grafo)
    consistente = all(HEURISTICA[u] <= c + HEURISTICA[v] for u, v, c in arestas)
    return distancias, admissivel, consistente


def validar_resultados(grafo, resultados, obrigatoria):
    validar_grafo(grafo)
    funcoes = (dfs, bfs, ucs, a_estrela)
    for funcao, resultado in zip(funcoes, resultados):
        assert resultado == funcao(grafo), "Execução não determinística."
        assert resultado.rota[0] == "A" and resultado.rota[-1] == "I"
        assert resultado.custo == custo_rota(grafo, resultado.rota)
        assert resultado.expandidos == resultado.processamento[:-1]
        assert len(set(resultado.descobertos)) == len(resultado.descobertos)
    assert resultados[0].processamento == list("ABCFEDGHI")
    assert resultados[0].rota == list("ABCFEDGHI")
    assert resultados[1].processamento == list("ABDCEGFHI")
    assert resultados[1].rota == list("ABCFI")
    distancias, admissivel, consistente = verificar_heuristica(grafo)
    assert admissivel and consistente
    assert resultados[2].custo == resultados[3].custo == distancias["A"] == 13
    assert obrigatoria == ucs_obrigatoria(grafo)
    rota = [s[0] for s in obrigatoria.rota]
    assert rota[0] == "A" and obrigatoria.rota[-1] == ("I", True, True)
    assert "D" in rota[:-1] and "F" in rota[:-1]
    assert obrigatoria.custo == custo_rota(grafo, rota)
    d, f = False, False
    for local, marcou_d, marcou_f in obrigatoria.rota:
        d, f = d or local == "D", f or local == "F"
        assert (marcou_d, marcou_f) == (d, f)
    # Constrói separadamente os 36 estados e suas transições para a referência.
    estados = [(u, d, f) for u in grafo for d in (False, True) for f in (False, True)]
    arestas = []
    for u, d, f in estados:
        for v, custo in grafo[u].items():
            destino = (v, True if v == "D" else d, True if v == "F" else f)
            arestas.append(((u, d, f), destino, custo))
    ref = referencia_bellman_ford(estados, arestas, ("A", False, False))
    assert obrigatoria.custo == ref[("I", True, True)] == 14


def formatar_rota(rota):
    return " → ".join(map(str, rota))


def apresentar_resultados():
    grafo = construir_grafo()
    resultados = [funcao(grafo) for funcao in (dfs, bfs, ucs, a_estrela)]
    obrigatoria = ucs_obrigatoria(grafo)
    validar_resultados(grafo, resultados, obrigatoria)
    print("Grafo validado: 9 vértices, 12 arestas não direcionadas.")
    for nome, r in zip(("DFS", "BFS", "UCS", "A*"), resultados):
        print(f"\n{nome}: {formatar_rota(r.rota)} | custo: {r.custo} minutos")
        print("Processamento:", formatar_rota(r.processamento))
        print(f"Expandidos ({len(r.expandidos)}): {formatar_rota(r.expandidos)}")
        print(f"Descobertos ({len(r.descobertos)}): {formatar_rota(r.descobertos)}")
    print("\nA*: estado | predecessor | g | h | f | melhorias (g anterior → novo)")
    for linha in resultados[3].tabela:
        atualizacoes = "; ".join(f"{v}: {ant} → {novo}"
                                 for v, ant, novo in linha["atualizacoes"]) or "nenhuma"
        print(f"{linha['estado']} | {linha['pai'] or '-'} | {linha['g']} | "
              f"{linha['h']} | {linha['f']} | {atualizacoes}")
    distancias, admissivel, consistente = verificar_heuristica(grafo)
    print("\nDistâncias exatas até I (Bellman-Ford):", distancias)
    print(f"Heurística admissível: {admissivel}; consistente: {consistente}")
    print("\nVisitas obrigatórias:", formatar_rota([s[0] for s in obrigatoria.rota]))
    print("Estados da rota:", formatar_rota(obrigatoria.rota))
    print(f"Custo: {obrigatoria.custo}; expandidos: {len(obrigatoria.expandidos)}; "
          f"processados: {len(obrigatoria.processamento)}; "
          f"descobertos: {len(obrigatoria.descobertos)}")
    print("Processamento estendido:", formatar_rota(obrigatoria.processamento))
    print("\nValidações concluídas: rotas, custos, ordem, reprodução, heurística e "
          "ótimos 13/14 conferidos por Bellman-Ford independente.")


if __name__ == "__main__":
    apresentar_resultados()
