"""Belo 28/09/2026 - correcao pedida pela Mileny na campanha de formulario.

1. Formulario certo = 1126167740367137 ("...Renda min 5001 | SET26 TEL"), nao o 2287635791803187.
   Troca o criativo de TODOS os anuncios da campanha de formulario (criativo novo identico, so o form muda).
2. Os 2 conjuntos novos (LAL CAPI e Base Quente) copiam a configuracao do conjunto dela
   "[BELO] Direct Publico Quente 180D — otimizacao lead" (120245805648780358):
   idade 25-60, geo cidades BH/Contagem/Vespasiano (home+recent), Advantage publico/semelhante/personalizado OFF,
   Instagram feed + reels + perfil. Mantem os publicos e exclusoes de cada conjunto.
Uso: python corrigir_belo_form_tel.py [--so-ler]
"""
import json
import sys
import time
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).parent))
import build_belo_form as fm  # noqa: E402

TOKEN, G, ACT = fm.TOKEN, fm.G, fm.ACT
CAMP_FORM = "120245805859660358"
FORM_TEL = "1126167740367137"
MODELO = "120245805648780358"
NOVOS = ["120245854126000358", "120245854129560358"]


def get(p, **k):
    k["access_token"] = TOKEN
    return requests.get(G + p, params=k, timeout=90).json()


def post(path, data, fatal=True):
    data = {k: (json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v) for k, v in data.items()}
    data["access_token"] = TOKEN
    r = requests.post(G + path, data=data, timeout=120).json()
    if "error" in r:
        e = r["error"]
        print(json.dumps({k: e.get(k) for k in ("code", "error_subcode", "error_user_title", "error_user_msg", "message")},
                         ensure_ascii=False, indent=1))
        if fatal:
            sys.exit(1)
    return r


f = get(FORM_TEL, fields="name,status,questions,context_card")
print("FORM TEL:", f.get("name"), f.get("status"))
for q in f.get("questions", []):
    print("   ", q["type"], "|", q.get("label"), "|", [o["value"] for o in q.get("options", [])][:8])
print("   tela:", (f.get("context_card", {}).get("content") or [""])[0][:300].replace("\n", " / "))
if "--so-ler" in sys.argv:
    sys.exit()

# 1. formulario TEL em todos os anuncios da campanha
novo_por_antigo = {}
for a in get(CAMP_FORM + "/ads", fields="id,name,adset{name},creative{id}", limit=100)["data"]:
    old = a["creative"]["id"]
    if old not in novo_por_antigo:
        c = get(old, fields="name,object_story_spec,asset_feed_spec,degrees_of_freedom_spec")
        oss = c["object_story_spec"]
        chave = "video_data" if "video_data" in oss else "link_data"
        d = oss[chave]
        if d.get("call_to_action", {}).get("value", {}).get("lead_gen_form_id") == FORM_TEL:
            novo_por_antigo[old] = old
        else:
            d["call_to_action"] = {"type": "SIGN_UP", "value": {"lead_gen_form_id": FORM_TEL}}
            if chave == "video_data" and d.get("image_hash"):
                d.pop("image_url", None)
            af = c.get("asset_feed_spec") or {}
            feed = {k: [{"text": x["text"]} for x in af.get(k, [])] for k in ("bodies", "titles", "descriptions") if af.get(k)}
            if feed:
                feed["optimization_type"] = "DEGREES_OF_FREEDOM"
            novo = post(ACT + "/adcreatives", {
                "name": (c.get("name") or a["name"]).split(" 2026-")[0] + " | TEL",
                "object_story_spec": {"page_id": oss["page_id"], "instagram_user_id": oss.get("instagram_user_id"), chave: d},
                **({"asset_feed_spec": feed} if feed else {}),
                **({"degrees_of_freedom_spec": c["degrees_of_freedom_spec"]} if c.get("degrees_of_freedom_spec") else {}),
            })["id"]
            novo_por_antigo[old] = novo
            print("criativo", a["name"], old, "->", novo)
            time.sleep(2)
    if novo_por_antigo[old] != old:
        r = post(a["id"], {"creative": {"creative_id": novo_por_antigo[old]}}, fatal=False)
        print("  anuncio", a["adset"]["name"], "|", a["name"], r)
        time.sleep(2)

# 2. configuracao do conjunto modelo nos 2 conjuntos novos
m = get(MODELO, fields="targeting")["targeting"]
for sid in NOVOS:
    t = get(sid, fields="name,targeting")
    nome, atual = t["name"], t["targeting"]
    novo_t = {
        "age_min": m["age_min"], "age_max": m["age_max"],
        "geo_locations": {"cities": [{"key": c["key"]} for c in m["geo_locations"]["cities"]],
                          "location_types": m["geo_locations"].get("location_types", ["home", "recent"])},
        "custom_audiences": [{"id": x["id"]} for x in atual.get("custom_audiences", [])],
        "excluded_custom_audiences": [{"id": x["id"]} for x in atual.get("excluded_custom_audiences", [])],
        "targeting_relaxation_types": {"lookalike": 0, "custom_audience": 0},
        "targeting_automation": {"advantage_audience": 0, "individual_setting": {"geo": 0}},
        # AP Ponto (regra da Mileny, 28/09): anuncios de formulario usam tambem Facebook e Audience Network.
        # Instagram igual ao modelo; Facebook e AN como ela configurou no Base Quente pelo painel.
        "publisher_platforms": ["facebook", "instagram", "audience_network"],
        "facebook_positions": ["feed", "story", "facebook_reels"],
        "instagram_positions": m["instagram_positions"],
        "audience_network_positions": ["classic", "rewarded_video"],
        "device_platforms": m["device_platforms"],
    }
    print("conjunto", nome, post(sid, {"targeting": novo_t}))
    time.sleep(2)

# conferencia
print("\n== conferencia")
for sid in NOVOS:
    s = get(sid, fields="name,status,targeting")
    t = s["targeting"]
    print(s["name"], s["status"], "| idade", t.get("age_min"), "-", t.get("age_max"),
          "| geo", [c["name"] for c in t.get("geo_locations", {}).get("cities", [])],
          "| relax", t.get("targeting_relaxation_types"), "| auto", t.get("targeting_automation"),
          "| plat", t.get("publisher_platforms"), "| fb", t.get("facebook_positions"), "| ig", t.get("instagram_positions"),
          "| an", t.get("audience_network_positions"), "| otim", t.get("targeting_optimization"))
forms = {}
for a in get(CAMP_FORM + "/ads", fields="name,adset{name},status,effective_status,creative{object_story_spec}", limit=100)["data"]:
    o = a["creative"]["object_story_spec"]
    d = o.get("video_data") or o.get("link_data") or {}
    fid = d.get("call_to_action", {}).get("value", {}).get("lead_gen_form_id")
    forms[fid] = forms.get(fid, 0) + 1
print("anuncios por formulario:", forms)
