#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Boali — AD15 Anderson (time de operacoes da franqueadora), 16/09/2026.

O Anderson NAO e franqueado: e do time de operacoes da Boali desde 2008
(inaugura loja, da consultoria, visita as operacoes). A copy nao pode vender
como depoimento de franqueado. Angulo: "operar franquia de alimentacao e
pesado" -> abertura em 1 hora, sem fogao, time da franqueadora junto.

Destinos (pedido da Mileny: tambem nos pinos, onde o publico ja conhece a marca):
  A (quente)  -> CP 04 QUENTE 180D FORMS
  B (pinos)   -> CP 08 PIN LOJA e PIN CIDADE
O CP 05 (LAL frio) ficou de fora de proposito: prova que nao e de franqueado
foi mal no frio (AD13 Natural Tech, R$275 por lead no CP 05 em 01-09/09).

Blueprint, form, CTA e opt-out de IA: os do build_depoimento.py (AD14).
Tudo sobe PAUSED.

Uso:
    python build_anderson.py --dry
    python build_anderson.py
    python build_anderson.py --video-id X --thumb-hash Y   # retomar
"""
import argparse
import os
import subprocess
import sys
import tempfile

import build_depoimento as base

VIDEO = os.path.expandvars(
    r"%USERPROFILE%\OneDrive\Área de Trabalho\CLAUDE CODE\franquias\boali"
    r"\criativos setembro\21 - Depoimento Anderson (funcionario) v2.mp4")
ROTULO = "AD15 - OPERACAO SEM FOGAO ANDERSON"

# Miniatura: o quadro 0 do video e a fachada com logo. Aos 6s e o Anderson
# falando para a camera, que e o que para o scroll.
THUMB_SEG = 6

LISTA = (
    "✅ Abertura da loja em 1 hora\n"
    "✅ Operação sem fogão\n"
    "✅ Time de operações da franqueadora na inauguração e no dia a dia\n"
    "✅ 19 anos de mercado\n"
    "✅ Investimento a partir de R$359.000\n\n"
)

COPY_QUENTE = (
    "Abrir a loja leva uma hora. E não tem fogão.\n\n"
    "Quem conta é o Anderson, do time de operações da Boali desde 2008. Ele "
    "inaugura lojas e acompanha cada franqueado de perto.\n\n"
    + LISTA +
    "Se você tem o capital e não quer um negócio que dependa de cozinha "
    "pesada, fale com um de nossos consultores.\n"
    "👇"
)

COPY_PINOS = (
    "Você conhece a Boali do lado de cá do balcão. Do lado de lá, a loja abre "
    "em uma hora e não tem fogão.\n\n"
    "Quem conta é o Anderson, do time de operações da Boali desde 2008.\n\n"
    + LISTA +
    "Ainda há praças disponíveis na sua região. Fale com um de nossos "
    "consultores.\n"
    "👇"
)

GRUPOS = [
    ("A", COPY_QUENTE, [
        ("120249949945780156", "CP 04 · QUENTE 180D FORMS", ""),
    ]),
    ("B", COPY_PINOS, [
        ("120251217473750156", "CP 08 · PIN LOJA", ""),
        ("120251205721260156", "CP 08 · PIN CIDADE", ""),
    ]),
]


def sobe_thumb():
    jpg = os.path.join(tempfile.gettempdir(), "boali_ad15_thumb.jpg")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(THUMB_SEG), "-i", VIDEO,
                    "-frames:v", "1", "-q:v", "2", jpg], check=True)
    # scripts/create.py image quebra no SDK atual (create_ad_image nao aceita
    # `files`, 16/09/2026). Vai direto na Graph API com os bytes em base64.
    import base64, json, urllib.parse, urllib.request
    with open(jpg, "rb") as f:
        corpo = urllib.parse.urlencode({
            "bytes": base64.b64encode(f.read()).decode(),
            "access_token": base.TOKEN,
        }).encode()
    req = urllib.request.Request(base.API + "%s/adimages" % base.CONTA, data=corpo)
    with urllib.request.urlopen(req, timeout=120) as r:
        imagens = json.load(r)["images"]
    h = next(iter(imagens.values()))["hash"]
    print("  OK   %-52s %s" % ("miniatura (6s)", h))
    return h


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--video-id")
    ap.add_argument("--thumb-hash")
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()

    print("\nBoali — %s (PAUSED)" % ROTULO)
    for letra, copy, destinos in GRUPOS:
        print("\n  Criativo %s -> %s" % (letra, ", ".join(d[1] for d in destinos)))
        for linha in copy.splitlines():
            print("        " + linha)
    if a.dry:
        print("\n  [dry] nada foi criado.")
        return

    video_id = a.video_id or base.sobe_video(VIDEO)
    thumb = a.thumb_hash or sobe_thumb()

    for letra, copy, destinos in GRUPOS:
        story = {
            "page_id": base.PAGE,
            "instagram_user_id": base.IG,
            "video_data": {
                "video_id": video_id,
                "image_hash": thumb,
                "title": base.TITULO,
                "message": copy,
                "call_to_action": {
                    "type": "SIGN_UP",
                    "value": {"lead_gen_form_id": base.FORM, "link": "http://fb.me/"},
                },
            },
        }
        criativo = base.post("%s/adcreatives" % base.CONTA, {
            "name": "Boali — %s [%s]" % (ROTULO, letra),
            "object_story_spec": story,
            "degrees_of_freedom_spec": base.SEM_IA,
        }, "criativo %s" % letra)
        for adset_id, nome, prefixo in destinos:
            base.post("%s/ads" % base.CONTA, {
                "name": prefixo + ROTULO,
                "adset_id": adset_id,
                "creative": {"creative_id": criativo},
                "status": "PAUSED",
            }, "ad em %s" % nome)

    print("\n  Tudo PAUSED. Conferir preview antes de ativar.")


if __name__ == "__main__":
    main()
