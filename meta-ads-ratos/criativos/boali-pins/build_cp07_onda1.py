#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Boali — CP 07 [FRIO] [PIN] [VIDEO_VIEW_THRUPLAY] — ONDA 1.

Topo do Funil Espiral para a hipotese da Mileny (09/09/2026): quem ja consumiu
Boali nao tem a objecao "nao conheco a marca", entao vale falar de franquia com
quem circula perto das lojas. Este script cria SO o topo (video). O fundo
(CP 08, captacao) so entra depois de 7-10 dias, quando o custom audience de
75% de visualizacao tiver base — ligar os dois juntos deixa o CP 08 sem publico
pra colher e ele cai no publico amplo do pin, que e o que a CP 06 ja faz.

DOIS conjuntos, porque `location_types` e um campo unico por conjunto e os dois
publicos tem relacao diferente com a marca:
  A) PIN LOJA    — home+recent, quem mora OU circula perto de loja que existe
  B) PIN CIDADE  — home, morador da praca satelite (pode nunca ter visto a loja)

Raios medidos em 09/09 via delivery_estimate, nao chutados. Tres foram corrigidos
depois da medicao:
  Cotia   5km -> 3km  (a 4km o alcance salta de 59.900 p/ 256.600: atravessa pra
                       Sao Paulo capital, que e praca FECHADA)
  Valinhos 4km -> 3km (a 4km salta de 48.600 p/ 197.100: compra Campinas)
  S.Caetano 3km -> 2km (a 3km ja da 1,00x a populacao do municipio; 15,3 km2 de area)
  Sta Barbara 5km -> 3km (5km da o mesmo alcance que 3km — raio maior sem ganho)

Nao repete os erros da campanha [ALCANCE][GEO][LOJAS BOALI][CIDADES E RAIOS]
(120248902105800156), que testou isso em jun-ago e gastou so R$39,80:
  - la tinha advantage_audience=1 (IA ligada); aqui vai 0
  - la nao tinha flexible_spec (zero filtro de publico); aqui herda o da CP 06
  - la otimizava REACH; aqui THRUPLAY, que e o que enche o custom audience
  - la varios pins caiam em Sao Paulo capital (praca FECHADA); aqui nenhum

Uso:
    python build_cp07_onda1.py --dry    # so mostra o que faria
    python build_cp07_onda1.py          # cria tudo PAUSED
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
ADSET_MODELO = "120250849139750156"       # CP 06 [SUDESTE] — molde de publico

# Criativos de video que ja rodam no CP 01 (frio, THRUPLAY).
CRIATIVOS = [
    ("1381773346831976", "00 - DEPOIMENTO 2a UNIDADE"),
    ("1929936107967079", "00 - Pati na BOALI RUN"),
]

NOME_CAMPANHA = "CP 07 - [FRIO] [PIN LOJAS] [VIDEO_VIEW_THRUPLAY] [ONDA 1]"

# (rotulo, lat, lon, raio_km)
PINS_LOJA = [
    ("Cambui / Campinas",        -22.90170, -47.05190, 4),
    ("Shopping ABC / St. Andre", -23.66783, -46.53339, 5),
    ("Shopping Colinas / SJC",   -23.20417, -45.90871, 5),
    ("Americana Shopping",       -22.74665, -47.30676, 5),
    ("Open Mall The Square / Cotia", -23.59019, -46.82505, 3),
]
PINS_CIDADE = [
    ("Sao Caetano do Sul",   -23.61644, -46.56796, 2),
    ("Valinhos",             -22.96912, -46.99582, 3),
    ("Paulinia",             -22.74105, -47.17430, 3),
    ("Santa Barbara d'Oeste", -22.75609, -47.41539, 3),
]

VERBA_LOJA = 5000      # centavos = R$50/dia
VERBA_CIDADE = 3000    # centavos = R$30/dia
# ABO e nao CBO de proposito: com CBO a Meta jogaria quase tudo no conjunto de
# loja (publico ~450 mil contra ~115 mil do satelite) e as pracas satelite —
# que sao justamente as que nunca rodaram — continuariam sem entrega.


def token():
    with open(os.path.join(SKILL, ".env"), encoding="utf-8") as f:
        for linha in f:
            if linha.strip().startswith("META_ADS_TOKEN"):
                return linha.split("=", 1)[1].strip().strip('"').strip("'")
    sys.exit("META_ADS_TOKEN nao encontrado no .env")


TOKEN = token()


def get(path, params):
    params = dict(params)
    params["access_token"] = TOKEN
    with urllib.request.urlopen(API + path + "?" + urllib.parse.urlencode(params),
                                timeout=60) as r:
        return json.load(r)


def post(path, params, oque):
    corpo = {k: (json.dumps(v) if isinstance(v, (dict, list)) else v)
             for k, v in params.items()}
    corpo["access_token"] = TOKEN
    dados = urllib.parse.urlencode(corpo).encode()
    try:
        with urllib.request.urlopen(urllib.request.Request(API + path, data=dados),
                                    timeout=60) as r:
            saida = json.load(r)
            print("  OK   %-46s %s" % (oque, saida.get("id")))
            return saida.get("id")
    except urllib.error.HTTPError as e:
        erro = json.loads(e.read().decode("utf-8")).get("error", {})
        print("  ERRO %-46s" % oque)
        print("       msg :", erro.get("message"))
        print("       user:", erro.get("error_user_title"), "|", erro.get("error_user_msg"))
        print("       sub :", erro.get("error_subcode"))
        return None


def checar_conta():
    c = get(CONTA, {"fields": "name,account_status,balance,disable_reason"})
    print("Conta  :", c.get("name"), "| status", c.get("account_status"), "(1=ativa)")
    if c.get("account_status") != 1:
        print("BLOQUEADO: conta fora do status 1, a Meta recusa criacao.")
        return False
    return True


def publico_base():
    """So o que define publico no conjunto da CP 06 que ja roda.

    Whitelist e nao copia do dict inteiro: arrastar o targeting completo traz
    campos que a API recusa na criacao (ex: age_range junto de
    advantage_audience=0, subcode 1487079 — aprendizado de 19/07).
    """
    tm = get(ADSET_MODELO, {"fields": "targeting"})["targeting"]
    alvo = {
        "age_min": tm["age_min"],
        "age_max": tm["age_max"],
        "flexible_spec": tm["flexible_spec"],
        # advantage_audience 0 e geo 0: sem otimizacao de IA e sem expansao
        # automatica de geo — a expansao de geo destruiria o pin, que e o
        # ponto inteiro desta campanha.
        "targeting_automation": {"advantage_audience": 0,
                                 "individual_setting": {"geo": 0}},
    }
    for campo in ("publisher_platforms", "instagram_positions", "device_platforms"):
        if tm.get(campo):
            alvo[campo] = tm[campo]
    return alvo


def geo(pins, tipos):
    return {
        "custom_locations": [
            {"latitude": la, "longitude": lo, "radius": r,
             "distance_unit": "kilometer"}
            for _, la, lo, r in pins
        ],
        # SEM location_types desde 11/09/2026 — ver build_cp08_captacao.py.
    }


def criar_adset(campanha, nome, alvo, verba, dry):
    if dry:
        print("  (dry) adset", nome, "| R$%.0f/dia | %d pins"
              % (verba / 100, len(alvo["geo_locations"]["custom_locations"])))
        return None
    return post(CONTA + "/adsets", {
        "name": nome,
        "campaign_id": campanha,
        "optimization_goal": "THRUPLAY",
        "billing_event": "IMPRESSIONS",
        # ON_VIDEO e obrigatorio aqui: os criativos sao video puro (video_data
        # sem link_data). Sem isso o adset nasce destination_type UNDEFINED e a
        # criacao do AD quebra com subcode 2061015 pedindo "website URL".
        "destination_type": "ON_VIDEO",
        # explicito por causa do subcode 2490487 (aprendizado de 14/07):
        # conjunto sem bid_strategy declarado quebra na criacao.
        "bid_strategy": "LOWEST_COST_WITHOUT_CAP",
        "daily_budget": verba,
        "targeting": alvo,
        "status": "PAUSED",
    }, "adset " + nome[:40])


def criar_ads(adset, rotulo, dry):
    for cid, nome in CRIATIVOS:
        if dry:
            print("  (dry) ad", nome, "-> adset", adset)
            continue
        post(CONTA + "/ads", {
            "name": "%s | %s" % (nome, rotulo),
            "adset_id": adset,
            "creative": {"creative_id": cid},
            # Advantage+ / standard enhancements sempre OPT_OUT (preferencia
            # registrada da Mileny; o painel liga sozinho).
            "degrees_of_freedom_spec": {
                "creative_features_spec": {
                    "standard_enhancements": {"enroll_status": "OPT_OUT"}
                }
            },
            "status": "PAUSED",
        }, "ad " + nome[:40])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    args = ap.parse_args()

    if not checar_conta():
        return 1

    alvo = publico_base()
    print("Publico: idade %s-%s | %s | %d grupos no flexible_spec"
          % (alvo["age_min"], alvo["age_max"],
             ",".join(alvo.get("publisher_platforms", [])),
             len(alvo["flexible_spec"])))
    print()

    print("Campanha:", NOME_CAMPANHA)
    if args.dry:
        campanha = "(dry)"
    else:
        campanha = post(CONTA + "/campaigns", {
            "name": NOME_CAMPANHA,
            "objective": "OUTCOME_ENGAGEMENT",
            "special_ad_categories": [],
            # Obrigatorio desde 09/2026 em campanha sem orcamento de campanha
            # (subcode 4834011). False de proposito: com True os conjuntos
            # compartilham 20% da verba, e o satelite perderia para o conjunto
            # de loja, que e 4x maior — o oposto do que este ABO quer garantir.
            "is_adset_budget_sharing_enabled": "false",
            "status": "PAUSED",
        }, "campanha")
        if not campanha:
            return 1

    # A) pin de loja — home + recent
    a = dict(alvo)
    a["geo_locations"] = geo(PINS_LOJA, ["home", "recent"])
    nome_a = "[FRIO] [PIN LOJA] [ONDA 1] CAMPINAS+ABC+SJC+AMERICANA+COTIA"
    print()
    print("Conjunto A —", nome_a)
    for r, _, _, raio in PINS_LOJA:
        print("    %-32s %dkm" % (r, raio))
    adset_a = criar_adset(campanha, nome_a, a, VERBA_LOJA, args.dry)
    if adset_a:
        criar_ads(adset_a, "PIN LOJA", args.dry)

    # B) pin de cidade satelite — so home
    b = dict(alvo)
    b["geo_locations"] = geo(PINS_CIDADE, ["home"])
    nome_b = "[FRIO] [PIN CIDADE] [ONDA 1] SATELITES SCS+VALINHOS+PAULINIA+STABARBARA"
    print()
    print("Conjunto B —", nome_b)
    for r, _, _, raio in PINS_CIDADE:
        print("    %-32s %dkm" % (r, raio))
    adset_b = criar_adset(campanha, nome_b, b, VERBA_CIDADE, args.dry)
    if adset_b:
        criar_ads(adset_b, "PIN CIDADE", args.dry)

    print()
    print("Tudo PAUSED. Verba proposta: R$%.0f/dia (A R$%.0f + B R$%.0f) — confirmar antes de ativar."
          % ((VERBA_LOJA + VERBA_CIDADE) / 100, VERBA_LOJA / 100, VERBA_CIDADE / 100))
    return 0


if __name__ == "__main__":
    sys.exit(main())
