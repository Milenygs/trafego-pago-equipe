#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Boali — CP 10 FUNDO (25/09/2026, ok da Mileny: "pode criar"). Tudo PAUSED.

Campanha OUTCOME_LEADS, ABO, com 2 conjuntos:
  A) [FUNDO] [LISTA CRM]  R$30/dia · otimiza LEAD_GENERATION
     publico: lista do CRM 120251445501230156 (pipeline ativo, 256 linhas)
  B) [FUNDO] [CAPI lead_qualificado]  R$50/dia · otimiza QUALITY_LEAD
     publico: abriu o formulario e nao enviou 90d + video 75% 180d + direct IG 365d
     exclui: enviou formulario 30d e a lista do CRM (leitura separada do A)
Os dois excluem desqualificados do CRM e AC/AM/RO/RR. So Instagram, 30-55,
sem expansao de publico. Anuncios: AD04 Rodrigo faturamento, AD20 Marcos, AD19.

Uso:
    python build_cp10_fundo.py     # cria/retoma (estado em cp10_fundo.json)
"""
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, "..", "boali-depoimento"))
import build_depoimento as b  # noqa: E402

ESTADO = os.path.join(AQUI, "cp10_fundo.json")
PIXEL = "4253291668254806"
LISTA = "120251445501230156"
VIDEO75 = "120250962270470156"
DESQUALIF = "120251264895210156"
DIA = 86400

ANUNCIOS = [  # (nome, criativo)
    ("AD04 - RODRIGO FATURAMENTO", "1025361703312632"),
    ("AD20 [FRANQUEADO] [VIDEO] MARCOS BABI RUA SHOPPING CORPORATIVA", "946032804690990"),
    ("AD19 [PROVA] [VIDEO] RODRIGO FALA DO ADRIANO LOJA ENXUTA", "1511616557396520"),
]


def carrega():
    return json.load(open(ESTADO, encoding="utf-8")) if os.path.exists(ESTADO) else {}


def salva(e):
    json.dump(e, open(ESTADO, "w", encoding="utf-8"), ensure_ascii=False, indent=2)


def post(path, params, oque):
    params = {k: (json.dumps(v) if isinstance(v, (dict, list)) else v) for k, v in params.items()}
    params["access_token"] = b.TOKEN
    req = urllib.request.Request(b.API + path, data=urllib.parse.urlencode(params).encode())
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            out = json.load(r)
    except urllib.error.HTTPError as ex:
        er = json.loads(ex.read().decode()).get("error", {})
        raise RuntimeError("%s: %s %s %s | %s" % (oque, er.get("code"), er.get("error_subcode"),
                                                  er.get("error_user_title") or er.get("message"),
                                                  er.get("error_user_msg", "")))
    print("  OK   %-45s %s" % (oque, out.get("id", out)))
    return out.get("id")


def publico_regra(nome, fonte, tipo, evento, dias, oque):
    regra = {"inclusions": {"operator": "or", "rules": [{
        "event_sources": [{"id": fonte, "type": tipo}],
        "retention_seconds": dias * DIA,
        "filter": {"operator": "and", "filters": [
            {"field": "event", "operator": "eq", "value": evento}]},
    }]}}
    return post("%s/customaudiences" % b.CONTA, {"name": nome, "rule": regra,
                                                 "prefill": "true"}, oque)


def targeting(incluir, excluir):
    return {
        "age_min": 30, "age_max": 55,
        "geo_locations": {"countries": ["BR"], "location_types": ["home", "recent"]},
        "excluded_geo_locations": {"regions": [
            {"key": "438"}, {"key": "441"}, {"key": "457"}, {"key": "458"}]},
        "custom_audiences": [{"id": i} for i in incluir],
        "excluded_custom_audiences": [{"id": i} for i in excluir],
        "publisher_platforms": ["instagram"],
        "instagram_positions": ["stream", "story", "reels", "profile_feed", "ig_search"],
        "device_platforms": ["mobile", "desktop"],
        "targeting_relaxation_types": {"lookalike": 0, "custom_audience": 0},
        "targeting_automation": {"advantage_audience": 0},
    }


def main():
    e = carrega()
    print("\nPublicos novos")
    if not e.get("form_abriu"):
        e["form_abriu"] = publico_regra("FORM_ABRIU_NAO_ENVIOU_90D (Boali)", b.PAGE, "lead",
                                        "close_form", 90, "publico abriu e nao enviou 90d")
        salva(e)
    if not e.get("form_enviou"):
        e["form_enviou"] = publico_regra("FORM_ENVIOU_30D (Boali)", b.PAGE, "lead",
                                         "submit_form", 30, "publico enviou formulario 30d")
        salva(e)
    if not e.get("ig_direct"):
        e["ig_direct"] = publico_regra("IG_DIRECT_365D (Boali)", b.IG, "ig_business",
                                       "ig_user_messaged_business", 365, "publico direct IG 365d")
        salva(e)

    print("\nCampanha")
    if not e.get("campanha"):
        e["campanha"] = post("%s/campaigns" % b.CONTA, {
            "name": "CP 10 - [FUNDO] [LISTA CRM + CAPI] [FORMS]",
            "objective": "OUTCOME_LEADS",
            "special_ad_categories": [],
            "is_adset_budget_sharing_enabled": "false",
            "status": "PAUSED",
        }, "campanha CP 10")
        salva(e)

    conjuntos = {
        "A": {
            "name": "[FUNDO] [LISTA CRM PIPELINE ATIVO] [FORMS] 30-55",
            "daily_budget": "3000",
            "optimization_goal": "LEAD_GENERATION",
            "promoted_object": {"page_id": b.PAGE},
            "targeting": targeting([LISTA], [DESQUALIF]),
        },
        "B": {
            "name": "[FUNDO] [CAPI LEAD_QUALIFICADO] ABRIU FORM + VIDEO 75 + DIRECT",
            "daily_budget": "5000",
            "optimization_goal": "QUALITY_LEAD",
            "promoted_object": {"page_id": b.PAGE, "pixel_id": PIXEL,
                                "custom_event_type": "OTHER",
                                "custom_event_str": "lead_qualificado",
                                "lead_ads_form_event_source_type": "onsite_crm_single_event"},
            "targeting": targeting([e["form_abriu"], VIDEO75, e["ig_direct"]],
                                   [DESQUALIF, e["form_enviou"], LISTA]),
        },
    }
    e.setdefault("conjuntos", {})
    e.setdefault("ads", {})
    for k, c in conjuntos.items():
        print("\nConjunto %s" % k)
        if not e["conjuntos"].get(k):
            e["conjuntos"][k] = post("%s/adsets" % b.CONTA, dict(c, **{
                "campaign_id": e["campanha"],
                "billing_event": "IMPRESSIONS",
                "destination_type": "ON_AD",
                "bid_strategy": "LOWEST_COST_WITHOUT_CAP",
                "status": "PAUSED",
            }), "conjunto %s" % k)
            salva(e)
        for nome, criativo in ANUNCIOS:
            chave = "%s|%s" % (k, criativo)
            if e["ads"].get(chave):
                continue
            e["ads"][chave] = post("%s/ads" % b.CONTA, {
                "name": nome,
                "adset_id": e["conjuntos"][k],
                "creative": {"creative_id": criativo},
                "status": "PAUSED",
            }, "ad %s" % nome[:30])
            salva(e)
    print("\nEstado em", ESTADO)


if __name__ == "__main__":
    main()
