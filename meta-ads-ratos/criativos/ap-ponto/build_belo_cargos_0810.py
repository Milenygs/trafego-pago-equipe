"""Belo 08/10/2026 - conjunto novo na LP: servidor publico, enfermagem e professores (R$50/dia, PAUSED).

Pedido da Mileny. Copia a configuracao do Interesse 25-45 da LP (pixel LEAD, FB+IG+AN, anunciante BR) com a
praca e a idade do conjunto modelo (BH/Contagem/Vespasiano, home+recent, 25-60, Advantage desligado).
Publico = cargos (work_positions) OU setores (industries), sem interesse de imovel por cima.
Anuncios: os mesmos criativos do Interesse (Locucao v1 e Leo v1), com o mesmo nome (utm_content no CV).
Uso: python build_belo_cargos_0810.py
"""
import json
import os
import sys
from pathlib import Path

import requests

SKILL = Path(os.path.expanduser("~/OneDrive/.claude/skills/meta-ads-ratos"))
env = (SKILL / ".env").read_text(encoding="utf-8")
TOKEN = [l.split("=", 1)[1].strip().strip('"') for l in env.splitlines() if l.startswith("META_ADS_TOKEN")][0]
G = "https://graph.facebook.com/v23.0/"

ACT = "act_1043516946010441"
PIXEL = "211205516600655"
CAMP = "120245790359480358"  # [BELO] Lançamento | Lead LP | SET26
NOME = "[BELO] Servidores Enfermagem Professores 25-60"
REGIONAL = {
    "regional_regulated_categories": ["BRAZIL_REGULATION", "VOLUNTARY_VERIFICATION"],
    "regional_regulation_identities": {"universal_beneficiary": "609854092925940",
                                       "universal_payer": "609854092925940"},
}
ANUNCIOS = {  # anuncio de origem no Interesse 25-45 -> mesmo nome no conjunto novo
    "VID Locucao Lancamento v1": "120245790413890358",
    "VID UGC Leo v1": "120245790442160358",
}
CARGOS = {
    "103122973061151": "Professor",
    "140985615918781": "Professora de Ed. Infantil",
    "208810049131419": "Auxiliar de Classe / Professora",
    "153495528089412": "Professor/Coordenador Pedagógico",
    "112301005450413": "Pedagogo",
    "139732142711124": "Professor de Educação Física",
    "137813726259835": "Professora de Língua Inglesa",
    "140630402637577": "Enfermeiro",
    "201153853387786": "Enfermeira",
    "102268143164382": "Enfermeira Chefe",
    "121063687942792": "Enfermeira do Trabalho",
    "110687332285785": "Técnico de Enfermagem",
    "190567127622783": "AUXILIAR DE ENFERMAGEM/TECNICO EM ENFERMAGEM",
    "157410400963650": "Auxiliar técnico de enfermagem",
    "115970118412995": "Servidor público no Brasil",
}
SETORES = {
    "6008888998983": "Educação e bibliotecas",
    "6012903159383": "Serviços de saúde e médicos",
    "6019621029983": "Funcionários do governo (global)",
}

TARGETING = {
    "age_min": 25, "age_max": 60,
    "geo_locations": {
        "cities": [{"key": "244661"}, {"key": "249756"}, {"key": "273969"}],  # BH, Contagem, Vespasiano
        "location_types": ["home", "recent"],
    },
    "excluded_custom_audiences": [{"id": "120245517540390358"}, {"id": "120245517540780358"}],
    "flexible_spec": [{
        "work_positions": [{"id": k, "name": v} for k, v in CARGOS.items()],
        "industries": [{"id": k, "name": v} for k, v in SETORES.items()],
    }],
    "targeting_automation": {"advantage_audience": 0, "individual_setting": {"geo": 0}},
    "targeting_relaxation_types": {"lookalike": 0, "custom_audience": 0},
    "publisher_platforms": ["facebook", "instagram", "audience_network"],
    "facebook_positions": ["feed", "right_hand_column", "story", "facebook_reels"],
    "instagram_positions": ["stream", "reels", "profile_feed"],
    "audience_network_positions": ["classic", "rewarded_video"],
    "device_platforms": ["mobile", "desktop"],
    "brand_safety_content_filter_levels": ["AN_RELAXED"],
}


def post(path, data, fatal=True):
    data = {k: (json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v) for k, v in data.items()}
    data["access_token"] = TOKEN
    r = requests.post(G + path, data=data).json()
    if "error" in r:
        print(json.dumps(r["error"], ensure_ascii=False, indent=1))
        if fatal:
            sys.exit(1)
    return r


def get(path, **params):
    params["access_token"] = TOKEN
    return requests.get(G + path, params=params).json()


def main():
    existentes = {a["name"]: a["id"] for a in get(CAMP + "/adsets", fields="name", limit=50).get("data", [])}
    if NOME in existentes:
        sys.exit(f"Conjunto ja existe: {existentes[NOME]}")

    criativos = {}
    for nome, ad_id in ANUNCIOS.items():
        cr = get(ad_id, fields="name,creative{id,url_tags,object_story_spec,asset_feed_spec}")
        criativos[nome] = cr["creative"]["id"]
        print("criativo", nome, cr["creative"]["id"], "| url_tags:", cr["creative"].get("url_tags"))

    r = post(ACT + "/adsets", {
        "name": NOME, "campaign_id": CAMP, "status": "PAUSED",
        "daily_budget": 5000, "billing_event": "IMPRESSIONS", "optimization_goal": "OFFSITE_CONVERSIONS",
        "bid_strategy": "LOWEST_COST_WITHOUT_CAP", "destination_type": "WEBSITE",
        "promoted_object": {"pixel_id": PIXEL, "custom_event_type": "LEAD"},
        "attribution_spec": [{"event_type": "CLICK_THROUGH", "window_days": 7}],
        "targeting": TARGETING, **REGIONAL,
    })
    adset = r["id"]
    print("adset", adset)

    for nome, cr_id in criativos.items():
        ad = post(ACT + "/ads", {"name": nome, "adset_id": adset,
                                 "creative": {"creative_id": cr_id}, "status": "PAUSED"}, fatal=False)
        print("ad", nome, ad.get("id"))

    print(json.dumps(get(adset, fields="name,status,effective_status,daily_budget,optimization_goal,promoted_object,"
                                         "targeting,regional_regulated_categories"), ensure_ascii=False, indent=1))
    print(json.dumps(get(adset + "/ads", fields="name,status,effective_status,creative{id}"), ensure_ascii=False, indent=1))
    est = get(adset + "/delivery_estimate", optimization_goal="OFFSITE_CONVERSIONS")
    for e in est.get("data", []):
        print("estimativa: publico", e.get("estimate_mau_lower_bound"), "a", e.get("estimate_mau_upper_bound"),
              "| pronto:", e.get("estimate_ready"))
    if "error" in est:
        print("estimativa:", est["error"].get("message"))


if __name__ == "__main__":
    main()
