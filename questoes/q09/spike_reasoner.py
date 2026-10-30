"""Etapa 00: integração mínima com HermiT real, sem recomendador final."""
import argparse
from importlib.metadata import version
import json
import os
from pathlib import Path
import platform
import subprocess
import sys


def run(output: Path, inconsistent: bool = False) -> dict:
    import owlready2 as ow

    ow.JAVA_EXE = os.environ.get("JAVA_EXE", "java")
    java = subprocess.run([ow.JAVA_EXE, "-version"], capture_output=True,
                          text=True, check=True)
    jar = Path(ow.__file__).parent / "hermit" / "HermiT.jar"
    hermit = subprocess.run([ow.JAVA_EXE, "-cp", str(jar),
                             "org.semanticweb.HermiT.cli.CommandLine", "--version"],
                            capture_output=True, text=True, check=True)
    print(json.dumps({"python": platform.python_version(),
                      "owlready2": version("owlready2"), "reasoner": "HermiT bundled",
                      "hermit": hermit.stdout.strip(),
                      "java": java.stderr.strip() or java.stdout.strip()}, ensure_ascii=False), flush=True)
    world = ow.World()
    onto = world.get_ontology("https://example.org/etapa00.owl")
    with onto:
        class Recurso(ow.Thing):
            pass

        class nivel(ow.DataProperty, ow.FunctionalProperty):
            domain = [Recurso]
            range = [str]

        class RecursoBasico(Recurso):
            equivalent_to = [Recurso & nivel.value("basico")]

        class RecursoAvancado(Recurso):
            pass

        ow.AllDisjoint([RecursoBasico, RecursoAvancado])
        recurso = Recurso("exemplo", nivel="basico")
        if inconsistent:
            recurso.is_a.append(RecursoAvancado)

    before = sorted(c.name for c in recurso.is_a)
    if RecursoBasico in recurso.is_a:
        raise RuntimeError("Tipo alvo já assertado antes do reasoner")
    output.mkdir(parents=True, exist_ok=True)
    onto.save(file=str(output / "asserted.owl"), format="rdfxml")
    # HermiT verifica consistência e classifica. Nenhum tipo é acrescentado em Python.
    try:
        with onto:
            ow.sync_reasoner([onto], debug=2)
    except ow.OwlReadyInconsistentOntologyError:
        if not inconsistent:
            raise
        return {"status": "OK", "controle": "inconsistencia rejeitada por HermiT"}
    if inconsistent:
        raise RuntimeError("HermiT não rejeitou o controle inconsistente")
    after = sorted(c.name for c in recurso.is_a)
    if RecursoBasico not in recurso.is_a:
        raise RuntimeError("HermiT terminou sem o tipo inferido esperado")
    onto.save(file=str(output / "inferred.owl"), format="rdfxml")
    return {"status": "OK", "consistente": True, "antes": before, "depois": after,
            "novo_tipo": "RecursoBasico", "saida": str(output)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("_tmp/q09"))
    parser.add_argument("--inconsistent", action="store_true",
                        help="Controle negativo: esperar rejeição real por inconsistência")
    args = parser.parse_args()
    try:
        result = run(args.output, args.inconsistent)
    except (ImportError, OSError, subprocess.SubprocessError) as exc:
        print(f"BLOQUEADO: dependência Java/Owlready2 indisponível: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:
        print(f"FALHA: reasoner/inferência: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
