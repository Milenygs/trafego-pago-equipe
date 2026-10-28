#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Casa de Vidro Paraty — video "Criativo Culinaria" nos conjuntos da GEO-PIN/WHATS (28/09/2026).

Pedido da Mileny: subir o video novo da pasta criativos ("Criativo Culinaria.mp4", 16s, so
musica) nas campanhas ativas de WhatsApp, com copy personalizada.
Video ja subido: 1711007663895650. Miniatura: quadro de 5,5s (mesa do cafe com o mar ao fundo).
Ice breakers (o 1o com "a partir de R$ 10 mil") vem do criativo do "Onde o verao 1"
(1399576785028475); os opt-outs de IA vem do V3 (1066794959461074), sem standard_enhancements.

Uso:
    python build_culinaria_whats.py --dry
    python build_culinaria_whats.py                    # imagem + criativo + 4 ads PAUSED
    python build_culinaria_whats.py --criativo ID      # retoma so os ads
"""
import argparse
import base64
import json
import os
import sys
import time

from build_geopin_whats import CONTA, PAGINA, INSTAGRAM, get, post

VIDEO = "1711007663895650"
THUMB = os.path.expandvars(r"$TEMP\cdv_culinaria\thumb_5.5.jpg")
MODELO_WELCOME = "1399576785028475"
MODELO_OPTOUT = "1066794959461074"

CONJUNTOS = [
    ("120249402954240510", "PIN MORA"),
    ("120249403004740510", "PIN DESTINO"),
    ("120249403702380510", "PIN LUGARES BR"),
    ("120249614066980510", "QUENTE"),  # pausado, esperando ativacao
]

TITULO = "Gastronomia caiçara de frente pro mar"
COPY = (
    "A mesa já está posta.\n\n"
    "O café da manhã é servido no deck, de frente para a baía de Paraty Mirim. E a gastronomia "
    "caiçara da casa acompanha o dia, com cardápio personalizado, criado para vocês.\n\n"
    "Uma casa inteira, só sua — não é suíte, não é pousada: é a propriedade completa, com piscina "
    "privativa de frente pro mar e acesso exclusivo de barco. 5 suítes para até 12 pessoas.\n\n"
    "Aqui, o tempo tem outro ritmo.\n\n"
    "👇 Chame no WhatsApp e consulte as datas disponíveis."
)


def sobe_miniatura(dry):
    if dry:
        return "DRY_HASH"
    dados = base64.b64encode(open(THUMB, "rb").read()).decode()
    r = post(CONTA + "/adimages", {"bytes": dados, "name": "CDV - Culinaria - thumb 5s.jpg"}, "miniatura")
    # adimages devolve {"images": {nome: {"hash": ...}}}, o post() so imprime; relê pela lista
    imgs = get(CONTA + "/adimages", {"fields": "hash,name,created_time", "limit": 5})["data"]
    return [i for i in imgs if i["name"] == "CDV - Culinaria - thumb 5s.jpg"][0]["hash"]


def criativo(dry):
    welcome = get(MODELO_WELCOME, {"fields": "object_story_spec"})["object_story_spec"]["video_data"]["page_welcome_message"]
    feats = get(MODELO_OPTOUT, {"fields": "degrees_of_freedom_spec"})["degrees_of_freedom_spec"]["creative_features_spec"]
    feats.pop("standard_enhancements", None)  # descontinuado na criacao (10/09)
    feats = {k: {"enroll_status": "OPT_OUT"} for k in feats}
    thumb = sobe_miniatura(dry)
    params = {
        "name": "CDV - Culinaria - A mesa posta [WHATS] - 28/09/2026",
        "object_story_spec": {"page_id": PAGINA, "instagram_user_id": INSTAGRAM, "video_data": {
            "video_id": VIDEO, "image_hash": thumb, "title": TITULO, "message": COPY,
            "call_to_action": {"type": "WHATSAPP_MESSAGE", "value": {"app_destination": "WHATSAPP"}},
            "page_welcome_message": welcome,
        }},
        "degrees_of_freedom_spec": {"creative_features_spec": feats},
    }
    if dry:
        print("  DRY  criativo (%d opt-outs)" % len(feats))
        print(COPY)
        return "DRY_CRIATIVO"
    cid = post(CONTA + "/adcreatives", params, "criativo Culinaria")
    if not cid:
        sys.exit("criativo falhou")
    return cid


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--criativo")
    a = ap.parse_args()
    cid = a.criativo or criativo(a.dry)
    for adset, rotulo in CONJUNTOS:
        nome = "AD - Culinaria - A mesa posta - " + rotulo
        if a.dry:
            print("  DRY  ad", nome, "->", adset)
            continue
        post(CONTA + "/ads", {"name": nome, "adset_id": adset, "creative": {"creative_id": cid},
                              "status": "PAUSED"}, nome)
        time.sleep(1.5)
