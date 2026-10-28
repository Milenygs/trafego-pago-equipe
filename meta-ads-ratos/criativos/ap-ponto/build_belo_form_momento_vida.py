"""Belo 28/09/2026 - conjunto C "Momento de Vida" na campanha de formulario (PAUSED).

Publico (OU): noivaram recentemente (1 ano), noivos recentes (6 meses), recem-casados (1 ano), mudou de casa
recentemente, novo emprego, interesse Aluguel (imoveis). Idade 25-45.
Configuracao padrao da Mileny (modelo 120245805648780358): cidades BH/Contagem/Vespasiano (home+recent), Advantage
publico/semelhante/personalizado OFF, Facebook feed/stories/reels + Instagram feed/reels/perfil + Audience Network.
Exclui compradores, complemento, leads do Belo pela LP e quem enviou formulario em 30d. R$150/dia.
Anuncios: os 4 videos com o formulario TEL (1126167740367137).
"""
import json
import sys
import time
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).parent))
import build_belo_form as fm  # noqa: E402

TOKEN, G, ACT, PAGE = fm.TOKEN, fm.G, fm.ACT, fm.PAGE
CAMP_FORM = "120245805859660358"
NOME = "[BELO][FORM] Momento de Vida 25-45"
CRIATIVOS_TEL = {"VID Locucao Lancamento v1": "2170993973765843", "VID UGC Leo v1": "2113833719217348",
                 "VID Engenheiro Sonho v1": "1602965031282218", "VID Engenheiro Familia v1": "1393303442431934"}
TARGETING = {
    "age_min": 25, "age_max": 45,
    "geo_locations": {"cities": [{"key": "244661"}, {"key": "249756"}, {"key": "273969"}],
                      "location_types": ["home", "recent"]},
    "flexible_spec": [{
        "life_events": [{"id": "6003050210972", "name": "Noivaram recentemente (1 ano)"},
                        {"id": "6002714398772", "name": "Noivos recentes (6 meses)"},
                        {"id": "6002714398172", "name": "Recém-casados (1 ano)"},
                        {"id": "6003054185372", "name": "Mudou de casa recentemente"},
                        {"id": "6005149512172", "name": "Novo emprego"}],
        "interests": [{"id": "6003328429697", "name": "Aluguel (imóveis)"}],
    }],
    "excluded_custom_audiences": [{"id": i} for i in ("120245517540390358", "120245517540780358",
                                                      "120245802351920358", "120245854125580358")],
    "targeting_relaxation_types": {"lookalike": 0, "custom_audience": 0},
    "targeting_automation": {"advantage_audience": 0, "individual_setting": {"geo": 0}},
    "publisher_platforms": ["facebook", "instagram", "audience_network"],
    "facebook_positions": ["feed", "story", "facebook_reels"],
    "instagram_positions": ["stream", "reels", "profile_feed"],
    "audience_network_positions": ["classic", "rewarded_video"],
    "device_platforms": ["mobile", "desktop"],
}
REGIONAL = {"regional_regulated_categories": ["BRAZIL_REGULATION", "VOLUNTARY_VERIFICATION"],
            "regional_regulation_identities": {"universal_beneficiary": "609854092925940",
                                               "universal_payer": "609854092925940"}}


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


existentes = {s["name"]: s["id"] for s in get(CAMP_FORM + "/adsets", fields="name")["data"]}
sid = existentes.get(NOME) or post(ACT + "/adsets", {
    "name": NOME, "campaign_id": CAMP_FORM, "status": "PAUSED", "daily_budget": 15000,
    "billing_event": "IMPRESSIONS", "optimization_goal": "LEAD_GENERATION", "destination_type": "ON_AD",
    "bid_strategy": "LOWEST_COST_WITHOUT_CAP", "promoted_object": {"page_id": PAGE},
    "targeting": TARGETING, **REGIONAL})["id"]
print("conjunto", NOME, sid)
ja = {a["name"] for a in get(sid + "/ads", fields="name")["data"]}
for n, cr in CRIATIVOS_TEL.items():
    if n not in ja:
        print("  anuncio", n, post(ACT + "/ads", {"name": n, "adset_id": sid, "creative": {"creative_id": cr},
                                                  "status": "PAUSED"}, fatal=False).get("id"))
        time.sleep(2)

s = get(sid, fields="name,status,daily_budget,targeting")
t = s["targeting"]
print("\n", s["name"], s["status"], "R$", int(s["daily_budget"]) / 100, "| idade", t.get("age_min"), "-", t.get("age_max"),
      "| geo", [c["name"] for c in t["geo_locations"]["cities"]], "| relax", t.get("targeting_relaxation_types"),
      "| auto", t.get("targeting_automation"), "| plat", t.get("publisher_platforms"))
print("  publico:", [x["name"] for fs in t.get("flexible_spec", []) for k in fs for x in fs[k]])
print("  exclui:", [a["name"] for a in t.get("excluded_custom_audiences", [])])
est = get(sid + "/delivery_estimate", optimization_goal="LEAD_GENERATION")
d = (est.get("data") or [{}])[0]
print("  alcance estimado:", d.get("estimate_mau_lower_bound"), "-", d.get("estimate_mau_upper_bound"))
for a in get(sid + "/ads", fields="name,status,creative{object_story_spec}")["data"]:
    o = a["creative"]["object_story_spec"].get("video_data", {})
    print("  ", a["name"], a["status"], "| form", o.get("call_to_action", {}).get("value", {}).get("lead_gen_form_id"))
