"""Controle didático de ventilação por inferência fuzzy de Mamdani."""

import argparse
import math

import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl


EXEMPLOS = (
    ("Ambiente frio", 15, 40),
    ("Ambiente ameno", 25, 50),
    ("Ambiente quente e úmido", 34, 85),
    ("Picos amena e média", 25, 55),
    ("Transição entre conjuntos", 30, 65),
    ("Limites mínimos", 0, 0),
    ("Frio e umidade máxima", 0, 100),
    ("Quente e umidade mínima", 40, 0),
    ("Limites máximos", 40, 100),
)


def construir_sistema():
    """Define os conjuntos e as nove combinações de regras da aplicação."""
    temperatura = ctrl.Antecedent(np.arange(0, 41, 1), "temperatura")
    umidade = ctrl.Antecedent(np.arange(0, 101, 1), "umidade")
    velocidade = ctrl.Consequent(
        np.arange(0, 101, 1), "velocidade", defuzzify_method="centroid"
    )

    temperatura["fria"] = fuzz.trapmf(temperatura.universe, [0, 0, 15, 22])
    temperatura["amena"] = fuzz.trimf(temperatura.universe, [18, 25, 32])
    temperatura["quente"] = fuzz.trapmf(temperatura.universe, [28, 34, 40, 40])

    umidade["baixa"] = fuzz.trapmf(umidade.universe, [0, 0, 30, 50])
    umidade["media"] = fuzz.trimf(umidade.universe, [35, 55, 75])
    umidade["alta"] = fuzz.trapmf(umidade.universe, [60, 80, 100, 100])

    velocidade["baixa"] = fuzz.trapmf(velocidade.universe, [0, 0, 20, 40])
    velocidade["media"] = fuzz.trimf(velocidade.universe, [30, 50, 70])
    velocidade["alta"] = fuzz.trapmf(velocidade.universe, [60, 80, 100, 100])
    velocidade.accumulation_method = np.fmax

    # Cada linha corresponde a uma temperatura e cada coluna a uma umidade.
    tabela = {
        "fria": ("baixa", "baixa", "baixa"),
        "amena": ("baixa", "media", "alta"),
        "quente": ("alta", "alta", "alta"),
    }
    regras = []
    for temp, saidas in tabela.items():
        for umid, saida in zip(("baixa", "media", "alta"), saidas):
            regras.append(
                ctrl.Rule(
                    temperatura[temp] & umidade[umid],
                    velocidade[saida],
                    label=f"{temp}_{umid}",
                    and_func=np.fmin,
                )
            )
    return ctrl.ControlSystem(regras)


def calcular_velocidade(temperatura, umidade, sistema=None):
    """Valida entradas escalares e calcula a saída sem recortar seus valores."""
    for nome, valor, limite, unidade in (
        ("Temperatura", temperatura, 40, "°C"),
        ("Umidade", umidade, 100, "%"),
    ):
        if not math.isfinite(valor) or not 0 <= valor <= limite:
            raise ValueError(
                f"{nome} deve ser um número finito entre 0 e {limite} {unidade}."
            )

    if sistema is None:
        sistema = construir_sistema()
    simulacao = ctrl.ControlSystemSimulation(sistema, clip_to_bounds=False)
    simulacao.input["temperatura"] = temperatura
    simulacao.input["umidade"] = umidade
    simulacao.compute()
    resultado = float(simulacao.output["velocidade"])
    if not math.isfinite(resultado) or not 0 <= resultado <= 100:
        raise RuntimeError("A inferência não produziu uma velocidade válida.")
    return resultado


def main():
    parser = argparse.ArgumentParser(
        description="Recomenda a velocidade de um ventilador por lógica fuzzy."
    )
    parser.add_argument("--temperatura", type=float, help="Temperatura entre 0 e 40 °C.")
    parser.add_argument("--umidade", type=float, help="Umidade relativa entre 0 e 100%%.")
    parser.add_argument(
        "--exemplos", action="store_true", help="Executa os cenários demonstrativos."
    )
    args = parser.parse_args()
    if args.exemplos:
        if args.temperatura is not None or args.umidade is not None:
            parser.error("Use --exemplos sem --temperatura e --umidade.")
        sistema = construir_sistema()
        for nome, temperatura, umidade in EXEMPLOS:
            velocidade = calcular_velocidade(temperatura, umidade, sistema)
            print(
                f"{nome}: {temperatura:g} °C, {umidade:g}% de umidade"
                f" -> velocidade: {velocidade:.2f}%"
            )
    else:
        if args.temperatura is None or args.umidade is None:
            parser.error("Informe --temperatura e --umidade, ou use --exemplos.")
        try:
            velocidade = calcular_velocidade(args.temperatura, args.umidade)
        except ValueError as erro:
            parser.error(str(erro))
        print(f"Velocidade recomendada: {velocidade:.2f}%")


if __name__ == "__main__":
    main()
