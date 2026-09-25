"""Belo 24/09/2026 - campanha de engajamento para o Direct com o post de lancamento do IG.

Publico = o do conjunto [DIRECT_insta] da ANIV17 (120245559079980358): 6 publicos quentes,
exclui Compradores + Complemento, Instagram sem Stories, 25-60, sem geo. R$100/dia. Tudo PAUSED.
Uso: python build_belo_direct.py
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
POST_IG = "18629435476003635"  # post de 23/09 "Um novo ponto para comecar uma nova historia" (Belo)
REGIONAL = {
    "regional_regulated_categories": ["BRAZIL_REGULATION", "VOLUNTARY_VERIFICATION"],
    "regional_regulation_identities": {"universal_beneficiary": "609854092925940",
                                       "universal_payer": "609854092925940"},
}
TARGETING = {
    "age_min": 25, "age_max": 60,
    "custom_audiences": [{"id": i} for i in (
        "120245517541240358",  # M_AP_Ponto_Qualificados_Sem_Vendas
        "120245517750200358",  # M_Site_Todos_180D
        "120245519551400358",  # M_MQL_Site_180D
        "120245519552380358",  # M_Simulacao_180D
        "120245540043470358",  # IG_ENGAJ_AP_PONTO_180D
        "120245540058970358",  # IG_VIDEO_AP_PONTO_50%_180D
    )],
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


camp = post(ACT + "/campaigns", {
    "name": "[BELO] Direct | Engajamento | SET26", "objective": "OUTCOME_ENGAGEMENT",
    "status": "PAUSED", "special_ad_categories": [], "is_adset_budget_sharing_enabled": "false",
})["id"]
print("campanha", camp)
time.sleep(1)
adset = post(ACT + "/adsets", {
    "name": "[BELO] Direct Público Quente 180D", "campaign_id": camp, "status": "PAUSED",
    "daily_budget": 10000, "billing_event": "IMPRESSIONS", "optimization_goal": "CONVERSATIONS",
    "destination_type": "INSTAGRAM_DIRECT", "bid_strategy": "LOWEST_COST_WITHOUT_CAP",
    "promoted_object": {"page_id": PAGE}, "targeting": TARGETING, **REGIONAL,
})["id"]
print("conjunto", adset)
time.sleep(1)
cr = post(ACT + "/adcreatives", {
    "name": "POST Lancamento Belo | Direct SET26",
    "object_id": PAGE, "instagram_user_id": IG, "source_instagram_media_id": POST_IG,
    "call_to_action": {"type": "INSTAGRAM_MESSAGE",
                       "value": {"app_destination": "INSTAGRAM_DIRECT", "link": "https://www.instagram.com/"}},
    "degrees_of_freedom_spec": {"creative_features_spec": {f: {"enroll_status": "OPT_OUT"} for f in OPT_OUT}},
})["id"]
print("criativo", cr)
time.sleep(1)
ad = post(ACT + "/ads", {"name": "POST Lançamento Belo", "adset_id": adset,
                         "creative": {"creative_id": cr}, "status": "PAUSED"})["id"]
print("anuncio", ad)
