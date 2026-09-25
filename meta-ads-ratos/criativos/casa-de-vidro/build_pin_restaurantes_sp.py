#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Casa de Vidro — 3o grupo: pinos em LUGARES (hotel de luxo, restaurante, academia)
em Sao Paulo e Rio.

Pedido da Mileny, reafirmado 4 vezes: "eu queria pinar os lugares mesmo", e
depois "exatamente nos hoteis de luxo e restaurantes, academias que so quem tem
dinheiro frequenta em sp e rj". Foi o pedido original dela em 08/09, que eu
substitui por pinos de bairro na epoca. A decisao e dela.

O que eu medi e ela decidiu mesmo assim (fica aqui para quem ler depois): 8 de 8
clusters de restaurante de SP caem DENTRO dos pinos de bairro que ja rodam — o
D.O.M. fica a 60 m do centro do pino dos Jardins. Em alcance, e repetido. O valor
esta em poder LER o resultado por tipo de lugar, que o pino de bairro nao permite.

Limite importante que isso NAO resolve: a Meta nao reporta resultado por
`custom_location`. Entao este conjunto responde "pinar lugar funciona?", e nao
"qual lugar funciona?". Para a segunda pergunta seria preciso um conjunto por
tipo (3x a verba) — fica para depois, se este ganhar dos bairros.

Duas escolhas tecnicas minhas, nao pedidas:

1. `adset_schedule` em duas janelas, todos os dias: 6h-9h e 18h-24h. Sem isso,
   um circulo de 1 km sobre o D.O.M. as 13h e o predio comercial do lado, nao o
   restaurante. A janela cobre os 3 tipos (jantar, academia de manha e de fim de
   tarde, hospede no hotel) e corta o bloco 9h-18h, que e a maior contaminacao.
   Exige `lifetime_budget` + `end_time` + `pacing_type: ["day_parting"]`.
   Para soltar 24h: tirar `adset_schedule`/`pacing_type` e usar daily_budget.

2. `location_types` omitido. A Meta recusa `recent`/`travel_in` desde 10/09
   (subcode 1870199) e o default virou "mora OU esteve recentemente" — que por
   sorte e exatamente o que um pino de lugar precisa.

Sobre pinos que se sobrepoem (Leblon tem 5 dentro de 1 km): dentro do MESMO
conjunto isso nao e problema — a Meta soma os `custom_locations` numa uniao, nao
compete entre eles. Competicao so haveria entre CONJUNTOS diferentes.

Coordenadas por endereco/quadra, nao pela porta. Com raio de 1 km, erro de
200-300 m nao tira o lugar de dentro do circulo.

ATENCAO: no painel a Meta mostra so latitude/longitude/raio — ela NAO guarda o
nome do lugar. O mapa nome->coordenada vive aqui e no documento do cliente.

Uso:
    python build_pin_restaurantes_sp.py --dry
    python build_pin_restaurantes_sp.py
"""
import argparse
import datetime as dt
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
CRIATIVO = "1066794959461074"          # V3, o mesmo dos outros 2 grupos

VERBA_TOTAL = 70000                    # R$ 700 em 14 dias (~R$50/dia), so nas janelas
DIAS = 14

# 6h-9h e 18h-24h (minutos do dia), todos os dias. 0=domingo ... 6=sabado.
TODOS_OS_DIAS = [0, 1, 2, 3, 4, 5, 6]
JANELAS = [
    {"start_minute": 360,  "end_minute": 540,  "days": TODOS_OS_DIAS},   # 06h-09h
    {"start_minute": 1080, "end_minute": 1440, "days": TODOS_OS_DIAS},   # 18h-24h
]

# (tipo, nome, bairro, cidade, lat, lon) — raio de 1 km, o minimo que a Meta aceita.
LUGARES = [
    # ---------------- SAO PAULO · restaurantes ----------------
    ("rest", "D.O.M.",                 "Jardins",            "SP", -23.5600, -46.6680),
    ("rest", "Fasano",                 "Jardins",            "SP", -23.5635, -46.6690),
    ("rest", "Rodeio",                  "Jardins",            "SP", -23.5640, -46.6660),
    ("rest", "Figueira Rubaiyat",       "Jardins",            "SP", -23.5655, -46.6650),
    ("rest", "Vento Haragano",          "Jardins",            "SP", -23.5675, -46.6745),
    ("rest", "Mani",                    "Jardim Paulistano",  "SP", -23.5742, -46.6822),
    ("rest", "Evvai",                   "Jardim Paulistano",  "SP", -23.5735, -46.6820),
    ("rest", "Jun Sakamoto",            "Pinheiros",          "SP", -23.5650, -46.6880),
    ("rest", "Nelita",                  "Pinheiros",          "SP", -23.5625, -46.6900),
    ("rest", "Tuju",                    "Vila Madalena",      "SP", -23.5565, -46.6890),
    ("rest", "Ryo Gastronomia",         "Itaim",              "SP", -23.5870, -46.6760),
    ("rest", "Varanda Grill",           "Itaim",              "SP", -23.5790, -46.6700),
    ("rest", "Parigi",                  "Itaim",              "SP", -23.5790, -46.6790),
    ("rest", "Kinoshita",               "Vila Nova Conceicao","SP", -23.5905, -46.6700),
    ("rest", "A Casa do Porco",         "Centro",             "SP", -23.5445, -46.6415),
    # ---------------- SAO PAULO · hoteis ----------------
    ("hotel", "Rosewood / Matarazzo",   "Bela Vista",         "SP", -23.5580, -46.6470),
    ("hotel", "Palacio Tangara",        "Panamby",            "SP", -23.6230, -46.7250),
    ("hotel", "Emiliano",               "Jardins",            "SP", -23.5615, -46.6720),
    ("hotel", "Hotel Unique",           "Jardim Paulista",    "SP", -23.5730, -46.6580),
    ("hotel", "Tivoli Mofarrej",        "Jardins",            "SP", -23.5680, -46.6560),
    ("hotel", "JW Marriott",            "Cidade Jardim",      "SP", -23.6010, -46.6960),
    # ---------------- SAO PAULO · academias ----------------
    ("gym",  "Les Cinq Gym",            "Jardins",            "SP", -23.5650, -46.6700),
    ("gym",  "Runner",                  "Itaim",              "SP", -23.5850, -46.6800),
    ("gym",  "Competition",             "Itaim",              "SP", -23.5880, -46.6830),
    ("gym",  "Cia Athletica Morumbi",   "Morumbi",            "SP", -23.6230, -46.6990),
    # ---------------- RIO · restaurantes ----------------
    ("rest", "Lasai",                   "Humaita",            "RJ", -22.9560, -43.1960),
    ("rest", "Oteque",                  "Botafogo",           "RJ", -22.9530, -43.1830),
    ("rest", "Oro",                     "Leblon",             "RJ", -22.9840, -43.2230),
    ("rest", "Antiquarius",             "Leblon",             "RJ", -22.9830, -43.2200),
    ("rest", "Sushi Leblon",            "Leblon",             "RJ", -22.9840, -43.2220),
    ("rest", "Gero",                    "Ipanema",            "RJ", -22.9840, -43.2060),
    ("rest", "Satyricon",               "Ipanema",            "RJ", -22.9845, -43.2030),
    ("rest", "Aprazivel",               "Santa Teresa",       "RJ", -22.9310, -43.1880),
    # ---------------- RIO · hoteis ----------------
    ("hotel", "Copacabana Palace",      "Copacabana",         "RJ", -22.9680, -43.1790),
    ("hotel", "Fasano Rio",             "Ipanema",            "RJ", -22.9855, -43.2010),
    ("hotel", "Emiliano Rio",           "Copacabana",         "RJ", -22.9740, -43.1830),
    ("hotel", "Sheraton Grand",         "Vidigal / Leblon",   "RJ", -22.9930, -43.2410),
    ("hotel", "Hotel Nacional",         "Sao Conrado",        "RJ", -23.0010, -43.2780),
    ("hotel", "Grand Hyatt",            "Barra da Tijuca",    "RJ", -23.0090, -43.3180),
    # ---------------- RIO · academias ----------------
    ("gym",  "Bodytech Leblon",         "Leblon",             "RJ", -22.9845, -43.2215),
    ("gym",  "Formula Academia",        "Leblon",             "RJ", -22.9835, -43.2230),
    ("gym",  "Bodytech Ipanema",        "Ipanema",            "RJ", -22.9835, -43.2050),
    ("gym",  "Bodytech Botafogo",       "Botafogo",           "RJ", -22.9520, -43.1810),
]

ROTULO = {"rest": "restaurante", "hotel": "hotel", "gym": "academia"}


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
    ap.add_argument("--status", default="ACTIVE", choices=["ACTIVE", "PAUSED"])
    args = ap.parse_args()

    conta = get(CONTA, {"fields": "name,account_status"})
    print("Conta  :", conta.get("name"), "| status", conta.get("account_status"))
    if conta.get("account_status") != 1:
        sys.exit("Conta fora do status 1 — a Meta recusa escrita de criativo/ad.")

    fim = dt.datetime.now().astimezone() + dt.timedelta(days=DIAS)

    locais = [{"latitude": la, "longitude": lo, "radius": 1,
               "distance_unit": "kilometer", "country": "BR"}
              for _, _, _, _, la, lo in LUGARES]

    alvo = {
        "age_min": 35,
        "age_max": 65,
        "geo_locations": {"custom_locations": locais},   # sem location_types (ver docstring)
        "publisher_platforms": ["instagram"],
        "excluded_custom_audiences": [{"id": IG_SEGUIDORES}],
        "targeting_automation": {"advantage_audience": 0},
    }

    print()
    print("%-12s %-24s %-20s %-3s %s"
          % ("Tipo", "Lugar", "Bairro", "UF", "coordenada (raio 1 km)"))
    print("-" * 88)
    for tipo, nome, bairro, uf, la, lo in LUGARES:
        print("%-12s %-24s %-20s %-3s %8.4f, %8.4f"
              % (ROTULO[tipo], nome, bairro, uf, la, lo))
    print("-" * 88)

    for uf in ("SP", "RJ"):
        linha = ["%s %d" % (ROTULO[t], sum(1 for x in LUGARES if x[0] == t and x[3] == uf))
                 for t in ("hotel", "rest", "gym")]
        print("%s: %s  (total %d)"
              % (uf, " · ".join(linha), sum(1 for x in LUGARES if x[3] == uf)))
    print("TOTAL: %d pinos de 1 km" % len(LUGARES))
    print()
    print("Verba  : R$ %.2f total em %d dias (~R$ %.2f/dia), so nas janelas"
          % (VERBA_TOTAL / 100, DIAS, VERBA_TOTAL / 100 / DIAS))
    print("Janelas: 6h-9h e 18h-24h, todos os dias (day_parting, ~9h/dia)")
    print("Fim    :", fim.strftime("%d/%m/%Y %H:%M"))
    print("Destino: WhatsApp", WHATSAPP, "| criativo", CRIATIVO, "(V3)")

    if args.dry:
        print()
        print("--dry: nada criado. Criaria 1 conjunto + 1 anuncio (%s)." % args.status)
        return

    print()
    print("Criando o conjunto...")
    adset = post(CONTA + "/adsets", {
        "name": "[PIN/LUGARES] HOTEL-RESTAURANTE-ACADEMIA SP-RJ",
        "campaign_id": CAMPANHA,
        "lifetime_budget": VERBA_TOTAL,
        "end_time": fim.isoformat(timespec="seconds"),
        "billing_event": "IMPRESSIONS",
        "optimization_goal": "CONVERSATIONS",
        "bid_strategy": "LOWEST_COST_WITHOUT_CAP",
        "destination_type": "WHATSAPP",
        "promoted_object": {"page_id": PAGINA, "whatsapp_phone_number": WHATSAPP},
        "targeting": alvo,
        "adset_schedule": JANELAS,
        "pacing_type": ["day_parting"],
        "status": args.status,
    }, "conjunto lugares")
    if not adset:
        sys.exit(1)

    time.sleep(1)
    print()
    print("Criando o anuncio...")
    post(CONTA + "/ads", {
        "name": "AD - A IA nao substitui V3 - PIN LUGARES",
        "adset_id": adset,
        "creative": {"creative_id": CRIATIVO},
        "status": args.status,
    }, "ad lugares")

    print()
    print("Conferir (os pinos voltam como coordenada, sem nome):")
    print("  read.py adset --id %s --fields name,targeting,adset_schedule,pacing_type" % adset)


if __name__ == "__main__":
    main()
