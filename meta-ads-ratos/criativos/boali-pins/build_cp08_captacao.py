#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Boali — CP 08 [FRIO] [PIN LOJAS] [FORMS] — ONDA 1. Captacao nos mesmos 9 pins.

E o fundo da tese da Mileny (09/09): quem mora perto de uma loja Boali ja conhece
a marca, entao da pra pedir o cadastro direto, sem precisar apresentar a rede.

Por que NAO esperou o publico de 75% de view do CP 07: eu tinha adiado por isso,
e estava errado. O publico de video serviria pra REFINAR o fundo; a tese em si
nao depende dele — ela e geografica, nao de retargeting. A Mileny corrigiu em
10/09 e tem razao: a proposta era video E captacao na mesma geo.

O argumento a favor esta nos numeros da CP 06, que testou o contrario (cidade
SEM loja): R$ 2.383 por 19 leads e, no cruzamento com o CRM, ZERO avanco no funil.

DIFERENCAS em relacao ao CP 07 (topo), de proposito:
  - OUTCOME_LEADS / LEAD_GENERATION / ON_AD, formulario nativo
  - **exclui Sao Paulo capital (269969)**: `primary_city_id` diz onde o CENTRO do
    pino caiu, mas o raio e um circulo e vaza divisa. Cotia (3 km), Santo Andre
    (5 km) e Sao Caetano (2 km) encostam na capital. No topo isso e barato; na
    captacao gera lead que quer abrir em praca FECHADA (35 lojas, 0 praca aberta).
  - exclui quem ja se cadastrou / ja e publico quente (mesmas listas da CP 05)
  - criativos: Rodrigo faturamento (maior taxa de avanco da conta, 21,4%) e o
    AD14 depoimento loja cheia. Os dois levam R$359.000 na copy.

Mantem do CP 07: os 9 pins e raios ja medidos, o flexible_spec da CP 06,
`advantage_audience: 0`, so Instagram, SEM Explorar, ABO com budget sharing off.

Uso:
    python build_cp08_captacao.py --dry
    python build_cp08_captacao.py          # cria tudo PAUSED
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

AQUI = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.abspath(os.path.join(AQUI, "..", ".."))
API = "https://graph.facebook.com/v21.0/"

CONTA = "act_295475086762368"
PAGE = "110751468238380"
FORM = "913523365113250"

NOME_CAMPANHA = "CP 08 - [FRIO] [PIN LOJAS] [FORMS] [ONDA 1]"

SP_CAPITAL = 269969
ESTADOS_FORA = ["BR:AC", "BR:AM", "BR:RO", "BR:RR"]

CRIATIVOS = [
    ("1025361703312632", "AD04 - RODRIGO FATURAMENTO"),
    ("1959958101342539", "AD14 - DEPOIMENTO LOJA CHEIA 691"),
]

# (rotulo, lat, lon, raio_km, primary_city_id) — medidos em 09/09, nao chutados
PINS_LOJA = [
    ("Americana Shopping",           -22.74665, -47.30676, 5, 241913),
    ("Cambui / Campinas",            -22.90170, -47.05190, 4, 247071),
    ("Shopping Colinas / SJC",       -23.20417, -45.90871, 5, 269667),
    ("Open Mall The Square / Cotia", -23.59019, -46.82505, 3, 250084),
    ("Shopping ABC / Santo Andre",   -23.66783, -46.53339, 5, 268652),
    # Mogi entrou em 10/09, depois do CP 08 ja criado. Faltava na onda 1 e e a
    # tese inteira: praca ABERTA com loja em operacao (Mogi Shopping, 4,6 km do
    # centro da praca). Raio medido no dia, amplo 30-55 Instagram:
    #   3 km = 123.200 · 5 km = 146.600 (+19%) · 8 km = 215.400 (+47%)
    # O salto do 5 pro 8 e Suzano/Poa entrando, e nenhuma das duas e praca
    # aberta — por isso para em 5. Com o flexible_spec cheio, 5 km da 70.200.
    ("Mogi Shopping / Mogi das Cruzes", -23.51578, -46.17974, 5, 260332),
]
PINS_CIDADE = [
    ("Paulinia",              -22.74105, -47.17430, 3, 263063),
    ("Santa Barbara d'Oeste", -22.75609, -47.41539, 3, 267873),
    ("Valinhos",              -22.96912, -46.99582, 3, 273506),
    ("Sao Caetano do Sul",    -23.61644, -46.56796, 2, 269009),
]

VERBA_LOJA = 5000     # R$ 50/dia
VERBA_CIDADE = 3000   # R$ 30/dia

FLEX = [
    {"interests": [{"id": i} for i in [
        "6003068349915", "6003147242240", "6003152657675", "6003254590688",
        "6003382102565", "6003384248805", "6003421670257", "6003559906449",
        "6004115167424"]]},
    {"interests": [{"id": i} for i in [
        "6003120739217", "6003325004380", "6003371567474", "6003388314512"]]},
]

EXCLUIR_PUBLICOS = [
    "120237818661500156",   # CADASTRO REALIZADO
    "120224942147330156",   # PEPA - BOALI 180DD
    "120238982678540156",   # PQ ENGAJADO RB
]


def token():
    with open(os.path.join(SKILL, ".env"), encoding="utf-8") as f:
        for linha in f:
            if linha.strip().startswith("META_ADS_TOKEN"):
                return linha.split("=", 1)[1].strip().strip('"').strip("'")
    sys.exit("META_ADS_TOKEN nao encontrado no .env")


TOKEN = token()


def post(path, params, oque):
    corpo = {k: (json.dumps(v) if isinstance(v, (dict, list)) else v)
             for k, v in params.items()}
    corpo["access_token"] = TOKEN
    dados = urllib.parse.urlencode(corpo).encode()
    try:
        with urllib.request.urlopen(urllib.request.Request(API + path, data=dados),
                                    timeout=90) as r:
            saida = json.load(r)
            print("  OK   %-50s %s" % (oque, saida.get("id")))
            return saida.get("id")
    except urllib.error.HTTPError as e:
        erro = json.loads(e.read().decode("utf-8")).get("error", {})
        print("  ERRO %-50s" % oque)
        print("       msg :", erro.get("message"))
        print("       user:", erro.get("error_user_title"), "|", erro.get("error_user_msg"))
        sys.exit(1)


def geo(pins, tipos):
    return {
        "custom_locations": [
            {"distance_unit": "kilometer", "latitude": la, "longitude": lo,
             "radius": r, "primary_city_id": cid, "region_id": 460, "country": "BR"}
            for _, la, lo, r, cid in pins
        ],
        # SEM location_types: omitido, a Meta grava sozinha ["home","recent"], que e
        # o padrao atual ("mora OU esteve recentemente"). Mandar recent/travel_in
        # por conta propria foi recusado em 10/09/2026 (aprendizados).
    }


def targeting(pins, tipos):
    return {
        "age_min": 30, "age_max": 55,
        "flexible_spec": FLEX,
        "geo_locations": geo(pins, tipos),
        # A exclusao e o que impede o vazamento do raio pra praca fechada.
        "excluded_geo_locations": {
            "cities": [{"key": str(SP_CAPITAL), "radius": 0}],
            "regions": [{"key": k} for k in ("438", "441", "457", "458")],
        },
        "excluded_custom_audiences": [{"id": a} for a in EXCLUIR_PUBLICOS],
        "targeting_automation": {"advantage_audience": 0,
                                 "individual_setting": {"geo": 0}},
        "publisher_platforms": ["instagram"],
        # SEM explore / explore_home — decisao da conta de 08/09.
        "instagram_positions": ["stream", "story", "reels", "profile_feed", "ig_search"],
        "device_platforms": ["mobile", "desktop"],
    }


CONJUNTOS = [
    ("[FRIO] [PIN LOJA] [FORMS] [ONDA 1] CAMPINAS+ABC+SJC+AMERICANA+COTIA+MOGI",
     PINS_LOJA, ["home", "recent"], VERBA_LOJA),
    ("[FRIO] [PIN CIDADE] [FORMS] [ONDA 1] SATELITES SCS+VALINHOS+PAULINIA+STABARBARA",
     PINS_CIDADE, ["home"], VERBA_CIDADE),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    args = ap.parse_args()

    print("\n%s" % NOME_CAMPANHA)
    print("  conta   :", CONTA)
    print("  objetivo: OUTCOME_LEADS · LEAD_GENERATION · ON_AD · form %s" % FORM)
    print("  exclui  : Sao Paulo capital (%d) + AC/AM/RO/RR + 3 publicos quentes"
          % SP_CAPITAL)
    print("  verba   : R$ %d + R$ %d = R$ %d/dia (ABO)"
          % (VERBA_LOJA / 100, VERBA_CIDADE / 100,
             (VERBA_LOJA + VERBA_CIDADE) / 100))
    for nome, pins, tipos, verba in CONJUNTOS:
        print("\n  %s" % nome)
        print("    location_types: %s · R$ %d/dia" % (tipos, verba / 100))
        for rot, la, lo, r, cid in pins:
            print("      %-32s %8.5f, %9.5f  %dkm  city %d" % (rot, la, lo, r, cid))
    print("\n  criativos: %s" % " · ".join(n for _, n in CRIATIVOS))
    print("  status   : PAUSED\n")

    if args.dry:
        print("  [dry] nada foi criado.\n")
        return

    campanha = post("%s/campaigns" % CONTA, {
        "name": NOME_CAMPANHA,
        "objective": "OUTCOME_LEADS",
        "status": "PAUSED",
        "special_ad_categories": [],
        "is_adset_budget_sharing_enabled": "false",
    }, "campanha")

    for nome, pins, tipos, verba in CONJUNTOS:
        adset = post("%s/adsets" % CONTA, {
            "name": nome,
            "campaign_id": campanha,
            "daily_budget": verba,
            "billing_event": "IMPRESSIONS",
            "optimization_goal": "LEAD_GENERATION",
            "bid_strategy": "LOWEST_COST_WITHOUT_CAP",
            "destination_type": "ON_AD",
            "promoted_object": {"page_id": PAGE},
            "targeting": targeting(pins, tipos),
            "status": "PAUSED",
        }, "conjunto %s" % ("LOJA" if "PIN LOJA" in nome else "CIDADE"))

        for cid, rotulo in CRIATIVOS:
            post("%s/ads" % CONTA, {
                "name": rotulo,
                "adset_id": adset,
                "creative": {"creative_id": cid},
                "status": "PAUSED",
            }, "  ad %s" % rotulo[:28])

    print("\n  Tudo PAUSED. Conferir antes de ativar.\n")


if __name__ == "__main__":
    main()
