#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Casa de Vidro — 4o grupo: hoteis de luxo FORA de SP e RJ.

Pedido da Mileny (10/09): "e se pinar tb hoteis de luxo em outros estados?",
depois de puxar uma analise do @casasiara.br (casa de alto padrao em Prea/CE,
42,4 mil seguidores, produto "Vilas" = casa inteira com piscina privativa).

Por que este grupo e diferente do [PIN/LUGARES] de SP-RJ:

1. **E alcance novo de verdade.** Em SP os 8 clusters de restaurante caiam DENTRO
   dos pinos de bairro (D.O.M. a 60 m do centro do pino dos Jardins). Aqui nao
   existe pino nenhum: a campanha inteira so alcanca SP e RJ hoje.

2. **Roda 24h, SEM `adset_schedule`.** A janela 6h-9h/18h-24h do grupo urbano
   existe para fugir da torre comercial ao lado do restaurante nos Jardins. Em
   Itacarezinho, no Quadrado de Trancoso ou na Reserva do Ibitipoca nao tem torre
   comercial — o circulo de 2 km e o resort e o mato, de dia e de noite. Aplicar
   a janela aqui perderia alcance sem tirar contaminacao nenhuma. Por isso
   `daily_budget` simples, sem lifetime/end_time/pacing.

3. **O pino mira o circuito concorrente, nao a cidade.** Pino em hotel alcanca
   quem esta VISITANDO aquele lugar, nao o rico que mora nele. Para pegar o rico
   de BH ou Curitiba o pino seria o bairro e a academia deles, nao o hotel.

O melhor pino da lista e a propria Casa Siara, em Prea, mais a vila de
Jericoacoara: mesmo produto (casa inteira, piscina privativa, praia de alto
padrao, cafe servido na casa), outra costa. O hospede dela e o hospede daqui.
Trancoso e Itacare pela mesma razao — e a pesquisa dela confirma que a Casa Siara
circula na Matuete e na Brazilian Luxury Travel, que e exatamente esse roteiro.

SOBE PAUSADO de proposito. A campanha ja tem 3 hipoteses nao testadas rodando a
~R$210/dia e nenhum resultado lido. Ligar em 16/09, junto com a 1a leitura — ou
antes, se ela pedir.

Uso:
    python build_pin_lugares_outros_estados.py --dry
    python build_pin_lugares_outros_estados.py              # cria PAUSED
    python build_pin_lugares_outros_estados.py --status ACTIVE
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
WHATSAPP = "5511969565817"
IG_SEGUIDORES = "120244196072220510"

CAMPANHA = "120249402919690510"        # [GEO-PIN/WHATS] ALTO PADRAO SP-RJ - 10/09
CRIATIVO = "1066794959461074"          # V3, o mesmo dos outros 3 grupos
VERBA_DIA = 5000                       # R$ 50/dia

# (uf, nome, lat, lon, raio_km)
LUGARES = [
    # ---- BA · circuito Trancoso / Itacare / Praia do Forte ----
    ("BA", "Trancoso — Quadrado (Uxua, Villas)", -16.5880, -39.0940, 3),
    ("BA", "Fasano Trancoso — Itapororoca",      -16.5600, -39.0760, 2),
    ("BA", "Txai Itacare — Itacarezinho",        -14.3480, -38.9960, 2),
    ("BA", "Tivoli Ecoresort Praia do Forte",    -12.5790, -38.0010, 2),
    # ---- CE · o circuito da Casa Siara ----
    ("CE", "Prea — Casa Siara",                   -2.9070, -40.5520, 2),
    ("CE", "Jericoacoara — vila",                 -2.7960, -40.5130, 3),
    # ---- SC ----
    ("SC", "Ponta dos Ganchos",                  -27.3180, -48.5590, 2),
    ("SC", "Jurere Internacional",               -27.4370, -48.4980, 3),
    # ---- MG ----
    ("MG", "Reserva do Ibitipoca",               -21.7050, -43.8900, 3),
    ("MG", "Botanique — Camanducaia",            -22.7500, -46.1300, 3),
    # ---- RS ----
    ("RS", "Gramado — Saint Andrews / Kurotel",  -29.3820, -50.8730, 3),
    # ---- DF ----
    ("DF", "Brasilia — orla do Lago Norte",      -15.7730, -47.8700, 3),
]


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
    with urllib.request.urlopen(API + path + "?" + urllib.parse.urlencode(params)) as r:
        return json.load(r)


def post(path, params, oque):
    corpo = {k: (json.dumps(v) if isinstance(v, (dict, list)) else v)
             for k, v in params.items()}
    corpo["access_token"] = TOKEN
    dados = urllib.parse.urlencode(corpo).encode()
    try:
        with urllib.request.urlopen(urllib.request.Request(API + path, data=dados)) as r:
            saida = json.load(r)
            print("  OK   %-30s %s" % (oque, saida.get("id") or saida))
            return saida.get("id")
    except urllib.error.HTTPError as e:
        erro = json.loads(e.read().decode("utf-8")).get("error", {})
        print("  ERRO %-30s" % oque)
        print("       msg :", erro.get("message"))
        print("       user:", erro.get("error_user_title"), "|", erro.get("error_user_msg"))
        print("       sub :", erro.get("error_subcode"))
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--status", default="PAUSED", choices=["ACTIVE", "PAUSED"])
    args = ap.parse_args()

    conta = get(CONTA, {"fields": "name,account_status"})
    print("Conta  :", conta.get("name"), "| status", conta.get("account_status"))
    if conta.get("account_status") != 1:
        sys.exit("Conta fora do status 1 — a Meta recusa escrita de criativo/ad.")

    locais = [{"latitude": la, "longitude": lo, "radius": r,
               "distance_unit": "kilometer", "country": "BR"}
              for _, _, la, lo, r in LUGARES]

    alvo = {
        "age_min": 35,
        "age_max": 65,
        "geo_locations": {"custom_locations": locais},   # sem location_types
        "publisher_platforms": ["instagram"],
        "excluded_custom_audiences": [{"id": IG_SEGUIDORES}],
        "targeting_automation": {"advantage_audience": 0},
    }

    print()
    print("%-4s %-40s %-22s %s" % ("UF", "Lugar", "coordenada", "raio"))
    print("-" * 78)
    for uf, nome, la, lo, r in LUGARES:
        print("%-4s %-40s %8.4f, %8.4f   %d km" % (uf, nome, la, lo, r))
    print("-" * 78)
    ufs = sorted(set(u for u, _, _, _, _ in LUGARES))
    print("%d pinos em %d estados (%s)" % (len(LUGARES), len(ufs), ", ".join(ufs)))
    print()
    print("Verba  : R$ %.2f/dia" % (VERBA_DIA / 100))
    print("Horario: 24h, SEM day_parting (resort isolado nao tem torre comercial ao lado)")
    print("Destino: WhatsApp", WHATSAPP, "| criativo", CRIATIVO, "(V3)")
    print("Status : %s" % args.status)

    if args.dry:
        print()
        print("--dry: nada criado. Criaria 1 conjunto + 1 anuncio (%s)." % args.status)
        return

    print()
    print("Criando o conjunto...")
    adset = post(CONTA + "/adsets", {
        "name": "[PIN/LUGARES-BR] HOTEIS DE LUXO OUTROS ESTADOS",
        "campaign_id": CAMPANHA,
        "daily_budget": VERBA_DIA,
        "billing_event": "IMPRESSIONS",
        "optimization_goal": "CONVERSATIONS",
        "bid_strategy": "LOWEST_COST_WITHOUT_CAP",
        "destination_type": "WHATSAPP",
        "promoted_object": {"page_id": PAGINA, "whatsapp_phone_number": WHATSAPP},
        "targeting": alvo,
        "status": args.status,
    }, "conjunto outros estados")
    if not adset:
        sys.exit(1)

    time.sleep(1)
    print()
    print("Criando o anuncio...")
    post(CONTA + "/ads", {
        "name": "AD - A IA nao substitui V3 - PIN LUGARES BR",
        "adset_id": adset,
        "creative": {"creative_id": CRIATIVO},
        "status": args.status,
    }, "ad outros estados")

    print()
    print("Para ligar depois:")
    print("  update.py adset --id %s --status ACTIVE" % adset)
    print("  (e o ad tambem — os dois sobem PAUSED juntos)")


if __name__ == "__main__":
    main()
