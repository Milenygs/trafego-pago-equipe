#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AFS Loja Mantena (MG) — anuncios da inauguracao.

Roda DEPOIS do build_inauguracao.py, que ja criou as 2 campanhas e os 2
conjuntos. Aqui sobem as imagens e sao criados os anuncios, todos PAUSED.

Inauguracao: 04/09/2026 a partir das 12h — Av. Jose Mol, 21, Mantena/MG.

  A) [INAUG] Reconhecimento | Mantena  — 2 anuncios SEM CTA
  B) [INAUG] Trafego Perfil | Mantena  — 2 anuncios com LEARN_MORE -> perfil

Cada anuncio serve o 4:5 no feed e o 9:16 em stories/reels, via
asset_customization_rules (mesmo padrao validado no build do Tomba).

Uso:
    python build_anuncios.py             # cria os 4 anuncios
    python build_anuncios.py --so A      # so a campanha de reconhecimento
    python build_anuncios.py --so B      # so a de trafego pro perfil
    python build_anuncios.py --sem-custom # plano B: 1 anuncio por formato
"""
import argparse
import json
import os
import sys
import time

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
# Conta, ativos e objetos ja criados
# ---------------------------------------------------------------------------

CONTA = "act_1984385632259800"          # CA01 MANTENA
PAGINA = "1332437986612101"             # Acai fruit show Mantena
INSTAGRAM = "17841437791016896"         # @acaifruitshowmantena
IG_USER = "acaifruitshowmantena"
PERFIL_IG = f"http://instagram.com/{IG_USER}"

CONJUNTOS = {
    "A": "120253323739610422",          # reconhecimento (REACH)
    "B": "120253323740090422",          # trafego perfil (LINK_CLICKS)
}

ENDERECO = "Av. José Mol, 21 — Mantena/MG"

# ---------------------------------------------------------------------------
# Os 2 conceitos entregues pela Mileny
# ---------------------------------------------------------------------------

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

# ---------------------------------------------------------------------------
# Posicionamentos — so Instagram (preferencia permanente da Mileny)
# ---------------------------------------------------------------------------

POS_FEED = ["stream", "explore", "explore_home", "profile_feed"]
POS_STORIES = ["story", "reels"]

# Enhancements automaticos desligados — regra permanente: anuncio sempre limpo.
DOF_SPEC = {
    "creative_features_spec": {
        chave: {"enroll_status": "OPT_OUT"}
        for chave in (
            "advantage_plus_creative", "enhance_cta", "text_optimizations",
            "video_auto_crop", "video_uncrop", "pac_relaxation",
        )
    }
}

# CTA so na campanha B. Nao usar VIEW_INSTAGRAM_PROFILE: o objetivo de
# reconhecimento recusa esse tipo (1885396) e perfil novo cai no 2016153.
CTA_TRAFEGO = "LEARN_MORE"

api = None
_cache_hash = {}


def chamar(metodo, caminho, params=None, files=None):
    """Chamada Graph com erro legivel (error_user_msg, nao so o subcode)."""
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


def subir_imagem(nome_arquivo):
    """Sobe a imagem e devolve o hash (cacheado por arquivo)."""
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


def criar_ad_customizado(conceito, conjunto_id, cta, sufixo):
    """1 anuncio que serve o 4:5 no feed e o 9:16 em stories/reels."""
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
                "customization_spec": {
                    "publisher_platforms": ["instagram"],
                    "instagram_positions": POS_FEED,
                },
                "image_label": {"name": "img_feed"},
                "priority": 1,
            },
            {
                "customization_spec": {
                    "publisher_platforms": ["instagram"],
                    "instagram_positions": POS_STORIES,
                },
                "image_label": {"name": "img_story"},
                "priority": 2,
            },
        ],
    }
    if cta:
        afs["call_to_action_types"] = [cta]

    criativo = chamar("POST", (CONTA, "adcreatives"), {
        "name": f"[INAUG] {conceito['nome']} | feed+stories | {sufixo}",
        "object_story_spec": json.dumps({
            "page_id": PAGINA,
            "instagram_user_id": INSTAGRAM,
        }),
        "asset_feed_spec": json.dumps(afs),
        "degrees_of_freedom_spec": json.dumps(DOF_SPEC),
    })
    anuncio = chamar("POST", (CONTA, "ads"), {
        "name": f"[INAUG] {conceito['nome']}",
        "adset_id": conjunto_id,
        "creative": json.dumps({"creative_id": criativo["id"]}),
        "status": "PAUSED",
    })
    print(f"    anuncio : {anuncio['id']}  {conceito['nome']} "
          f"(criativo {criativo['id']})")


def criar_ad_simples(conceito, conjunto_id, formato, cta, sufixo):
    """Plano B: 1 anuncio por formato, sem placement customization."""
    h = subir_imagem(conceito[formato])

    # photo_data puro nao roda no Instagram (subcode 2446383) — usar link_data.
    link_data = {
        "image_hash": h,
        "link": PERFIL_IG,
        "message": conceito["legenda"],
        "name": conceito["titulo"],
    }
    if cta:
        link_data["call_to_action"] = {"type": cta, "value": {"link": PERFIL_IG}}

    criativo = chamar("POST", (CONTA, "adcreatives"), {
        "name": f"[INAUG] {conceito['nome']} | {formato} | {sufixo}",
        "object_story_spec": json.dumps({
            "page_id": PAGINA,
            "instagram_user_id": INSTAGRAM,
            "link_data": link_data,
        }),
        "degrees_of_freedom_spec": json.dumps(DOF_SPEC),
    })
    anuncio = chamar("POST", (CONTA, "ads"), {
        "name": f"[INAUG] {conceito['nome']} | {formato}",
        "adset_id": conjunto_id,
        "creative": json.dumps({"creative_id": criativo["id"]}),
        "status": "PAUSED",
    })
    print(f"    anuncio : {anuncio['id']}  {conceito['nome']} [{formato}]")


def montar(rotulo, conjunto_id, cta, sem_custom):
    print(f"\n=== {rotulo} ===")
    for conceito in CONCEITOS:
        if sem_custom:
            for formato in ("feed", "stories"):
                criar_ad_simples(conceito, conjunto_id, formato, cta, rotulo)
                time.sleep(1)
        else:
            criar_ad_customizado(conceito, conjunto_id, cta, rotulo)
            time.sleep(1)


def main():
    global api
    ap = argparse.ArgumentParser()
    ap.add_argument("--so", choices=["A", "B"], help="so uma das campanhas")
    ap.add_argument("--sem-custom", action="store_true",
                    help="1 anuncio por formato, sem placement customization")
    args = ap.parse_args()

    init_api()
    api = FacebookAdsApi.get_default_api()

    if args.so in (None, "A"):
        montar("A-reconhecimento", CONJUNTOS["A"], None, args.sem_custom)
    if args.so in (None, "B"):
        montar("B-trafego", CONJUNTOS["B"], CTA_TRAFEGO, args.sem_custom)

    print("\nTudo PAUSED. Falta credito na conta e ativar os 3 niveis.")


if __name__ == "__main__":
    main()
