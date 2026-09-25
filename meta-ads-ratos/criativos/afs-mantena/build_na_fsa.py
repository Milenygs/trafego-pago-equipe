#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AFS Mantena — build completo na conta da LOJA FSA (decisao da Mileny 25/08:
rodar tudo pela conta principal).

Conta       : act_1441561347702342 (CA - LOJA FSA)
Pagina / IG : os da loja de MANTENA (1332437986612101 / @acaifruitshowmantena)
Geo         : municipio de Mantena/MG (key 259174, raio 0)

  A) [INAUG] Reconhecimento | Mantena  R$550  30/08 -> 04/09  freq 3/dia
  B) [INAUG] Trafego Perfil | Mantena  R$450  hoje  -> 31/08  LEARN_MORE

Diferente do build na conta propria, aqui o start_time ja nasce certo: a
campanha A pode ser ativada junto com a B e a Meta so comeca a entregar em
30/08 sozinha (start_time nao e editavel depois — subcode 1815377).

Tudo criado PAUSED. Uso:
    python build_na_fsa.py --dry-run
    python build_na_fsa.py
"""
import argparse
import json
import os
import sys
import time
from datetime import datetime, timedelta

PASTA_CRIATIVOS = (
    r"C:\Users\MilenyGalvão\OneDrive\Área de Trabalho\CLAUDE CODE"
    r"\franquias\acai-fruit-show\loja mantena"
)

AQUI = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.abspath(os.path.join(AQUI, "..", ".."))
sys.path.insert(0, os.path.join(SKILL, "scripts"))

from lib import init_api  # noqa: E402
from facebook_business.api import FacebookAdsApi  # noqa: E402

# ---------------------------------------------------------------------------

CONTA = "act_1441561347702342"          # CA - LOJA FSA (Fraga Maia)
PAGINA = "1332437986612101"             # Acai fruit show Mantena
INSTAGRAM = "17841437791016896"         # @acaifruitshowmantena
IG_USER = "acaifruitshowmantena"
PERFIL_IG = f"http://instagram.com/{IG_USER}"

GEO_KEY_MANTENA = "259174"
ENDERECO = "Av. José Mol, 21 — Mantena/MG"

VERBA_RECONHECIMENTO = 55000            # R$550
VERBA_TRAFEGO = 45000                   # R$450

INICIO_RECONHECIMENTO = "2026-08-30T00:00:00-0300"
FIM_RECONHECIMENTO = "2026-09-04T23:59:00-0300"
FIM_TRAFEGO = "2026-08-31T23:59:00-0300"

POS_FEED = ["stream", "explore", "explore_home", "profile_feed"]
POS_STORIES = ["story", "reels"]
POS_TODOS = POS_FEED + POS_STORIES

DOF_SPEC = {
    "creative_features_spec": {
        chave: {"enroll_status": "OPT_OUT"}
        for chave in (
            "advantage_plus_creative", "enhance_cta", "text_optimizations",
            "video_auto_crop", "video_uncrop", "pac_relaxation",
        )
    }
}

CONCEITOS = [
    {
        "nome": "COPO SHOW",
        "feed": "COPO SHOW - MANTENA FEED.png",
        "stories": "COPO SHOW - MANTENA STORIES.png",
        "titulo": "100 Copos Show na inauguração",
        "legenda": (
            "100 COPOS SHOW para os primeiros clientes! 🥤💜\n\n"
            "É isso mesmo: na inauguração do Açaí Fruit Show Mantena, os "
            "primeiros clientes ganham um Copo Show.\n\n"
            "Dia 4 de setembro, a partir das 12h. Chega cedo — é por ordem "
            "de chegada!\n\n"
            f"📍 {ENDERECO}\n"
            "🗓️ 04/09, a partir das 12h"
        ),
    },
    {
        "nome": "TODO MUNDO VAI",
        "feed": "TODO MUNDO  VAI - MANTENA FEED.png",
        "stories": "TODO MUNDO  VAI - MANTENA - STORY.png",
        "titulo": "Compre 1 e ganhe outro na inauguração",
        "legenda": (
            "COMPRE 1 E GANHE OUTRO na mega inauguração! 💜🍨\n\n"
            "O Açaí Fruit Show Mantena abre dia 4 de setembro, a partir das "
            "12h — e no dia é compre 1, ganhe outro.\n\n"
            "Chama quem você quer levar e vem com a gente. Todo mundo vai!\n\n"
            f"📍 {ENDERECO}\n"
            "🗓️ 04/09, a partir das 12h\n\n"
            "*Promoção válida no dia da inauguração, conforme regulamento "
            "na loja."
        ),
    },
]

api = None
_cache_hash = {}


def chamar(metodo, caminho, params=None, files=None):
    try:
        return api.call(metodo, caminho, params=params or {}, files=files or {}).json()
    except Exception as exc:  # noqa: BLE001
        corpo = getattr(exc, "_body", None) or getattr(exc, "body", None)
        if isinstance(corpo, dict):
            err = corpo.get("error", corpo)
            msg = err.get("error_user_msg") or err.get("message")
            sub = err.get("error_subcode") or err.get("code")
            raise SystemExit(f"\nFALHOU em {'/'.join(caminho)} [{sub}]\n  {msg}\n")
        raise SystemExit(f"\nFALHOU em {'/'.join(caminho)}\n  {exc}\n")


def targeting():
    return {
        "geo_locations": {
            "cities": [{"key": GEO_KEY_MANTENA, "radius": 0,
                        "distance_unit": "kilometer"}],
            "location_types": ["home", "recent"],
        },
        "age_min": 18,
        "age_max": 65,
        "publisher_platforms": ["instagram"],
        "instagram_positions": POS_TODOS,
        "targeting_automation": {"advantage_audience": 0},
    }


def subir_imagem(nome_arquivo):
    if nome_arquivo in _cache_hash:
        return _cache_hash[nome_arquivo]
    caminho = os.path.join(PASTA_CRIATIVOS, nome_arquivo)
    if not os.path.exists(caminho):
        raise SystemExit(f"\nArquivo nao encontrado:\n  {caminho}\n")
    with open(caminho, "rb") as fh:
        res = chamar("POST", (CONTA, "adimages"), files={nome_arquivo: fh})
    h = list(res.get("images", {}).values())[0]["hash"]
    _cache_hash[nome_arquivo] = h
    print(f"    imagem subida : {h[:12]}...  {nome_arquivo}")
    return h


def criar_campanha(nome, objetivo):
    c = chamar("POST", (CONTA, "campaigns"), {
        "name": nome,
        "objective": objetivo,
        "status": "PAUSED",
        "special_ad_categories": json.dumps([]),
        "buying_type": "AUCTION",
        "is_adset_budget_sharing_enabled": "false",
    })
    print(f"  campanha : {c['id']}  {nome}")
    return c["id"]


def criar_conjunto(campanha_id, nome, extras):
    params = {
        "name": nome,
        "campaign_id": campanha_id,
        "billing_event": "IMPRESSIONS",
        # explicito, senao subcode 2490487
        "bid_strategy": "LOWEST_COST_WITHOUT_CAP",
        "status": "PAUSED",
        "targeting": json.dumps(targeting()),
    }
    params.update(extras)
    cj = chamar("POST", (CONTA, "adsets"), params)
    print(f"  conjunto : {cj['id']}  {nome}")
    return cj["id"]


def criar_ad(conceito, conjunto_id, cta, sufixo):
    h_feed = subir_imagem(conceito["feed"])
    h_story = subir_imagem(conceito["stories"])

    afs = {
        "images": [
            {"hash": h_feed, "adlabels": [{"name": "img_feed"}]},
            {"hash": h_story, "adlabels": [{"name": "img_story"}]},
        ],
        "bodies": [{"text": conceito["legenda"]}],
        "titles": [{"text": conceito["titulo"]}],
        "link_urls": [{"website_url": PERFIL_IG}],
        "ad_formats": ["SINGLE_IMAGE"],
        "asset_customization_rules": [
            {
                "customization_spec": {"publisher_platforms": ["instagram"],
                                       "instagram_positions": POS_FEED},
                "image_label": {"name": "img_feed"},
                "priority": 1,
            },
            {
                "customization_spec": {"publisher_platforms": ["instagram"],
                                       "instagram_positions": POS_STORIES},
                "image_label": {"name": "img_story"},
                "priority": 2,
            },
        ],
    }
    if cta:
        afs["call_to_action_types"] = [cta]

    criativo = chamar("POST", (CONTA, "adcreatives"), {
        "name": f"[INAUG] Mantena {conceito['nome']} | feed+stories | {sufixo}",
        "object_story_spec": json.dumps({"page_id": PAGINA,
                                         "instagram_user_id": INSTAGRAM}),
        "asset_feed_spec": json.dumps(afs),
        "degrees_of_freedom_spec": json.dumps(DOF_SPEC),
    })
    anuncio = chamar("POST", (CONTA, "ads"), {
        "name": f"[INAUG] Mantena {conceito['nome']}",
        "adset_id": conjunto_id,
        "creative": json.dumps({"creative_id": criativo["id"]}),
        "status": "PAUSED",
    })
    print(f"    anuncio : {anuncio['id']}  {conceito['nome']}")
    return anuncio["id"]


def main():
    global api
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    init_api()
    api = FacebookAdsApi.get_default_api()

    inicio_trafego = (datetime.now() + timedelta(minutes=15)).strftime(
        "%Y-%m-%dT%H:%M:%S-0300")

    plano = [
        {
            "rotulo": "A-reconhecimento",
            "campanha": "[INAUG] Reconhecimento | Mantena",
            "objetivo": "OUTCOME_AWARENESS",
            "conjunto": "Mantena Cidade | 18-65 | IG",
            "extras": {
                "optimization_goal": "REACH",
                "lifetime_budget": VERBA_RECONHECIMENTO,
                "start_time": INICIO_RECONHECIMENTO,
                "end_time": FIM_RECONHECIMENTO,
                # 3/dia: com ~19 mil pessoas, 2/dia nao deixa a verba escoar
                "frequency_control_specs": json.dumps(
                    [{"event": "IMPRESSIONS", "interval_days": 1,
                      "max_frequency": 3}]),
            },
            "cta": None,
        },
        {
            "rotulo": "B-trafego",
            "campanha": "[INAUG] Trafego Perfil | Mantena",
            "objetivo": "OUTCOME_TRAFFIC",
            "conjunto": "Mantena Cidade | 18-65 | IG",
            "extras": {
                "optimization_goal": "LINK_CLICKS",
                "destination_type": "WEBSITE",
                "lifetime_budget": VERBA_TRAFEGO,
                "start_time": inicio_trafego,
                "end_time": FIM_TRAFEGO,
            },
            "cta": "LEARN_MORE",
        },
    ]

    if args.dry_run:
        print(json.dumps(plano, ensure_ascii=False, indent=2))
        return

    criados = {}
    for item in plano:
        print(f"\n=== {item['rotulo']} ===")
        camp = criar_campanha(item["campanha"], item["objetivo"])
        cj = criar_conjunto(camp, item["conjunto"], item["extras"])
        ads = []
        for conceito in CONCEITOS:
            ads.append(criar_ad(conceito, cj, item["cta"], item["rotulo"]))
            time.sleep(1)
        criados[item["rotulo"]] = {"campanha": camp, "conjunto": cj, "ads": ads}

    print("\n=== IDS ===")
    print(json.dumps(criados, ensure_ascii=False, indent=2))
    print("\nTudo PAUSED na conta da FSA. Falta credito e ativar os 3 niveis.")


if __name__ == "__main__":
    main()
