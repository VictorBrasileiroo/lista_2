"""KNN categórico com K = 3 e avaliação Leave-One-Out, sem dependências externas."""

import csv
from collections import Counter
from pathlib import Path


K = 3
ATRIBUTOS = (
    "historia_credito",
    "divida",
    "garantia",
    "renda",
    "emprego",
    "comprometimento",
)


def carregar_dados(caminho):
    with caminho.open(encoding="utf-8", newline="") as arquivo:
        leitor = csv.DictReader(arquivo)
        assert leitor.fieldnames == ["id", *ATRIBUTOS, "risco"]
        dados = list(leitor)

    assert len(dados) == 30, "A base deve conter exatamente 30 instâncias."
    assert [item["id"] for item in dados] == [f"E{i}" for i in range(1, 31)]
    assert Counter(item["risco"] for item in dados) == {
        "Alto": 10, "Moderado": 10, "Baixo": 10
    }
    assert all(set(item) == {"id", *ATRIBUTOS, "risco"} for item in dados)
    assert all(all(item[campo] for campo in ATRIBUTOS) for item in dados)
    assert all(distancia_hamming(item, item) == 0 for item in dados)
    return dados


def distancia_hamming(a, b):
    """Conta diferenças apenas nos seis atributos, sem id nem risco."""
    return sum(a[atributo] != b[atributo] for atributo in ATRIBUTOS)


def ordenar_candidatos(alvo, dados):
    """Exclui o alvo e ordena por distância e número da instância."""
    candidatos = [
        (distancia_hamming(alvo, item), item)
        for item in dados
        if item["id"] != alvo["id"]
    ]
    return sorted(candidatos, key=lambda par: (par[0], int(par[1]["id"][1:])))


def votar(vizinhos):
    votos = Counter(item["risco"] for _, item in vizinhos)
    somas = {
        classe: sum(d for d, item in vizinhos if item["risco"] == classe)
        for classe in votos
    }
    prevista = min(votos, key=lambda classe: (-votos[classe], somas[classe], classe))
    return prevista, votos, somas


def classificar(alvo, dados):
    candidatos = ordenar_candidatos(alvo, dados)
    assert len(candidatos) >= K
    vizinhos = candidatos[:K]
    assert all(item["id"] != alvo["id"] for _, item in candidatos)
    prevista, votos, somas = votar(vizinhos)
    return prevista, vizinhos, votos, somas


def leave_one_out(dados):
    resultados = []
    for alvo in dados:
        candidatos = ordenar_candidatos(alvo, dados)
        assert len(candidatos) == 29
        prevista, vizinhos, _, _ = classificar(alvo, dados)
        resultados.append((alvo, prevista, vizinhos))
    return resultados


def main():
    dados = carregar_dados(Path(__file__).with_name("dados.csv"))
    print("Validação: 30 instâncias; 10 por classe; distância própria zero.")
    print("K = 3; Hamming não normalizada sobre seis atributos.")

    alvo = dados[0]
    print("\nDemonstração de E1: distâncias às outras 29 instâncias")
    for item in dados:
        if item["id"] != alvo["id"]:
            print(f'{item["id"]:>3}: {distancia_hamming(alvo, item)}')

    prevista, vizinhos, votos, somas = classificar(alvo, dados)
    print("\nTrês vizinhos de E1 (id, distância, classe):")
    for distancia, item in vizinhos:
        print(f'{item["id"]}: {distancia}, {item["risco"]}')
    print("Votação (classe, votos, soma das distâncias):")
    for classe in ("Alto", "Moderado", "Baixo"):
        print(f'{classe}: {votos.get(classe, 0)}, {somas.get(classe, 0)}')
    print(f'Previsão: {prevista}; classe real: {alvo["risco"]}.')

    resultados = leave_one_out(dados)
    erros = [(alvo, prevista, vizinhos) for alvo, prevista, vizinhos in resultados
             if prevista != alvo["risco"]]
    acertos = len(resultados) - len(erros)
    print("\nLeave-One-Out: próprio alvo excluído em todas as 30 classificações.")
    print(f"Acertos: {acertos}; erros: {len(erros)}; "
          f"acurácia: {acertos / len(resultados):.2%}.")
    print("Instâncias classificadas incorretamente (id, real, prevista, vizinhos):")
    for alvo, prevista, vizinhos in erros:
        resumo = ", ".join(
            f'{item["id"]} (d={d}, {item["risco"]})' for d, item in vizinhos
        )
        print(f'{alvo["id"]}: {alvo["risco"]} -> {prevista}; {resumo}')


if __name__ == "__main__":
    main()
