#!/usr/bin/env python3
"""
Açaí Fruit Show Cidade Nova (act_4213499778794589) — Cardápio Web | Pedir agora | 12 e 13/09

Pedido da Mileny em 11/09/2026 (repassando a Cristhielly Canela): tráfego com botão
"Pedir agora" levando para o cardápio web da loja. Sábado 12 e domingo 13/09, das 12h
às 19h, R$ 100 de verba total, 8 bairros. O criativo chega depois — este script sobe
só campanha + conjunto, ambos PAUSED. O anúncio sai do build_anuncio.py.

Decisões:
- Conta da própria loja (CA - AFS Cidade Nova, cartão da loja), não a CA - LOJA FSA:
  a FSA estava com R$ 12 de saldo e jogaria o gasto no extrato da Fraga Maia.
- LINK_CLICKS: a conta não tem pixel, então LANDING_PAGE_VIEWS não teria como medir.
- Vitalício + day_parting: programação de horário só existe com orçamento vitalício.
- 1 pino de 1 km por bairro (raio mínimo da Meta). Coordenadas do OpenStreetMap;
  Cidade Nova, Campo Limpo e Parque Ipê batem com os pinos que a loja usou em maio.
- Sem location_types: a Meta aplica sozinha o padrão atual ("mora ou esteve").

Uso:
  python build_campanha.py                    # cria campanha + conjunto
  python build_campanha.py --campanha ID      # reaproveita campanha já criada
"""
import argparse, json, os, sys
from datetime import date

SCRIPTS = os.path.join(os.environ["USERPROFILE"], "OneDrive", ".claude", "skills",
                       "meta-ads-ratos", "scripts")
sys.path.insert(0, SCRIPTS)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from lib import init_api
from facebook_business.api import FacebookAdsApi
from facebook_business.exceptions import FacebookRequestError

ACT = "act_4213499778794589"
NOME_CAMPANHA = "[TRÁFEGO] Cardápio Web | Pedir agora | 12 e 13/09"
NOME_CONJUNTO = "8 Bairros | 18-55 | IG | Sáb e Dom 12h-19h"

# days da Meta: 0 = domingo ... 6 = sábado
assert date(2026, 9, 12).weekday() == 5 and date(2026, 9, 13).weekday() == 6

PINOS = [
    ("Cidade Nova",     -12.22596, -38.96103),
    ("Campo Limpo",     -12.21499, -38.97149),
    ("Parque Ipê",      -12.21336, -38.95812),
    ("Pampalona",       -12.22516, -38.97970),
    ("Gabriela",        -12.23052, -38.98486),
    ("Jardim Cruzeiro", -12.24309, -38.97933),
    ("Baraúnas",        -12.23553, -38.96761),
    ("Queimadinha",     -12.24020, -38.96110),  # meio dos 2 pontos que o OSM dá pro bairro
]

TARGETING = {
    "geo_locations": {"custom_locations": [
        {"latitude": lat, "longitude": lng, "radius": 1, "distance_unit": "kilometer"}
        for _, lat, lng in PINOS]},
    "age_min": 18,
    "age_max": 55,
    "publisher_platforms": ["instagram"],
    "instagram_positions": ["stream", "story", "reels", "explore", "explore_home",
                            "profile_feed", "ig_search"],
    "targeting_automation": {"advantage_audience": 0},
}

init_api()
api = FacebookAdsApi.get_default_api()


def chamar(metodo, path, params):
    try:
        return api.call(metodo, path, params=params).json()
    except FacebookRequestError as e:
        err = (e.body() or {}).get("error", {})
        raise SystemExit(f"ERRO {metodo} {'/'.join(path)}: {err.get('message')} | "
                         f"subcode {err.get('error_subcode')} | "
                         f"{err.get('error_user_title')} — {err.get('error_user_msg')}")


ap = argparse.ArgumentParser()
ap.add_argument("--campanha", help="ID de campanha já criada (pula a criação)")
args = ap.parse_args()

# --- 1. Campanha -------------------------------------------------------------
if args.campanha:
    camp_id = args.campanha
    print(f"Campanha reaproveitada: {camp_id}")
else:
    camp_id = chamar("POST", (ACT, "campaigns"), {
        "name": NOME_CAMPANHA,
        "objective": "OUTCOME_TRAFFIC",
        "buying_type": "AUCTION",
        "special_ad_categories": [],
        "is_adset_budget_sharing_enabled": False,
        "status": "PAUSED",
    })["id"]
    print(f"Campanha criada: {camp_id}")

# --- 2. Conjunto -------------------------------------------------------------
adset_id = chamar("POST", (ACT, "adsets"), {
    "name": NOME_CONJUNTO,
    "campaign_id": camp_id,
    "lifetime_budget": 10000,                         # R$ 100,00
    "start_time": "2026-09-12T12:00:00-0300",
    "end_time": "2026-09-13T19:00:00-0300",
    "pacing_type": ["day_parting"],
    "adset_schedule": [{"start_minute": 720, "end_minute": 1140,   # 12h-19h
                        "days": [6, 0], "timezone_type": "USER"}],
    "optimization_goal": "LINK_CLICKS",
    "billing_event": "IMPRESSIONS",
    "bid_strategy": "LOWEST_COST_WITHOUT_CAP",
    "destination_type": "WEBSITE",
    "targeting": TARGETING,
    "status": "PAUSED",
})["id"]
print(f"Conjunto criado: {adset_id}")

# --- 3. Conferência por releitura --------------------------------------------
conf = {
    "campanha": chamar("GET", (camp_id,), {
        "fields": "name,objective,status,effective_status,is_adset_budget_sharing_enabled"}),
    "conjunto": chamar("GET", (adset_id,), {
        "fields": "name,status,effective_status,lifetime_budget,start_time,end_time,"
                  "pacing_type,adset_schedule,optimization_goal,billing_event,"
                  "destination_type,targeting"}),
    "estimativa": chamar("GET", (ACT, "delivery_estimate"), {
        "targeting_spec": TARGETING, "optimization_goal": "LINK_CLICKS"}),
}
t = conf["conjunto"].get("targeting", {})
checks = {
    "so_instagram": t.get("publisher_platforms") == ["instagram"],
    "8_pinos_1km": len(t.get("geo_locations", {}).get("custom_locations", [])) == 8,
    "day_parting": conf["conjunto"].get("pacing_type") == ["day_parting"],
    "horario_12_19": [(s["start_minute"], s["end_minute"])
                      for s in conf["conjunto"].get("adset_schedule", [])] == [(720, 1140)],
    "vitalicio_100": conf["conjunto"].get("lifetime_budget") == "10000",
    "pausados": conf["campanha"].get("status") == "PAUSED"
                and conf["conjunto"].get("status") == "PAUSED",
}
conf["checks"] = checks
print(json.dumps(checks, ensure_ascii=False, indent=2))
est = (conf["estimativa"].get("data") or [{}])[0]
print(f"Público estimado: {est.get('estimate_mau_lower_bound')} a "
      f"{est.get('estimate_mau_upper_bound')} pessoas")

dest = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resultado_campanha.json")
with open(dest, "w", encoding="utf-8") as f:
    json.dump({"campaign_id": camp_id, "adset_id": adset_id, "pinos": PINOS,
               "confirmacao": conf}, f, ensure_ascii=False, indent=2)
print("\n=> " + dest)
