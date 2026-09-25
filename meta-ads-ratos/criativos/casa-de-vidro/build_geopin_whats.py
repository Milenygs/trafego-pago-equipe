#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Casa de Vidro Paraty — GEO-PIN v2, destino WhatsApp (10/09/2026).

Pedido da Mileny: refazer a campanha de pinos igual a de 08/09, porque a
original deu "Atualizacao necessaria" no anuncio do PIN/DESTINO
(issue 1885255, 09/09 17h31) e ela pausou a campanha inteira em 10/09 11h47.
Duas mudancas em relacao a original:
  1. destino WhatsApp em vez do site  -> CONVERSATIONS + destination_type WHATSAPP
  2. criativo novo: "A IA nao vai substituir isso V2"

O que e copiado fielmente da campanha `120249369648020510`: objetivo
OUTCOME_LEADS, ABO, os 25 pinos do PIN/MORA e os 9 do PIN/DESTINO com os mesmos
raios e `location_types`, 35-65, so Instagram, sem interesse nenhum,
`advantage_audience: 0`, IG_SEGUIDORES excluido, R$80/dia por conjunto.

A copy vem do criativo `1394480209485938` (aprovado, ja rodou) — so a ultima
linha muda, porque "faca sua reserva" mandava pro site e agora o destino e
conversa. O `page_welcome_message` (3 ice breakers, com o "a partir de R$ 10 mil
- minimo 2 noites") vem do criativo de WhatsApp `1058479113508257`: e ele que
qualifica o lead na porta, que e o ponto do teste de pino.

Uso:
    python build_geopin_whats.py --dry   # mostra tudo, nao escreve nada
    python build_geopin_whats.py         # cria campanha + 2 conjuntos + 2 ads
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
PAGINA = "949028168287242"
INSTAGRAM = "17841472733937596"
WHATSAPP = "5511969565817"          # o mesmo dos 5 conjuntos da campanha de WhatsApp
IG_SEGUIDORES = "120244196072220510"

VIDEO_V2 = "1731618151452761"       # "A IA nao vai substituir isso - VS02.mp4"
CRIATIVO_COPY = "1394480209485938"  # fonte da copy + do opt-out de IA
CRIATIVO_WPP = "1058479113508257"   # fonte do page_welcome_message (ice breakers)

ORIGEM_MORA = "120249369649830510"    # le os 25 pinos daqui
ORIGEM_DESTINO = "120249369651930510" # le os 9 pinos daqui

# A copy aprovada fecha em "Conheca a casa completa e faca sua reserva!", que
# era CTA de site. No destino conversa, a ultima linha vira convite a conversa.
FIM_ANTIGO = "👇 Conheça a casa completa e faça sua reserva!"
FIM_NOVO = "👇 Chame no WhatsApp e consulte as datas disponíveis."

SEM_ENHANCEMENTS_MIN = {
    "advantage_plus_creative": {"enroll_status": "OPT_OUT"},
    "enhance_cta": {"enroll_status": "OPT_OUT"},
    "text_optimizations": {"enroll_status": "OPT_OUT"},
    "image_touchups": {"enroll_status": "OPT_OUT"},
    "video_auto_crop": {"enroll_status": "OPT_OUT"},
}


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
            print("  OK   %-40s %s" % (oque, saida.get("id") or saida))
            return saida.get("id")
    except urllib.error.HTTPError as e:
        erro = json.loads(e.read().decode("utf-8")).get("error", {})
        print("  ERRO %-40s" % oque)
        print("       msg :", erro.get("message"))
        print("       user:", erro.get("error_user_title"), "|", erro.get("error_user_msg"))
        print("       sub :", erro.get("error_subcode"))
        return None


def checar():
    conta = get(CONTA, {"fields": "name,account_status,balance"})
    status = conta.get("account_status")
    print("Conta    :", conta.get("name"))
    print("Status   :", status, "(1=ativa)")
    print("Em aberto: R$ %.2f" % (int(conta.get("balance", 0)) / 100))
    if status != 1:
        print("BLOQUEADO — fora do status 1 a Meta recusa /adcreatives (subcode 1487194).")
        return False
    return True


def thumb(video_id):
    dados = get(video_id + "/thumbnails").get("data", [])
    for t in dados:
        if t.get("is_preferred"):
            return t["uri"]
    return dados[0]["uri"] if dados else None


def pinos(adset_id):
    """Os custom_locations e o location_types do conjunto original, intactos."""
    geo = get(adset_id, {"fields": "targeting"})["targeting"]["geo_locations"]
    locais = []
    for p in geo["custom_locations"]:
        locais.append({k: p[k] for k in
                       ("latitude", "longitude", "radius", "distance_unit", "country")
                       if k in p})
    # `frequently_in` a Meta acrescenta sozinha na ativacao (ver aprendizados.md);
    # nao vale a pena pedir — pedimos so o que foi decidido.
    tipos = [t for t in geo["location_types"] if t != "frequently_in"]
    # 10/09/2026: a Meta passou a RECUSAR `recent` e `travel_in` (subcode 1870199,
    # "Remova todos os valores do campo location_types") — todo direcionamento por
    # local agora alcanca quem mora OU esteve ali recentemente, e isso nao e mais
    # configuravel. `home` sozinho ainda e aceito. Foi o que quebrou o PIN/DESTINO
    # da campanha de 08/09 ("Atualizacao necessaria", issue 1885255).
    if set(tipos) - {"home"}:
        tipos = []
    return locais, tipos


def copy_base():
    c = get(CRIATIVO_COPY, {"fields": "object_story_spec,degrees_of_freedom_spec"})
    msg = c["object_story_spec"]["video_data"]["message"]
    if FIM_ANTIGO in msg:
        msg = msg.replace(FIM_ANTIGO, FIM_NOVO)
    else:
        print("AVISO: a ultima linha esperada mudou no criativo modelo — confira a copy.")
    dof = c.get("degrees_of_freedom_spec", {}).get("creative_features_spec", {})
    return msg, dof


def boas_vindas():
    vd = get(CRIATIVO_WPP, {"fields": "object_story_spec"})["object_story_spec"]
    return vd["link_data"].get("page_welcome_message")


def alvo(locais, tipos):
    geo = {"custom_locations": locais}
    if tipos:
        geo["location_types"] = tipos
    return {
        "age_min": 35,
        "age_max": 65,
        "geo_locations": geo,
        "publisher_platforms": ["instagram"],
        "excluded_custom_audiences": [{"id": IG_SEGUIDORES}],
        "targeting_automation": {"advantage_audience": 0},
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--status", default="ACTIVE", choices=["ACTIVE", "PAUSED"])
    ap.add_argument("--campanha", help="reusar uma campanha ja criada em vez de criar outra")
    ap.add_argument("--criativo", help="reusar um criativo ja criado em vez de criar outro")
    ap.add_argument("--so", help="subir so o conjunto cujo apelido casa (ex: DESTINO)")
    args = ap.parse_args()

    if not checar():
        sys.exit(1)

    msg, dof = copy_base()
    welcome = boas_vindas()
    capa = thumb(VIDEO_V2)

    mora_locais, mora_tipos = pinos(ORIGEM_MORA)
    dest_locais, dest_tipos = pinos(ORIGEM_DESTINO)

    conjuntos = [
        ("[PIN/MORA] BAIRROS ALTO PADRAO SP-RJ", mora_locais, mora_tipos, "PIN MORA"),
        ("[PIN/DESTINO] ANGRA-ILHABELA-BUZIOS-CAMPOS-PARATY", dest_locais, dest_tipos, "PIN DESTINO"),
    ]

    print()
    print("Video    :", VIDEO_V2)
    print("Capa     :", (capa or "SEM THUMB")[:90])
    print("Destino  : WhatsApp", WHATSAPP, "(CONVERSATIONS + destination_type WHATSAPP)")
    print("Opt-out de IA:", len(dof), "features lidas do criativo", CRIATIVO_COPY)
    print("Boas-vindas:", "herdado do criativo de WhatsApp" if welcome else "NENHUM — confira")
    print()
    print("Copy:")
    print("  " + msg.replace("\n", "\n  "))
    print()
    for nome, locais, tipos, _ in conjuntos:
        print("%-52s %2d pinos  location_types=%s  R$80/dia"
              % (nome, len(locais), tipos))

    if args.dry:
        print()
        print("--dry: nada criado. Criaria 1 campanha, 2 conjuntos e 2 anuncios (%s)." % args.status)
        return

    print()
    if args.campanha:
        campanha = args.campanha
        print("Reusando a campanha", campanha)
    else:
        print("Criando campanha...")
        campanha = criar_campanha(args.status)
    if not campanha:
        sys.exit(1)

    print()
    print("Criando criativo...")
    video_data = {
        "video_id": VIDEO_V2,
        "message": msg,
        "image_url": capa,
        # No CTA WHATSAPP_MESSAGE a Meta RECUSA o parametro `link` (subcode 1815630):
        # o numero vem do `promoted_object` do conjunto, nao do criativo. Melhor assim —
        # e o numero fixo dentro do spec que deu o bug de 25/08 (31 em vez do 11).
        "call_to_action": {
            "type": "WHATSAPP_MESSAGE",
            "value": {"app_destination": "WHATSAPP"},
        },
    }
    if welcome:
        video_data["page_welcome_message"] = welcome
    spec = {"page_id": PAGINA, "instagram_user_id": INSTAGRAM, "video_data": video_data}

    def criar_criativo(features):
        return post(CONTA + "/adcreatives", {
            "name": "CDV - A IA nao vai substituir isso V2 [WHATS] - 10/09/2026",
            "object_story_spec": spec,
            "degrees_of_freedom_spec": {"creative_features_spec": features},
        }, "criativo V2 WhatsApp")

    if args.criativo:
        criativo = args.criativo
        print("  --   reusando o criativo", criativo)
    else:
        criativo = criar_criativo(dof or SEM_ENHANCEMENTS_MIN)
        if not criativo and dof:
            print("       -> repetindo com o subset minimo de opt-out")
            criativo = criar_criativo(SEM_ENHANCEMENTS_MIN)
    if not criativo:
        print("Sem criativo — campanha %s ficou vazia. Nada de ad." % campanha)
        sys.exit(1)

    print()
    print("Criando conjuntos e anuncios...")
    for nome, locais, tipos, apelido in conjuntos:
        if args.so and args.so.upper() not in apelido.upper():
            print("  --   %-40s pulado (--so %s)" % (apelido, args.so))
            continue
        adset = post(CONTA + "/adsets", {
            "name": nome,
            "campaign_id": campanha,
            "daily_budget": 8000,
            "billing_event": "IMPRESSIONS",
            "optimization_goal": "CONVERSATIONS",
            "bid_strategy": "LOWEST_COST_WITHOUT_CAP",
            "destination_type": "WHATSAPP",
            "promoted_object": {"page_id": PAGINA, "whatsapp_phone_number": WHATSAPP},
            "targeting": alvo(locais, tipos),
            "status": args.status,
        }, "conjunto " + apelido)
        time.sleep(1)
        if not adset:
            continue
        post(CONTA + "/ads", {
            "name": "AD - A IA nao substitui V2 - " + apelido,
            "adset_id": adset,
            "creative": {"creative_id": criativo},
            "status": args.status,
        }, "ad " + apelido)
        time.sleep(1)

    print()
    print("Conferir a entrega e a analise em 1-2h:")
    print("  read.py ads-by-campaign --campaign %s --fields id,name,effective_status,issues_info"
          % campanha)


def criar_campanha(status):
    return post(CONTA + "/campaigns", {
        "name": "[GEO-PIN/WHATS] ALTO PADRAO SP-RJ - 10/09",
        "objective": "OUTCOME_LEADS",
        "buying_type": "AUCTION",
        "special_ad_categories": [],
        "is_adset_budget_sharing_enabled": False,   # exigido nesta conta (subcode 4834011)
        "status": status,
    }, "campanha")


if __name__ == "__main__":
    main()
