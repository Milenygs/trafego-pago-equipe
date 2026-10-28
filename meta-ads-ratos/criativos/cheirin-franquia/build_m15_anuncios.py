#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cheirin Bao MT — anuncios do conjunto novo "M | 15 - QUENTE ALTA INTENCAO" (03/10/2026).

Publico: quem abriu o formulario e nao enviou + quem viu 75% dos videos de franquia
dos anuncios. Ja viu prova; o que falta e convite e resposta a objecao. Reusa os
criativos ja criados (mesmo form, SIGN_UP, IA em OPT_OUT). Tudo PAUSED.

Uso: python build_m15_anuncios.py --ad38 <creative_id do AD38>
"""
import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

SKILL = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
API = "https://graph.facebook.com/v21.0/"
CONTA = "act_884652616778712"
ADSET = "120258142897550212"
TOKEN = [l.split("=", 1)[1].strip().strip('"') for l in open(os.path.join(SKILL, ".env"), encoding="utf-8")
         if l.strip().startswith("META_ADS_TOKEN")][0]


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
        err = json.loads(e.read().decode()).get("error", {})
        print("  ERRO %-52s %s | %s" % (oque, err.get("message"), err.get("error_user_msg")))
        sys.exit(1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ad38", required=True)
    a = ap.parse_args()
    pecas = [
        ("M15 - AD31 [FUNDADOR] franquia tira seu dinheiro", "2035662353720458"),
        ("M15 - AD38 [FUNDADOR] cadeia de ponta a ponta", a.ad38),
        ("M15 - AD30 [PROVA] multifranqueado 4 lojas", "1407684954211808"),
        ("M15 - DRE 146k", "1092194586544651"),
    ]
    for nome, cr in pecas:
        post("%s/ads" % CONTA, {"name": nome, "adset_id": ADSET, "creative": {"creative_id": cr}, "status": "PAUSED"}, nome)
        time.sleep(2)


if __name__ == "__main__":
    main()
