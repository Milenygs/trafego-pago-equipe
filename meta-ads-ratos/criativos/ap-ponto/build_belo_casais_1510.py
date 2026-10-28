"""Belo 15/10/2026 - conjunto novo na LP: noivos, recem-casados e pais de bebe (R$100/dia, PAUSED).

Pedido da Mileny: publico de primeiro ape que vai financiar, para o video do Leo sobre familia e sonho.
Copia a configuracao do Servidores (build_belo_cargos_0810.py): pixel LEAD, FB+IG+AN, anunciante BR.
Praca de 15/10: BH (cidade) + Vespasiano (cidade) 20 km, expansao geo desligada. Idade 25-45.
Publico (um grupo, OU): noivos 3m/6m/1a, recem-casados 3m/6m/1a, pais de bebe ate 12 meses e de 1 a 2 anos.
Estimativa de 15/10 (delivery_estimate): 28,8 mil a 33,8 mil pessoas.
Anuncio: VID Locucao Lancamento v1 (controle, criativo do Interesse). O Leo familia entra quando o video chegar.
Entra no lugar do Interesse 25-45: o Interesse so pausa quando a Mileny ativar este.
Uso: python build_belo_casais_1510.py
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
NOME = "[BELO] Noivos Recem-casados Pais Bebe 25-45"
REGIONAL = {
    "regional_regulated_categories": ["BRAZIL_REGULATION", "VOLUNTARY_VERIFICATION"],
    "regional_regulation_identities": {"universal_beneficiary": "609854092925940",
                                       "universal_payer": "609854092925940"},
}
ANUNCIOS = {  # anuncio de origem no Interesse 25-45 -> mesmo nome no conjunto novo
    "VID Locucao Lancamento v1": "120245790413890358",
}
EVENTOS = {
    "6012631862383": "Noivaram recentemente (3 meses)",
    "6002714398772": "Noivos recentes (6 meses)",
    "6003050210972": "Noivaram recentemente (1 ano)",
    "6013133420583": "Recém-casados (3 meses)",
    "6003050226972": "Recém-casados (6 meses)",
    "6002714398172": "Recém-casados (1 ano)",
}
FAMILIA = {
    "6023005372383": "Pais, mães ou responsáveis (até 12 meses)",
    "6023005458383": "Pais com crianças pequenas (1 a 2 anos de idade)",
}

TARGETING = {
    "age_min": 25, "age_max": 45,
    "geo_locations": {
        "cities": [{"key": "244661"},  # Belo Horizonte, cidade sem raio
                   {"key": "273969", "radius": 20, "distance_unit": "kilometer"}],  # Vespasiano 20 km
        "location_types": ["home", "recent"],
    },
    "excluded_custom_audiences": [{"id": "120245517540390358"}, {"id": "120245517540780358"}],
    "flexible_spec": [{
        "life_events": [{"id": k, "name": v} for k, v in EVENTOS.items()],
        "family_statuses": [{"id": k, "name": v} for k, v in FAMILIA.items()],
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
    conta = get(ACT, fields="account_status")
    if conta.get("account_status") != 1:
        sys.exit(f"Conta sem permitir escrita: {conta}")

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
        "daily_budget": 10000, "billing_event": "IMPRESSIONS", "optimization_goal": "OFFSITE_CONVERSIONS",
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
                                         "attribution_spec,targeting,regional_regulated_categories"),
                     ensure_ascii=False, indent=1))
    print(json.dumps(get(adset + "/ads", fields="name,status,effective_status,creative{id,url_tags}"),
                     ensure_ascii=False, indent=1))
    est = get(adset + "/delivery_estimate", optimization_goal="OFFSITE_CONVERSIONS")
    for e in est.get("data", []):
        print("estimativa: publico", e.get("estimate_mau_lower_bound"), "a", e.get("estimate_mau_upper_bound"),
              "| pronto:", e.get("estimate_ready"))
    if "error" in est:
        print("estimativa:", est["error"].get("message"))


if __name__ == "__main__":
    main()
