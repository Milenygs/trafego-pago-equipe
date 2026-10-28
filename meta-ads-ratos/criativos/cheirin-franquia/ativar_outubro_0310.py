#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cheirin Bao MT — ativacao aprovada pela Mileny em 03/10/2026 ("pode sim, por favor").
Verba diaria total continua em R$1.010 (VD02 +R$100, 04 LAL -R$100).
"""
import json
import sys
import time
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_outubro_depoimentos as b  # noqa: E402

VD02 = "120257017816020212"
LAL04 = "120256940815900212"

PAUSAR = [
    ("120257348587180212", "[PINO SP] 1 milhao varias unidades"),
    ("120257664844110212", "[PINO SP] depoimento clt"),
]
ATIVAR_ADS = [
    ("120258143483510212", "VD02 · Franqueada- raissa"),
    ("120258142884420212", "PINO SP · AD30"),
    ("120258142932050212", "PINO SP · AD38"),
    ("120258142912060212", "PINO SP · AD34 Cleber"),
    ("120258142926300212", "PINO SP · AD36"),
    ("120258142928830212", "PINO SP · AD37"),
    ("120258142884230212", "Quente · AD30"),
    ("120258142889070212", "Quente · AD31"),
]


def main():
    for i, nome in PAUSAR:
        b.post(i, {"status": "PAUSED"}, "pausado " + nome)
        time.sleep(2)
    b.post(LAL04, {"daily_budget": 10000}, "04 LAL R$200 -> R$100")
    time.sleep(2)
    ad30 = b.post("%s/ads" % b.CONTA, {"name": "AD30 [PROVA] multifranqueado 4 lojas", "adset_id": VD02,
                                       "creative": {"creative_id": "1407684954211808"}, "status": "PAUSED"},
                  "VD02 · AD30 criado (PAUSED)")
    time.sleep(2)
    ATIVAR_ADS.append((ad30, "VD02 · AD30"))
    for i, nome in ATIVAR_ADS:
        b.post(i, {"status": "ACTIVE"}, "ativado " + nome)
        time.sleep(2)
    b.post(VD02, {"status": "ACTIVE"}, "conjunto VD02 Raissa religado (R$100)")
    print(json.dumps({"vd02_ad30": ad30}))


if __name__ == "__main__":
    main()
