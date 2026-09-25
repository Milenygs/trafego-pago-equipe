#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Casa de Vidro Paraty - inclui "Viajantes internacionais frequentes" nos
conjuntos ativos da [GEO-PIN/WHATS] (13/09/2026).

Pedido da Mileny: nos conjuntos ativos, incluir um interesse/comportamento que
RESTRINJA o publico atual ("e tambem deve corresponder a") ligado a quem viaja
para o exterior.

Os 4 conjuntos rodam so com pino + idade (sem flexible_spec). Entao o
comportamento entra como UM grupo unico de flexible_spec = E logico com o geo.
Um grupo so nao e "direcionamento combinado" (2+ grupos, o que deu 1870250 na
Cheirin MT), entao nao cai nessa trava.

Comportamento: 6022788483583 "Viajantes internacionais frequentes" -
"Pessoas que viajaram para outros paises mais de uma vez nos ultimos 6 meses".

location_types: a Meta recusa `recent` enviado como escolha (1870199). Nos
conjuntos que leem frequently_in,home,recent o campo e OMITIDO (default
atual); no PIN/MORA, que le frequently_in,home, reenvia ["home"].

Uso:
    python add_viajante_internacional_geopin.py          # so mede, nao escreve
    python add_viajante_internacional_geopin.py --apply  # grava e rele
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
CAMPANHA = "120249402919690510"
CONJUNTOS = [
    "120249402954240510",  # [PIN/MORA]
    "120249403004740510",  # [PIN/DESTINO]
    "120249403592920510",  # [PIN/LUGARES]
    "120249403702380510",  # [PIN/LUGARES-BR]
]
COMPORTAMENTO = {"id": "6022788483583", "name": "Viajantes internacionais frequentes"}


def token():
    caminho = os.path.join(SKILL, ".env")
    for linha in open(caminho, encoding="utf-8"):
        if linha.strip().startswith("META_ADS_TOKEN"):
            return linha.split("=", 1)[1].strip().strip('"')
    sys.exit("META_ADS_TOKEN nao encontrado em " + caminho)


TOKEN = token()


def chamar(metodo, path, params=None):
    params = dict(params or {})
    params["access_token"] = TOKEN
    dados = urllib.parse.urlencode(params)
    if metodo == "GET":
        req = urllib.request.Request(API + path + "?" + dados)
    else:
        req = urllib.request.Request(API + path, data=dados.encode(), method="POST")
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        corpo = e.read().decode()
        try:
            err = json.loads(corpo).get("error", {})
        except Exception:
            err = {"message": corpo}
        return {"_erro": {
            "code": err.get("code"), "subcode": err.get("error_subcode"),
            "msg": err.get("message"), "user_title": err.get("error_user_title"),
            "user_msg": err.get("error_user_msg")}}


def limpar_targeting(t):
    """Targeting lido -> targeting enviavel, com o comportamento incluso."""
    novo = json.loads(json.dumps(t))
    geo = novo.get("geo_locations", {})
    pinos = []
    for p in geo.get("custom_locations", []):
        pinos.append({k: p[k] for k in ("latitude", "longitude", "radius", "distance_unit") if k in p})
    geo["custom_locations"] = pinos
    tipos = geo.get("location_types") or []
    if "recent" in tipos or "travel_in" in tipos:
        geo.pop("location_types", None)
    elif tipos:
        geo["location_types"] = ["home"]
    novo["geo_locations"] = geo
    novo["excluded_custom_audiences"] = [{"id": a["id"]} for a in novo.get("excluded_custom_audiences", [])]
    novo.pop("age_range", None)
    novo["flexible_spec"] = [{"behaviors": [COMPORTAMENTO]}]
    return novo


def alcance(spec):
    r = chamar("GET", CONTA + "/delivery_estimate", {
        "targeting_spec": json.dumps(spec),
        "optimization_goal": "CONVERSATIONS",
    })
    if "_erro" in r:
        return "ERRO " + json.dumps(r["_erro"], ensure_ascii=False)
    d = (r.get("data") or [{}])[0]
    lo, hi = d.get("estimate_mau_lower_bound"), d.get("estimate_mau_upper_bound")
    aviso = "  (SENTINELA, nao e medida)" if lo == 1000 and hi == 1000 else ""
    return "%s - %s%s" % (lo, hi, aviso)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    ins = chamar("GET", CAMPANHA + "/insights", {
        "level": "adset", "date_preset": "maximum",
        "fields": "adset_id,adset_name,spend,reach,impressions,frequency,cpm,actions",
    })
    por_conjunto = {}
    for linha in ins.get("data", []):
        conversas = 0
        for a in linha.get("actions", []):
            if a["action_type"] == "onsite_conversion.messaging_conversation_started_7d":
                conversas = int(a["value"])
        por_conjunto[linha["adset_id"]] = (linha, conversas)

    relatorio = []
    for cid in CONJUNTOS:
        cj = chamar("GET", cid, {"fields": "name,effective_status,targeting"})
        if "_erro" in cj:
            print(cid, "ERRO leitura", cj["_erro"])
            continue
        t = cj["targeting"]
        novo = limpar_targeting(t)
        linha, conv = por_conjunto.get(cid, ({}, 0))
        gasto = float(linha.get("spend", 0) or 0)
        item = {
            "id": cid, "nome": cj["name"], "status": cj["effective_status"],
            "pinos": len(t.get("geo_locations", {}).get("custom_locations", [])),
            "location_types_lido": t.get("geo_locations", {}).get("location_types"),
            "chaves_targeting": sorted(t.keys()),
            "tinha_flexible_spec": "flexible_spec" in t,
            "gasto": gasto, "alcance_real": linha.get("reach"), "freq": linha.get("frequency"),
            "cpm": linha.get("cpm"), "conversas": conv,
            "custo_conversa": round(gasto / conv, 2) if conv else None,
            "alcance_estimado_hoje": alcance(t),
            "alcance_estimado_com_viajante": alcance(novo),
        }
        if args.apply:
            r = chamar("POST", cid, {"targeting": json.dumps(novo)})
            item["post"] = r
            time.sleep(3)
            relido = chamar("GET", cid, {"fields": "targeting,effective_status"})
            rt = relido.get("targeting", {})
            item["relido_flexible_spec"] = rt.get("flexible_spec")
            item["relido_pinos"] = len(rt.get("geo_locations", {}).get("custom_locations", []))
            item["relido_location_types"] = rt.get("geo_locations", {}).get("location_types")
            item["relido_excluidos"] = rt.get("excluded_custom_audiences")
            item["relido_idade"] = [rt.get("age_min"), rt.get("age_max")]
            item["relido_status"] = relido.get("effective_status")
            time.sleep(2)
        relatorio.append(item)

    print(json.dumps(relatorio, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
