"""Belo 15/10/2026 (pedido da Mileny, urgente): lead chegando de fora da praca (ex.: Diamantina).

Todos os conjuntos ATIVOS ficam so com Belo Horizonte (cidade, sem raio) + Vespasiano 15 km.
- Vespasiano 15 km vai como pino (custom_locations) no centro de Vespasiano: raio de cidade no Meta e no minimo 17 km.
- Expansao de localizacao do Advantage desligada (targeting_automation.individual_setting.geo = 0).
  O LAL LP 120245790363030358 estava com geo = 1.
- location_types segue home + recent (modelo da Mileny, "moram ou estiveram").
Backup do targeting anterior em geo_backup_1510.json (mesma pasta).
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
BACKUP = Path(__file__).with_name("geo_backup_1510.json")

GEO = {
    "cities": [{"key": "244661"}],  # Belo Horizonte, cidade
    "custom_locations": [{"latitude": -19.691944, "longitude": -43.922778, "radius": 15,
                          "distance_unit": "kilometer", "name": "Vespasiano 15 km"}],
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
if not BACKUP.exists():
    BACKUP.write_text(json.dumps(ativos, ensure_ascii=False, indent=1), encoding="utf-8")
print(len(ativos), "conjuntos ativos | backup:", BACKUP.name)

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
