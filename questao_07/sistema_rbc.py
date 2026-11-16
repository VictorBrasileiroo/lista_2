"""Protótipo didático de RBC. Base artificial, sem validação clínica.

Somente biblioteca padrão. As orientações não são prescrições clínicas.
"""

import argparse
import difflib
import json
from pathlib import Path
import tempfile
import unicodedata


BASE = Path(__file__).resolve().with_name("casos.json")
AVISO = (
    "PROTÓTIPO EDUCACIONAL: casos fictícios, sem validação clínica.\n"
    "Similaridade não é probabilidade médica. Não substitui avaliação profissional.\n"
    "As orientações ilustrativas não constituem prescrições clínicas."
)


def normalizar(texto):
    texto = unicodedata.normalize("NFD", texto.strip().lower())
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return "_".join(texto.replace("_", " ").split())


def carregar_base(caminho=BASE):
    """Recusa estruturas inválidas sem sobrescrever a base original."""
    try:
        casos = json.loads(Path(caminho).read_text(encoding="utf-8"))
    except FileNotFoundError as erro:
        raise ValueError("Base JSON ausente. Restaure casos.json junto ao programa.") from erro
    except (OSError, UnicodeError, json.JSONDecodeError) as erro:
        raise ValueError("Não foi possível ler uma base JSON válida: " + str(erro)) from erro
    if not isinstance(casos, list) or not casos:
        raise ValueError("A base deve ser uma lista não vazia de casos.")
    ids = set()
    for caso in casos:
        if not isinstance(caso, dict) or set(caso) != {
            "id", "sintomas", "diagnostico", "tratamento"
        }:
            raise ValueError("Cada caso deve conter id, sintomas, diagnostico e tratamento.")
        identificador = caso["id"]
        if type(identificador) is not int or identificador < 1 or identificador in ids:
            raise ValueError("Os IDs devem ser inteiros positivos únicos.")
        ids.add(identificador)
        sintomas = caso["sintomas"]
        if (not isinstance(sintomas, list) or not sintomas
                or any(not isinstance(s, str) or not s or normalizar(s) != s for s in sintomas)
                or len(set(sintomas)) != len(sintomas)):
            raise ValueError("Sintomas devem ser uma lista não vazia, normalizada e sem repetições.")
        for campo in ("diagnostico", "tratamento"):
            if not isinstance(caso[campo], str) or not caso[campo].strip():
                raise ValueError("Diagnóstico e tratamento devem ser textos não vazios.")
    return casos


def interpretar_sintomas(texto, casos):
    vocabulario = {s for caso in casos for s in caso["sintomas"]}
    partes = texto.split(",")
    if any(not p.strip() for p in partes):
        raise ValueError("Informe sintomas não vazios separados por vírgulas.")
    sintomas = {normalizar(p) for p in partes}
    desconhecidos = sintomas - vocabulario
    if desconhecidos:
        mensagens = []
        for sintoma in sorted(desconhecidos):
            sugestoes = difflib.get_close_matches(sintoma, sorted(vocabulario), n=1)
            dica = " (talvez: " + sugestoes[0] + ")" if sugestoes else ""
            mensagens.append(sintoma + dica)
        raise ValueError("Sintomas desconhecidos: " + ", ".join(mensagens)
                         + ". Corrija a entrada; nenhum termo foi descartado.")
    return sintomas


def jaccard(a, b):
    a, b = set(a), set(b)
    uniao = a | b
    return len(a & b) / len(uniao) if uniao else 0.0


def recuperar(sintomas, casos):
    resultados = [(jaccard(sintomas, c["sintomas"]), c) for c in casos]
    return sorted(resultados, key=lambda item: (-item[0], item[1]["id"]))


def reutilizar(resultados):
    if not resultados or resultados[0][0] == 0:
        return None
    pontuacao, caso = resultados[0]
    diagnosticos = sorted({c["diagnostico"] for p, c in resultados if p == pontuacao})
    return {"caso": caso, "similaridade": pontuacao, "empatados": diagnosticos}


def exibir_consulta(sintomas, casos):
    print("\nConsulta: " + ", ".join(sorted(sintomas)))
    resultados = recuperar(sintomas, casos)
    print("Três casos mais semelhantes (desempate pelo menor ID):")
    for pontuacao, caso in resultados[:3]:
        print(f"  ID {caso['id']:02d} | {caso['diagnostico']} | "
              f"Jaccard = {pontuacao:.4f} ({pontuacao:.2%})")
        print("    Sintomas: " + ", ".join(caso["sintomas"]))
    sugestao = reutilizar(resultados)
    if sugestao is None:
        print("Não existe correspondência suficiente. Nenhum diagnóstico será sugerido.")
        return None
    caso = sugestao["caso"]
    if len(sugestao["empatados"]) > 1:
        print("AMBIGUIDADE na maior similaridade: " + ", ".join(sugestao["empatados"]))
        print("O ID apenas determina a ordem; não resolve a ambiguidade clínica.")
    print("Hipótese educacional do primeiro caso: " + caso["diagnostico"])
    print("Orientação ilustrativa: " + caso["tratamento"])
    print("Sintomas compartilhados: " + ", ".join(sorted(set(caso["sintomas"]) & sintomas)))
    print("A pontuação mede sobreposição de conjuntos, não confiança clínica.")
    return sugestao


def revisar(sugestao, acao, casos, diagnostico=None):
    """A revisão é uma decisão de demonstração, sem validação médica real."""
    if acao == "3":
        return None
    if acao not in ("1", "2"):
        raise ValueError("Opção de revisão inválida. Escolha 1, 2 ou 3.")
    if sugestao is None:
        raise ValueError("Não existe sugestão para revisar.")
    if acao == "1":
        caso = sugestao["caso"]
    else:
        candidatos = sorted((c for c in casos if c["diagnostico"] == diagnostico),
                            key=lambda c: c["id"])
        if not candidatos or diagnostico == sugestao["caso"]["diagnostico"]:
            raise ValueError("Selecione outra condição existente na base.")
        caso = candidatos[0]
    return {"diagnostico": caso["diagnostico"], "tratamento": caso["tratamento"],
            "revisado": True}


def reter(caminho, sintomas, revisao):
    if not revisao or revisao.get("revisado") is not True:
        raise ValueError("Retenção exige confirmação ou correção da revisão.")
    casos = carregar_base(caminho)
    sintomas = interpretar_sintomas(",".join(sorted(sintomas)), casos)
    condicao = revisao.get("diagnostico")
    orientacao = revisao.get("tratamento")
    if not any(c["diagnostico"] == condicao and c["tratamento"] == orientacao for c in casos):
        raise ValueError("Diagnóstico e orientação devem corresponder a um caso da base.")
    novo = {"id": max(c["id"] for c in casos) + 1, "sintomas": sorted(sintomas),
            "diagnostico": condicao, "tratamento": orientacao}
    casos.append(novo)
    # Serializa antes de abrir para escrita, evitando truncamento por erro de conversão.
    conteudo = json.dumps(casos, ensure_ascii=False, indent=2) + "\n"
    Path(caminho).write_text(conteudo, encoding="utf-8")
    return novo


def demonstrar(caminho=BASE):
    original = Path(caminho).read_bytes()
    casos = carregar_base(caminho)
    print("\nCENÁRIO A: caso semelhante")
    exibir_consulta(interpretar_sintomas("febre, tosse, dor no corpo, fadiga", casos), casos)
    print("\nCENÁRIO B: caso ambíguo")
    exibir_consulta(interpretar_sintomas("coriza, espirros", casos), casos)
    print("Sintomas compartilhados e pesos iguais impedem distinguir as condições empatadas.")
    print("\nCENÁRIO C: revisão e retenção em cópia temporária")
    # O diretório temporário fica junto ao programa e é removido ao final.
    with tempfile.TemporaryDirectory(prefix="demo_", dir=Path(caminho).parent) as pasta:
        copia = Path(pasta) / "casos.json"
        copia.write_bytes(original)
        sintomas = interpretar_sintomas("febre, tosse, fadiga", casos)
        sugestao = exibir_consulta(sintomas, casos)
        revisao = revisar(sugestao, "1", casos)
        print("Operador simulado: confirmação de " + revisao["diagnostico"])
        print("Confirmação didática, sem validação médica real.")
        novo = reter(copia, sintomas, revisao)
        print(f"Retido ID {novo['id']}; encerrada a etapa de escrita.")
        recarregados = carregar_base(copia)
        print(f"Base relida do disco: {len(recarregados)} casos. Nova consulta:")
        exibir_consulta(sintomas, recarregados)
        assert recuperar(sintomas, recarregados)[0][1]["id"] == novo["id"]
    assert Path(caminho).read_bytes() == original
    print("\nDemonstração concluída; base original preservada byte a byte.")


def interagir(caminho=BASE):
    while True:
        casos = carregar_base(caminho)
        print("\nVocabulário: " + ", ".join(sorted({s for c in casos for s in c["sintomas"]})))
        texto = input("Sintomas separados por vírgulas (ou sair): ")
        if normalizar(texto) == "sair":
            return
        try:
            sintomas = interpretar_sintomas(texto, casos)
        except ValueError as erro:
            print(erro)
            continue
        sugestao = exibir_consulta(sintomas, casos)
        if sugestao is None:
            continue
        while True:
            acao = input("Revisão: 1 confirmar, 2 corrigir, 3 rejeitar/cancelar: ").strip()
            diagnostico = None
            if acao == "2":
                condicoes = sorted({c["diagnostico"] for c in casos}
                                   - {sugestao["caso"]["diagnostico"]})
                for numero, condicao in enumerate(condicoes, 1):
                    print(f"  {numero}: {condicao}")
                escolha = input("Número da outra condição (0 cancela): ").strip()
                if escolha == "0":
                    acao = "3"
                elif escolha.isdecimal() and 1 <= int(escolha) <= len(condicoes):
                    diagnostico = condicoes[int(escolha) - 1]
            try:
                revisao = revisar(sugestao, acao, casos, diagnostico)
                break
            except ValueError as erro:
                print(erro)
        if revisao is None:
            print("Revisão cancelada. Nenhum caso armazenado.")
            continue
        print("Revisão didática: " + revisao["diagnostico"])
        print("Orientação correspondente: " + revisao["tratamento"])
        print("A decisão do operador não constitui validação médica real.")
        while True:
            salvar = normalizar(input("Armazenar o caso revisado? (s/n): "))
            if salvar in ("s", "n"):
                break
            print("Opção inválida. Digite s ou n.")
        if salvar == "s":
            novo = reter(caminho, sintomas, revisao)
            print(f"Caso ID {novo['id']} armazenado no JSON.")
        else:
            print("Caso não armazenado.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--demo", action="store_true", help="Executa três cenários em cópia temporária.")
    args = parser.parse_args()
    print(AVISO)
    try:
        carregar_base()
        if args.demo:
            demonstrar()
        else:
            interagir()
    except (ValueError, OSError) as erro:
        print("Erro: " + str(erro))
        return 1
    except (EOFError, KeyboardInterrupt):
        print("\nExecução encerrada. Consultas pendentes não foram armazenadas.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
