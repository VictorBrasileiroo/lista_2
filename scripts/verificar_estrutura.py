"""Verificação APENAS ESTRUTURAL do scaffold; não aprova nenhuma questão."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = [ROOT / "questoes" / f"q{i:02d}" / "README.md" for i in range(1, 16)]
EXPECTED += [ROOT / name for name in ["AGENTS.md", "README.md", "docs/01-matriz-de-requisitos.md", "docs/03-validacao.md", "prompts/00-inicial-codex.md"]]
missing = [str(p.relative_to(ROOT)) for p in EXPECTED if not p.is_file()]
if missing:
    print("FALHA: estrutura incompleta:\n" + "\n".join(missing))
    raise SystemExit(1)
print("OK: estrutura inicial presente (15 pastas de questões).")
print("ATENÇÃO: isto NÃO testa implementação, qualidade, inferência, fontes ou entrega.")
