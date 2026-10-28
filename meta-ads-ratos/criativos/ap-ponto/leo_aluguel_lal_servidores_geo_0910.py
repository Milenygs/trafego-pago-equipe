"""Belo 09/10/2026 (ok da Mileny: "pode sim e pode ativar o que sugeriu").

1. Servidores (120246003834740358): tira Contagem -> BH (cidade) + Vespasiano 20 km, home + recent.
2. LAL LP (120245790363030358): anuncio `VID UGC Leo Aluguel v1` com o criativo de LP 1817675009651382 (o mesmo do
   Interesse), ATIVO. O "VID Engenheiro Sonho v2" do Form, que deu 3 Simulacao+ em 36 leads no CV, e o video
   VID_UGC_Leo_Aluguel_v1 (2119042812320120), trocado no Gerenciador em 04/10.
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
SERVIDORES = "120246003834740358"
LAL = "120245790363030358"
CRIATIVO_ALUGUEL = "1817675009651382"
NOME = "VID UGC Leo Aluguel v1"


def get(path, **p):
    p["access_token"] = TOKEN
    return requests.get(G + path, params=p, timeout=180).json()


def post(path, data, fatal=False):
    data = {k: (json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v) for k, v in data.items()}
    data["access_token"] = TOKEN
    r = requests.post(G + path, data=data, timeout=180).json()
    if "error" in r:
        print("  ERRO", path, json.dumps(r["error"], ensure_ascii=False)[:500])
        if fatal:
            sys.exit(1)
    return r


# 1. geo de Servidores
t = get(SERVIDORES, fields="targeting")["targeting"]
t["geo_locations"] = {
    "cities": [{"key": "244661"}, {"key": "273969", "radius": 20, "distance_unit": "kilometer"}],
    "location_types": ["home", "recent"],
}
r = post(SERVIDORES, {"targeting": t})
print("Servidores geo:", "ok" if "error" not in r else "falhou")
time.sleep(2)

# 2. criativo do Leo Aluguel: conferir link, UTM e IA antes de usar
c = get(CRIATIVO_ALUGUEL, fields="name,url_tags,object_story_spec{video_data{video_id,call_to_action}},degrees_of_freedom_spec")
vd = c["object_story_spec"]["video_data"]
ia_on = [k for k, v in (c.get("degrees_of_freedom_spec") or {}).get("creative_features_spec", {}).items()
         if v.get("enroll_status") != "OPT_OUT"]
print("criativo:", c["name"][:60], "| video", vd["video_id"], "| link", vd["call_to_action"]["value"].get("link"),
      "| url_tags ok:", "utm_content={{ad.name}}" in (c.get("url_tags") or ""), "| IA ligada:", ia_on or "nenhuma")
if vd["video_id"] != "2119042812320120" or "belo.apponto.com.br" not in vd["call_to_action"]["value"].get("link", ""):
    sys.exit("criativo inesperado, nada criado")

existentes = [a["name"] for a in get(LAL + "/ads", fields="name", limit=50).get("data", [])]
if NOME in existentes:
    sys.exit(f"{NOME} ja existe no LAL")
ad = post(ACT + "/ads", {"name": NOME, "adset_id": LAL, "creative": {"creative_id": CRIATIVO_ALUGUEL},
                         "status": "PAUSED"}, fatal=True)
print("anuncio criado PAUSED:", ad["id"])
time.sleep(3)
post(ad["id"], {"status": "ACTIVE"})
print("ativado (ok da Mileny)")

# conferir
s = get(SERVIDORES, fields="name,targeting{geo_locations}")
print("\nServidores geo agora:", json.dumps(s["targeting"]["geo_locations"], ensure_ascii=False))
for a in get(LAL + "/ads", fields="name,status,effective_status", limit=50).get("data", []):
    if a["status"] == "ACTIVE":
        print("  LAL ativo:", a["name"], "|", a["effective_status"], "|", a["id"])
