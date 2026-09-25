#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Casa de Vidro — trocar o video do criativo da [GEO-PIN/WHATS] (10/09/2026).

Pedido dela, ~1h depois de subir a campanha: "o video e a versao 3, desculpa e
ja coloquei na pasta". A V2 tinha acabado de subir, com gasto zero e nenhum
aprendizado — entao a troca e feita **no lugar**, atualizando o `creative` dos 2
anuncios que ja existem, em vez de criar ads novos e pausar os antigos. Mesma
campanha, mesmos conjuntos, mesmos IDs de anuncio; so a midia muda.

O criativo novo e clonado do que esta no ar (`1612225557231619`): mesma copy,
mesmo CTA de WhatsApp, mesmas boas-vindas com os ice breakers, mesmo opt-out de
IA. Troca o `video_id` e a thumbnail.

Uso:
    python trocar_video_geopin_whats.py --video <ID> --dry
    python trocar_video_geopin_whats.py --video <ID>
"""
import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

AQUI = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.abspath(os.path.join(AQUI, "..", ".."))
API = "https://graph.facebook.com/v21.0/"

CONTA = "act_792396727164193"
CRIATIVO_ATUAL = "1612225557231619"   # V2, no ar desde 10/09 — fonte de tudo menos a midia
ADS = [
    ("120249402958140510", "PIN MORA"),
    ("120249403006590510", "PIN DESTINO"),
]
NOME_NOVO = "CDV - A IA nao vai substituir isso V3 [WHATS] - 10/09/2026"


def token():
    caminho = os.path.join(SKILL, ".env")
    for linha in open(caminho, encoding="utf-8"):
        if linha.strip().startswith("META_ADS_TOKEN"):
            return linha.split("=", 1)[1].strip().strip('"')
    sys.exit("META_ADS_TOKEN nao encontrado em " + caminho)


TOKEN = token()


def get(path, params=None):
    params = dict(params or {})
    params["access_token"] = TOKEN
    url = API + path + "?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url) as r:
        return json.load(r)


def post(path, params, oque):
    corpo = {k: (json.dumps(v) if isinstance(v, (dict, list)) else v)
             for k, v in params.items()}
    corpo["access_token"] = TOKEN
    dados = urllib.parse.urlencode(corpo).encode()
    try:
        with urllib.request.urlopen(urllib.request.Request(API + path, data=dados)) as r:
            saida = json.load(r)
            print("  OK   %-34s %s" % (oque, saida.get("id") or saida))
            return saida.get("id") or True
    except urllib.error.HTTPError as e:
        erro = json.loads(e.read().decode("utf-8")).get("error", {})
        print("  ERRO %-34s" % oque)
        print("       msg :", erro.get("message"))
        print("       user:", erro.get("error_user_title"), "|", erro.get("error_user_msg"))
        print("       sub :", erro.get("error_subcode"))
        return None


def thumb(video_id):
    dados = get(video_id + "/thumbnails").get("data", [])
    for t in dados:
        if t.get("is_preferred"):
            return t["uri"]
    return dados[0]["uri"] if dados else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", required=True, help="video_id novo (a V3)")
    ap.add_argument("--dry", action="store_true")
    args = ap.parse_args()

    c = get(CRIATIVO_ATUAL, {"fields": "object_story_spec,degrees_of_freedom_spec"})
    spec = c["object_story_spec"]
    vd = dict(spec["video_data"])
    dof = c.get("degrees_of_freedom_spec", {}).get("creative_features_spec", {})

    capa = thumb(args.video)
    antigo = vd.get("video_id")
    vd["video_id"] = args.video
    vd["image_url"] = capa
    # A capa e a do video novo: sem tirar o image_hash da V2, a Meta reusa ele.
    vd.pop("image_hash", None)
    # O `link` de api.whatsapp.com a Meta preenche sozinha e RECUSA no POST
    # (subcode 1815630) — tirar antes de reenviar.
    cta = dict(vd.get("call_to_action") or {})
    if cta.get("value"):
        cta["value"] = {"app_destination": "WHATSAPP"}
        vd["call_to_action"] = cta

    novo_spec = {k: v for k, v in spec.items() if k != "video_data"}
    novo_spec["video_data"] = vd

    print("Criativo fonte :", CRIATIVO_ATUAL)
    print("Video  %s -> %s" % (antigo, args.video))
    print("Capa           :", (capa or "SEM THUMB")[:90])
    print("Opt-out de IA  :", len(dof), "features herdadas")
    print("Boas-vindas    :", "sim" if vd.get("page_welcome_message") else "NAO — confira")
    print("CTA            :", json.dumps(vd.get("call_to_action"), ensure_ascii=False))
    print("Copy (1a linha):", vd["message"].split("\n")[0])

    if args.dry:
        print()
        print("--dry: nada escrito. Criaria 1 criativo e trocaria nos %d ads." % len(ADS))
        return

    print()
    print("Criando o criativo da V3...")
    novo = post(CONTA + "/adcreatives", {
        "name": NOME_NOVO,
        "object_story_spec": novo_spec,
        "degrees_of_freedom_spec": {"creative_features_spec": dof},
    }, "criativo V3")
    if not novo:
        print("Sem criativo novo — os ads seguem com a V2, nada foi tocado.")
        sys.exit(1)

    print()
    print("Trocando o criativo nos anuncios (mesmos IDs, sem ad novo)...")
    for ad_id, apelido in ADS:
        post(ad_id, {"creative": {"creative_id": novo}}, "ad " + apelido)
        time.sleep(1)

    print()
    print("Criativo novo:", novo)
    print("Conferir a saida da analise em 1-2h:")
    print("  read.py ads-by-campaign --campaign 120249402919690510 "
          "--fields name,effective_status,issues_info,creative")


if __name__ == "__main__":
    main()
