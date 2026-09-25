#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Boali — junta os 2 conjuntos de formulario da CP 08 num so (16/09/2026, ok da Mileny).

  fica : PIN LOJA   120251217473750156 (o que trouxe lead) — recebe os 4 pinos dos satelites,
         location_types home+recent para todos, verba R$110 (60+50), nome novo
  pausa: PIN CIDADE 120251205721260156

Por que: os dois estavam em aprendizado com R$50-60/dia e CPL > R$150 (2-3 leads/semana
cada) — separados nenhum sai do aprendizado. Os anuncios sao os mesmos nos dois, entao
nada com lead fica preso no conjunto pausado (erro da Cheirin em 15/09).

Edicao pela Graph API direta (nao pelo conector, que forca PAUSED). Targeting vai
INTEIRO (a Meta substitui, nao mescla). Estado anterior salvo em backup_*.json.

Uso:  python juntar_cp08_pinos.py --dry | python juntar_cp08_pinos.py
"""
import argparse
import json
import os
import sys
import time

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, "..", "boali-depoimento"))
import build_depoimento as b  # noqa: E402

LOJA = "120251217473750156"
CIDADE = "120251205721260156"
VERBA = 11000
NOME = ("[FRIO] [PIN LOJA+CIDADE] [FORMS] [ONDA 1] CAMPINAS+ABC+SJC+AMERICANA+COTIA+MOGI"
        "+SCS+VALINHOS+PAULINIA+STABARBARA")
CAMPOS = "name,status,effective_status,daily_budget,targeting"
PINO_OK = ("latitude", "longitude", "radius", "distance_unit", "name", "address_string")


def limpa(pinos):
    return [{k: p[k] for k in PINO_OK if k in p} for p in pinos]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()

    loja = b.get(LOJA, {"fields": CAMPOS})
    cidade = b.get(CIDADE, {"fields": CAMPOS})
    carimbo = time.strftime("%Y%m%d-%H%M%S")
    with open(os.path.join(AQUI, "backup_cp08_%s.json" % carimbo), "w", encoding="utf-8") as f:
        json.dump({"loja": loja, "cidade": cidade}, f, ensure_ascii=False, indent=2)

    t = loja["targeting"]
    geo = t["geo_locations"]
    p_loja = limpa(geo.get("custom_locations", []))
    p_cid = limpa(cidade["targeting"]["geo_locations"].get("custom_locations", []))
    geo["custom_locations"] = p_loja + p_cid
    geo["location_types"] = ["home", "recent"]
    print("pinos: loja %d + cidade %d = %d" % (len(p_loja), len(p_cid), len(geo["custom_locations"])))
    print("excluded_geo:", json.dumps(t.get("excluded_geo_locations"), ensure_ascii=False)[:200])
    print("excl_aud:", [x["id"] for x in t.get("excluded_custom_audiences", [])])
    print("verba: %s -> %s | cidade: %s" % (loja["daily_budget"], VERBA, cidade["effective_status"]))

    corpo = {"name": NOME, "daily_budget": VERBA, "targeting": t}
    val = dict(corpo, execution_options=["validate_only"])
    b.post(LOJA, val, "validate_only LOJA")
    if a.dry:
        print("[dry] nada gravado")
        return
    time.sleep(5)
    b.post(LOJA, corpo, "LOJA: pinos + verba + nome")
    time.sleep(5)
    b.post(CIDADE, {"status": "PAUSED"}, "CIDADE: PAUSED")
    time.sleep(5)

    l2 = b.get(LOJA, {"fields": CAMPOS})
    c2 = b.get(CIDADE, {"fields": "effective_status"})
    g2 = l2["targeting"]["geo_locations"]
    print("\nconferido LOJA: %s | %s | R$%s | %d pinos | %s | excl_aud %d | idade %s-%s | flex %d"
          % (l2["status"], l2["effective_status"], int(l2["daily_budget"]) / 100,
             len(g2.get("custom_locations", [])), g2.get("location_types"),
             len(l2["targeting"].get("excluded_custom_audiences", [])),
             l2["targeting"].get("age_min"), l2["targeting"].get("age_max"),
             len(l2["targeting"].get("flexible_spec", []))))
    print("primary_city_id:", [p.get("primary_city_id") for p in g2.get("custom_locations", [])])
    print("excluded_geo:", json.dumps(l2["targeting"].get("excluded_geo_locations"), ensure_ascii=False)[:200])
    print("conferido CIDADE:", c2["effective_status"])


if __name__ == "__main__":
    main()
