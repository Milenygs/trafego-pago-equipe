#!/usr/bin/env python3
"""
AFS Loja Mantena (MG) — build da inauguracao.

Cria a estrutura das 2 campanhas de inauguracao na conta CA01 MANTENA,
tudo PAUSED. Nao cria anuncios: os criativos ainda nao existem.

Estrutura:
  A) [INAUG] Reconhecimento | Mantena  — OUTCOME_AWARENESS / REACH  — R$550
  B) [INAUG] Trafego Perfil | Mantena  — OUTCOME_TRAFFIC / LINK_CLICKS — R$450

Ambas: cidade de Mantena/MG inteira (raio 0), 18-65, so Instagram.

Uso:
    python build_inauguracao.py            # cria
    python build_inauguracao.py --dry-run  # so mostra os payloads
"""
import os
import sys
import json
import argparse
from datetime import datetime, timedelta

SKILL = os.path.expandvars(r"%USERPROFILE%\OneDrive\.claude\skills\meta-ads-ratos\scripts")
sys.path.insert(0, SKILL)

from lib import init_api  # noqa: E402
from facebook_business.adobjects.adaccount import AdAccount  # noqa: E402

# ---------------------------------------------------------------------------
# Constantes da conta (levantadas 25/08/2026)
# ---------------------------------------------------------------------------
ACCOUNT = "act_1984385632259800"          # CA01 MANTENA (BM acaifruitshow.fsa)
PAGE_ID = "1332437986612101"              # Acai fruit show Mantena
IG_USER_ID = "17841437791016896"          # @acaifruitshowmantena (10 seguidores)
IG_USERNAME = "acaifruitshowmantena"
GEO_KEY_MANTENA = "259174"                # Mantena, Minas Gerais

# Verba (centavos)
VERBA_RECONHECIMENTO = 55000              # R$550
VERBA_TRAFEGO = 45000                     # R$450

FIM = "2026-09-04T23:59:00-0300"          # dia da inauguracao (a confirmar)

# Campanhas ja criadas em execucoes anteriores (evita duplicar ao reexecutar).
CAMPANHAS_EXISTENTES = {
    "reconhecimento": "120253323731300422",
}

# ---------------------------------------------------------------------------

INSTAGRAM_POSITIONS = ["stream", "story", "reels", "explore", "explore_home",
                       "profile_feed", "ig_search"]


def targeting():
    """Cidade de Mantena inteira, 18-65, so Instagram, sem publico Advantage+."""
    return {
        "geo_locations": {
            "cities": [{"key": GEO_KEY_MANTENA, "radius": 0, "distance_unit": "kilometer"}],
            "location_types": ["home", "recent"],
        },
        "age_min": 18,
        "age_max": 65,
        "publisher_platforms": ["instagram"],
        "instagram_positions": INSTAGRAM_POSITIONS,
        "targeting_automation": {"advantage_audience": 0},
    }


def build(dry_run=False):
    init_api()
    account = AdAccount(ACCOUNT)
    inicio = (datetime.now() + timedelta(minutes=15)).strftime("%Y-%m-%dT%H:%M:%S-0300")
    criados = {}

    plano = [
        {
            "chave": "reconhecimento",
            "campanha": {
                "name": "[INAUG] Reconhecimento | Mantena",
                "objective": "OUTCOME_AWARENESS",
                "status": "PAUSED",
                "special_ad_categories": [],
                "buying_type": "AUCTION",
                "is_adset_budget_sharing_enabled": False,
            },
            "conjunto": {
                "name": "Mantena Cidade | 18-65 | IG",
                "optimization_goal": "REACH",
                "billing_event": "IMPRESSIONS",
                # explicito: sem ele a API recusa com subcode 2490487
                "bid_strategy": "LOWEST_COST_WITHOUT_CAP",
                "lifetime_budget": VERBA_RECONHECIMENTO,
                "start_time": inicio,
                "end_time": FIM,
                "status": "PAUSED",
                "targeting": targeting(),
                # teto de frequencia: no maximo 2 impressoes por pessoa por dia.
                # Em cidade de ~19 mil no IG, sem teto a verba viraria repeticao.
                "frequency_control_specs": [
                    {"event": "IMPRESSIONS", "interval_days": 1, "max_frequency": 2}
                ],
            },
        },
        {
            "chave": "trafego_perfil",
            "campanha": {
                "name": "[INAUG] Trafego Perfil | Mantena",
                "objective": "OUTCOME_TRAFFIC",
                "status": "PAUSED",
                "special_ad_categories": [],
                "buying_type": "AUCTION",
                "is_adset_budget_sharing_enabled": False,
            },
            "conjunto": {
                # LINK_CLICKS -> instagram.com/<perfil>, e nao PROFILE_VISIT:
                # perfil novo costuma cair no subcode 2016153 ("conta nao elegivel
                # a anuncios de Visita ao Perfil"), que so estoura na criacao do
                # ANUNCIO. Ver aprendizados.md 2026-08-10 (Tomba).
                "name": "Mantena Cidade | 18-65 | IG",
                "optimization_goal": "LINK_CLICKS",
                "billing_event": "IMPRESSIONS",
                "bid_strategy": "LOWEST_COST_WITHOUT_CAP",
                "destination_type": "WEBSITE",
                "lifetime_budget": VERBA_TRAFEGO,
                "start_time": inicio,
                "end_time": FIM,
                "status": "PAUSED",
                "targeting": targeting(),
            },
        },
    ]

    for item in plano:
        camp_params = item["campanha"]
        if dry_run:
            print(f"\n--- CAMPANHA {camp_params['name']} ---")
            print(json.dumps(camp_params, ensure_ascii=False, indent=2))
            print(json.dumps(item["conjunto"], ensure_ascii=False, indent=2))
            continue

        camp_id = CAMPANHAS_EXISTENTES.get(item["chave"])
        if camp_id:
            print(f"[--] campanha {camp_params['name']} ja existe -> {camp_id}")
        else:
            camp_id = account.create_campaign(params=camp_params)["id"]
            print(f"[OK] campanha {camp_params['name']} -> {camp_id}")

        adset_params = dict(item["conjunto"], campaign_id=camp_id)
        adset = account.create_ad_set(params=adset_params)
        print(f"[OK] conjunto {adset_params['name']} -> {adset['id']}")

        criados[item["chave"]] = {"campanha": camp_id, "conjunto": adset["id"]}

    if criados:
        print("\n=== IDS ===")
        print(json.dumps(criados, ensure_ascii=False, indent=2))
    return criados


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    build(dry_run=ap.parse_args().dry_run)
