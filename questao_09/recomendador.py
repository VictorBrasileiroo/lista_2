"""Recomendação educacional com OWL 2, SPARQL nativo e HermiT real.

Construção: python recomendador.py --construir
Demonstração: python recomendador.py --demo
Consulta: python recomendador.py --tema ia --nivel basico --formato digital
"""

import argparse
import hashlib
import os
from pathlib import Path
import shutil
import sys

import owlready2 as ow


ARQUIVO = Path(__file__).resolve().with_name("ontologia.owl")
IRI = "https://example.org/ia/2026.2/livros.owl#"
PREFIXO = f"PREFIX q: <{IRI}>\n"
TEMAS = {"ia": "inteligencia_artificial", "computacao": "computacao",
         "programacao": "programacao", "literatura": "literatura",
         "aprendizado_maquina": "aprendizado_maquina", "pln": "pln"}
NIVEIS = {"basico": "LivroIntrodutorio", "avancado": "LivroAvancado"}
FORMATOS = {"digital": "LivroDigital", "fisico": "LivroFisico"}


def exigir(condicao, mensagem):
    """Não usar assert: as verificações devem funcionar mesmo com python -O."""
    if not condicao:
        raise RuntimeError(mensagem)


def construir():
    """Gera somente fatos declarados. Nenhum reasoner é chamado aqui."""
    world = ow.World()
    try:
        onto = world.get_ontology(IRI)
        with onto:
            class Publicacao(ow.Thing): pass
            class Livro(Publicacao): pass
            class LivroTecnico(Livro): pass
            class LivroFiccao(Livro): pass
            class LivroIntrodutorio(Livro): pass
            class LivroAvancado(Livro): pass
            class LivroDigital(Livro): pass
            class LivroFisico(Livro): pass
            class LivroIA(LivroTecnico): pass
            class LivroIntrodutorioIA(LivroIA, LivroIntrodutorio): pass
            class Autor(ow.Thing): pass
            class Leitor(ow.Thing): pass
            class Tema(ow.Thing): pass
            class TemaComputacao(Tema): pass
            class TemaIA(TemaComputacao): pass
            class TemaProgramacao(TemaComputacao): pass
            class TemaLiteratura(Tema): pass
            class Nivel(ow.Thing): pass
            class NivelBasico(Nivel): pass
            class NivelAvancado(Nivel): pass
            class Formato(ow.Thing): pass
            class FormatoDigital(Formato): pass
            class FormatoFisico(Formato): pass
            class Editora(ow.Thing): pass

            class temAutor(ow.ObjectProperty):
                domain = [Livro]; range = [Autor]
            class autorDe(ow.ObjectProperty):
                domain = [Autor]; range = [Livro]; inverse_property = temAutor
            class abordaTema(ow.ObjectProperty):
                domain = [Livro]; range = [Tema]
            class temNivel(ow.ObjectProperty):
                domain = [Livro]; range = [Nivel]
            class temFormato(ow.ObjectProperty):
                domain = [Livro]; range = [Formato]
            class publicadoPor(ow.ObjectProperty):
                domain = [Publicacao]; range = [Editora]
            class prefereTema(ow.ObjectProperty):
                domain = [Leitor]; range = [Tema]
            class prefereNivel(ow.ObjectProperty):
                domain = [Leitor]; range = [Nivel]
            class prefereFormato(ow.ObjectProperty):
                domain = [Leitor]; range = [Formato]
            class subTemaDe(ow.ObjectProperty, ow.TransitiveProperty):
                domain = [Tema]; range = [Tema]
            class relacionadoA(ow.ObjectProperty, ow.SymmetricProperty):
                domain = [Tema]; range = [Tema]
            class titulo(ow.DataProperty):
                domain = [Publicacao]; range = [str]
            class nome(ow.DataProperty):
                domain = [Autor | Leitor | Tema | Nivel | Formato | Editora]
                range = [str]
            class anoPublicacao(ow.DataProperty):
                domain = [Publicacao]; range = [int]
            class idioma(ow.DataProperty):
                domain = [Publicacao]; range = [str]
            class numeroPaginas(ow.DataProperty):
                domain = [Livro]; range = [int]
            class isbn(ow.DataProperty):
                domain = [Livro]; range = [str]
            class descricao(ow.DataProperty):
                domain = [Publicacao]; range = [str]

            LivroTecnico.equivalent_to = [Livro & abordaTema.some(TemaComputacao)]
            LivroFiccao.equivalent_to = [Livro & abordaTema.some(TemaLiteratura)]
            LivroIntrodutorio.equivalent_to = [Livro & temNivel.some(NivelBasico)]
            LivroAvancado.equivalent_to = [Livro & temNivel.some(NivelAvancado)]
            LivroDigital.equivalent_to = [Livro & temFormato.some(FormatoDigital)]
            LivroFisico.equivalent_to = [Livro & temFormato.some(FormatoFisico)]
            LivroIA.equivalent_to = [Livro & abordaTema.some(TemaIA)]
            LivroIntrodutorioIA.equivalent_to = [LivroIA & LivroIntrodutorio]
            Livro.is_a.extend([temAutor.some(Autor), abordaTema.some(Tema),
                              temNivel.some(Nivel), temFormato.some(Formato),
                              publicadoPor.some(Editora)])
            ow.AllDisjoint([Publicacao, Autor, Leitor, Tema, Nivel, Formato, Editora])
            ow.AllDisjoint([LivroTecnico, LivroFiccao])
            ow.AllDisjoint([TemaComputacao, TemaLiteratura])
            ow.AllDisjoint([NivelBasico, NivelAvancado])
            ow.AllDisjoint([FormatoDigital, FormatoFisico])

            computacao = TemaComputacao("computacao", nome=["Computação"])
            ia = TemaIA("inteligencia_artificial", nome=["Inteligência artificial"], subTemaDe=[computacao])
            am = TemaIA("aprendizado_maquina", nome=["Aprendizado de máquina"], subTemaDe=[ia])
            pln = TemaIA("pln", nome=["Processamento de linguagem natural"], subTemaDe=[am])
            programacao = TemaProgramacao("programacao", nome=["Programação"], subTemaDe=[computacao])
            literatura = TemaLiteratura("literatura", nome=["Literatura"])
            ia.relacionadoA = [programacao]
            basico = NivelBasico("basico", nome=["Básico"])
            avancado = NivelAvancado("avancado", nome=["Avançado"])
            digital = FormatoDigital("digital", nome=["Digital"])
            fisico = FormatoFisico("fisico", nome=["Físico"])
            autores = [Autor(f"autor_{i}", nome=[n]) for i, n in enumerate(
                ["Ana Prado", "Bruno Reis", "Clara Luz", "Davi Melo"], 1)]
            editoras = [Editora("editora_1", nome=["Editora Horizonte Didático"]),
                        Editora("editora_2", nome=["Editora Trilhas do Saber"])]
            # Toda a base bibliográfica é fictícia; os códigos não são ISBN reais.
            dados = [
                ("livro_1", "Primeiros passos em inteligência artificial", ia, basico, digital, 180),
                ("livro_2", "Linguagem natural para iniciantes", pln, basico, digital, 210),
                ("livro_3", "Aprendizado de máquina em profundidade", am, avancado, digital, 420),
                ("livro_4", "Inteligência artificial no papel", ia, basico, fisico, 200),
                ("livro_5", "Programação desde o começo", programacao, basico, digital, 240),
                ("livro_6", "Algoritmos e programação avançada", programacao, avancado, fisico, 380),
                ("livro_7", "Contos da biblioteca azul", literatura, basico, fisico, 160),
                ("livro_8", "Narrativas e labirintos", literatura, avancado, digital, 290),
            ]
            for i, (ident, titulo_, tema, nivel, formato, paginas) in enumerate(dados):
                Livro(ident, titulo=[titulo_], abordaTema=[tema], temNivel=[nivel],
                      temFormato=[formato], temAutor=[autores[i % 4]],
                      publicadoPor=[editoras[i % 2]], anoPublicacao=[2024 + i % 3],
                      idioma=["pt-BR"], numeroPaginas=[paginas], isbn=[f"FICT-{i+1:03}"],
                      descricao=[f"Obra fictícia para estudo de {tema.nome[0].lower()}."])
            Leitor("leitora_ana", nome=["Ana, perfil ilustrativo"], prefereTema=[ia],
                   prefereNivel=[basico], prefereFormato=[digital])
            Leitor("leitor_caio", nome=["Caio, perfil ilustrativo"], prefereTema=[programacao],
                   prefereNivel=[avancado], prefereFormato=[fisico])
        onto.save(file=str(ARQUIVO), format="rdfxml")
    finally:
        world.close()
    print(f"Ontologia declarada salva em {ARQUIVO}")


def carregar():
    world = ow.World()
    try:
        # fileobj evita a conversão incorreta de file:///C:/ pelo Owlready2 no Windows.
        with ARQUIVO.open("rb") as origem:
            onto = world.get_ontology(IRI).load(fileobj=origem)
        exigir(onto.base_iri == IRI, "IRI inesperada na ontologia carregada.")
        return world, onto
    except Exception:
        world.close()
        raise


def consultar(world, corpo, parametros=()):
    return list(world.sparql(PREFIXO + corpo, list(parametros)))


def classes(world, individuo):
    return {c.name for (c,) in consultar(world, """
        SELECT DISTINCT ?c { ?? a ?c . FILTER(isIRI(?c)) }
    """, [individuo]) if c.iri.startswith(IRI)}


def relaciona(world, origem, destino):
    return bool(consultar(world, "SELECT ?a { ?? q:subTemaDe ?? . BIND(?? AS ?a) }",
                          [origem, destino, origem]))


def raciocinar(world, onto):
    java = os.environ.get("JAVA_EXE") or shutil.which("java")
    exigir(bool(java), "Java não encontrado. Configure PATH ou JAVA_EXE com o executável Java.")
    ow.JAVA_EXE = java
    # HermiT recebe apenas esta ontologia; inferências ficam no grafo separado padrão.
    # debug=1 permite auditar no stderr o comando Java realmente executado.
    ow.sync_reasoner([onto], infer_property_values=True, debug=1)
    exigir(not list(world.inconsistent_classes()), "Há classes insatisfatíveis na ontologia.")


def recomendar(world, onto, tema, nivel, formato):
    """Seleção SPARQL exige classes cuja pertinência foi inferida pelo HermiT."""
    return consultar(world, """
        SELECT DISTINCT ?livro ?titulo ?tema ?nomeTema ?nomeNivel ?nomeFormato ?autor
        WHERE {
          ?livro a/rdfs:subClassOf* ??1 ; a/rdfs:subClassOf* ??2 ;
                 q:titulo ?titulo ; q:abordaTema ?tema ;
                 q:temNivel ??3 ; q:temFormato ??4 ; q:temAutor ?a .
          ?tema q:subTemaDe* ??5 ; q:nome ?nomeTema .
          ??3 q:nome ?nomeNivel . ??4 q:nome ?nomeFormato . ?a q:nome ?autor .
        } ORDER BY ?titulo ?autor
    """, [onto[NIVEIS[nivel]], onto[FORMATOS[formato]], onto[nivel],
          onto[formato], onto[TEMAS[tema]]])


def exibir_recomendacoes(world, onto, tema, nivel, formato, antes=None):
    linhas = recomendar(world, onto, tema, nivel, formato)
    print(f"\nPreferências: tema={tema}, nível={nivel}, formato={formato}")
    if not linhas:
        print("Nenhum livro compatível encontrado na base de conhecimento.")
    for livro, titulo_, tema_livro, nome_tema, nome_nivel, nome_formato, autor in linhas:
        print(f"- {titulo_} ({autor})")
        print(f"  Fatos consultados: tema={nome_tema}; nível={nome_nivel}; formato={nome_formato}.")
        if tema_livro != onto[TEMAS[tema]]:
            print(f"  Hierarquia: {tema_livro.name} subTemaDe {TEMAS[tema]} (caminho semântico).")
        obtidas = classes(world, livro)
        relevantes = obtidas.intersection({NIVEIS[nivel], FORMATOS[formato], "LivroIntrodutorioIA"})
        novas = relevantes - antes[livro.name] if antes is not None else relevantes
        print("  Classificação após HermiT: " + ", ".join(sorted(novas)) + ".")
    return linhas


def teste_inconsistencia():
    world, onto = carregar()
    try:
        # Alteração somente neste World em memória. Não chamar save().
        onto.livro_1.is_a.extend([onto.LivroTecnico, onto.LivroFiccao])
        try:
            ow.sync_reasoner([onto], infer_property_values=True, debug=1)
        except ow.OwlReadyInconsistentOntologyError:
            print("Teste negativo aprovado: HermiT detectou LivroTecnico ∩ LivroFiccao.")
            return
        raise RuntimeError("Teste negativo falhou: HermiT não detectou a inconsistência.")
    finally:
        world.close()


def demo(world, onto):
    original = hashlib.sha256(ARQUIVO.read_bytes()).hexdigest()
    livros = sorted(onto.Livro.instances(), key=lambda x: x.name)
    contagens = (len(list(onto.classes())), len(list(onto.object_properties())),
                 len(list(onto.data_properties())), len(list(onto.individuals())))
    exigir(contagens[0] >= 10 and sum(contagens[1:3]) >= 15, "Contagens insuficientes.")
    exigir(len(livros) >= 8, "Base com menos de oito livros.")
    exigir(all(list(p.get_relations()) for p in onto.properties()), "Propriedade sem uso.")
    print(f"Estrutura carregada: {contagens[0]} classes, {contagens[1]} propriedades de objeto, "
          f"{contagens[2]} de dados, {contagens[3]} indivíduos; {len(livros)} livros.")
    antes = {livro.name: classes(world, livro) for livro in livros}
    exigir(all(c == {"Livro"} for c in antes.values()), "Há tipos especializados já declarados.")
    for livro in livros[:2]:
        print(f"Antes: {livro.name} = {sorted(antes[livro.name])}")
    exigir(not relaciona(world, onto.pln, onto.inteligencia_artificial),
           "Relação transitiva de teste já declarada.")
    previas = recomendar(world, onto, "ia", "basico", "digital")
    exigir(not previas, "A consulta deveria depender das classes inferidas.")
    print(f"Consulta de recomendação antes do HermiT: {len(previas)} resultados.")
    raciocinar(world, onto)
    print("Consistência principal confirmada por HermiT; nenhuma classe insatisfatível.")
    for livro in livros:
        depois = classes(world, livro)
        print(f"Após: {livro.name}; novos tipos RDF = {sorted(depois - antes[livro.name])}")
    for livro in livros[:2]:
        exigir("LivroIntrodutorioIA" in classes(world, livro), "Classificação IA não produzida.")
    exigir(relaciona(world, onto.pln, onto.inteligencia_artificial),
           "HermiT não materializou a relação transitiva esperada.")
    print("Relação ausente antes e presente após: pln subTemaDe inteligencia_artificial.")
    print("\nSPARQL 1: livros e autores")
    autores = consultar(world, """SELECT DISTINCT ?titulo ?nome {
        ?l a/rdfs:subClassOf* q:Livro ; q:titulo ?titulo ; q:temAutor ?a .
        ?a q:nome ?nome . } ORDER BY ?titulo""")
    exigir(len(autores) == 8, "Consulta de livros e autores inesperada.")
    for linha in autores:
        print(" | ".join(map(str, linha)))
    print("\nSPARQL 2: tema IA, incluindo subtemas")
    por_tema = consultar(world, """SELECT DISTINCT ?titulo {
        ?l q:titulo ?titulo ; q:abordaTema ?tema .
        ?tema q:subTemaDe* q:inteligencia_artificial . } ORDER BY ?titulo""")
    exigir(len(por_tema) == 4, "Consulta de tema inesperada.")
    for (titulo_,) in por_tema: print(titulo_)
    print("\nSPARQL 3: classe inferida LivroIntrodutorioIA")
    introdutorios = consultar(world, """SELECT DISTINCT ?titulo {
        ?l a/rdfs:subClassOf* q:LivroIntrodutorioIA ; q:titulo ?titulo .
        } ORDER BY ?titulo""")
    exigir(len(introdutorios) == 3, "Consulta de classe inferida inesperada.")
    for (titulo_,) in introdutorios: print(titulo_)
    print("\nSPARQL 4: seleção e características para justificativa")
    resultado = exibir_recomendacoes(world, onto, "ia", "basico", "digital", antes)
    exigir({r[0].name for r in resultado} == {"livro_1", "livro_2"}, "Recomendação inesperada.")
    segundo = exibir_recomendacoes(world, onto, "programacao", "avancado", "fisico", antes)
    exigir({r[0].name for r in segundo} == {"livro_6"}, "Segundo cenário inesperado.")
    vazio = exibir_recomendacoes(world, onto, "literatura", "basico", "digital", antes)
    exigir(not vazio, "Cenário sem resultados inesperado.")
    teste_inconsistencia()
    exigir(hashlib.sha256(ARQUIVO.read_bytes()).hexdigest() == original,
           "O arquivo de origem foi alterado durante a demonstração.")
    print("SHA-256 preservado: " + original)
    print("Todas as verificações estruturais e de execução da demo foram aprovadas.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modo = parser.add_mutually_exclusive_group()
    modo.add_argument("--construir", action="store_true", help="Recriar o OWL com fatos declarados.")
    modo.add_argument("--demo", action="store_true", help="Executar a demonstração e validação completas.")
    parser.add_argument("--tema", choices=sorted(TEMAS))
    parser.add_argument("--nivel", choices=sorted(NIVEIS))
    parser.add_argument("--formato", choices=sorted(FORMATOS))
    args = parser.parse_args()
    preferencias = [args.tema, args.nivel, args.formato]
    if (args.demo or args.construir) and any(preferencias):
        parser.error("Use --demo/--construir separadamente das preferências.")
    if not (args.demo or args.construir) and not all(preferencias):
        parser.error("Informe --tema, --nivel e --formato, ou use --demo/--construir.")
    try:
        if args.construir:
            construir()
            return 0
        if not ARQUIVO.is_file():
            parser.error("ontologia.owl não encontrada. Execute --construir primeiro.")
        world, onto = carregar()
        try:
            if args.demo:
                demo(world, onto)
            else:
                antes = {livro.name: classes(world, livro) for livro in onto.Livro.instances()}
                raciocinar(world, onto)
                exibir_recomendacoes(world, onto, args.tema, args.nivel, args.formato, antes)
        finally:
            world.close()
        return 0
    except (ow.OwlReadyJavaError, ow.OwlReadyInconsistentOntologyError,
            OSError, RuntimeError) as erro:
        print(f"Falha na execução: {erro}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
