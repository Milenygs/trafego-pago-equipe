#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Casa de Vidro Paraty — 2 carrosseis nos 4 conjuntos ativos da GEO-PIN/WHATS (15/09/2026).

Pedido da Mileny: subir o "Casa de Vidro — Carrossel Eventos- whats 2" (ja rodou na
campanha de WhatsApp antiga) nos conjuntos ativos, em 2 versoes com copy diferente
e so 4 imagens cada, mantendo a 1a imagem (a que tem a frase na arte).

Base: criativo 990953357192435 (10 imagens). Tres correcoes em relacao a ele:
  - numero de WhatsApp: o original tem wa.me/553197681409 fixo em cada card (bug de
    25/08). Aqui o link e o generico api.whatsapp.com/send e o CTA vai SEM `link`
    (subcode 1815630) — o numero vem do promoted_object do conjunto (5511969565817).
  - instagram_user_id: o original nao tinha.
  - ordem dos cards travada: multi_share_optimized=false e end card desligado.
Ice breakers (com o "a partir de R$ 10 mil") e os 83 opt-outs de IA vem do criativo
V3 que ja roda nesses conjuntos (1066794959461074).

Uso:
    python build_carrosseis_geopin.py --dry
    python build_carrosseis_geopin.py                 # cria 2 criativos + 8 ads PAUSED
    python build_carrosseis_geopin.py --criativos A_ID,B_ID   # retoma so os ads
"""
import argparse
import json
import sys
import time

from build_geopin_whats import CONTA, PAGINA, INSTAGRAM, SEM_ENHANCEMENTS_MIN, get, post

CRIATIVO_V3 = "1066794959461074"
LINK = "https://api.whatsapp.com/send"

CONJUNTOS = [
    ("120249402954240510", "PIN MORA"),
    ("120249403004740510", "PIN DESTINO"),
    ("120249403592920510", "PIN LUGARES"),
    ("120249403702380510", "PIN LUGARES BR"),
]

CAPA = "03a59f3ac9a32805ef6b39d0a5e55578"  # DSCF5388 com "Uma experiencia que ninguem esquece"

CARROSSEIS = [
    {
        "chave": "A",
        "nome": "Carrossel Eventos A - Casa inteira",
        "cards": [
            (CAPA, None),
            ("ff842608ffbd032742dfb5074338944d", "Vista exclusiva."),        # DSCF5299 casal na piscina
            ("dc98fd3b5dca3a465edceb82c22d4808", "Conforto elevado."),       # DSCF4260 deck com mesa
            ("c59536d5c870c7f7271b3a2114a0fba9", "Natureza e privacidade."), # DSCF5429 casa + palmeiras
        ],
        "copy": (
            "Raro. Inteiro. Só de vocês.\n\n"
            "Uma casa inteira em Paraty Mirim — não é suíte, não é pousada: é a propriedade "
            "completa, com piscina privativa de frente pro mar e acesso exclusivo de barco. "
            "5 suítes para até 12 pessoas.\n\n"
            "O mar, a casa, e as pessoas que importam.\n\n"
            "👇 Chame no WhatsApp e consulte as datas disponíveis."
        ),
    },
    {
        "chave": "B",
        "nome": "Carrossel Eventos B - Experiencia",
        "cards": [
            (CAPA, None),
            ("7d6d3aa78e93e27790c9655b46a86fc5", "Piscina privativa."),         # DSCF5415 ducha + piscina infinita
            ("1ca2baff36bb207ca59f646c94739a3e", "O mar pertinho."),            # DSCF5548 pier
            ("7369f473411a93eb85c2ad55e54376c1", "Paraty Mirim ao amanhecer."), # DSCF4823 quarto com vista
        ],
        "copy": (
            "Para quem sabe que uma casa inteira vale mais do que um hotel.\n\n"
            "Em Paraty Mirim, a Casa de Vidro é locação integral da propriedade: piscina infinita, "
            "costeira privativa e serviços personalizados, com concierge 24/7, chef, barqueiro e "
            "serviço de praia.\n\n"
            "Aqui, o tempo tem outro ritmo.\n\n"
            "👇 Chame no WhatsApp e consulte as datas disponíveis."
        ),
    },
]


def base_v3():
    c = get(CRIATIVO_V3, {"fields": "object_story_spec,degrees_of_freedom_spec"})
    welcome = c["object_story_spec"]["video_data"].get("page_welcome_message")
    dof = c.get("degrees_of_freedom_spec", {}).get("creative_features_spec", {})
    return welcome, dof


def spec_carrossel(car, welcome):
    cta = {"type": "WHATSAPP_MESSAGE", "value": {"app_destination": "WHATSAPP"}}
    cards = []
    for h, titulo in car["cards"]:
        card = {"link": LINK, "image_hash": h, "call_to_action": cta}
        if titulo:
            card["name"] = titulo
        cards.append(card)
    link_data = {
        "link": LINK,
        "message": car["copy"],
        "child_attachments": cards,
        "multi_share_end_card": False,
        "multi_share_optimized": False,
        "call_to_action": cta,
    }
    if welcome:
        link_data["page_welcome_message"] = welcome
    return {"page_id": PAGINA, "instagram_user_id": INSTAGRAM, "link_data": link_data}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--criativos", help="A_ID,B_ID ja criados — so cria os ads")
    args = ap.parse_args()

    welcome, dof = base_v3()
    print("Boas-vindas:", "herdado do V3" if welcome else "NENHUM")
    print("Opt-outs   :", len(dof))
    for car in CARROSSEIS:
        print("\n== %s (%d cards)" % (car["nome"], len(car["cards"])))
        print("  " + car["copy"].replace("\n", "\n  "))
        for h, t in car["cards"]:
            print("   -", h, t or "(capa)")
    if args.dry:
        print("\n--dry: nada criado. Criaria 2 criativos e %d ads PAUSED." % (2 * len(CONJUNTOS)))
        return

    ids = args.criativos.split(",") if args.criativos else []
    if not ids:
        print("\nCriando criativos...")
        for car in CARROSSEIS:
            spec = spec_carrossel(car, welcome)
            nome = "CDV - %s [WHATS] - 15/09/2026" % car["nome"]
            cid = post(CONTA + "/adcreatives", {
                "name": nome, "object_story_spec": spec,
                "degrees_of_freedom_spec": {"creative_features_spec": dof or SEM_ENHANCEMENTS_MIN},
            }, "criativo " + car["chave"])
            if not cid and dof:
                print("       -> repetindo com o subset minimo de opt-out")
                cid = post(CONTA + "/adcreatives", {
                    "name": nome, "object_story_spec": spec,
                    "degrees_of_freedom_spec": {"creative_features_spec": SEM_ENHANCEMENTS_MIN},
                }, "criativo " + car["chave"] + " (min)")
            if not cid:
                sys.exit("Criativo %s falhou — nenhum ad criado." % car["chave"])
            ids.append(cid)
            time.sleep(1)

    print("\nCriando ads (PAUSED)...")
    criados = []
    for car, cid in zip(CARROSSEIS, ids):
        for adset, apelido in CONJUNTOS:
            ad = post(CONTA + "/ads", {
                "name": "AD - %s - %s" % (car["nome"], apelido),
                "adset_id": adset,
                "creative": {"creative_id": cid},
                "status": "PAUSED",
            }, "ad %s %s" % (car["chave"], apelido))
            criados.append((car["chave"], apelido, ad))
            time.sleep(1)

    print("\nRESUMO")
    print("criativos:", ids)
    print(json.dumps(criados, ensure_ascii=False))


if __name__ == "__main__":
    main()
