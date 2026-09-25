#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AFS Osasco — build da inauguracao (12/09/2026).

Conta       : act_1075513944839445 (C01 OSASCO)
Pagina / IG : 1309426062248408 / 17841466580616871
Geo         : PINO na loja, raio 8km
              R. Sao Nicolau, 27 - Santo Antonio, Osasco/SP, 06132-093, loja 4
              lat -23.5601509 / lng -46.7995541

  A) [INAUG] Reconhecimento Pino 8km | Osasco   R$500  hoje -> 13/09
     Post organico do Instagram, publico aberto (sem interesses), so Instagram.

  B) ajuste do conjunto de trafego que a Mileny ja subiu (120252648786760472):
     troca cidade Osasco inteira -> PINO 8km, e fecha em so Instagram.

Tudo criado PAUSED. Uso:
    python build_inauguracao.py --reach     # so estimativa de publico
    python build_inauguracao.py --dry-run   # mostra o plano
    python build_inauguracao.py             # cria a campanha A
    python build_inauguracao.py --ajusta-trafego   # aplica o ajuste B
"""
import argparse
import json
import os
import sys
from datetime import datetime, timedelta

AQUI = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.abspath(os.path.join(AQUI, "..", ".."))
sys.path.insert(0, os.path.join(SKILL, "scripts"))

from lib import init_api  # noqa: E402
from facebook_business.api import FacebookAdsApi  # noqa: E402

# ---------------------------------------------------------------------------

CONTA = "act_1075513944839445"
PAGINA = "1309426062248408"
INSTAGRAM = "17841466580616871"

LAT = -23.5601509
LNG = -46.7995541
RAIO_KM = 8

# post organico: "ALO, OSASCO!" 28/08 — 36 likes, 3 comentarios (melhor do perfil)
POST_IG = "18027260741894112"

VERBA_RECONHECIMENTO = 50000            # R$500 em centavos
FIM_RECONHECIMENTO = "2026-09-13T23:59:00-0300"

ADSET_TRAFEGO = "120252648786760472"    # "Pino_loja osasco" da [Trafego_perfil]

POS_TODOS = ["stream", "story", "reels", "explore", "explore_home",
             "profile_feed", "ig_search"]

DOF_SPEC = {
    "creative_features_spec": {
        chave: {"enroll_status": "OPT_OUT"}
        for chave in (
            "advantage_plus_creative", "enhance_cta", "text_optimizations",
            "video_auto_crop", "video_uncrop", "pac_relaxation",
        )
    }
}

api = None


def chamar(metodo, caminho, params=None):
    try:
        return api.call(metodo, caminho, params=params or {}).json()
    except Exception as exc:  # noqa: BLE001
        corpo = getattr(exc, "_body", None) or getattr(exc, "body", None)
        if isinstance(corpo, dict):
            err = corpo.get("error", corpo)
            msg = err.get("error_user_msg") or err.get("message")
            sub = err.get("error_subcode") or err.get("code")
            raise SystemExit("\nFALHOU em %s [%s]\n  %s\n"
                             % ("/".join(map(str, caminho)), sub, msg))
        raise SystemExit("\nFALHOU em %s\n  %s\n"
                         % ("/".join(map(str, caminho)), exc))


def targeting():
    """Pino na loja, raio 8km, publico aberto, so Instagram, sem IA."""
    return {
        "geo_locations": {
            "custom_locations": [{
                "latitude": LAT,
                "longitude": LNG,
                "radius": RAIO_KM,
                "distance_unit": "kilometer",
            }],
            "location_types": ["home", "recent"],
        },
        "age_min": 18,
        "age_max": 65,
        "publisher_platforms": ["instagram"],
        "instagram_positions": POS_TODOS,
        "device_platforms": ["mobile", "desktop"],
        "targeting_automation": {"advantage_audience": 0},
    }


def estimar():
    res = chamar("GET", (CONTA, "delivery_estimate"), {
        "optimization_goal": "REACH",
        "targeting_spec": json.dumps(targeting()),
    })
    dados = (res.get("data") or [{}])[0]
    print("\n=== ALCANCE ESTIMADO — pino %dkm ===" % RAIO_KM)
    print("  endereco : R. Sao Nicolau, 27 - Santo Antonio, Osasco/SP")
    print("  pino     : %s , %s" % (LAT, LNG))
    print("  publico  : %s a %s pessoas"
          % (f"{dados.get('estimate_mau_lower_bound', 0):,}".replace(",", "."),
             f"{dados.get('estimate_mau_upper_bound', 0):,}".replace(",", ".")))
    print("  json     : %s" % json.dumps(dados, ensure_ascii=False)[:400])
    return dados


def criar_reconhecimento():
    inicio = (datetime.now() + timedelta(minutes=20)).strftime(
        "%Y-%m-%dT%H:%M:%S-0300")

    camp = chamar("POST", (CONTA, "campaigns"), {
        "name": "[INAUG] Reconhecimento Pino 8km | Osasco",
        "objective": "OUTCOME_AWARENESS",
        "status": "PAUSED",
        "special_ad_categories": json.dumps([]),
        "buying_type": "AUCTION",
        "is_adset_budget_sharing_enabled": "false",
    })
    print("  campanha : %s" % camp["id"])

    conj = chamar("POST", (CONTA, "adsets"), {
        "name": "Pino 8km | 18-65 | aberto | IG",
        "campaign_id": camp["id"],
        "billing_event": "IMPRESSIONS",
        "optimization_goal": "REACH",
        "bid_strategy": "LOWEST_COST_WITHOUT_CAP",
        "lifetime_budget": VERBA_RECONHECIMENTO,
        "start_time": inicio,
        "end_time": FIM_RECONHECIMENTO,
        "status": "PAUSED",
        "targeting": json.dumps(targeting()),
        "frequency_control_specs": json.dumps(
            [{"event": "IMPRESSIONS", "interval_days": 1, "max_frequency": 2}]),
    })
    print("  conjunto : %s" % conj["id"])

    criativo = chamar("POST", (CONTA, "adcreatives"), {
        "name": "[INAUG] Osasco | post ALO OSASCO | organico",
        "instagram_user_id": INSTAGRAM,
        "source_instagram_media_id": POST_IG,
        "degrees_of_freedom_spec": json.dumps(DOF_SPEC),
    })
    print("  criativo : %s" % criativo["id"])

    anuncio = chamar("POST", (CONTA, "ads"), {
        "name": "[INAUG] Osasco | ALO OSASCO",
        "adset_id": conj["id"],
        "creative": json.dumps({"creative_id": criativo["id"]}),
        "status": "PAUSED",
    })
    print("  anuncio  : %s" % anuncio["id"])

    return {"campanha": camp["id"], "conjunto": conj["id"],
            "criativo": criativo["id"], "anuncio": anuncio["id"]}


def ajustar_trafego():
    """Troca cidade Osasco inteira pelo pino 8km e fecha em so Instagram.
    Mantem o resto do conjunto (PROFILE_VISIT / INSTAGRAM_PROFILE / R$800)."""
    atual = chamar("GET", (ADSET_TRAFEGO,), {"fields": "name,targeting"})
    novo = dict(atual.get("targeting") or {})
    # campo descontinuado pela Meta — se reenviado, erro 1870197
    novo.pop("targeting_optimization", None)
    novo["geo_locations"] = targeting()["geo_locations"]
    novo["publisher_platforms"] = ["instagram"]
    novo["instagram_positions"] = POS_TODOS
    novo["targeting_automation"] = {"advantage_audience": 0}

    chamar("POST", (ADSET_TRAFEGO,), {"targeting": json.dumps(novo)})
    print("  conjunto %s atualizado: pino 8km + so Instagram" % ADSET_TRAFEGO)
    depois = chamar("GET", (ADSET_TRAFEGO,), {"fields": "name,targeting"})
    print(json.dumps(depois, ensure_ascii=False, indent=2)[:900])


def main():
    global api
    ap = argparse.ArgumentParser()
    ap.add_argument("--reach", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--ajusta-trafego", action="store_true")
    args = ap.parse_args()

    init_api()
    api = FacebookAdsApi.get_default_api()

    if args.reach:
        estimar()
        return

    if args.dry_run:
        print(json.dumps({
            "conta": CONTA,
            "targeting": targeting(),
            "verba": VERBA_RECONHECIMENTO,
            "fim": FIM_RECONHECIMENTO,
            "post": POST_IG,
        }, ensure_ascii=False, indent=2))
        return

    if args.ajusta_trafego:
        print("\n=== B) ajuste do conjunto de trafego ===")
        ajustar_trafego()
        return

    print("\n=== A) Reconhecimento pino 8km ===")
    ids = criar_reconhecimento()
    print("\n=== IDS ===")
    print(json.dumps(ids, ensure_ascii=False, indent=2))
    print("\nCriado PAUSED. Ativar depois de conferir.")


if __name__ == "__main__":
    main()
