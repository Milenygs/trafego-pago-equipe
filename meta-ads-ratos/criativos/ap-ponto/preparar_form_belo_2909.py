"""Belo 28/09/2026 (noite) - prepara a campanha de formulario para ativar em 29/09 06:00 (tudo continua PAUSED).

Pedido da Mileny: verba R$100/dia e ativar so Momento de Vida (C), LAL Compradores e LAL Qualificados CAPI (A).
1. Verba R$100 nos 3 conjuntos.
2. LAL Compradores (conjunto antigo de 24/09) na configuracao padrao dela: 25-60, cidades BH/Contagem/Vespasiano,
   Advantage OFF, FB feed/stories/reels + IG feed/reels/perfil + AN, exclusoes iguais aos conjuntos novos.
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
C_VIDA, LAL_COMP, A_CAPI = "120245855388890358", "120245805860620358", "120245854126000358"
PADRAO = {
    "age_min": 25, "age_max": 60,
    "geo_locations": {"cities": [{"key": "244661"}, {"key": "249756"}, {"key": "273969"}], "location_types": ["home", "recent"]},
    "targeting_relaxation_types": {"lookalike": 0, "custom_audience": 0},
    "targeting_automation": {"advantage_audience": 0, "individual_setting": {"geo": 0}},
    "publisher_platforms": ["facebook", "instagram", "audience_network"],
    "facebook_positions": ["feed", "story", "facebook_reels"],
    "instagram_positions": ["stream", "reels", "profile_feed"],
    "audience_network_positions": ["classic", "rewarded_video"],
    "device_platforms": ["mobile", "desktop"],
}
EXCLUIR = ["120245517540390358", "120245517540780358", "120245802351920358", "120245854125580358"]


def get(p, **k):
    k["access_token"] = TOKEN
    return requests.get(G + p, params=k, timeout=90).json()


def post(path, data):
    data = {k: (json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v) for k, v in data.items()}
    data["access_token"] = TOKEN
    r = requests.post(G + path, data=data, timeout=120).json()
    if "error" in r:
        e = r["error"]
        print(json.dumps({k: e.get(k) for k in ("code", "error_subcode", "error_user_title", "error_user_msg", "message")},
                         ensure_ascii=False, indent=1))
    return r


# 2. LAL Compradores no padrao (mantem o publico LAL dele)
t = get(LAL_COMP, fields="targeting")["targeting"]
novo = dict(PADRAO)
novo["custom_audiences"] = [{"id": a["id"]} for a in t.get("custom_audiences", [])]
novo["excluded_custom_audiences"] = [{"id": i} for i in EXCLUIR]
print("LAL Compradores padrao:", post(LAL_COMP, {"targeting": novo}))
time.sleep(2)

# 1. verba R$100
for sid in (C_VIDA, LAL_COMP, A_CAPI):
    print("verba", sid, post(sid, {"daily_budget": 10000}))
    time.sleep(2)

print("\n== conferencia (tudo deve estar PAUSED)")
for sid in (C_VIDA, LAL_COMP, A_CAPI):
    s = get(sid, fields="name,status,daily_budget,targeting")
    tt = s["targeting"]
    print(s["name"], "|", s["status"], "| R$", int(s["daily_budget"]) / 100, "| idade", tt.get("age_min"), "-", tt.get("age_max"),
          "| geo", [c["name"] for c in tt.get("geo_locations", {}).get("cities", [])], "| relax", tt.get("targeting_relaxation_types"),
          "| plat", tt.get("publisher_platforms"))
    print("    inclui:", [a["name"] for a in tt.get("custom_audiences", [])] or [x["name"] for fs in tt.get("flexible_spec", []) for k in fs for x in fs[k]])
    print("    exclui:", [a["name"] for a in tt.get("excluded_custom_audiences", [])])
    for a in get(sid + "/ads", fields="name,status,creative{object_story_spec}")["data"]:
        o = a["creative"]["object_story_spec"]
        d = o.get("video_data") or o.get("link_data") or {}
        print("      anuncio", a["name"], a["status"], "| form", d.get("call_to_action", {}).get("value", {}).get("lead_gen_form_id"))
print("campanha:", get("120245805859660358", fields="name,status"))
