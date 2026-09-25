#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lembrete de recarga - Grupo TFS (Saborazzi, TrendPel, Industria/Revendedores).
Disparado pela tarefa agendada "RecargaTFS-Mileny".

REDUNDANTE desde 02/09/2026: o aviso de boleto passou a sair no resumo diario
das 7h (resumo_telegram.py, bloco "BOLETOS"), que le o mesmo calendario. Esta
tarefa pode ser desativada. Enquanto existir, manda a agenda REAL vinda do
contas.yaml em vez da mensagem fixa quinzenal antiga (R$250/500/750 a cada
14 dias), que ficou desatualizada quando o ciclo virou 28 dias.
"""
import json
import os
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import _load_env_file, print_error
import boletos as calendario


def main():
    bloco = calendario.montar_hoje()
    texto = calendario.texto_telegram(bloco)
    if not texto:
        print("Nenhum boleto acionavel hoje; nada enviado.")
        return

    _load_env_file()
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        print_error("TELEGRAM_BOT_TOKEN/TELEGRAM_CHAT_ID nao configurados no .env da skill.")
        sys.exit(2)

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = json.dumps({"chat_id": chat_id, "text": texto}).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        resp.read()
    print("Lembrete de boleto enviado.")


if __name__ == "__main__":
    main()
