#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Adiciona o criativo "4 - BASTIDORES" nas campanhas de publico QUENTE (CP-04)
e LAL (CP-05) da conta de franquia da Acai Fruit Show.

Pedido da Mileny (18/08/2026): subir o video novo nas duas campanhas com copy
personalizada por publico.

Video: 4 - BASTIDORES.mp4 (1080x1920, 29s) — reel de bastidores da industria.
Roteiro: "a maioria das lojas de acai que abrem hoje nao passa de 1 ano. Nao e
porque nao vende, vende e vende muito. Quebra por ponto e custo de manter o
negocio de pe. Separei um material com 5 pontos que mostram o que diferencia
quem quebra de quem lucra."
ATENCAO: o video termina com CTA organico ("comenta QUERO que eu te mando").
A copy redireciona pro botao Saiba mais / formulario.

Tudo criado PAUSED.

Uso:
    python build_bastidores.py --checar     # so valida, nao cria nada
    python build_bastidores.py              # cria criativos + anuncios
"""
import argparse
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.abspath(os.path.join(AQUI, "..", ".."))
sys.path.insert(0, os.path.join(SKILL, "scripts"))

from lib import init_api, print_json, safe_delay  # noqa: E402

from facebook_business.adobjects.adaccount import AdAccount  # noqa: E402
from facebook_business.adobjects.adset import AdSet  # noqa: E402

# ---------------------------------------------------------------------------
# Ativos da conta (contas.yaml + leitura dos criativos [FINAL] de 10/08)
# ---------------------------------------------------------------------------

CONTA = "act_835633356015496"
PAGINA = "635135693023206"
INSTAGRAM = "17841409335988444"

VIDEO_ID = "1714897866398632"          # upload de 18/08/2026
THUMB_HASH = None                       # usamos image_url da miniatura preferida
THUMB_URL = None                        # resolvido em runtime via /thumbnails

FORM_QUALIFICADO = "1800556261308285"   # o mesmo dos anuncios [FINAL] vivos na CP-10
LINK_PLACEHOLDER = "http://fb.me/"      # obrigatorio mesmo em lead ad puro

# Enhancements da Meta desligados (regra permanente da Mileny)
DOF = {
    "creative_features_spec": {
        "advantage_plus_creative": {"enroll_status": "OPT_OUT"},
        "enhance_cta": {"enroll_status": "OPT_OUT"},
        "text_optimizations": {"enroll_status": "OPT_OUT"},
        "video_auto_crop": {"enroll_status": "OPT_OUT"},
        "video_uncrop": {"enroll_status": "OPT_OUT"},
        "pac_relaxation": {"enroll_status": "OPT_OUT"},
    }
}

# ---------------------------------------------------------------------------
# Destinos + copy por publico
# ---------------------------------------------------------------------------

DESTINOS = [
    {
        "slug": "QUENTE",
        "adset": "120250573311500081",   # 00 - QUENTE - 180D [ESTATICOS] (CP-04)
        "ad_nome": "AD-F5 BASTIDORES 1 ANO [QUENTE]",
        "titulo": "A maioria não passa de 1 ano. Aqui essa parte já está resolvida.",
        "copy": (
            "Você já acompanha a marca. Então vale ouvir a parte que quase ninguém "
            "do setor fala.\n\n"
            "A maioria das lojas de açaí que abrem hoje não passa de 1 ano. E não é "
            "porque açaí não vende — vende, e vende muito. Quebra por ponto mal "
            "escolhido, margem apertada e custo de manter a operação de pé.\n\n"
            "Do nosso lado essa parte já está resolvida: indústria própria há 10 anos, "
            "34 unidades em 7 estados e ZERO royalties — o que a loja fatura fica com você. "
            "Suporte do ponto à inauguração.\n\n"
            "Investimento a partir de R$ 270 mil.\n\n"
            "Toca em Saiba mais, responde 3 perguntas e a gente te manda os 5 pontos "
            "que separam quem quebra de quem lucra."
        ),
    },
    {
        "slug": "LAL",
        "adset": "120247355994920081",   # REGIOES_EXPANSAO_LAL (CP-05)
        "ad_nome": "AD14 BASTIDORES 1 ANO [LAL]",
        "titulo": "O que separa quem quebra de quem lucra no açaí",
        "copy": (
            "Todo mundo olha uma loja de açaí cheia e acha que é dinheiro fácil.\n\n"
            "A verdade é que a maioria das que abrem não passa de 1 ano. Não é falta de "
            "venda — é ponto mal escolhido, margem que some e custo fixo que ninguém "
            "calcula antes de assinar.\n\n"
            "A Açaí Fruit Show tem indústria própria há 10 anos e 34 unidades em 7 estados. "
            "Você compra direto da fábrica, não paga royalties e tem suporte do ponto à "
            "inauguração.\n\n"
            "Investimento a partir de R$ 270 mil.\n\n"
            "Toca em Saiba mais e recebe os 5 pontos que separam quem quebra de quem lucra, "
            "junto com as informações da franquia."
        ),
    },
]


def thumb_preferida(api_token=None):
    """Miniatura preferida do video — video_data exige image_hash ou image_url."""
    from facebook_business.adobjects.advideo import AdVideo
    video = AdVideo(VIDEO_ID)
    thumbs = video.get_thumbnails(fields=["uri", "is_preferred"])
    for t in thumbs:
        if t.get("is_preferred"):
            return t["uri"]
    return thumbs[0]["uri"]


def limpar_ig_search(adset_id):
    """ig_search quebra anuncio de VIDEO em campanha de formulario (2446429).

    Regra registrada em aprendizados.md (17/08). O conjunto QUENTE da CP-04 foi
    montado so com estaticos e carrega o posicionamento; tirar antes de subir video.
    """
    adset = AdSet(adset_id)
    adset.api_get(fields=["targeting", "name"])
    targeting = adset["targeting"].export_all_data()
    pos = targeting.get("instagram_positions") or []
    if "ig_search" not in pos:
        print(f"  {adset_id}: sem ig_search, nada a fazer")
        return False
    targeting["instagram_positions"] = [p for p in pos if p != "ig_search"]
    targeting.pop("age_range", None)          # conflita com advantage_audience: 0
    targeting.pop("targeting_optimization", None)   # campo removido pela Meta
    adset.api_update(params={"targeting": targeting})
    print(f"  {adset_id}: ig_search removido -> {targeting['instagram_positions']}")
    safe_delay(1)
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--checar", action="store_true", help="so valida, nao cria")
    args = ap.parse_args()

    init_api()
    conta = AdAccount(CONTA)

    thumb = thumb_preferida()
    print(f"Miniatura preferida: {thumb[:80]}...")

    if args.checar:
        for d in DESTINOS:
            adset = AdSet(d["adset"])
            adset.api_get(fields=["name", "status", "optimization_goal",
                                  "destination_type", "campaign_id"])
            print(f"{d['slug']}: {adset['name']} | {adset.get('status')} | "
                  f"{adset.get('optimization_goal')} | {adset.get('destination_type')}")
        return

    print("\n== Posicionamentos ==")
    for d in DESTINOS:
        limpar_ig_search(d["adset"])

    print("\n== Criativos + anuncios ==")
    for d in DESTINOS:
        spec = {
            "page_id": PAGINA,
            "instagram_user_id": INSTAGRAM,
            "video_data": {
                "video_id": VIDEO_ID,
                "title": d["titulo"],
                "message": d["copy"],
                "image_url": thumb,
                "call_to_action": {
                    "type": "LEARN_MORE",
                    "value": {
                        "lead_gen_form_id": FORM_QUALIFICADO,
                        "link": LINK_PLACEHOLDER,
                    },
                },
            },
        }
        criativo = conta.create_ad_creative(params={
            "name": f"CR BASTIDORES 1 ANO [{d['slug']}] 2026-08-18",
            "object_story_spec": spec,
        })
        safe_delay(1)
        print(f"{d['slug']}: criativo {criativo['id']}")

        ad = conta.create_ad(params={
            "name": d["ad_nome"],
            "adset_id": d["adset"],
            "creative": {"creative_id": criativo["id"]},
            "status": "PAUSED",
            "degrees_of_freedom_spec": DOF,
        })
        safe_delay(1)
        print(f"{d['slug']}: anuncio {ad['id']} (PAUSED)")


if __name__ == "__main__":
    main()
