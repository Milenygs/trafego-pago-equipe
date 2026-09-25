#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sobe o criativo "4 - BASTIDORES" nas campanhas de CAPTACAO que estao ATIVAS
na conta de franquia da Acai Fruit Show (pedido da Mileny, 18/08/2026).

Campanhas ativas de captacao (formulario nativo, ON_AD + LEAD_GENERATION):
  CP-10 [PRACAS COM LOJA] — marca conhecida na praca  -> copy PRACA
  CP-09 [EXPANSAO]        — BA sem loja, marca chegando -> copy EXPANSAO
  CP-07 [FRIO] [PERSONAS] — FR01 quem ja tem negocio    -> copy OPERADOR

Fora daqui ficaram a CP-04 (QUENTE) e a CP-05 (LAL): as duas estao PAUSADAS.
A CP-12 (WEBNAR 18/08) tambem esta pausada e leva pro site, nao pro formulario.

Video: 1714897866398632 (4 - BASTIDORES.mp4, 1080x1920, 29s).
Formulario: 1800556261308285 (AFS FRANQUIA QUALIFICADO) — o mesmo dos
anuncios ativos das tres campanhas.

Os anuncios sao criados PAUSED e ativados no fim (--ativar, padrao ligado).
Nao mexe em verba nem em posicionamento: os conjuntos ja estao rodando.

Uso:
    python build_bastidores_captacao.py --checar
    python build_bastidores_captacao.py
"""
import argparse
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.abspath(os.path.join(AQUI, "..", ".."))
sys.path.insert(0, os.path.join(SKILL, "scripts"))

from lib import init_api, safe_delay  # noqa: E402

from facebook_business.adobjects.adaccount import AdAccount  # noqa: E402
from facebook_business.adobjects.adset import AdSet  # noqa: E402
from facebook_business.adobjects.ad import Ad  # noqa: E402
from facebook_business.adobjects.advideo import AdVideo  # noqa: E402

CONTA = "act_835633356015496"
PAGINA = "635135693023206"
INSTAGRAM = "17841409335988444"

VIDEO_ID = "1714897866398632"
FORM = "1800556261308285"
LINK_PLACEHOLDER = "http://fb.me/"

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
# Copy por camada. O gancho do video (a maioria nao passa de 1 ano) e o mesmo;
# muda a ponte pro publico e a prova que fecha.
# ---------------------------------------------------------------------------

COPY = {
    "PRACA": {
        "titulo": "A maioria não passa de 1 ano. Aqui essa parte já está resolvida.",
        "texto": (
            "Você já viu uma Açaí Fruit Show cheia na sua cidade. Então vale ouvir a "
            "parte que quase ninguém do setor fala.\n\n"
            "A maioria das lojas de açaí que abrem hoje não passa de 1 ano. E não é "
            "porque açaí não vende — vende, e vende muito. Quebra por ponto mal "
            "escolhido, margem apertada e custo de manter a operação de pé.\n\n"
            "Do nosso lado essa parte já está resolvida: indústria própria há 10 anos, "
            "34 unidades em 7 estados e ZERO royalties — o que a loja fatura fica com "
            "você. Suporte do ponto à inauguração.\n\n"
            "Investimento a partir de R$ 270 mil.\n\n"
            "Toca em Saiba mais, responde 3 perguntas e a gente te manda os 5 pontos "
            "que separam quem quebra de quem lucra."
        ),
    },
    "EXPANSAO": {
        "titulo": "O que separa quem quebra de quem lucra no açaí",
        "texto": (
            "Todo mundo olha uma loja de açaí cheia e acha que é dinheiro fácil.\n\n"
            "A verdade é que a maioria das que abrem não passa de 1 ano. Não é falta de "
            "venda — é ponto mal escolhido, margem que some e custo fixo que ninguém "
            "calcula antes de assinar.\n\n"
            "A Açaí Fruit Show tem indústria própria há 10 anos e 34 unidades em 7 "
            "estados, e agora está abrindo unidades na sua região. Você compra direto da "
            "fábrica, não paga royalties e tem suporte do ponto à inauguração.\n\n"
            "Investimento a partir de R$ 270 mil.\n\n"
            "Toca em Saiba mais e recebe os 5 pontos que separam quem quebra de quem "
            "lucra, junto com as informações da franquia."
        ),
    },
    "OPERADOR": {
        "titulo": "Você já sabe o que quebra um negócio. É disso que eu vim falar.",
        "texto": (
            "Quem já toca um negócio sabe: o problema quase nunca é a venda. É a margem, "
            "o ponto e o custo fixo que ninguém calcula antes de assinar o contrato.\n\n"
            "Por isso a maioria das lojas de açaí que abrem hoje não passa de 1 ano. E "
            "não é porque açaí não vende — vende, e vende muito.\n\n"
            "Na Açaí Fruit Show você compra direto da nossa indústria, que roda há 10 "
            "anos, opera sem pagar royalties e entra numa rede de 34 unidades em 7 "
            "estados, com suporte do ponto à inauguração.\n\n"
            "Investimento a partir de R$ 270 mil.\n\n"
            "Toca em Saiba mais, responde 3 perguntas e a gente te manda os 5 pontos "
            "que separam quem quebra de quem lucra."
        ),
    },
}

# adset_id, rotulo, chave de copy, nome do anuncio
DESTINOS = [
    ("120250617671110081", "CP-10 CJ1 [MG NUCLEO]",  "PRACA",    "AD-F5 BASTIDORES 1 ANO"),
    ("120250617671460081", "CP-10 CJ2 [BA Salvador]", "PRACA",   "AD-F5 BASTIDORES 1 ANO"),
    ("120250617671930081", "CP-10 CJ3 [SP]",          "PRACA",   "AD-F5 BASTIDORES 1 ANO"),
    ("120250617672780081", "CP-10 CJ4 [ES+MG]",       "PRACA",   "AD-F5 BASTIDORES 1 ANO"),
    ("120250579800090081", "CP-09 FR-BAEXP",          "EXPANSAO", "CV03 BASTIDORES 1 ANO"),
    ("120250573663400081", "CP-07 FR01 [OPERADOR]",   "OPERADOR", "AD-F5 BASTIDORES 1 ANO"),
]


def thumb_preferida():
    thumbs = AdVideo(VIDEO_ID).get_thumbnails(fields=["uri", "is_preferred"])
    for t in thumbs:
        if t.get("is_preferred"):
            return t["uri"]
    return thumbs[0]["uri"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--checar", action="store_true")
    ap.add_argument("--sem-ativar", action="store_true",
                    help="deixa os anuncios PAUSED em vez de ativar no fim")
    args = ap.parse_args()

    init_api()
    conta = AdAccount(CONTA)

    if args.checar:
        for adset_id, rot, chave, _ in DESTINOS:
            a = AdSet(adset_id)
            a.api_get(fields=["name", "effective_status", "optimization_goal",
                              "destination_type"])
            print(f"{rot:26s} | {a.get('effective_status'):16s} | "
                  f"{a.get('optimization_goal')} / {a.get('destination_type')} | copy={chave}")
        return

    thumb = thumb_preferida()

    # 1 criativo por copy, reaproveitado nos conjuntos da mesma camada
    # (mesmo creative_id preserva a prova social entre conjuntos)
    criativos = {}
    print("== Criativos ==")
    for chave, c in COPY.items():
        spec = {
            "page_id": PAGINA,
            "instagram_user_id": INSTAGRAM,
            "video_data": {
                "video_id": VIDEO_ID,
                "title": c["titulo"],
                "message": c["texto"],
                "image_url": thumb,
                "call_to_action": {
                    "type": "LEARN_MORE",
                    "value": {"lead_gen_form_id": FORM, "link": LINK_PLACEHOLDER},
                },
            },
        }
        cr = conta.create_ad_creative(params={
            "name": f"CR BASTIDORES 1 ANO [{chave}] 2026-08-18",
            "object_story_spec": spec,
        })
        criativos[chave] = cr["id"]
        safe_delay(1)
        print(f"  {chave}: {cr['id']}")

    print("\n== Anuncios ==")
    criados = []
    for adset_id, rot, chave, nome in DESTINOS:
        ad = conta.create_ad(params={
            "name": nome,
            "adset_id": adset_id,
            "creative": {"creative_id": criativos[chave]},
            "status": "PAUSED",
            "degrees_of_freedom_spec": DOF,
        })
        criados.append((ad["id"], rot))
        safe_delay(1)
        print(f"  {rot:26s} -> {ad['id']}")

    if args.sem_ativar:
        print("\n--sem-ativar: anuncios ficaram PAUSED")
        return

    print("\n== Ativando ==")
    for ad_id, rot in criados:
        for tentativa in range(3):
            try:
                Ad(ad_id).api_update(params={"status": "ACTIVE"})
                print(f"  {rot:26s} -> ACTIVE")
                break
            except Exception as e:   # erro transitorio da Meta (codigo 2)
                if tentativa == 2:
                    print(f"  {rot:26s} -> FALHOU: {e}")
                else:
                    print(f"  {rot:26s} -> retry em 20s ({e})")
                    safe_delay(20)
        safe_delay(1)


if __name__ == "__main__":
    main()
