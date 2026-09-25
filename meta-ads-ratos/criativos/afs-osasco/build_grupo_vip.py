#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AFS Osasco — campanha do GRUPO VIP no WhatsApp.

Conta   : act_1075513944839445 (C01 OSASCO)
Destino : grupo VIP no WhatsApp (link externo chat.whatsapp.com)
Periodo : hoje -> 12/09 (dia da inauguracao)
Verba   : R$1.040 vitalicio
Geo     : mesmo pino da loja, raio 8km
Criativo: "CONVITE GRUPO VIP OSASCO.mp4" + copy Variante A

Por que OUTCOME_TRAFFIC e nao OUTCOME_ENGAGEMENT: o destino e um LINK de grupo
(chat.whatsapp.com). O objetivo de engajamento com destination_type WHATSAPP faz
click-to-WhatsApp, que abre conversa com o numero comercial e NAO entra em grupo.
Para levar ao grupo o caminho e trafego otimizado por LINK_CLICKS.

Uso:
    python build_grupo_vip.py --dry-run
    python build_grupo_vip.py            # cria PAUSED
    python build_grupo_vip.py --ativar   # cria e ja ativa os 3 niveis
"""
import argparse
import json
import os
import sys
import time
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

PASTA = (r"C:\Users\MilenyGalvão\OneDrive\Área de Trabalho\CLAUDE CODE"
         r"\franquias\acai-fruit-show\acai fruit show osasco")
VIDEO = "CONVITE GRUPO VIP OSASCO.mp4"

LINK_GRUPO = "https://chat.whatsapp.com/HJrllSS3mhP70TzZT9lVVe"

LAT, LNG, RAIO_KM = -23.5601509, -46.7995541, 8

VERBA = 104000                                   # R$1.040 em centavos
FIM = "2026-09-12T23:59:00-0300"                 # dia da inauguracao

POS_TODOS = ["stream", "story", "reels", "explore", "explore_home",
             "profile_feed", "ig_search"]

TITULO = "Entra no grupo VIP da inauguração"
DESCRICAO = "Dia 12, no Santo Antônio."
COPY = (
    "Osasco, tá chegando o dia. 💜\n\n"
    "Dia 12 o Açaí Fruit Show abre as portas aqui no Santo Antônio — e quem "
    "tá no grupo VIP fica sabendo de tudo primeiro.\n\n"
    "É lá que a gente avisa o horário de abertura, solta os detalhes do "
    "compre 1 e ganhe outro e conta o que vai rolar no dia.\n\n"
    "📍 R. São Nicolau, 27 — Santo Antônio, Osasco\n\n"
    "Entra antes de encher. 👇"
)

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


def chamar(metodo, caminho, params=None, files=None):
    try:
        return api.call(metodo, caminho, params=params or {},
                        files=files or {}).json()
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
    return {
        "geo_locations": {
            "custom_locations": [{
                "latitude": LAT, "longitude": LNG,
                "radius": RAIO_KM, "distance_unit": "kilometer",
            }],
            # sem location_types: `recent` descontinuado em 10/09/2026 (aprendizados 11/09)
        },
        "age_min": 18,
        "age_max": 65,
        "publisher_platforms": ["instagram"],
        "instagram_positions": POS_TODOS,
        "targeting_automation": {"advantage_audience": 0},
    }


def subir_video():
    caminho = os.path.join(PASTA, VIDEO)
    if not os.path.exists(caminho):
        raise SystemExit("\nVideo nao encontrado:\n  %s\n" % caminho)
    tam = os.path.getsize(caminho) / 1024 / 1024
    print("  subindo video (%.1f MB)..." % tam)
    with open(caminho, "rb") as fh:
        res = chamar("POST", (CONTA, "advideos"), files={VIDEO: fh})
    vid = res["id"]
    print("  video    : %s" % vid)
    return vid


def esperar_video(vid, limite=40):
    """Video recem-subido fica em processing; criativo falha se subir antes."""
    for tentativa in range(limite):
        res = chamar("GET", (vid,), {"fields": "status"})
        estado = (res.get("status") or {}).get("video_status")
        if estado == "ready":
            print("  video pronto")
            return True
        if estado == "error":
            raise SystemExit("  video falhou no processamento: %s" % res)
        print("    ... %s (%d/%d)" % (estado, tentativa + 1, limite))
        time.sleep(15)
    print("  AVISO: video ainda processando — criativo pode sair sem thumb")
    return False


def thumb_do_video(vid):
    res = chamar("GET", (vid, "thumbnails"), {"fields": "uri,is_preferred"})
    imgs = res.get("data") or []
    if not imgs:
        return None
    preferida = next((i for i in imgs if i.get("is_preferred")), imgs[0])
    return preferida.get("uri")


def build(ativar):
    inicio = (datetime.now() + timedelta(minutes=20)).strftime(
        "%Y-%m-%dT%H:%M:%S-0300")
    estado = "ACTIVE" if ativar else "PAUSED"

    vid = subir_video()
    esperar_video(vid)
    thumb = thumb_do_video(vid)
    print("  thumb    : %s" % (thumb[:70] + "..." if thumb else "nenhuma"))

    camp = chamar("POST", (CONTA, "campaigns"), {
        "name": "[INAUG] Grupo VIP WhatsApp | Osasco",
        "objective": "OUTCOME_TRAFFIC",
        "status": estado,
        "special_ad_categories": json.dumps([]),
        "buying_type": "AUCTION",
        "is_adset_budget_sharing_enabled": "false",
    })
    print("  campanha : %s" % camp["id"])

    conj = chamar("POST", (CONTA, "adsets"), {
        "name": "Pino 8km | 18-65 | aberto | IG",
        "campaign_id": camp["id"],
        "billing_event": "IMPRESSIONS",
        "optimization_goal": "LINK_CLICKS",
        "destination_type": "WEBSITE",
        "bid_strategy": "LOWEST_COST_WITHOUT_CAP",
        "lifetime_budget": VERBA,
        "start_time": inicio,
        "end_time": FIM,
        "status": estado,
        "targeting": json.dumps(targeting()),
    })
    print("  conjunto : %s" % conj["id"])

    video_data = {
        "video_id": vid,
        "message": COPY,
        "title": TITULO,
        "link_description": DESCRICAO,
        "call_to_action": {"type": "LEARN_MORE",
                           "value": {"link": LINK_GRUPO}},
    }
    if thumb:
        video_data["image_url"] = thumb

    criativo = chamar("POST", (CONTA, "adcreatives"), {
        "name": "[INAUG] Osasco | CONVITE GRUPO VIP | video",
        "object_story_spec": json.dumps({
            "page_id": PAGINA,
            "instagram_user_id": INSTAGRAM,
            "video_data": video_data,
        }),
        "degrees_of_freedom_spec": json.dumps(DOF_SPEC),
    })
    print("  criativo : %s" % criativo["id"])

    anuncio = chamar("POST", (CONTA, "ads"), {
        "name": "[INAUG] Osasco | CONVITE GRUPO VIP",
        "adset_id": conj["id"],
        "creative": json.dumps({"creative_id": criativo["id"]}),
        "status": estado,
    })
    print("  anuncio  : %s" % anuncio["id"])

    return {"campanha": camp["id"], "conjunto": conj["id"],
            "video": vid, "criativo": criativo["id"], "anuncio": anuncio["id"]}


def main():
    global api
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--ativar", action="store_true")
    args = ap.parse_args()

    init_api()
    api = FacebookAdsApi.get_default_api()

    if args.dry_run:
        print(json.dumps({
            "conta": CONTA, "link": LINK_GRUPO, "verba": VERBA, "fim": FIM,
            "video": os.path.join(PASTA, VIDEO),
            "existe": os.path.exists(os.path.join(PASTA, VIDEO)),
            "targeting": targeting(), "copy": COPY, "titulo": TITULO,
        }, ensure_ascii=False, indent=2))
        return

    print("\n=== C) Grupo VIP WhatsApp ===")
    ids = build(args.ativar)
    print("\n=== IDS ===")
    print(json.dumps(ids, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
