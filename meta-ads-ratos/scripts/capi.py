#!/usr/bin/env python3
"""
Meta Ads Ratos - CAPI / Conversion Leads
Envia eventos de funil (lead qualificado, reuniao, venda) do CRM de volta
para o Meta, para habilitar a otimizacao Conversion Leads.

Ver arquitetura completa em: references/capi-crm.md

Uso:
  # Evento unico (lead veio de formulario nativo Meta -> usar lead_id)
  python capi.py send --pixel 123456 --event-name lead_qualificado \
      --lead-id 9876543210 --crm rd_station

  # Evento por email/telefone (lead veio de landing page)
  python capi.py send --pixel 123456 --event-name venda \
      --email "pessoa@email.com" --phone "+5551999998888" --crm kommo

  # Teste no Events Manager (aba Testar eventos)
  python capi.py send --pixel 123456 --event-name lead_qualificado \
      --lead-id 9876543210 --test-code TEST12345

  # Lote via CSV (colunas: event_name,event_time,lead_id,email,phone)
  python capi.py batch --pixel 123456 --csv eventos.csv --crm rd_station

Nomes de evento padronizados (usar sempre os mesmos em todos os clientes):
  lead_qualificado, reuniao_agendada, proposta_enviada, venda, lead_desqualificado
"""

import argparse
import csv
import datetime as dt
import hashlib
import json
import os
import re
import sys
import time
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import _load_env_file, print_error

GRAPH_VERSION = os.environ.get("META_GRAPH_VERSION", "v23.0")


def _token():
    _load_env_file()
    token = os.environ.get("META_ADS_TOKEN")
    if not token:
        print_error("META_ADS_TOKEN nao encontrado no .env da skill.")
        sys.exit(2)
    return token


def _sha256(valor):
    return hashlib.sha256(valor.encode("utf-8")).hexdigest()


def _norm_email(email):
    return _sha256(email.strip().lower())


def _norm_phone(phone):
    """Normaliza para digitos com DDI (assume BR/55 se faltar) e hasheia."""
    digitos = re.sub(r"\D", "", phone)
    if len(digitos) in (10, 11):  # sem DDI
        digitos = "55" + digitos
    return _sha256(digitos)


def _parse_event_time(valor):
    if not valor:
        return int(time.time())
    if valor.isdigit():
        return int(valor)
    # aceita 2026-07-09 ou 2026-07-09T14:30
    try:
        return int(dt.datetime.fromisoformat(valor).timestamp())
    except ValueError:
        print_error(f"event_time invalido: {valor} (use unix timestamp ou ISO ex: 2026-07-09T14:30)")
        sys.exit(2)


def montar_evento(event_name, event_time=None, lead_id=None, email=None, phone=None, crm=None):
    user_data = {}
    if lead_id:
        user_data["lead_id"] = int(lead_id)
    if email:
        user_data["em"] = [_norm_email(email)]
    if phone:
        user_data["ph"] = [_norm_phone(phone)]
    if not user_data:
        print_error("Evento precisa de pelo menos lead_id, email ou phone para o Meta casar o usuario.")
        sys.exit(2)
    evento = {
        "event_name": event_name,
        "event_time": _parse_event_time(event_time),
        "action_source": "system_generated",
        "user_data": user_data,
        "custom_data": {"event_source": "crm"},
    }
    if crm:
        evento["custom_data"]["lead_event_source"] = crm
    return evento


def enviar(pixel_id, eventos, test_code=None):
    token = _token()
    url = f"https://graph.facebook.com/{GRAPH_VERSION}/{pixel_id}/events"
    payload = {"data": eventos, "access_token": token}
    if test_code:
        payload["test_event_code"] = test_code
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print_error(f"CAPI HTTP {e.code}: {body}")
        sys.exit(1)


def cmd_send(args):
    evento = montar_evento(args.event_name, args.event_time, args.lead_id,
                           args.email, args.phone, args.crm)
    resp = enviar(args.pixel, [evento], args.test_code)
    print(json.dumps({"enviado": evento["event_name"], "resposta": resp},
                     indent=2, ensure_ascii=False))


def cmd_batch(args):
    eventos = []
    with open(args.csv, "r", encoding="utf-8-sig", newline="") as f:
        for i, row in enumerate(csv.DictReader(f), start=2):
            nome = (row.get("event_name") or "").strip()
            if not nome:
                print(f"Linha {i}: sem event_name, pulando.", file=sys.stderr)
                continue
            eventos.append(montar_evento(
                nome,
                (row.get("event_time") or "").strip() or None,
                (row.get("lead_id") or "").strip() or None,
                (row.get("email") or "").strip() or None,
                (row.get("phone") or "").strip() or None,
                args.crm,
            ))
    if not eventos:
        print_error("Nenhum evento valido no CSV.")
        sys.exit(2)

    total = {"events_received": 0, "lotes": 0}
    for inicio in range(0, len(eventos), 100):  # limite da API: 1000/req; 100 por seguranca
        lote = eventos[inicio:inicio + 100]
        resp = enviar(args.pixel, lote, args.test_code)
        total["events_received"] += resp.get("events_received", 0)
        total["lotes"] += 1
        time.sleep(1)
    print(json.dumps({"eventos_no_csv": len(eventos), **total}, indent=2, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(description="Envio de eventos CRM -> Meta (CAPI / Conversion Leads)")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("send", help="Envia um evento")
    p.add_argument("--pixel", required=True, help="ID do pixel/dataset do cliente")
    p.add_argument("--event-name", required=True, help="ex: lead_qualificado, venda")
    p.add_argument("--event-time", help="Unix timestamp ou ISO (padrao: agora)")
    p.add_argument("--lead-id", help="leadgen_id do formulario nativo Meta (melhor match)")
    p.add_argument("--email", help="Email do lead (sera hasheado SHA-256)")
    p.add_argument("--phone", help="Telefone do lead (normalizado +55, hasheado)")
    p.add_argument("--crm", help="Nome do CRM de origem: rd_station, kommo, pipedrive...")
    p.add_argument("--test-code", help="test_event_code do Events Manager (para validar)")
    p.set_defaults(func=cmd_send)

    p = sub.add_parser("batch", help="Envia eventos em lote de um CSV")
    p.add_argument("--pixel", required=True)
    p.add_argument("--csv", required=True, help="CSV com colunas: event_name,event_time,lead_id,email,phone")
    p.add_argument("--crm", help="Nome do CRM de origem")
    p.add_argument("--test-code", help="test_event_code para validar antes do envio real")
    p.set_defaults(func=cmd_batch)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
