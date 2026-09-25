#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cheirin Bao franquia — campanha 12 [SITE] [FRANQUEADOS] (120257321396340212).

Troca o EVENTO DE OTIMIZACAO dos 2 conjuntos:

  de  [M] LEAD/LP FRANQUEADOS  (2554956741641990)
      PageView em poscadastro.cheirinbao.com.br/franqueados/
      pixel 1113125670113540  —  ~1 disparo/dia

  para CB | LEAD FORM - LP FRANQUEADOS  (2534280440331279)
      evento lead_form em bl.cheirinbao.com.br
      pixel 2525428314626049  —  70 disparos em 14 dias (~5/dia)

Motivo: os 2 conjuntos estao em LEARNING com conversions=0. A Meta pede ~50
conversoes/semana por conjunto pra sair do aprendizado; a 1/dia nunca chega.
O poscadastro continua medindo e aparecendo no relatorio — so deixa de ser alvo.

promoted_object e IMUTAVEL depois de publicado (subcode 3260011) => conjunto novo.
promoted_object com pixel_id + custom_conversion_id juntos da subcode 1885014
=> mandar SO o custom_conversion_id (a Meta resolve o pixel sozinha).

Uso:
    python build_12_leadform.py --dry-run   # so mostra o que faria
    python build_12_leadform.py             # cria PAUSED
    python build_12_leadform.py --ativar    # cria, ativa os novos e pausa os velhos
"""
import argparse
import json
import os
import sys
import time

AQUI = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.abspath(os.path.join(AQUI, "..", ".."))
sys.path.insert(0, os.path.join(SKILL, "scripts"))

from lib import init_api  # noqa: E402
from facebook_business.adobjects.adaccount import AdAccount  # noqa: E402
from facebook_business.adobjects.adset import AdSet  # noqa: E402
from facebook_business.adobjects.ad import Ad  # noqa: E402

CONTA = "act_884652616778712"
CAMPANHA = "120257321396340212"
CONVERSAO_NOVA = "2534280440331279"      # CB | LEAD FORM - LP FRANQUEADOS

ORIGINAIS = ["120257347973560212", "120257348521850212"]

# Enhancements automaticos desligados — regra permanente da Mileny.
DOF_SPEC = {
    "creative_features_spec": {
        chave: {"enroll_status": "OPT_OUT"}
        for chave in (
            "advantage_plus_creative", "enhance_cta", "text_optimizations",
            "video_auto_crop", "video_uncrop", "pac_relaxation",
        )
    }
}


def limpar_targeting(t):
    """Normaliza o targeting lido pra um payload aceito na criacao."""
    # explore_home sozinho e recusado na criacao (subcode 2490392) — a leitura
    # de conjunto feito no painel devolve so ele, mas a API exige "explore" junto
    posicoes = list(t["instagram_positions"])
    if "explore_home" in posicoes and "explore" not in posicoes:
        posicoes.append("explore")

    limpo = {
        "age_min": t["age_min"],
        "age_max": t["age_max"],
        "publisher_platforms": t["publisher_platforms"],
        "instagram_positions": posicoes,
        "device_platforms": t["device_platforms"],
        # advantage+ audience desligado, como no original
        "targeting_automation": t.get("targeting_automation", {}),
        "targeting_relaxation_types": t.get("targeting_relaxation_types", {}),
    }

    # publicos: a leitura devolve id+name, a escrita quer so o id
    if t.get("custom_audiences"):
        limpo["custom_audiences"] = [{"id": a["id"]} for a in t["custom_audiences"]]
    if t.get("excluded_custom_audiences"):
        limpo["excluded_custom_audiences"] = [
            {"id": a["id"]} for a in t["excluded_custom_audiences"]
        ]

    # geo: so key/country por regiao (name volta na leitura e nao e aceito)
    geo = t.get("geo_locations", {})
    novo_geo = {}
    if geo.get("regions"):
        novo_geo["regions"] = [{"key": r["key"]} for r in geo["regions"]]
    if geo.get("cities"):
        novo_geo["cities"] = [
            {k: v for k, v in c.items() if k in ("key", "radius", "distance_unit")}
            for c in geo["cities"]
        ]
    # location_types NAO e copiado: omitido, a Meta aplica o padrao atual sozinha
    # (aprendizados 10/09 e 11/09/2026)
    limpo["geo_locations"] = novo_geo

    # NUNCA incluir excluded_geo_locations: nesta conta o campo gruda e volta
    # sozinho (aprendizados 12-17/08). Tambem fora: targeting_optimization
    # (removido pela Meta, subcode 1870197) e age_range (conflita com
    # advantage_audience=0, subcode 1487079).
    return limpo


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--ativar", action="store_true",
                   help="ativa os novos e pausa os antigos")
    args = p.parse_args()

    init_api()
    resultado = []

    for antigo_id in ORIGINAIS:
        antigo = AdSet(antigo_id).api_get(fields=[
            "name", "daily_budget", "billing_event", "optimization_goal",
            "destination_type", "bid_strategy", "attribution_spec", "targeting",
        ])
        d = antigo.export_all_data()
        nome_novo = f"{d['name']} | lead_form"

        params = {
            "name": nome_novo,
            "campaign_id": CAMPANHA,
            "daily_budget": d["daily_budget"],
            "billing_event": d["billing_event"],
            "optimization_goal": d["optimization_goal"],
            "destination_type": d["destination_type"],
            "bid_strategy": d["bid_strategy"],
            "attribution_spec": d["attribution_spec"],
            "targeting": limpar_targeting(d["targeting"]),
            # so o custom_conversion_id — com pixel_id junto da subcode 1885014
            "promoted_object": {"custom_conversion_id": CONVERSAO_NOVA},
            "status": "PAUSED",
        }

        print(f"\n=== {nome_novo}")
        if args.dry_run:
            print(json.dumps(params, indent=1, ensure_ascii=False))
            continue

        novo = AdAccount(CONTA).create_ad_set(params=params)
        novo_id = novo["id"]
        print(f"  conjunto novo = {novo_id}  (R$ {int(d['daily_budget'])/100:.2f}/dia)")
        time.sleep(2)

        # replica os anuncios ativos, reaproveitando os MESMOS criativos
        # (mantem a prova social e as url_tags por franqueado)
        ads_novos = []
        for a in AdSet(antigo_id).get_ads(
                fields=["name", "creative", "effective_status"], params={"limit": 50}):
            ad = a.export_all_data()
            if ad["effective_status"] != "ACTIVE":
                continue
            novo_ad = AdAccount(CONTA).create_ad(params={
                "name": ad["name"],
                "adset_id": novo_id,
                "creative": {"creative_id": ad["creative"]["id"]},
                "status": "PAUSED",
                "degrees_of_freedom_spec": DOF_SPEC,
            })
            print(f"     ad {novo_ad['id']}  {ad['name']}  "
                  f"(creative {ad['creative']['id']})")
            ads_novos.append(novo_ad["id"])
            time.sleep(2)

        resultado.append({"antigo": antigo_id, "novo": novo_id, "ads": ads_novos})

    if args.dry_run:
        return

    print("\n" + json.dumps(resultado, indent=1, ensure_ascii=False))

    if args.ativar:
        print("\n--- ativando os novos e pausando os antigos")
        for r in resultado:
            AdSet(r["novo"]).api_update(params={"status": "ACTIVE"})
            time.sleep(2)
            for ad_id in r["ads"]:
                Ad(ad_id).api_update(params={"status": "ACTIVE"})
                time.sleep(2)
            AdSet(r["antigo"]).api_update(params={"status": "PAUSED"})
            time.sleep(2)
            print(f"  {r['novo']} ATIVO  |  {r['antigo']} pausado")

        # a conta ja teve excluded_geo_locations voltando sozinho ao entrar
        # em veiculacao — conferir depois de ativar
        time.sleep(30)
        for r in resultado:
            s = AdSet(r["novo"]).api_get(fields=["name", "targeting"])
            excl = s["targeting"].get("excluded_geo_locations")
            print(f"  excluded_geo em {s['name'][:40]}: "
                  f"{'LIMPO' if not excl else excl}")


if __name__ == "__main__":
    main()
