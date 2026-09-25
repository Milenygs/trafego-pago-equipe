#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Boali — +20% de verba na captacao de leads de 19/09 (agora) ate 21/09 (seg) 10h.
Pedido da Mileny em 19/09/2026: "aumente hoje 20% do investimento nas campanhas de
captacao de leads e deixe ate segunda as 10h" / "aumento somente na captacao".

Mecanismo: periodo de alta demanda (POST /{id}/budget_schedules). A verba base nao
muda e a Meta volta sozinha no time_end — nao depende de agendador local.
budget_value ABSOLUTE em centavos (aprendido na Cheirin, 13/09). Limite de 1
chamada a cada 30s por objeto: le, espera 35s, grava, espera 35s, rele.

Fora: Ironman e CP 01/02/03 (nao sao captacao) e CP 08 onda 1 (pausada pela Mileny).

Uso:
    python verba_fds_20pct.py            # so le os periodos existentes
    python verba_fds_20pct.py --aplicar
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
sys.path.insert(0, os.path.join(AQUI, "..", "boali-depoimento"))
import build_depoimento as base  # noqa: E402

BRT = dt.timezone(dt.timedelta(hours=-3))
FIM = int(dt.datetime(2026, 9, 21, 10, 0, tzinfo=BRT).timestamp())

# (id, nome, verba base em centavos) — lida na conta em 19/09
ALVOS = [
    ("120249949141410156", "CP 04 quente (campanha CBO)", 30000),
    ("120250111279010156", "CP 05 LAL (campanha CBO)", 18000),
    ("120251313225380156", "CP 08 PIN LOJAS CAPITAL (conjunto)", 12000),
]


def le(obj_id):
    try:
        return base.get("%s/budget_schedules" % obj_id,
                        {"fields": "id,budget_value,budget_value_type,time_start,time_end,status"})
    except urllib.error.HTTPError as e:
        return {"erro": json.loads(e.read().decode("utf-8")).get("error", {}).get("message")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--aplicar", action="store_true")
    a = ap.parse_args()

    print("Fim do periodo: %s (unix %d)" % (dt.datetime.fromtimestamp(FIM, BRT), FIM))
    print("\nANTES")
    for obj, nome, _v in ALVOS:
        print("  %s %-38s %s" % (obj, nome, le(obj)))
    if not a.aplicar:
        return

    time.sleep(35)
    # A Meta so aceita inicio em :00/:15/:30/:45 (erro "Periodo de alta demanda invalido").
    inicio = ((int(time.time()) + 300) // 900 + 1) * 900
    print("\nAPLICANDO (inicio %s)" % dt.datetime.fromtimestamp(inicio, BRT))
    for obj, nome, v in ALVOS:
        extra = int(round(v * 0.20))
        base.post("%s/budget_schedules" % obj, {
            "budget_value": extra,
            "budget_value_type": "ABSOLUTE",
            "time_start": inicio,
            "time_end": FIM,
        }, "%s +R$%.2f" % (nome, extra / 100))

    time.sleep(35)
    print("\nDEPOIS")
    for obj, nome, _v in ALVOS:
        print("  %s %-38s %s" % (obj, nome, le(obj)))


if __name__ == "__main__":
    main()
