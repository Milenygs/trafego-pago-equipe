#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Boali — 24/09/2026: troca o video do AD20 Marcos Babi pela versao sem o trecho
do peso ("BOALI - Marcos Babi (sem trecho do peso).mp4", 29,9s) nos 4 ads.
Mesmas copies, mesmo titulo, miniatura aos 3s. Os ads mantem id e status (PAUSED).

Uso:
    python troca_babi_cortado.py
"""
import json
import os

import build_rodrigo_setembro as r
from build_rodrigo_setembro import base
import build_babi_lojacheia as pinos
import build_babi_quente_lal as ql

ESTADO = os.path.join(r.AQUI, "criados_2026-09-24d.json")
r.ESTADO = ESTADO
ARQUIVO = "BOALI - Marcos Babi (sem trecho do peso)"
ROTULO = "AD20 [FRANQUEADO] [VIDEO] MARCOS BABI RUA SHOPPING CORPORATIVA CORTE"

# letra -> (copy, [ad ids])
TROCAS = {
    "A": (pinos.AD20_PINOS, ["120251425985370156", "120251425985640156"]),
    "Q": (ql.AD20_QUENTE, ["120251426472570156"]),
    "F": (ql.AD20_FRIO, ["120251426472780156"]),
}


def main():
    e = r.carrega()
    video = r.acha_video(ARQUIVO)
    if not e.get("video_id"):
        e["video_id"] = r.sobe_video_simples(video)
        r.salva(e)
    if not e.get("thumb"):
        e["thumb"] = r.sobe_thumb(video, 3, "AD20corte")
        r.salva(e)
    e.setdefault("trocados", {})
    for letra, (copy, ads) in TROCAS.items():
        ck = "criativo_" + letra
        if not e.get(ck):
            e[ck] = base.post("%s/adcreatives" % base.CONTA, {
                "name": "Boali — %s [%s]" % (ROTULO, letra),
                "object_story_spec": {
                    "page_id": base.PAGE,
                    "instagram_user_id": base.IG,
                    "video_data": {
                        "video_id": e["video_id"],
                        "image_hash": e["thumb"],
                        "title": "De loja de rua a corporativa",
                        "link_description": r.DESCRICAO,
                        "message": copy,
                        "call_to_action": {
                            "type": "SIGN_UP",
                            "value": {"lead_gen_form_id": base.FORM,
                                      "link": "http://fb.me/"},
                        },
                    },
                },
                "degrees_of_freedom_spec": base.SEM_IA,
            }, "criativo corte %s" % letra)
            r.salva(e)
        for ad in ads:
            if ad in e["trocados"]:
                continue
            base.post(ad, {"creative": {"creative_id": e[ck]}}, "troca no ad %s" % ad)
            e["trocados"][ad] = e[ck]
            r.salva(e)
    print("\n  RELEITURA")
    for letra, (_c, ads) in TROCAS.items():
        for ad in ads:
            a = base.get(ad, {"fields": "name,status,effective_status,adset{name},creative{id}"})
            print("  %s  %-7s %-15s criativo %s  %s" % (
                ad, a["status"], a["effective_status"], a["creative"]["id"],
                a["adset"]["name"][:45]))


if __name__ == "__main__":
    main()
