#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cheirin Bao MKT (act_1398047248415230) - campanha de visualizacao de video (ThruPlay) com o reel do
Eduardo "Olha esse numero@meu Brasil!!!" (@schroedereduardo, media 17962265880236362, 15/10/2026 18h36).
Pedido da Mileny (15/10): "crie uma campanha de video view do perfil do Eduardo, usando publico quente -
120D, Wilton, Franquia cheirin bao e cheirin bao oficial, brasil todo, 25-55 anos, orcamento 100/dia".

Etapas (estado em estado_vv_eduardo_1510.json; rodar de novo continua de onde parou):
  1. publicos 120D "Envolvimento todos" na MKT: @cheirinbao, @cheirinbaofranquias e Wilton
  2. campanha PAUSED (ABO)
  3. conjunto PAUSED, THRUPLAY, R$100/dia, BR, 25-55, so Instagram, sem expansao
  4. criativo de parceria (identidade @cheirinbao + post do Eduardo), sem CTA, IA em OPT_OUT
  5. anuncio PAUSED
Escritas com 2s de intervalo e retry de 60/120/180s no rate limit (regra da MKT).
"""
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")

AQUI = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.abspath(os.path.join(AQUI, "..", ".."))
API = "https://graph.facebook.com/v21.0/"
CONTA = "act_1398047248415230"
PAGE = "639778989482866"
IG_CB = "17841400169946431"          # @cheirinbao (identidade do anuncio)
MEDIA_EDU = "17962265880236362"      # reel "Olha esse numero@meu Brasil!!!"
ESTADO = os.path.join(AQUI, "estado_vv_eduardo_1510.json")

# fontes ig_business (lidas das regras dos publicos existentes em 15/10)
PUBLICOS = [
    ("pub_cb", "[IG CHEIRIN BAO OFICIAL] Envolvimento todos - 120D", "934954819849986"),
    ("pub_franquias", "[IG CB FRANQUIAS] Envolvimento todos - 120D", "9317933804989351"),
    ("pub_wilton", "[IG WILTON] Envolvimento todos - 120D", "1485692271546087"),
]

NOME_CAMP = "[MKT] [THRUPLAY] Reel Eduardo - Olha esse numero | Quente 120D BR | 15-10"
NOME_CONJ = "Quente 120D (Cheirin oficial + CB Franquias + Wilton) | BR | 25-55 | IG | R$100"
NOME_AD = "AD01 - Eduardo - Olha esse numero (parceria)"

OPT_OUT = ["advantage_plus_creative", "enhance_cta", "text_optimizations", "video_auto_crop", "video_uncrop",
           "pac_relaxation", "video_filtering", "inline_comment"]


def token():
    with open(os.path.join(SKILL, ".env"), encoding="utf-8") as f:
        for linha in f:
            if linha.strip().startswith("META_ADS_TOKEN"):
                return linha.split("=", 1)[1].strip().strip('"').strip("'")


TOKEN = token()


def post(path, params, oque):
    corpo = {k: (json.dumps(v) if isinstance(v, (dict, list)) else v) for k, v in params.items()}
    corpo["access_token"] = TOKEN
    for espera in (60, 120, 180, None):
        try:
            with urllib.request.urlopen(urllib.request.Request(API + path, data=urllib.parse.urlencode(corpo).encode()),
                                        timeout=120) as r:
                i = json.load(r).get("id")
                print("  OK   %-52s %s" % (oque, i), flush=True)
                time.sleep(2)
                return i
        except urllib.error.HTTPError as e:
            err = json.loads(e.read().decode("utf-8")).get("error", {})
            limite = err.get("code") in (4, 17, 32, 613, 80004) or err.get("error_subcode") == 2446079
            if limite and espera:
                print("  rate limit em %s, esperando %ss" % (oque, espera), flush=True)
                time.sleep(espera)
                continue
            print("  ERRO %-52s %s | sub %s | %s" % (oque, err.get("message"), err.get("error_subcode"),
                                                     err.get("error_user_msg")), flush=True)
            return None


def salva(e):
    json.dump(e, open(ESTADO, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def main():
    e = json.load(open(ESTADO, encoding="utf-8")) if os.path.exists(ESTADO) else {}

    # 1. publicos
    for chave, nome, fonte in PUBLICOS:
        if e.get(chave):
            continue
        regra = {"inclusions": {"operator": "or", "rules": [{
            "event_sources": [{"type": "ig_business", "id": fonte}],
            "retention_seconds": 120 * 86400,
            "filter": {"operator": "and", "filters": [{"field": "event", "operator": "eq", "value": "ig_business_profile_all"}]},
        }]}}
        e[chave] = post(CONTA + "/customaudiences", {"name": nome, "rule": regra, "prefill": "true"}, "publico " + nome)
        salva(e)
    publicos = [e[c] for c, _, _ in PUBLICOS if e.get(c)]
    if not publicos:
        print("Nenhum publico criado: parando.")
        return

    # 2. campanha
    if not e.get("campanha"):
        e["campanha"] = post(CONTA + "/campaigns", {
            "name": NOME_CAMP, "objective": "OUTCOME_AWARENESS", "status": "PAUSED",
            "special_ad_categories": [], "buying_type": "AUCTION",
            "is_adset_budget_sharing_enabled": "false",
        }, "campanha")
        salva(e)
    if not e.get("campanha"):
        return

    # 3. conjunto
    if not e.get("conjunto"):
        targeting = {
            "age_min": 25, "age_max": 55,
            "geo_locations": {"countries": ["BR"], "location_types": ["home", "recent"]},
            "custom_audiences": [{"id": i} for i in publicos],
            "publisher_platforms": ["instagram"],
            "instagram_positions": ["stream", "story", "explore", "reels", "explore_home", "profile_feed"],
            "device_platforms": ["mobile", "desktop"],
            "targeting_relaxation_types": {"lookalike": 0, "custom_audience": 0},
            "targeting_automation": {"advantage_audience": 0, "individual_setting": {"age": 0, "gender": 0, "geo": 0}},
        }
        e["conjunto"] = post(CONTA + "/adsets", {
            "name": NOME_CONJ, "campaign_id": e["campanha"], "status": "PAUSED",
            "daily_budget": 10000, "billing_event": "IMPRESSIONS", "optimization_goal": "THRUPLAY",
            "bid_strategy": "LOWEST_COST_WITHOUT_CAP", "targeting": targeting,
        }, "conjunto")
        salva(e)
    if not e.get("conjunto"):
        return

    # 4. criativo de parceria (doc "Instagram Partnership Ads", caminho do media ID). Permissao de conta
    #    @schroedereduardo -> @cheirinbao: Approved (branded_content_ad_permissions 1553757659347961, lida em 15/10).
    #    O post e do Eduardo; o "sponsor" e a marca (na campanha de 17/09 era o inverso: post da marca, sponsor o Eduardo).
    if not e.get("criativo"):
        e["criativo"] = post(CONTA + "/adcreatives", {
            "name": "Parceria Eduardo - Olha esse numero 15-10",
            "object_id": PAGE,
            "source_instagram_media_id": MEDIA_EDU,
            "facebook_branded_content": {"sponsor_page_id": PAGE},
            "instagram_branded_content": {"sponsor_id": IG_CB},
            "branded_content": {"ad_format": 1},
            "contextual_multi_ads": {"enroll_status": "OPT_OUT"},
            "degrees_of_freedom_spec": {"creative_features_spec": {k: {"enroll_status": "OPT_OUT"} for k in OPT_OUT}},
        }, "criativo parceria")
        salva(e)
    if not e.get("criativo"):
        return

    # 5. anuncio
    if not e.get("anuncio"):
        e["anuncio"] = post(CONTA + "/ads", {
            "name": NOME_AD, "adset_id": e["conjunto"], "status": "PAUSED",
            "creative": {"creative_id": e["criativo"]},
        }, "anuncio")
        salva(e)
    print(json.dumps(e, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
