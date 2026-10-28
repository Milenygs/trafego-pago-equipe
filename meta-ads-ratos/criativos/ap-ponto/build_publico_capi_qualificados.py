"""AP Ponto 28/09/2026 - publico dos leads QUALIFICADOS que o CV devolve pelo CAPI + lookalike.

Eventos de servidor do CV no pixel 211205516600655 (30d em 28/09): Schedule 319, AnaliseCredito 61,
SubmitApplication 28, Purchase 32 (Contact 407 fica de fora: e so "lead contatado").
M_CAPI_Qualificados_180D = quem teve Schedule, SubmitApplication, AnaliseCredito ou Purchase em 180 dias.
M_LAL_1_CAPI_Qualificados = lookalike 1% BR dele (usar SEMPRE com geo RMBH no conjunto).
Nao cria conjunto nem gasta verba.
"""
import json
import os
import sys
import time
from pathlib import Path

import requests

SKILL = Path(os.path.expanduser("~/OneDrive/.claude/skills/meta-ads-ratos"))
env = (SKILL / ".env").read_text(encoding="utf-8")
TOKEN = [l.split("=", 1)[1].strip().strip('"') for l in env.splitlines() if l.startswith("META_ADS_TOKEN")][0]
G = "https://graph.facebook.com/v23.0/"
ACT, PIXEL = "act_1043516946010441", "211205516600655"
EVENTOS = ["Schedule", "SubmitApplication", "AnaliseCredito", "Purchase"]


def get(p, **k):
    k["access_token"] = TOKEN
    return requests.get(G + p, params=k, timeout=90).json()


def post(path, data):
    data = {k: (json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v) for k, v in data.items()}
    data["access_token"] = TOKEN
    return requests.post(G + path, data=data, timeout=120).json()


existentes = {a["name"]: a["id"] for a in get(ACT + "/customaudiences", fields="name", limit=500).get("data", [])}
nome = "M_CAPI_Qualificados_180D"
if nome in existentes:
    src = existentes[nome]
    print(nome, "ja existe", src)
else:
    rule = {"inclusions": {"operator": "or", "rules": [{
        "event_sources": [{"id": PIXEL, "type": "pixel"}], "retention_seconds": 180 * 86400,
        "filter": {"operator": "or", "filters": [{"field": "event", "operator": "eq", "value": e} for e in EVENTOS]},
    }]}}
    r = post(ACT + "/customaudiences", {"name": nome, "rule": rule, "prefill": True,
                                        "description": "CV via CAPI: Schedule/SubmitApplication/AnaliseCredito/Purchase 180d. Semente de LAL."})
    print(nome, r)
    src = r.get("id")
    time.sleep(3)

nome_lal = "M_LAL_1_CAPI_Qualificados"
if src and nome_lal not in existentes:
    r = post(ACT + "/customaudiences", {"name": nome_lal, "subtype": "LOOKALIKE", "origin_audience_id": src,
                                        "lookalike_spec": {"country": "BR", "ratio": 0.01, "type": "similarity"}})
    print(nome_lal, r)
print(json.dumps(get(src, fields="name,approximate_count_lower_bound,approximate_count_upper_bound,operation_status,delivery_status"), ensure_ascii=False))
