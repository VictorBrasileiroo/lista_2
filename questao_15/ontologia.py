"""OWL 2 e HermiT: projetos universitários inteiramente fictícios.

python ontologia.py --construir
python ontologia.py --demo
python ontologia.py --teste-inconsistencia
"""

import argparse
import hashlib
from importlib.metadata import version
import os
from pathlib import Path
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET

try:
    import owlready2 as owl
except ImportError:
    sys.exit("Owlready2 ausente. Execute: python -m pip install -r requirements.txt")


ARQUIVO = Path(__file__).resolve().with_name("ontologia.owl")
IRI = "https://example.org/ia/2026.2/projetos.owl#"
CLASSES = (
    "Pessoa", "Estudante", "EstudantePesquisador", "EstudantePesquisadorIA",
    "Professor", "Projeto", "ProjetoPesquisa", "ProjetoExtensao", "ProjetoAtivo",
    "ProjetoEncerrado", "AreaConhecimento", "AreaComputacao", "AreaIA",
)
INDIVIDUOS = (
    "estudante_ana", "estudante_bruno", "estudante_clara", "professor_alex",
    "projeto_ia", "projeto_redes", "projeto_extensao", "computacao", "ia", "pln",
)
PERGUNTAS = (
    ("Ana é EstudantePesquisador", "estudante_ana", "EstudantePesquisador"),
    ("Ana é EstudantePesquisadorIA", "estudante_ana", "EstudantePesquisadorIA"),
    ("Bruno é EstudantePesquisador", "estudante_bruno", "EstudantePesquisador"),
)


def exigir(condicao, mensagem):
    """Verificação executável também com python -O."""
    if not condicao:
        raise RuntimeError(mensagem)


def consultar(world, corpo, parametros=()):
    return list(world.sparql(f"PREFIX q: <{IRI}>\n" + corpo, list(parametros)))


def pertence(world, individuo, classe):
    # Consulta triplas e a hierarquia existente; não calcula definições OWL.
    # Owlready2 pode guardar apenas o tipo inferido mais específico de Ana.
    return bool(consultar(world, "SELECT ?i { ?? a/rdfs:subClassOf* ?? . "
                          "BIND(?? AS ?i) }", [individuo, classe, individuo]))


def relacao_transitiva(world, onto):
    # Caminho de comprimento 1: exige a tripla efetiva no banco, sem fecho Python
    # e sem caminho SPARQL transitivo que anteciparia o resultado do HermiT.
    return bool(consultar(world, "SELECT ?p { q:pln q:subAreaDe q:computacao . "
                          "BIND(q:pln AS ?p) }"))


def resultados(world, onto):
    valores = [pertence(world, onto[i], onto[c]) for _, i, c in PERGUNTAS]
    return valores + [relacao_transitiva(world, onto)]


def validar_declarada(world, onto):
    """Confere o modelo recarregado, incluindo ausência das conclusões alvo."""
    exigir(onto.base_iri == IRI, "IRI inesperada na ontologia.")
    exigir({c.name for c in onto.classes()} == set(CLASSES), "Classes inesperadas.")
    dominios = {
        "participaDe": (onto.Estudante, onto.Projeto),
        "temArea": (onto.Projeto, onto.AreaConhecimento),
        "orientadoPor": (onto.Projeto, onto.Professor),
        "subAreaDe": (onto.AreaConhecimento, onto.AreaConhecimento),
    }
    exigir({p.name for p in onto.object_properties()} == set(dominios),
           "Propriedades de objeto inesperadas.")
    for nome, (dominio, alcance) in dominios.items():
        exigir(onto[nome].domain == [dominio] and onto[nome].range == [alcance],
               f"Domínio ou alcance incorreto: {nome}.")
    exigir({p.name for p in onto.data_properties()} == {"nome", "titulo"},
           "Propriedades de dados inesperadas.")
    exigir({i.name for i in onto.individuals()} == set(INDIVIDUOS),
           "Indivíduos inesperados.")
    exigir(owl.TransitiveProperty in onto.subAreaDe.is_a,
           "subAreaDe precisa ser transitiva.")
    for filha, pai in (
        ("Estudante", "Pessoa"), ("Professor", "Pessoa"),
        ("EstudantePesquisador", "Estudante"),
        ("EstudantePesquisadorIA", "EstudantePesquisador"),
        ("ProjetoPesquisa", "Projeto"), ("ProjetoExtensao", "Projeto"),
        ("ProjetoAtivo", "Projeto"), ("ProjetoEncerrado", "Projeto"),
        ("AreaComputacao", "AreaConhecimento"), ("AreaIA", "AreaComputacao"),
    ):
        exigir(onto[pai] in onto[filha].is_a, f"Hierarquia incorreta: {filha}.")
    exigir(onto.EstudantePesquisador.equivalent_to == [
        onto.Estudante & onto.participaDe.some(onto.ProjetoPesquisa)],
        "Definição de EstudantePesquisador incorreta.")
    exigir(onto.EstudantePesquisadorIA.equivalent_to == [
        onto.Estudante & onto.participaDe.some(
            onto.ProjetoPesquisa & onto.temArea.some(onto.AreaIA))],
        "Definição de EstudantePesquisadorIA incorreta.")
    exigir(any(set(d.entities) == {onto.ProjetoAtivo, onto.ProjetoEncerrado}
               for d in onto.disjoint_classes()), "Disjunção dos estados ausente.")
    tipos = {
        "estudante_ana": [onto.Estudante], "estudante_bruno": [onto.Estudante],
        "estudante_clara": [onto.Estudante], "professor_alex": [onto.Professor],
        "projeto_ia": [onto.ProjetoPesquisa, onto.ProjetoAtivo],
        "projeto_redes": [onto.ProjetoPesquisa, onto.ProjetoAtivo],
        "projeto_extensao": [onto.ProjetoExtensao, onto.ProjetoAtivo],
        "computacao": [onto.AreaComputacao], "ia": [onto.AreaIA], "pln": [onto.AreaIA],
    }
    for nome, classes in tipos.items():
        exigir(set(onto[nome].is_a) == set(classes), f"Tipos declarados incorretos: {nome}.")
    for estudante, projeto, area in (
        ("estudante_ana", "projeto_ia", "ia"),
        ("estudante_bruno", "projeto_redes", "computacao"),
        ("estudante_clara", "projeto_extensao", "computacao"),
    ):
        exigir(onto[estudante].participaDe == [onto[projeto]], "Participação incorreta.")
        exigir(onto[projeto].temArea == [onto[area]], "Área do projeto incorreta.")
        exigir(onto[projeto].orientadoPor == [onto.professor_alex], "Orientação incorreta.")
    exigir(onto.pln.subAreaDe == [onto.ia] and onto.ia.subAreaDe == [onto.computacao],
           "Hierarquia declarada das áreas incorreta.")
    exigir(not consultar(world, "SELECT ?i { ?i a ?c . VALUES ?c "
                         "{ q:EstudantePesquisador q:EstudantePesquisadorIA } }"),
           "Há pesquisadores preenchidos manualmente.")
    exigir(not any(resultados(world, onto)), "Conclusões alvo já presentes antes do HermiT.")


def carregar():
    exigir(ARQUIVO.is_file(), "ontologia.owl ausente. Execute primeiro --construir.")
    raiz = ET.parse(ARQUIVO).getroot()
    exigir(raiz.tag == "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}RDF",
           "O arquivo precisa estar em RDF/XML.")
    world = owl.World()
    try:
        # fileobj evita ambiguidades de URI file:///C:/ no Windows.
        with ARQUIVO.open("rb") as origem:
            onto = world.get_ontology(IRI).load(fileobj=origem)
        validar_declarada(world, onto)
        return world, onto
    except Exception:
        world.close()
        raise


def construir():
    world = owl.World()
    try:
        onto = world.get_ontology(IRI)
        with onto:
            class Pessoa(owl.Thing): pass
            class Estudante(Pessoa): pass
            class EstudantePesquisador(Estudante): pass
            class EstudantePesquisadorIA(EstudantePesquisador): pass
            class Professor(Pessoa): pass
            class Projeto(owl.Thing): pass
            class ProjetoPesquisa(Projeto): pass
            class ProjetoExtensao(Projeto): pass
            class ProjetoAtivo(Projeto): pass
            class ProjetoEncerrado(Projeto): pass
            class AreaConhecimento(owl.Thing): pass
            class AreaComputacao(AreaConhecimento): pass
            class AreaIA(AreaComputacao): pass

            class participaDe(owl.ObjectProperty):
                domain = [Estudante]; range = [Projeto]
            class temArea(owl.ObjectProperty):
                domain = [Projeto]; range = [AreaConhecimento]
            class orientadoPor(owl.ObjectProperty):
                domain = [Projeto]; range = [Professor]
            class subAreaDe(owl.ObjectProperty, owl.TransitiveProperty):
                domain = [AreaConhecimento]; range = [AreaConhecimento]
            class nome(owl.DataProperty):
                domain = [Pessoa | AreaConhecimento]; range = [str]
            class titulo(owl.DataProperty):
                domain = [Projeto]; range = [str]

            EstudantePesquisador.equivalent_to = [
                Estudante & participaDe.some(ProjetoPesquisa)]
            EstudantePesquisadorIA.equivalent_to = [
                Estudante & participaDe.some(ProjetoPesquisa & temArea.some(AreaIA))]
            owl.AllDisjoint([ProjetoAtivo, ProjetoEncerrado])
            onto.metadata.comment.append(
                "Cenário inteiramente fictício para a Questão 15. "
                "Os estados dos projetos referem-se a um único instante.")

            computacao = AreaComputacao("computacao", nome=["Computação"])
            ia = AreaIA("ia", nome=["Inteligência artificial"], subAreaDe=[computacao])
            AreaIA("pln", nome=["Processamento de linguagem natural"], subAreaDe=[ia])
            professor = Professor("professor_alex", nome=["Alex, perfil fictício"])
            dados = (
                ("projeto_ia", "Pesquisa de agentes inteligentes", ProjetoPesquisa, ia),
                ("projeto_redes", "Pesquisa de redes universitárias", ProjetoPesquisa, computacao),
                ("projeto_extensao", "Oficinas de inclusão digital", ProjetoExtensao, computacao),
            )
            for identificador, texto, categoria, area in dados:
                projeto = categoria(identificador, titulo=[texto], temArea=[area],
                                    orientadoPor=[professor])
                projeto.is_a.append(ProjetoAtivo)
            for pessoa, projeto in (("ana", "projeto_ia"), ("bruno", "projeto_redes"),
                                    ("clara", "projeto_extensao")):
                Estudante(f"estudante_{pessoa}", nome=[f"{pessoa.title()}, perfil fictício"],
                          participaDe=[onto[projeto]])
        validar_declarada(world, onto)
        onto.save(file=str(ARQUIVO), format="rdfxml")
    finally:
        world.close()
    recarregado, _ = carregar()
    recarregado.close()
    print(f"RDF/XML salvo e recarregado: {ARQUIVO}")
    print("Verificados: 13 classes, 4 propriedades de objeto, 2 de dados e 10 indivíduos.")
    print("Classificações alvo e relação transitiva ausentes dos fatos declarados.")


def raciocinar(world, onto):
    java = os.environ.get("JAVA_EXE") or shutil.which("java")
    exigir(bool(java), "Java ausente. Configure PATH ou JAVA_EXE com o executável Java.")
    verificacao = subprocess.run([java, "-version"], capture_output=True, text=True, check=True)
    owl.JAVA_EXE = java
    print(f"Python {sys.version.split()[0]}; Owlready2 {version('owlready2')}")
    print((verificacao.stderr or verificacao.stdout).strip())
    print(f"Java: {java}")
    print("Executando HermiT real com infer_property_values=True...", flush=True)
    # Sem 'with onto': as conclusões ficam no grafo de inferências em memória.
    owl.sync_reasoner([onto], infer_property_values=True, debug=1)
    exigir(not list(world.inconsistent_classes()), "Há classes insatisfatíveis no modelo.")


def preservar_arquivo(original):
    exigir(hashlib.sha256(ARQUIVO.read_bytes()).digest() == original,
           "A ontologia principal foi alterada durante o raciocínio.")
    world, _ = carregar()
    world.close()
    print("Ontologia principal intacta: SHA-256 igual e fatos originais recarregados.")


def demonstrar():
    original = hashlib.sha256(ARQUIVO.read_bytes()).digest()
    world, onto = carregar()
    try:
        antes = resultados(world, onto)
        print("Antes do HermiT: as quatro conclusões alvo estão ausentes.", flush=True)
        raciocinar(world, onto)
        depois = resultados(world, onto)
        rotulos = [p[0] for p in PERGUNTAS] + ["PLN subAreaDe Computacao"]
        for rotulo, inicio, fim in zip(rotulos, antes, depois):
            exigir(not inicio and fim, f"Inferência esperada não produzida: {rotulo}.")
            print(f"VERIFICADO: {rotulo} | antes: não declarada | depois: inferida")
        print("Ontologia principal consistente; nenhuma classe insatisfatível.")
        exigir(not pertence(world, onto.estudante_bruno, onto.EstudantePesquisadorIA),
               "Classificação inesperada para Bruno neste cenário.")
        exigir(not pertence(world, onto.estudante_clara, onto.EstudantePesquisador),
               "Classificação inesperada para Clara neste cenário.")
        print("Bruno como pesquisador de IA e Clara como pesquisadora: "
              "classificações não inferidas, sem concluir suas negações.")
    finally:
        world.close()
        preservar_arquivo(original)


def testar_inconsistencia():
    original = hashlib.sha256(ARQUIVO.read_bytes()).digest()
    world, onto = carregar()
    try:
        print("Verificando a consistência da base antes da alteração negativa...", flush=True)
        raciocinar(world, onto)
        with onto:
            onto.projeto_ia.is_a.append(onto.ProjetoEncerrado)
        exigir(pertence(world, onto.projeto_ia, onto.ProjetoAtivo)
               and pertence(world, onto.projeto_ia, onto.ProjetoEncerrado),
               "O cenário negativo não contém os dois estados.")
        print("Cenário negativo em memória: projeto_ia ativo e encerrado.", flush=True)
        try:
            raciocinar(world, onto)
        except owl.OwlReadyInconsistentOntologyError:
            print("VERIFICADO: HermiT lançou OwlReadyInconsistentOntologyError, "
                  "resultado esperado do teste negativo.")
        else:
            raise RuntimeError("HermiT não detectou a inconsistência esperada.")
    finally:
        world.close()
        preservar_arquivo(original)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modos = parser.add_mutually_exclusive_group(required=True)
    modos.add_argument("--construir", action="store_true")
    modos.add_argument("--demo", action="store_true")
    modos.add_argument("--teste-inconsistencia", action="store_true")
    args = parser.parse_args()
    try:
        if args.construir:
            construir()
        elif args.demo:
            demonstrar()
        else:
            testar_inconsistencia()
    except Exception as erro:
        print(f"ERRO: {type(erro).__name__}: {erro}", file=sys.stderr)
        print("Não foi possível concluir a verificação. Nenhuma inferência é simulada.\n"
              "Reprodução no PowerShell, na pasta questao_15:\n"
              "  python -m pip install -r requirements.txt\n"
              "  java -version\n"
              "  python ontologia.py --construir\n"
              "  python ontologia.py --demo\n"
              "  python ontologia.py --teste-inconsistencia", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
