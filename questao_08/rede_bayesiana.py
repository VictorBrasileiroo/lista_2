"""Rede bayesiana educacional com probabilidades hipotéticas, sem uso clínico."""

import argparse
from itertools import product
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from pgmpy.factors.discrete import TabularCPD
from pgmpy.inference import VariableElimination
from pgmpy.models import DiscreteBayesianNetwork
from pgmpy.readwrite import BIFReader, BIFWriter

PASTA = Path(__file__).resolve().parent
ESTADOS = ["Não", "Sim"]
VARIAVEIS = ["Exposicao", "Gripe", "Febre", "Tosse", "DorMuscular"]
SINTOMAS = ["Febre", "Tosse", "DorMuscular"]
OBSERVAVEIS = ["Exposicao", *SINTOMAS]
ARESTAS = [("Exposicao", "Gripe"), *[("Gripe", s) for s in SINTOMAS]]
EXPERIMENTOS = [
    ("A priori", {}),
    ("1 / 2.1: febre", {"Febre": "Sim"}),
    ("2.2: febre e tosse", {"Febre": "Sim", "Tosse": "Sim"}),
    ("2.3: três sintomas", dict.fromkeys(SINTOMAS, "Sim")),
    ("3: sintomas ausentes", dict.fromkeys(SINTOMAS, "Não")),
    ("Adicional: exposição presente", {"Exposicao": "Sim"}),
    ("Adicional: exposição ausente", {"Exposicao": "Não"}),
    ("Adicional: exposição e três sintomas", {"Exposicao": "Sim", **dict.fromkeys(SINTOMAS, "Sim")}),
    ("Adicional: sem exposição, três sintomas", {"Exposicao": "Não", **dict.fromkeys(SINTOMAS, "Sim")}),
]


def construir_rede():
    """A ordem de linhas e de estados dos pais é sempre Não, Sim."""
    rede = DiscreteBayesianNetwork(ARESTAS)
    rede.add_cpds(TabularCPD("Exposicao", 2, [[0.80], [0.20]],
                             state_names={"Exposicao": ESTADOS.copy()}))
    tabelas = {
        "Gripe": ("Exposicao", [[0.95, 0.70], [0.05, 0.30]]),
        "Febre": ("Gripe", [[0.85, 0.15], [0.15, 0.85]]),
        "Tosse": ("Gripe", [[0.65, 0.20], [0.35, 0.80]]),
        "DorMuscular": ("Gripe", [[0.80, 0.25], [0.20, 0.75]]),
    }
    for variavel, (pai, valores) in tabelas.items():
        rede.add_cpds(TabularCPD(
            variavel, 2, valores, evidence=[pai], evidence_card=[2],
            state_names={variavel: ESTADOS.copy(), pai: ESTADOS.copy()},
        ))
    validar_estrutura(rede)
    return rede


def exigir(condicao, mensagem):
    if not condicao:
        raise ValueError(mensagem)


def validar_estrutura(rede):
    exigir(set(rede.nodes()) == set(VARIAVEIS), "Variáveis inesperadas.")
    exigir(set(rede.edges()) == set(ARESTAS), "Arestas inesperadas.")
    exigir(len(SINTOMAS) == 3, "São necessários três sintomas.")
    exigir(rede.check_model(), "Modelo inválido no pgmpy.")
    exigir(len(rede.get_cpds()) == 5, "São necessárias cinco CPTs.")
    for cpd in rede.get_cpds():
        for estados in cpd.state_names.values():
            exigir(estados == ESTADOS, "Ordem de estados incorreta.")
        valores = cpd.get_values()
        exigir(np.all((valores >= 0) & (valores <= 1)), "Probabilidade inválida.")
        exigir(np.allclose(valores.sum(axis=0), 1, rtol=0, atol=1e-12),
               "Coluna de CPT não normalizada.")


def validar_evidencias(evidencias):
    for variavel, estado in evidencias.items():
        if variavel == "Gripe":
            raise ValueError("Gripe é a variável consultada; informe exposição ou sintomas.")
        if variavel not in OBSERVAVEIS:
            raise ValueError(f"Variável desconhecida: {variavel}. Use {', '.join(OBSERVAVEIS)}.")
        if estado not in ESTADOS:
            raise ValueError(f"Estado inválido para {variavel}: {estado}. Use Não ou Sim.")


def ler_evidencias(texto):
    """Rejeita repetições antes que um dicionário possa sobrescrevê-las."""
    if not texto.strip():
        raise ValueError("Evidências vazias. Para a priori, execute sem --evidencias.")
    resultado = {}
    for item in texto.split(","):
        if item.count("=") != 1:
            raise ValueError(f"Formato inválido: {item!r}. Use Variavel=Estado.")
        variavel, estado = (parte.strip() for parte in item.split("="))
        if variavel in resultado:
            tipo = "repetida" if resultado[variavel] == estado else "contraditória"
            raise ValueError(f"Evidência {tipo}: {variavel}.")
        resultado[variavel] = estado
    validar_evidencias(resultado)
    return resultado


def consultar(rede, evidencias=None):
    evidencias = {} if evidencias is None else dict(evidencias)
    validar_evidencias(evidencias)
    fator = VariableElimination(rede).query(
        variables=["Gripe"], evidence=evidencias, show_progress=False,
    )
    distribuicao = {estado: float(fator.get_value(Gripe=estado)) for estado in ESTADOS}
    exigir(np.isclose(sum(distribuicao.values()), 1, rtol=0, atol=1e-12),
           "Posterior não normalizada.")
    return distribuicao


def exportar_e_conferir(rede):
    """Compara também a ordem dos estados e os eixos de cada CPT."""
    caminho = PASTA / "modelo.bif"
    caminho.write_text(str(BIFWriter(rede)), encoding="utf-8")
    importada = BIFReader(string=caminho.read_text(encoding="utf-8")).get_model()
    validar_estrutura(importada)
    for variavel in VARIAVEIS:
        original = rede.get_cpds(variavel)
        copia = importada.get_cpds(variavel)
        exigir(original.variables == copia.variables, "Eixos da CPT alterados no BIF.")
        exigir(original.state_names == copia.state_names, "Estados alterados no BIF.")
        exigir(np.allclose(original.get_values(), copia.get_values(), rtol=0, atol=1e-12),
               "Valores da CPT alterados no BIF.")
    return importada


def gerar_grafo(rede):
    grafo = nx.DiGraph(rede.edges())
    exigir(set(grafo.nodes) == set(VARIAVEIS) and set(grafo.edges) == set(ARESTAS),
           "Diagrama incompatível com a rede.")
    posicoes = {"Exposicao": (0, 2.2), "Gripe": (0, 1.1),
                "Febre": (-1.6, 0), "Tosse": (0, 0), "DorMuscular": (1.6, 0)}
    fig, ax = plt.subplots(figsize=(10, 5.8), facecolor="white")
    nx.draw_networkx_nodes(grafo, posicoes, ax=ax, node_size=6200,
                           node_color="#e1f0ef", edgecolors="#17605c", linewidths=1.8)
    nx.draw_networkx_labels(grafo, posicoes, ax=ax, font_size=12, font_color="#143b3a")
    nx.draw_networkx_edges(grafo, posicoes, ax=ax, node_size=6200,
                           arrows=True, arrowsize=24, edge_color="#17605c", width=2)
    ax.set_title("Rede bayesiana educacional: gripe", fontsize=18, pad=22)
    ax.text(0.5, -0.06, "Estados: Não / Sim | Probabilidades hipotéticas, sem validação clínica",
            ha="center", transform=ax.transAxes, fontsize=11, color="#4c5756")
    ax.set_xlim(-2.4, 2.4)
    ax.set_ylim(-0.6, 2.8)
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(PASTA / "rede.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def validar_resultados(rede, importada):
    """Verificações reproduzíveis, sem implementar outro motor de inferência."""
    exigir(np.isclose(consultar(rede)["Sim"], 0.20 * 0.30 + 0.80 * 0.05),
           "A priori diferente de 10%.")
    bayes_febre = (0.85 * 0.10) / (0.85 * 0.10 + 0.15 * 0.90)
    exigir(np.isclose(consultar(rede, {"Febre": "Sim"})["Sim"], bayes_febre),
           "Inferência com febre diverge do teorema de Bayes.")
    esperados = [0.10, 0.38636363636363635, 0.5900216919739696,
                 0.8436724565756824, 0.001881821603312006]
    for (_, evidencias), esperado in zip(EXPERIMENTOS, esperados):
        exigir(np.isclose(consultar(rede, evidencias)["Sim"], esperado, rtol=0, atol=1e-12),
               f"Resultado inesperado: {evidencias}.")
    # Quatro observáveis, cada um ausente da consulta, Não ou Sim: 3**4 = 81.
    for estados in product([None, *ESTADOS], repeat=len(OBSERVAVEIS)):
        evidencias = {v: e for v, e in zip(OBSERVAVEIS, estados) if e is not None}
        antes, depois = consultar(rede, evidencias), consultar(importada, evidencias)
        exigir(all(0 <= p <= 1 for p in antes.values()), "Posterior fora de [0, 1].")
        exigir(all(np.isclose(antes[e], depois[e], rtol=0, atol=1e-12) for e in ESTADOS),
               "Inferência alterada após importar o BIF.")
    invalidas = ["", "Febre", "Febre=Sim,", "Febre=Talvez", "Idade=Sim",
                 "Gripe=Sim", "Febre=Sim,Febre=Sim", "Febre=Sim,Febre=Não",
                 "=Sim", "Febre=Sim=Não"]
    for texto in invalidas:
        try:
            ler_evidencias(texto)
        except ValueError:
            continue
        raise ValueError(f"Entrada inválida aceita: {texto!r}.")
    # D-separação: sintomas independentes dado Gripe, dependentes sem condicioná-la.
    for a, b in [("Febre", "Tosse"), ("Febre", "DorMuscular"), ("Tosse", "DorMuscular")]:
        exigir(not rede.is_dconnected(a, b, observed=["Gripe"]), "Independência incorreta.")
        exigir(rede.is_dconnected(a, b), "Dependência marginal não representada.")
    print("Validação OK: estrutura, CPTs, Bayes, 81 consultas e BIF, 10 entradas inválidas e d-separação.")


def mostrar(nome, evidencias, distribuicao):
    descricao = ", ".join(f"{v}={e}" for v, e in evidencias.items()) or "nenhuma"
    print(f"\n{nome}\nEvidências: {descricao}")
    for estado, probabilidade in distribuicao.items():
        percentual = f"{probabilidade * 100:.6f}".replace(".", ",")
        print(f"P(Gripe={estado} | evidências) = {probabilidade:.10f} ({percentual}%)")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    grupo = parser.add_mutually_exclusive_group()
    grupo.add_argument("--demo", action="store_true", help="Executa experimentos, valida e gera BIF e PNG.")
    grupo.add_argument("--evidencias", help='Exemplo: "Febre=Sim,Tosse=Sim". Estados: Não, Sim.')
    args = parser.parse_args()
    try:
        evidencias = ler_evidencias(args.evidencias) if args.evidencias is not None else {}
        rede = construir_rede()
        print("Modelo educacional. Probabilidades hipotéticas, sem validação clínica.")
        if args.demo:
            importada = exportar_e_conferir(rede)
            validar_resultados(rede, importada)
            gerar_grafo(rede)
            for nome, evidencias in EXPERIMENTOS:
                mostrar(nome, evidencias, consultar(rede, evidencias))
            print(f"\nArtefatos gerados em: {PASTA}")
        else:
            mostrar("A priori", {}, consultar(rede))
            if evidencias:
                mostrar("Consulta", evidencias, consultar(rede, evidencias))
    except ValueError as erro:
        parser.error(str(erro))


if __name__ == "__main__":
    main()
