#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build da campanha de PERFIL das lojas fisicas — conta MKT - CHEIRINBAO.

Pedido da Mileny (14/08/2026):
  - pinos nos enderecos das lojas fisicas, raio de 5km cada
  - pracas: Guarulhos, Ribeirao Preto, Centro do Rio, Campo Grande (RJ),
    Barra da Tijuca, Niteroi + ABC paulista
  - idade 30-55, todos os generos
  - criativos = as postagens de hoje do Instagram, R$100/dia cada

Estrutura: 1 campanha, 1 conjunto POR POST (ABO, R$100/dia cada), mesmo
targeting em todos. Tudo criado PAUSED.

PRE-REQUISITO: o system user precisa de acesso a conta act_1398047248415230.
Hoje a API responde (#200) "Ad account owner has NOT grant ads_management or
ads_read permission" — o script para na checagem inicial sem criar nada.

Uso:
    python build_lojas.py --checar          # so verifica pre-requisitos
    python build_lojas.py --posts 3         # so os N posts mais recentes
    python build_lojas.py                   # build completo
"""
import argparse
import json
import os
import sys
import time

AQUI = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.abspath(os.path.join(AQUI, "..", ".."))
sys.path.insert(0, os.path.join(SKILL, "scripts"))

from lib import init_api  # noqa: E402

# ---------------------------------------------------------------------------
# Conta e ativos
# ---------------------------------------------------------------------------

CONTA = "act_1398047248415230"        # MKT - CHEIRINBAO (passada pela Mileny)
PAGINA = "639778989482866"            # Cheirin Bao — CONFIRMAR na conta MKT
INSTAGRAM = "17841400169946431"       # perfil do Emporio Mineiro Cheirin Bao
PERFIL_IG = "http://instagram.com/cheirinbao"

VERBA_POR_POST = 10000                # centavos = R$100/dia por post
RAIO_KM = 5
IDADE_MIN, IDADE_MAX = 30, 55

# ---------------------------------------------------------------------------
# Pinos — todas as lojas de cada praca (escolha da Mileny: pinar todas).
# Levantados na web em 14/08/2026 — CONFERIR contra a lista oficial de unidades
# antes de ativar. Cada endereco vira um pino de 5km; pinos vizinhos se somam,
# nao duplicam entrega.
# ---------------------------------------------------------------------------

LOJAS = [
    # --- Guarulhos / SP
    "Rua Gabriel Machado, 180, Centro, Guarulhos, SP, Brazil",
    "Avenida Paulo Faccini, 1539, Bosque Maia, Guarulhos, SP, Brazil",
    "Avenida Sao Bento, 1485, Vila Galvao, Guarulhos, SP, Brazil",
    "Rodovia Presidente Dutra, Vila Itapegica, Guarulhos, SP, Brazil",
    "Rua Jaguarema, 26, Parque Jurema, Guarulhos, SP, Brazil",
    # --- Ribeirao Preto / SP
    "Rua Doutor Isaac Teodoro de Lima, 715, Jardim Iraja, Ribeirao Preto, SP, Brazil",
    "Avenida Coronel Fernando Ferreira Leite, 1540, Ribeirao Preto, SP, Brazil",
    "Rua Senador Cesar Vergueiro, 480, Jardim Sao Luiz, Ribeirao Preto, SP, Brazil",
    # --- Centro do Rio / RJ
    "Avenida Rio Branco, 177, Centro, Rio de Janeiro, RJ, Brazil",
    "Avenida Rio Branco, 25, Centro, Rio de Janeiro, RJ, Brazil",
    # --- Campo Grande / RJ
    "Rua Augusto de Vasconcelos, 331, Campo Grande, Rio de Janeiro, RJ, Brazil",
    "Avenida Maria Teresa, 260, Campo Grande, Rio de Janeiro, RJ, Brazil",
    "Estrada do Lameirao Pequeno, 345, Campo Grande, Rio de Janeiro, RJ, Brazil",
    # --- Barra da Tijuca / RJ
    "Avenida Embaixador Abelardo Bueno, 3500, Barra da Tijuca, Rio de Janeiro, RJ, Brazil",
    "Avenida Olegario Maciel, 519, Barra da Tijuca, Rio de Janeiro, RJ, Brazil",
    "Avenida Marechal Henrique Lott, 120, Barra da Tijuca, Rio de Janeiro, RJ, Brazil",
    "Avenida das Americas, 4666, Barra da Tijuca, Rio de Janeiro, RJ, Brazil",
    # --- Niteroi / RJ
    "Rua Presidente Backer, 155, Icarai, Niteroi, RJ, Brazil",
    "Avenida Rui Barbosa, 153, Sao Francisco, Niteroi, RJ, Brazil",
    "Avenida Visconde de Sepetiba, 935, Centro, Niteroi, RJ, Brazil",
    "Avenida Central Ewerton Xavier, 2346, Itaipu, Niteroi, RJ, Brazil",
    # --- ABC paulista
    "Rua Doutor Cesario Mota, 134, Centro, Santo Andre, SP, Brazil",
    "Rua das Goiabeiras, 264, Jardim, Santo Andre, SP, Brazil",
    "Rua Jurubatuba, 1350, Centro, Sao Bernardo do Campo, SP, Brazil",
]

# ---------------------------------------------------------------------------
# Posts do Instagram de 14/08/2026 (mais recente primeiro).
# Puxados com: read.py instagram-posts --ig-id 17841400169946431
# ---------------------------------------------------------------------------

POSTS = [
    ("18069784670440956", "Waffle do Chef"),
    ("17956029962997400", "Cafe ta gelado"),
    ("18044058617814400", "R$1.500 pra comer"),
    ("18188166679400490", "Lugar gostoso"),
    ("18070685018481104", "Bolo de Chocolate"),
    ("18079710131438320", "Resolver umas coisas em Minas"),
    ("18160040422487184", "Cheesecakes novos"),
    ("17902081104515509", "Cafe especial"),
    ("17951545251239135", "Affogato"),
    ("17894530779657369", "Quem era voce na infancia"),
    ("18140444902566163", "A gente ate pode falar"),
    ("18156863857487613", "Um cafezin, uma pausa"),
]

# Posicionamentos — so Instagram (preferencia permanente da Mileny).
# explore_home exige "explore" junto, senao a API rejeita (subcode 2490392).
POS_INSTAGRAM = ["stream", "explore", "explore_home", "profile_feed",
                 "story", "reels"]

# Enhancements automaticos desligados — regra permanente: anuncio limpo.
DOF_SPEC = {
    "creative_features_spec": {
        chave: {"enroll_status": "OPT_OUT"}
        for chave in (
            "advantage_plus_creative", "enhance_cta", "text_optimizations",
            "video_auto_crop", "video_uncrop", "pac_relaxation",
        )
    }
}


def targeting():
    return {
        "age_min": IDADE_MIN,
        "age_max": IDADE_MAX,
        # sem "genders" = homens e mulheres
        "geo_locations": {
            "custom_locations": [
                {
                    "address_string": endereco,
                    "radius": RAIO_KM,
                    "distance_unit": "kilometer",
                }
                for endereco in LOJAS
            ],
            # sem location_types: `recent` descontinuado em 10/09/2026 (aprendizados 11/09)
        },
        "publisher_platforms": ["instagram"],
        "instagram_positions": POS_INSTAGRAM,
        "device_platforms": ["mobile", "desktop"],
        "targeting_automation": {
            "advantage_audience": 0,
            "individual_setting": {"age": 0, "gender": 0},
        },
    }


# ---------------------------------------------------------------------------

init_api()
from facebook_business.api import FacebookAdsApi  # noqa: E402

api = FacebookAdsApi.get_default_api()


def chamar(metodo, caminho, params=None):
    """Chamada Graph com erro legivel (error_user_msg, nao so o subcode)."""
    try:
        return api.call(metodo, caminho, params=params or {}).json()
    except Exception as exc:  # noqa: BLE001
        corpo = getattr(exc, "_body", None) or getattr(exc, "body", None)
        if isinstance(corpo, dict):
            err = corpo.get("error", corpo)
            msg = err.get("error_user_msg") or err.get("message")
            sub = err.get("error_subcode") or err.get("code")
            raise SystemExit(f"\nFALHOU em {'/'.join(caminho)} [{sub}]\n  {msg}\n")
        raise SystemExit(f"\nFALHOU em {'/'.join(caminho)}\n  {exc}\n")


def checar_prerequisitos():
    print("Checando pre-requisitos...\n")

    conta = chamar("GET", (CONTA,), {
        "fields": "name,account_status,disable_reason,balance,is_prepay_account",
    })
    status = conta.get("account_status")
    print(f"  conta    : {conta.get('name')} — status {status}")
    if status != 1:
        raise SystemExit(
            f"\nBLOQUEADO: conta com account_status {status} "
            f"(disable_reason {conta.get('disable_reason')}).\n"
        )

    paginas = chamar("GET", ("me", "accounts"), {"fields": "id", "limit": 200})
    if PAGINA not in {p["id"] for p in paginas.get("data", [])}:
        raise SystemExit(
            f"\nBLOQUEADO: pagina {PAGINA} fora do /me/accounts do system user.\n"
            "Sem acesso de Anunciante na pagina o criativo falha "
            "(erro 10 / subcode 3858749).\n"
        )
    print(f"  pagina   : {PAGINA} OK")
    print(f"  pinos    : {len(LOJAS)} lojas x {RAIO_KM}km")
    print(f"  posts    : {len(POSTS)} do Instagram\n")


def criar_campanha():
    nome = "[MKT] Perfil | Lojas 5km | 30-55"
    c = chamar("POST", (CONTA, "campaigns"), {
        "name": nome,
        "objective": "OUTCOME_TRAFFIC",
        "status": "PAUSED",
        "special_ad_categories": json.dumps([]),
        "buying_type": "AUCTION",
        # ABO exige este campo explicito (subcode 4834011)
        "is_adset_budget_sharing_enabled": "false",
    })
    print(f"  campanha : {c['id']}  {nome}")
    return c["id"]


def criar_conjunto(campanha_id, rotulo, perfil):
    """Um conjunto por post, R$100/dia.

    perfil=True tenta Visita ao Perfil (o que a Mileny pediu). Se a conta nao
    for elegivel, o build cai pra LINK_CLICKS com link do perfil — mesmo
    destino, e o que ja foi usado no Tomba (subcode 2016153).
    """
    params = {
        "name": f"{rotulo} | lojas 5km | 30-55",
        "campaign_id": campanha_id,
        "status": "PAUSED",
        "billing_event": "IMPRESSIONS",
        "bid_strategy": "LOWEST_COST_WITHOUT_CAP",
        "daily_budget": VERBA_POR_POST,
        "targeting": json.dumps(targeting()),
    }
    if perfil:
        params["optimization_goal"] = "VISIT_INSTAGRAM_PROFILE"
        params["destination_type"] = "INSTAGRAM_PROFILE"
        params["promoted_object"] = json.dumps(
            {"instagram_profile_id": INSTAGRAM})
    else:
        params["optimization_goal"] = "LINK_CLICKS"

    cj = chamar("POST", (CONTA, "adsets"), params)
    print(f"  conjunto : {cj['id']}  {rotulo}")
    return cj["id"]


def criar_ad(post_id, rotulo, conjunto_id):
    """Anuncio a partir do post organico do Instagram (dark post nao — e o
    proprio post, entao curtidas e comentarios somam no organico)."""
    criativo = chamar("POST", (CONTA, "adcreatives"), {
        "name": f"[MKT] {rotulo}",
        "source_instagram_media_id": post_id,
        "instagram_user_id": INSTAGRAM,
        "object_story_spec": json.dumps({"page_id": PAGINA,
                                         "instagram_user_id": INSTAGRAM}),
        "degrees_of_freedom_spec": json.dumps(DOF_SPEC),
    })
    anuncio = chamar("POST", (CONTA, "ads"), {
        "name": f"[MKT] {rotulo}",
        "adset_id": conjunto_id,
        "creative": json.dumps({"creative_id": criativo["id"]}),
        "status": "PAUSED",
    })
    print(f"    anuncio: {anuncio['id']} (criativo {criativo['id']})")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--checar", action="store_true",
                    help="so verifica pre-requisitos, nao cria nada")
    ap.add_argument("--posts", type=int,
                    help="usar so os N posts mais recentes (default: todos)")
    ap.add_argument("--sem-perfil", action="store_true",
                    help="ja cria como LINK_CLICKS, sem tentar Visita ao Perfil")
    args = ap.parse_args()

    checar_prerequisitos()
    if args.checar:
        print("Pre-requisitos OK — pronto pra rodar o build.")
        return

    posts = POSTS[:args.posts] if args.posts else POSTS
    total = len(posts) * VERBA_POR_POST / 100
    print(f"=== {len(posts)} posts x R$ {VERBA_POR_POST / 100:.0f}/dia "
          f"= R$ {total:.0f}/dia ===\n")

    campanha_id = criar_campanha()
    for post_id, rotulo in posts:
        conjunto_id = criar_conjunto(campanha_id, rotulo,
                                     perfil=not args.sem_perfil)
        criar_ad(post_id, rotulo, conjunto_id)
        time.sleep(1)

    print("\nTudo criado PAUSED. Antes de ativar:")
    print("  1. conferir preview: read.py preview --creative <id> --format all")
    print("  2. conferir o alcance dos pinos no mapa do Ads Manager")
    print("  3. ativar os 3 niveis: campanha -> conjuntos -> anuncios")
    print(f"\nCampanha: {campanha_id}")


if __name__ == "__main__":
    main()
