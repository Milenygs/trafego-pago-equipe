"""Belo 24/09/2026 - trafego para o perfil do IG com o post de lancamento (18629435476003635).

BH 17 km + Contagem 17 km + Vespasiano 20 km, 25-60 (mesma idade da campanha de Direct), interesses de
imovel para filtrar, exclui compradores. R$30/dia. Tudo PAUSED.
Uso: python build_belo_perfil.py
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
PAGE = "198169833565944"
IG = "17841401339383360"
POST_IG = "18629435476003635"
REGIONAL = {
    "regional_regulated_categories": ["BRAZIL_REGULATION", "VOLUNTARY_VERIFICATION"],
    "regional_regulation_identities": {"universal_beneficiary": "609854092925940",
                                       "universal_payer": "609854092925940"},
}
TARGETING = {
    "age_min": 25, "age_max": 60,
    "geo_locations": {"cities": [
        # raio minimo de cidade aceito pela Meta: 17 km (10 e 15 deram subcode 1487110)
        {"key": "244661", "radius": 17, "distance_unit": "kilometer"},  # Belo Horizonte
        {"key": "249756", "radius": 17, "distance_unit": "kilometer"},  # Contagem
        {"key": "273969", "radius": 20, "distance_unit": "kilometer"},  # Vespasiano
    ]},
    "flexible_spec": [{"interests": [{"id": "6002976176121"}, {"id": "6002986908368"},
                                     {"id": "6003103732434"}, {"id": "6003418314031"}]}],
    "excluded_custom_audiences": [{"id": "120245517540390358"}, {"id": "120245517540780358"}],
    "publisher_platforms": ["instagram"],
    "instagram_positions": ["stream", "explore", "reels", "profile_feed"],
    "device_platforms": ["mobile", "desktop"],
    "targeting_automation": {"advantage_audience": 0},
}
OPT_OUT = ["advantage_plus_creative", "enhance_cta", "inline_comment", "text_optimizations",
           "image_touchups", "image_uncrop", "adapt_to_placement", "show_summary", "reveal_details_over_time"]


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


# --campanha ID reaproveita a campanha ja criada (24/09: 120245801355950358)
camp = sys.argv[sys.argv.index("--campanha") + 1] if "--campanha" in sys.argv else post(ACT + "/campaigns", {
    "name": "[BELO] Perfil | Tráfego | SET26", "objective": "OUTCOME_TRAFFIC",
    "status": "PAUSED", "special_ad_categories": [], "is_adset_budget_sharing_enabled": "false",
})["id"]
print("campanha", camp)
time.sleep(1)
adset = post(ACT + "/adsets", {
    "name": "[BELO] Perfil BH Contagem Vespasiano 25-60", "campaign_id": camp, "status": "PAUSED",
    "daily_budget": 3000, "billing_event": "IMPRESSIONS", "optimization_goal": "PROFILE_VISIT",
    "destination_type": "INSTAGRAM_PROFILE", "bid_strategy": "LOWEST_COST_WITHOUT_CAP",
    "promoted_object": {"page_id": PAGE, "smart_pse_enabled": False}, "targeting": TARGETING, **REGIONAL,
})["id"]
print("conjunto", adset)
time.sleep(1)
cr = post(ACT + "/adcreatives", {
    "name": "POST Lancamento Belo | Perfil SET26",
    "object_id": PAGE, "instagram_user_id": IG, "source_instagram_media_id": POST_IG,
    "call_to_action": {"type": "VIEW_INSTAGRAM_PROFILE", "value": {"link": "https://www.instagram.com/apponto/"}},
    "degrees_of_freedom_spec": {"creative_features_spec": {f: {"enroll_status": "OPT_OUT"} for f in OPT_OUT}},
})["id"]
print("criativo", cr)
time.sleep(1)
ad = post(ACT + "/ads", {"name": "POST Lançamento Belo", "adset_id": adset,
                         "creative": {"creative_id": cr}, "status": "PAUSED"})["id"]
print("anuncio", ad)
