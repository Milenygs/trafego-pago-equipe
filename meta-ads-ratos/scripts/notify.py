#!/usr/bin/env python3
"""
Meta Ads Ratos - Notificacoes (Telegram)

Setup (uma vez):
  1. No Telegram, falar com @BotFather -> /newbot -> copiar o token
  2. Mandar qualquer mensagem para o bot criado
  3. Rodar: python notify.py chat-id   (descobre o chat_id automaticamente)
  4. Preencher no .env da skill:
       TELEGRAM_BOT_TOKEN="123456:ABC..."
       TELEGRAM_CHAT_ID="123456789"

Uso:
  python notify.py test                        # valida token e envia msg de teste
  python notify.py chat-id                     # descobre o chat_id (apos mandar msg pro bot)
  python notify.py telegram --text "mensagem"
  python notify.py telegram --file caminho.md  # envia conteudo de um arquivo
"""

import argparse
import json
import os
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import _load_env_file, print_error

MAX_LEN = 4000  # limite do Telegram e 4096; margem de seguranca


def _config():
    _load_env_file()
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not token:
        print_error("TELEGRAM_BOT_TOKEN nao configurado no .env da skill.")
        print("  Siga o setup no topo deste arquivo (python notify.py --help).", file=sys.stderr)
        sys.exit(2)
    return token, chat_id


def _api(token, method, payload=None):
    url = f"https://api.telegram.org/bot{token}/{method}"
    data = json.dumps(payload or {}).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print_error(f"Telegram HTTP {e.code}: {body}")
        sys.exit(1)


def _upload(token, method, campos, arquivo_campo, caminho):
    """POST multipart/form-data — usado pelo sendDocument, que nao aceita JSON."""
    import mimetypes
    import uuid

    limite = f"----metaadsratos{uuid.uuid4().hex}"
    nome = os.path.basename(caminho)
    tipo = mimetypes.guess_type(nome)[0] or "application/octet-stream"
    with open(caminho, "rb") as f:
        conteudo = f.read()

    partes = []
    for chave, valor in campos.items():
        partes.append(
            f'--{limite}\r\nContent-Disposition: form-data; name="{chave}"\r\n\r\n{valor}\r\n'.encode("utf-8")
        )
    partes.append(
        f'--{limite}\r\nContent-Disposition: form-data; name="{arquivo_campo}"; '
        f'filename="{nome}"\r\nContent-Type: {tipo}\r\n\r\n'.encode("utf-8")
    )
    partes.append(conteudo)
    partes.append(f"\r\n--{limite}--\r\n".encode("utf-8"))
    corpo = b"".join(partes)

    url = f"https://api.telegram.org/bot{token}/{method}"
    req = urllib.request.Request(
        url, data=corpo,
        headers={"Content-Type": f"multipart/form-data; boundary={limite}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print_error(f"Telegram HTTP {e.code}: {body}")
        sys.exit(1)


def _chunks(text):
    while text:
        if len(text) <= MAX_LEN:
            yield text
            return
        corte = text.rfind("\n", 0, MAX_LEN)
        if corte < MAX_LEN // 2:
            corte = MAX_LEN
        yield text[:corte]
        text = text[corte:].lstrip("\n")


def cmd_test(args):
    token, chat_id = _config()
    me = _api(token, "getMe")
    print(f"Bot OK: @{me['result']['username']}")
    if not chat_id:
        print_error("TELEGRAM_CHAT_ID nao configurado. Rode: python notify.py chat-id")
        sys.exit(2)
    _api(token, "sendMessage", {"chat_id": chat_id, "text": "Meta Ads Ratos: notificacao de teste funcionando."})
    print("Mensagem de teste enviada.")


def cmd_chat_id(args):
    token, _ = _config()
    updates = _api(token, "getUpdates")
    chats = {}
    for u in updates.get("result", []):
        msg = u.get("message") or u.get("channel_post") or {}
        chat = msg.get("chat")
        if chat:
            chats[chat["id"]] = chat.get("username") or chat.get("title") or chat.get("first_name")
    if not chats:
        print("Nenhuma conversa encontrada. Mande uma mensagem qualquer para o bot no Telegram e rode de novo.")
        return
    print("Chats encontrados (use o id no TELEGRAM_CHAT_ID do .env):")
    for cid, nome in chats.items():
        print(f"  chat_id: {cid}  ({nome})")


def cmd_telegram(args):
    token, chat_id = _config()
    if not chat_id:
        print_error("TELEGRAM_CHAT_ID nao configurado. Rode: python notify.py chat-id")
        sys.exit(2)
    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            text = f.read()
    elif args.text:
        text = args.text
    else:
        print_error("Informe --text ou --file.")
        sys.exit(2)
    enviados = 0
    for parte in _chunks(text):
        _api(token, "sendMessage", {
            "chat_id": chat_id, "text": parte, "disable_web_page_preview": True,
        })
        enviados += 1
    print(f"Enviado ({enviados} mensagem(ns)).")


def cmd_document(args):
    """Manda um arquivo como anexo. Existe porque o Extrato diario roda em sessao
    headless, onde nao ha ferramenta de publicar Artifact — sem isso o relatorio
    fica so no disco da maquina dela e nunca chega no celular."""
    token, chat_id = _config()
    if not chat_id:
        print_error("TELEGRAM_CHAT_ID nao configurado. Rode: python notify.py chat-id")
        sys.exit(2)
    if not os.path.isfile(args.path):
        print_error(f"Arquivo nao encontrado: {args.path}")
        sys.exit(2)
    campos = {"chat_id": chat_id}
    if args.caption:
        campos["caption"] = args.caption[:1024]
    _upload(token, "sendDocument", campos, "document", args.path)
    print(f"Anexo enviado: {os.path.basename(args.path)}")


def main():
    parser = argparse.ArgumentParser(description="Notificacoes Telegram")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("test", help="Valida token e envia mensagem de teste").set_defaults(func=cmd_test)
    sub.add_parser("chat-id", help="Descobre o chat_id apos mandar msg pro bot").set_defaults(func=cmd_chat_id)

    p = sub.add_parser("telegram", help="Envia mensagem")
    p.add_argument("--text", help="Texto da mensagem")
    p.add_argument("--file", help="Arquivo com o texto")
    p.set_defaults(func=cmd_telegram)

    p = sub.add_parser("document", help="Envia um arquivo como anexo (ex: o HTML do Extrato)")
    p.add_argument("--path", required=True, help="Caminho do arquivo a anexar")
    p.add_argument("--caption", help="Legenda curta (max 1024 chars)")
    p.set_defaults(func=cmd_document)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
