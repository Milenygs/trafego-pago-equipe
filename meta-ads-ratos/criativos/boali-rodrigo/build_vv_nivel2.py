#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Boali — 2 videos de nivel 2 (marca + fundador) no video view, alimentando o quente (02/10/2026).

Pedido da Mileny: "atualize visualizacao de video com dois videos da pasta criativos para video viwes.
Entram no nivel 2 do funil espiral e falam sobre marca; um deles e o dono falando de franquia. Use um
publico que alimentamos a captacao de leads no publico quente."

  1. Os 2 videos entram no CP 03 [VIDEO_VIEW_THRUPLAY] [180D], no conjunto ativo "— 3"
     (criativo novo entra em conjunto que ja existe). Sem botao (regra de 21/07), IA toda OPT_OUT. PAUSED.
  2. Publico [VV 50%] dos 2 videos, 180D, pelo video_id de topo do criativo (copia na Pagina, regra de 26/09 e 28/09).
  3. Esse publico entra no conjunto quente do CP 04 (mesmo desenho do VV2 da Casa de Vidro, 28/09).
     A edicao reinicia o aprendizado do CP 04, entao roda separada: --cp04 validar | aplicar.

    python build_vv_nivel2.py --dry
    python build_vv_nivel2.py                 # sobe videos, criativos, ads PAUSED e o publico
    python build_vv_nivel2.py --cp04 validar  # validate_only no targeting do CP 04
    python build_vv_nivel2.py --cp04 aplicar
"""
import argparse
import json
import os
import sys
import time

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
sys.path.insert(0, os.path.join(AQUI, "..", "boali-depoimento"))
import build_depoimento as base  # noqa: E402
from build_rodrigo_setembro import sobe_thumb, sobe_video_simples  # noqa: E402

PASTA = os.path.expandvars(
    r"%USERPROFILE%\OneDrive\Área de Trabalho\CLAUDE CODE\franquias\boali\criativos para video viwes")
ESTADO = os.path.join(AQUI, "criados_2026-10-02_vv.json")

CP03_CONJUNTO = "120250112177130156"   # [180D] [PEPA + VV + SITE] [ON_VIDEO] — 3 (ACTIVE, THRUPLAY/ON_VIDEO)
CP04_QUENTE = "120249949945780156"     # [QUENTE 180D] [FORMS - CADASTROS] [ON_AD] (ACTIVE)
NOME_PUBLICO = "[VV 50%] NIVEL 2 - RECUSOU O FUNDO + RODRIGO VENDER FRANQUIA 180D"

AD22 = (
    "Ele disse não ao dinheiro de um fundo para não perder o controle da própria empresa.\n\n"
    "A condição era abrir 80 lojas em 18 meses. Para o Rodrigo Barros, esse ritmo não deixava "
    "espaço para manter a qualidade, e a resposta foi não.\n\n"
    "A Boali seguiu crescendo do jeito dela: os fundadores perto da operação, um time de suporte "
    "direto aos franqueados e marcas compradas com os próprios fundadores continuando no negócio.\n\n"
    "Capital paciente vale mais que capital grande."
)

AD23 = (
    "Vender franquia é fácil. O difícil é entregar.\n\n"
    "Quem investe numa franquia não compra só uma marca. Compra o fornecedor que chega no prazo, "
    "o mesmo produto em todas as lojas e uma estrutura que continua atendendo depois da assinatura.\n\n"
    "O Rodrigo, dono da Boali, está há mais de 19 anos construindo essa estrutura. Antes de escolher "
    "uma franquia, pergunte quem vai abastecer a sua loja."
)

PECAS = [
    {
        "chave": "AD22",
        "arquivo": "ele recusou 28 milhoes.mp4",
        "rotulo": "AD22 [MARCA] [VIDEO] RECUSOU O FUNDO CAPITAL PACIENTE",
        "thumb_seg": 0.5,   # cartela "Ele recusou R$28 milhoes" com o Rodrigo no alto
        "titulo": "Capital paciente",
        "copy": AD22,
    },
    {
        "chave": "AD23",
        "arquivo": "video rodrigo- vender franquia.mp4",
        "rotulo": "AD23 [FUNDADOR] [VIDEO] VENDER FRANQUIA E FACIL O DIFICIL E ENTREGAR",
        "thumb_seg": 1,
        "titulo": "O difícil é entregar",
        "copy": AD23,
    },
]


def carrega():
    if os.path.exists(ESTADO):
        with open(ESTADO, encoding="utf-8") as f:
            return json.load(f)
    return {}


def salva(estado):
    with open(ESTADO, "w", encoding="utf-8") as f:
        json.dump(estado, f, ensure_ascii=False, indent=2)


def video_da_pagina(criativo, video_upload):
    # Logo apos o POST, o video_id de topo ainda e o do upload (sem Pagina, da #2654).
    # A copia na Pagina chega com outro ID, em segundos ou minutos (02/10: AD22 ~1 min).
    for _ in range(40):
        c = base.get(criativo, {"fields": "video_id"})
        if c.get("video_id") and c["video_id"] != video_upload:
            return c["video_id"]
        time.sleep(15)
    sys.exit("criativo %s ainda sem a copia do video na Pagina; rodar de novo mais tarde" % criativo)


def cria(estado, dry):
    for p in PECAS:
        e = estado.setdefault(p["chave"], {})
        video = os.path.join(PASTA, p["arquivo"])
        story = {"page_id": base.PAGE, "instagram_user_id": base.IG,
                 "video_data": {"video_id": e.get("video_id", "<upload>"), "image_hash": e.get("thumb", "<thumb>"),
                                "title": p["titulo"], "message": p["copy"]}}
        if dry:
            print("\n  DRY %s  %s\n%s" % (p["chave"], p["rotulo"], json.dumps(story, ensure_ascii=False, indent=1)))
            continue
        print("\n  %s — %s" % (p["chave"], p["arquivo"]))
        if not e.get("video_id"):
            e["video_id"] = sobe_video_simples(video)
            salva(estado)
        if not e.get("thumb"):
            e["thumb"] = sobe_thumb(video, p["thumb_seg"], p["chave"])
            salva(estado)
        story["video_data"].update(video_id=e["video_id"], image_hash=e["thumb"])
        if not e.get("criativo"):
            e["criativo"] = base.post("%s/adcreatives" % base.CONTA, {
                "name": "Boali — %s [VV sem botao]" % p["rotulo"],
                "object_story_spec": story,                 # video view: sem call_to_action
                "degrees_of_freedom_spec": base.SEM_IA,
                "contextual_multi_ads": {"enroll_status": "OPT_OUT"},
            }, "criativo %s" % p["chave"])
            if not e["criativo"]:
                sys.exit("parou no criativo %s" % p["chave"])
            salva(estado)
        if not e.get("video_pagina") or e["video_pagina"] == e["video_id"]:
            e["video_pagina"] = video_da_pagina(e["criativo"], e["video_id"])
            print("  OK   %-52s %s" % ("video na Pagina %s" % p["chave"], e["video_pagina"]))
            salva(estado)
        if not e.get("ad"):
            e["ad"] = base.post("%s/ads" % base.CONTA, {
                "name": p["rotulo"], "adset_id": CP03_CONJUNTO,
                "creative": {"creative_id": e["criativo"]}, "status": "PAUSED",
            }, "ad %s no CP 03" % p["chave"])
            salva(estado)
    if dry:
        return
    if not estado.get("publico"):
        estado["publico"] = base.post("%s/customaudiences" % base.CONTA, {
            "name": NOME_PUBLICO, "subtype": "ENGAGEMENT", "retention_days": 180, "prefill": "true",
            "rule": [{"event_name": "video_view_50_percent", "object_id": estado[p["chave"]]["video_pagina"]}
                     for p in PECAS],
        }, "publico VV 50% nivel 2")
        salva(estado)
    print("\n  RELEITURA")
    for p in PECAS:
        ad = base.get(estado[p["chave"]]["ad"], {"fields": "name,status,effective_status,issues_info"})
        print("  %s  %-7s %-15s %s  issues=%s" % (ad["id"], ad["status"], ad["effective_status"], ad["name"],
                                                  ad.get("issues_info", "-")))
    pub = base.get(estado["publico"], {"fields": "name,operation_status,approximate_count_lower_bound"})
    print("  publico %s  %s  %s" % (pub["id"], pub["name"], pub.get("operation_status")))


def cp04(estado, modo):
    aud = estado.get("publico")
    if not aud:
        sys.exit("publico ainda nao criado")
    t = base.get(CP04_QUENTE, {"fields": "name,targeting"})["targeting"]
    ids = [c["id"] for c in t.get("custom_audiences", [])]
    if aud in ids:
        print("  ja esta no CP 04")
        return
    t["custom_audiences"].append({"id": aud, "name": NOME_PUBLICO})
    params = {"targeting": t}       # objeto inteiro como veio, so com o publico a mais
    if modo == "validar":
        params["execution_options"] = ["validate_only"]
    r = base.post(CP04_QUENTE, params, "CP 04 + publico VV (%s)" % modo)
    print("  resposta:", r)
    if modo == "aplicar":
        time.sleep(5)
        t2 = base.get(CP04_QUENTE, {"fields": "effective_status,targeting"})
        nomes = [c.get("name") for c in t2["targeting"].get("custom_audiences", [])]
        print("  releitura: %s publicos, novo dentro=%s, status=%s" % (
            len(nomes), aud in [c["id"] for c in t2["targeting"]["custom_audiences"]], t2["effective_status"]))
        print("  relax:", t2["targeting"].get("targeting_relaxation_types"),
              "| geo:", t2["targeting"].get("geo_locations"))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--cp04", choices=["validar", "aplicar"])
    a = ap.parse_args()
    estado = carrega()
    if a.cp04:
        cp04(estado, a.cp04)
    else:
        cria(estado, a.dry)
