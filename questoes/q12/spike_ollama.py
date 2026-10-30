"""Etapa 00: chamada real ao Ollama e validação determinística de JSON."""
import argparse
import json
import os
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen


def validate_response(response: object) -> dict:
    if not isinstance(response, dict) or response.get("done") is not True:
        raise ValueError("Envelope deve ser objeto com done=true")
    if not isinstance(response.get("model"), str) or not response["model"].strip():
        raise ValueError("Envelope sem modelo utilizado")
    message = response.get("message")
    if not isinstance(message, dict) or message.get("role") != "assistant":
        raise ValueError("Envelope sem message de assistant")
    if not isinstance(message.get("content"), str):
        raise ValueError("message.content deve ser texto JSON")
    content = json.loads(message["content"])
    if not isinstance(content, dict) or set(content) != {"intencao", "duracao_minutos"}:
        raise ValueError("Conteúdo deve conter somente intencao e duracao_minutos")
    if content["intencao"] != "estudar":
        raise ValueError("Intenção esperada: estudar")
    duration = content["duracao_minutos"]
    if type(duration) is not int or duration <= 0:
        raise ValueError("Duração deve ser inteiro positivo (não booleano)")
    # Caso de referência independente: pedido fixo de meia hora = 30 minutos.
    if duration != 30:
        raise ValueError("Pedido de meia hora deve resultar em 30 minutos")
    return content


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default=os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434"))
    parser.add_argument("--model", default=os.environ.get("OLLAMA_MODEL"))
    parser.add_argument("--timeout", type=float, default=60)
    args = parser.parse_args()
    parsed = urlsplit(args.url)
    if (parsed.scheme not in {"http", "https"} or not parsed.hostname
            or parsed.username or parsed.password or parsed.query or parsed.fragment
            or parsed.path not in {"", "/"}):
        parser.error("--url deve ser a origem HTTP(S), sem credenciais, caminho ou query")
    if not args.model or not args.model.strip():
        print("BLOQUEADO: informe --model ou OLLAMA_MODEL instalado no servidor", file=sys.stderr)
        return 2
    if args.timeout <= 0:
        parser.error("--timeout deve ser positivo")
    endpoint = args.url.rstrip("/") + "/api/chat"
    payload = {"model": args.model, "stream": False, "format": "json",
               "options": {"temperature": 0, "seed": 42},
               "messages": [{"role": "user", "content":
                   'Quero estudar por meia hora. Responda somente JSON com as chaves '
                   'intencao ("estudar") e duracao_minutos (inteiro).'}]}
    print(json.dumps({"endpoint": endpoint, "modelo_solicitado": args.model,
                      "timeout_s": args.timeout}, ensure_ascii=False), flush=True)
    request = Request(endpoint, data=json.dumps(payload).encode("utf-8"),
                      headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urlopen(request, timeout=args.timeout) as response:
            envelope = json.load(response)
    except HTTPError as exc:
        print(f"BLOQUEADO: Ollama HTTP {exc.code}; verifique servidor e modelo instalado", file=sys.stderr)
        return 2
    except (URLError, TimeoutError, OSError) as exc:
        print(f"BLOQUEADO: sem conexão/resposta de Ollama: {exc}", file=sys.stderr)
        return 2
    except (ValueError, UnicodeError) as exc:
        print(f"FALHA: resposta HTTP não é JSON válido: {exc}", file=sys.stderr)
        return 1
    try:
        content = validate_response(envelope)
    except (ValueError, TypeError) as exc:
        print(f"FALHA: contrato JSON rejeitado: {exc}", file=sys.stderr)
        return 1
    print(json.dumps({"status": "OK", "modelo_retornado": envelope["model"],
                      "resposta_validada": content}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
