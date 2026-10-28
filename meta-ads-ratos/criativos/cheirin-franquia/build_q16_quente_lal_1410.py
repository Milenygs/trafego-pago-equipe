#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cheirin Bao MT — conjunto "16 - QUENTE + LAL" na campanha 09 (14/10/2026).

Pedido da Mileny: publicos de engajamento do IG (print) + video 50% Cheirin e Edu
+ os publicos do 04 LAL, tudo num conjunto so, com a geo da captacao.
Decisoes dela (14/10): R$130/dia; AD38 + VD03 Raissa; 04 LAL pausa quando este
for ativado. Tudo PAUSED. Video 50% do @cheirinbao entra depois (so pelo painel).

Molde: 04 LAL 120256940815900212 (otimizacao, geo, posicionamentos) e M | 15
120258142897550212 (exclusoes, inclusive os 2 publicos M, para nao disputar com ele).
Estado em estado_q16_quente_lal_1410.json (nao recria o que ja existe).
"""
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
CONTA = "act_884652616778712"
CAMPANHA = "120256940795740212"  # 09 Captacao
PAGE = "639778989482866"
ESTADO = os.path.join(AQUI, "estado_q16_quente_lal_1410.json")
NOME = "✅16 - QUENTE + LAL | IG 120D + video 50% + LAL | 30-55"

INCLUIR = [
    "120258417970600212",  # [IG CB FRANQUIAS] Engajou post - 120D
    "120258417971050212",  # [IG CB FRANQUIAS] Enviou mensagem - 120D
    "120258417971430212",  # [IG CB FRANQUIAS] Envolvimento todos - 120D
    "120258417972290212",  # [IG CB FRANQUIAS] Salvou - 120D
    "120258417973400212",  # [IG CB FRANQUIAS] Visitou - 120D
    "120258417973520212",  # [IG CHEIRIN BAO] Envolvimento todos - 120D
    "120253568067060212",  # IG_ENGAJ_EDU_180D
    "120234774548750212",  # [PIXEL] - PAGEVIEW - 180D
    "120253567902650212",  # IG_VIDEO_EDU_50%_180D
    "120234889309030212",  # [VV] - 95% (do 04 LAL)
    "120234889518910212",  # LAL COF (do 04 LAL)
    "120256487711990212",  # LAL LEAD_QUALIFICADO (do 04 LAL)
    "120257500073500212",  # LAL COMPRADORES + QUALIFICADOS (do 04 LAL)
]
EXCLUIR = [
    "120233836786710212",  # CHEIRIN BAO - FRANQUEADOS - BASE RD
    "120234070196910212",  # BASE LEADS - CHEIRIN BAO - RD
    "120256528143040212",  # CHEIRIN BAO - CRM PIPELINE 05/08
    "120248081540700212",  # BL | Leads Perdidos CRM
    "120256989043910212",  # LEAD_FORMS_90D
    "120257459142480212",  # SITE_LEADDESQUALIFICADO_90D (CAPI)
    "120258142894270212",  # M | FORM ENVIOU 90D
    "120258142893940212",  # M | FORM ABRIU E NAO ENVIOU 90D (publico do M | 15)
    "120258142894390212",  # M | VIDEO FRANQUIA ANUNCIOS 75% 180D (publico do M | 15)
]
CIDADES = ["241991", "242415", "243550", "244887", "245683", "247054", "250158", "252968", "253249", "254063",
           "255675", "256537", "256863", "256952", "260819", "261132", "267187", "267730", "270761", "272278",
           "274261", "274425", "894776"]  # as 23 do 04 LAL / Quente / M | 15
ANUNCIOS = [
    ("Q16 - AD38 [FUNDADOR] cadeia de ponta a ponta", "1791060845582908"),
    ("VD03 - franqueada_raissa", "28628709006796872"),  # criativo original (corte curto 3993), IA em OPT_OUT
]


def token():
    with open(os.path.join(SKILL, ".env"), encoding="utf-8") as f:
        for linha in f:
            if linha.strip().startswith("META_ADS_TOKEN"):
                return linha.split("=", 1)[1].strip().strip('"').strip("'")
    sys.exit("META_ADS_TOKEN nao encontrado")


TOKEN = token()


def post(path, params, oque):
    corpo = {k: (json.dumps(v) if isinstance(v, (dict, list)) else v) for k, v in params.items()}
    corpo["access_token"] = TOKEN
    try:
        with urllib.request.urlopen(urllib.request.Request(API + path, data=urllib.parse.urlencode(corpo).encode()),
                                    timeout=120) as r:
            i = json.load(r).get("id")
            print("  OK   %-52s %s" % (oque, i), flush=True)
            return i
    except urllib.error.HTTPError as e:
        err = json.loads(e.read().decode("utf-8")).get("error", {})
        print("  ERRO %-52s %s | sub %s | %s" % (oque, err.get("message"), err.get("error_subcode"),
                                                 err.get("error_user_msg")))
        sys.exit(1)


def salva(e):
    json.dump(e, open(ESTADO, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def main():
    e = json.load(open(ESTADO, encoding="utf-8")) if os.path.exists(ESTADO) else {}
    if not e.get("adset"):
        e["adset"] = post("%s/adsets" % CONTA, {
            "name": NOME,
            "campaign_id": CAMPANHA,
            "daily_budget": "13000",
            "billing_event": "IMPRESSIONS",
            "optimization_goal": "LEAD_GENERATION",
            "bid_strategy": "LOWEST_COST_WITHOUT_CAP",
            "destination_type": "ON_AD",
            "promoted_object": {"page_id": PAGE},
            "attribution_spec": [{"event_type": "CLICK_THROUGH", "window_days": 1}],
            "targeting": {
                "age_min": 30, "age_max": 55,
                "geo_locations": {"cities": [{"key": k} for k in CIDADES], "regions": [{"key": "460"}],
                                  "location_types": ["home", "recent"]},
                "custom_audiences": [{"id": i} for i in INCLUIR],
                "excluded_custom_audiences": [{"id": i} for i in EXCLUIR],
                "publisher_platforms": ["instagram"],
                "instagram_positions": ["stream", "story", "explore", "reels", "explore_home", "profile_feed"],
                "device_platforms": ["mobile", "desktop"],
                "targeting_relaxation_types": {"lookalike": 0, "custom_audience": 0},
                "targeting_automation": {"advantage_audience": 0, "individual_setting": {"geo": 0}},
            },
            "status": "PAUSED",
        }, "conjunto 16 - QUENTE + LAL")
        salva(e)
    for nome, cr in ANUNCIOS:
        if e.get(nome):
            print("  JA   %-52s %s" % (nome, e[nome]))
            continue
        time.sleep(35)  # #613: >=35s entre escritas no mesmo conjunto
        e[nome] = post("%s/ads" % CONTA, {"name": nome, "adset_id": e["adset"],
                                          "creative": {"creative_id": cr}, "status": "PAUSED"}, nome)
        salva(e)
    print(json.dumps(e, ensure_ascii=False))


if __name__ == "__main__":
    main()
