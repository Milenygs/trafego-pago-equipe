"""Belo 15/10/2026 (Mileny): troca o pino de Vespasiano 15 km pela cidade de Vespasiano com raio de 20 km.

Todos os conjuntos ATIVOS: Belo Horizonte (cidade, sem raio) + Vespasiano (cidade) 20 km, expansao geo desligada,
location_types home + recent. Raio de cidade no Meta e no minimo 17 km, por isso os 15 km tinham ido como pino.
Backup da geo original (antes de 15/10) em geo_backup_1510.json.
"""
import json
import os
import sys
import time
from pathlib import Path

import requests

sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
env = (Path(os.path.expanduser("~/OneDrive/.claude/skills/meta-ads-ratos")) / ".env").read_text(encoding="utf-8")
TOKEN = [l.split("=", 1)[1].strip().strip('"') for l in env.splitlines() if l.startswith("META_ADS_TOKEN")][0]
G = "https://graph.facebook.com/v23.0/"
ACT = "act_1043516946010441"

GEO = {
    "cities": [{"key": "244661"},  # Belo Horizonte, cidade
               {"key": "273969", "radius": 20, "distance_unit": "kilometer"}],  # Vespasiano 20 km
    "location_types": ["home", "recent"],
}


def get(path, **p):
    p["access_token"] = TOKEN
    return requests.get(G + path, params=p, timeout=180).json()


def post(path, data):
    data = {k: (json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v) for k, v in data.items()}
    data["access_token"] = TOKEN
    return requests.post(G + path, data=data, timeout=180).json()


ativos = get(ACT + "/adsets", fields="id,name,effective_status,targeting", limit=200,
             effective_status=json.dumps(["ACTIVE"]))["data"]
print(len(ativos), "conjuntos ativos")

for a in ativos:
    t = a["targeting"]
    t["geo_locations"] = GEO
    t.pop("excluded_geo_locations", None)
    auto = t.get("targeting_automation") or {}
    auto["individual_setting"] = {**(auto.get("individual_setting") or {}), "geo": 0}
    t["targeting_automation"] = auto
    r = post(a["id"], {"targeting": t})
    if "error" in r:
        e = r["error"]
        print("ERRO", a["name"], "|", e.get("error_subcode"), e.get("error_user_msg") or e.get("message"))
        sys.exit(1)
    time.sleep(2)
    n = get(a["id"], fields="targeting{geo_locations,targeting_automation}")["targeting"]
    print("ok |", a["name"], "|", a["id"])
    print("   geo:", json.dumps(n.get("geo_locations"), ensure_ascii=False))
    print("   auto:", json.dumps(n.get("targeting_automation"), ensure_ascii=False))
