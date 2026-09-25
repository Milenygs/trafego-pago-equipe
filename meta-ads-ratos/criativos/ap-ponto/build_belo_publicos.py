"""Belo 24/09/2026 - publicos do pixel da LP do Belo + exclusao de quem ja virou lead.

M_Belo_Leads_Obrigado_180D: chegou na /obrigado (enviou o contato) -> EXCLUIR do RMKT e do Direct do Belo.
M_Site_Belo_180D: visitou belo.apponto.com.br -> INCLUIR no RMKT do Belo.
Uso: python build_belo_publicos.py
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
ACT = "act_1043516946010441"
PIXEL = "211205516600655"
RMKT_LP = "120245790367990358"      # [BELO] Remarketing 180D
DIRECT = "120245801239900358"       # [BELO] Direct Publico Quente 180D


def get(p, **k):
    k["access_token"] = TOKEN
    return requests.get(G + p, params=k).json()


def post(path, data):
    data = {k: (json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v) for k, v in data.items()}
    data["access_token"] = TOKEN
    r = requests.post(G + path, data=data).json()
    if "error" in r:
        e = r["error"]
        print(json.dumps({k: e.get(k) for k in ("code", "error_subcode", "error_user_title", "error_user_msg", "message")},
                         ensure_ascii=False, indent=1))
        sys.exit(1)
    return r


def publico(nome, trecho_url, descricao):
    existentes = {a["name"]: a["id"] for a in get(ACT + "/customaudiences", fields="name", limit=500).get("data", [])}
    if nome in existentes:
        print(nome, "ja existe", existentes[nome])
        return existentes[nome]
    rule = {"inclusions": {"operator": "or", "rules": [{
        "event_sources": [{"id": PIXEL, "type": "pixel"}],
        "retention_seconds": 180 * 86400,
        "filter": {"operator": "and", "filters": [{"field": "url", "operator": "i_contains", "value": trecho_url}]},
    }]}}
    r = post(ACT + "/customaudiences", {"name": nome, "description": descricao, "rule": rule, "prefill": True})
    print(nome, r["id"])
    time.sleep(1)
    return r["id"]


leads = publico("M_Belo_Leads_Obrigado_180D", "belo.apponto.com.br/obrigado",
                "Enviou o contato na LP do Belo (chegou na /obrigado). Excluir do RMKT e do Direct.")
site = publico("M_Site_Belo_180D", "belo.apponto.com.br",
               "Visitou a LP do Belo (180 dias). Remarketing do Belo.")


def ajusta(adset_id, incluir=None, excluir=None):
    t = get(adset_id, fields="targeting")["targeting"]
    if incluir:
        ids = {a["id"] for a in t.get("custom_audiences", [])}
        if incluir not in ids:
            t.setdefault("custom_audiences", []).append({"id": incluir})
    if excluir:
        ids = {a["id"] for a in t.get("excluded_custom_audiences", [])}
        if excluir not in ids:
            t.setdefault("excluded_custom_audiences", []).append({"id": excluir})
    for k in ("age_range",):
        t.pop(k, None)
    post(adset_id, {"targeting": t})
    t2 = get(adset_id, fields="name,targeting{custom_audiences,excluded_custom_audiences}")
    print(t2["name"], "| inclui:", [a["name"] for a in t2["targeting"].get("custom_audiences", [])],
          "| exclui:", [a["name"] for a in t2["targeting"].get("excluded_custom_audiences", [])])


ajusta(RMKT_LP, incluir=site, excluir=leads)
ajusta(DIRECT, excluir=leads)
