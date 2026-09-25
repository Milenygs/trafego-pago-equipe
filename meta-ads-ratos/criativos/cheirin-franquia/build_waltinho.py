#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cheirin Bao franquia (act_884652616778712) — sobe o criativo "waltinho"
(degustacao no escritorio) nos dois conjuntos que a Mileny pediu:

  01 - Leads Quente + Geo   120256940806870212
  04 - LAL —FRANQUEADOS     120256940815900212

Copy diferente por conjunto (nivel de consciencia do Funil Espiral):
o quente ja conhece o modelo e precisa de proximo passo; o LAL precisa
da prova de que o produto se explica sozinho antes do convite.

Padroes copiados do ad modelo "1 milhao varias unidades" (120257337770450212):
  - ad set LEAD_GENERATION + destination_type ON_AD (formulario nativo)
  - CTA LEARN_MORE com lead_gen_form_id + link (obrigatorio mesmo em ON_AD)
  - Instagram-only, enhancements da Meta todos OPT_OUT

Uso:
    python build_waltinho.py --video-id 123   # reaproveita video ja subido
    python build_waltinho.py                  # sobe o video e cria tudo
    python build_waltinho.py --ativar         # cria e ja ativa os 2 anuncios
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
from facebook_business.adobjects.adaccount import AdAccount  # noqa: E402
from facebook_business.adobjects.advideo import AdVideo  # noqa: E402
from facebook_business.adobjects.adimage import AdImage  # noqa: E402
from facebook_business.adobjects.ad import Ad  # noqa: E402
from facebook_business.adobjects.adset import AdSet  # noqa: E402

# ---------------------------------------------------------------------------
# Ativos da conta
# ---------------------------------------------------------------------------

CONTA = "act_884652616778712"
PAGINA = "639778989482866"
INSTAGRAM = "17841400169946431"
FORM = "3282443085242041"                  # formulario nativo em uso na campanha
LINK = "https://bl.cheirinbao.com.br/"     # mesmo link do ad modelo (destino real = form)

VIDEO = os.path.join(
    os.path.expanduser("~"),
    "OneDrive", "Área de Trabalho", "CLAUDE CODE", "franquias",
    "cheirin-bao", "criativos", "waltinho vídeo para trafego.mp4",
)

TITULO = "Franquia Cheirin Bão"

COPY_QUENTE = (
    "A gente levou o café passado na hora e o hot dog mineiro pra dentro de "
    "um escritório. Ninguém ali era cliente da marca.\n\n"
    "Bastou a primeira mordida: \"É bom, hein? É bom.\"\n\n"
    "Essa reação é o que sustenta o faturamento de uma loja Cheirin Bão. "
    "Produto que dispensa apresentação, consumo que se repete de manhã e de "
    "tarde, e mais de 1.000 unidades no Brasil provando que funciona longe "
    "de Minas também.\n\n"
    "Você já entendeu o modelo. O que decide agora é a praça — e as melhores "
    "saem primeiro.\n\n"
    "👇 Clique, responda em 1 minuto e fale hoje com um consultor."
)

COPY_LAL = (
    "Isso aqui não é propaganda. É a cara de quem provou Cheirin Bão pela "
    "primeira vez.\n\n"
    "Café passado na hora, pão de queijo e hot dog mineiro entregues num "
    "escritório comum. A sala inteira parou o que estava fazendo.\n\n"
    "Enquanto a maioria das franquias precisa explicar o produto pro cliente, "
    "a nossa é entendida na primeira mordida. São mais de 1.000 unidades no "
    "Brasil e novas inaugurações todo mês.\n\n"
    "Se você procura um negócio com marca pronta, produto validado e operação "
    "simples de tocar, vale 1 minuto do seu tempo.\n\n"
    "👇 Clique e receba os números da franquia."
)

ALVOS = [
    {
        "adset": "120256940806870212",
        "nome_ad": "Quente - waltinho-degustacao-escritorio",
        "nome_creative": "waltinho-degustacao [QUENTE]",
        "copy": COPY_QUENTE,
    },
    {
        "adset": "120256940815900212",
        "nome_ad": "LAL - waltinho-degustacao-escritorio",
        "nome_creative": "waltinho-degustacao [LAL]",
        "copy": COPY_LAL,
    },
]

# Enhancements automaticos desligados — regra permanente da Mileny.
DOF_SPEC = {
    "creative_features_spec": {
        chave: {"enroll_status": "OPT_OUT"}
        for chave in (
            "advantage_plus_creative", "enhance_cta", "text_optimizations",
            "video_auto_crop", "video_uncrop", "pac_relaxation",
        )
    }
}


def subir_video(caminho):
    print(f"→ subindo {os.path.basename(caminho)} "
          f"({os.path.getsize(caminho) / 1e6:.1f} MB)...")
    video = AdVideo(parent_id=CONTA)
    video[AdVideo.Field.filepath] = caminho
    video[AdVideo.Field.name] = "waltinho degustacao escritorio"
    video.remote_create()
    vid = video["id"]
    print(f"  video_id = {vid}")
    return vid


def esperar_thumbnail(video_id, tentativas=30, espera=10):
    """A miniatura so existe depois que a Meta termina de processar o video."""
    for i in range(tentativas):
        thumbs = AdVideo(video_id).get_thumbnails(fields=["uri", "is_preferred"])
        lista = [t.export_all_data() for t in thumbs]
        if lista:
            preferida = next((t for t in lista if t.get("is_preferred")), lista[0])
            print(f"  miniatura pronta ({len(lista)} disponiveis)")
            return preferida["uri"]
        print(f"  processando video... ({i + 1}/{tentativas})")
        time.sleep(espera)
    raise RuntimeError("video nao terminou de processar — rodar de novo com --video-id")


def subir_thumbnail(uri):
    """Baixa a miniatura e sobe como arquivo.

    `create_ad_image` com `url` e recusado com erro 3 ("Application does not
    have the capability") — o app so tem permissao pro upload por arquivo.
    """
    import tempfile
    import urllib.request

    destino = os.path.join(tempfile.gettempdir(), "thumb_waltinho.jpg")
    urllib.request.urlretrieve(uri, destino)

    imagem = AdImage(parent_id=CONTA)
    imagem[AdImage.Field.filename] = destino
    imagem.remote_create()
    h = imagem[AdImage.Field.hash]
    print(f"  image_hash = {h}")
    return h


def criar_creative(nome, mensagem, video_id, image_hash):
    spec = {
        "page_id": PAGINA,
        "instagram_user_id": INSTAGRAM,
        "video_data": {
            "video_id": video_id,
            "image_hash": image_hash,
            "title": TITULO,
            "message": mensagem,
            "call_to_action": {
                "type": "LEARN_MORE",
                "value": {"lead_gen_form_id": FORM, "link": LINK},
            },
        },
    }
    creative = AdAccount(CONTA).create_ad_creative(params={
        "name": nome,
        "object_story_spec": spec,
        "degrees_of_freedom_spec": DOF_SPEC,
    })
    cid = creative["id"]
    print(f"  creative_id = {cid}  ({nome})")
    return cid


def criar_ad(nome, adset_id, creative_id, ativar=False):
    ad = AdAccount(CONTA).create_ad(params={
        "name": nome,
        "adset_id": adset_id,
        "creative": {"creative_id": creative_id},
        "status": "ACTIVE" if ativar else "PAUSED",
        "degrees_of_freedom_spec": DOF_SPEC,
    })
    print(f"  ad_id = {ad['id']}  ({nome}) [{'ACTIVE' if ativar else 'PAUSED'}]")
    return ad["id"]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--video", default=VIDEO, help="caminho do mp4")
    p.add_argument("--video-id", help="reaproveita um video ja subido")
    p.add_argument("--image-hash", help="reaproveita a miniatura ja subida")
    p.add_argument("--ativar", action="store_true", help="cria os ads ja ACTIVE")
    args = p.parse_args()

    init_api()

    video_id = args.video_id or subir_video(args.video)
    image_hash = args.image_hash or subir_thumbnail(esperar_thumbnail(video_id))

    resultado = {"video_id": video_id, "image_hash": image_hash, "ads": []}
    for alvo in ALVOS:
        print(f"\n=== {alvo['nome_ad']}")
        cid = criar_creative(alvo["nome_creative"], alvo["copy"], video_id, image_hash)
        time.sleep(2)
        ad_id = criar_ad(alvo["nome_ad"], alvo["adset"], cid, ativar=args.ativar)
        time.sleep(2)
        resultado["ads"].append({
            "adset": alvo["adset"], "creative_id": cid, "ad_id": ad_id,
        })

    print("\n" + json.dumps(resultado, indent=1, ensure_ascii=False))

    # conferencia: a conta ja teve problema de excluded_geo_locations voltando
    # sozinho quando anuncio novo entra em veiculacao (aprendizados 12-17/08).
    for alvo in ALVOS:
        s = AdSet(alvo["adset"]).api_get(fields=["name", "targeting"])
        excl = s["targeting"].get("excluded_geo_locations")
        print(f"excluded_geo em {s['name']}: {'LIMPO' if not excl else excl}")


if __name__ == "__main__":
    main()
