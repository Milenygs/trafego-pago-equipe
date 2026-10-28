#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cheirin Bao MT — otimizacoes de 05/10/2026 (ok da Mileny: "pode fazer as alteracoes entao").

1. M | 15 QUENTE ALTA INTENCAO: expansao de publico desligada (custom_audience 1 -> 0). Ligou sozinha quando a Mileny
   editou os publicos pelo painel em 04/10; a regra da conta e 0/0.
2. Santoro R$110 -> R$130 e PINO SP R$240 -> R$220 (total igual, R$1.170): Santoro e o unico conjunto que avancou no CRM
   de 02 a 04/10 (1 lead_qualificado + 4 confirmado capital); PINO SP R$186 por lead e 0 qualificado.
3. 01 Quente: expansao desligada (lookalike/custom_audience 1 -> 0) e exclusao dos 2 publicos M do M | 15, num reinicio so.
   No 04 LAL a mesma troca (02/10) manteve o volume, baixou o CPL (R$80 -> R$72) e zerou os desqualificados.
Em todos: targeting_automation com advantage_audience 0 e geo 0 (regra da conta). O targeting vai completo (a API troca
o objeto inteiro); se a Meta recusar ig_search em video com formulario (2446429), sai so o ig_search.
"""
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_outubro_depoimentos as b  # noqa: E402

M15 = "120258142897550212"
QUENTE = "120256940806870212"
SANTORO = "120256940847150212"
PINO = "120257337905370212"
M_FORM = "120258142893940212"    # M | FORM ABRIU E NAO ENVIOU 90D
M_VIDEO = "120258142894390212"   # M | VIDEO FRANQUIA ANUNCIOS 75% 180D


def post(path, params):
    corpo = {k: (json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v) for k, v in params.items()}
    corpo["access_token"] = b.TOKEN
    req = urllib.request.Request(b.API + path, data=urllib.parse.urlencode(corpo).encode())
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return True, json.load(r)
    except urllib.error.HTTPError as e:
        return False, json.loads(e.read().decode("utf-8")).get("error", {})


def tenta(path, params, oque):
    for _ in range(3):
        ok, r = post(path, params)
        if ok:
            print("  OK   %s" % oque)
            return True
        if r.get("code") in (17, 613) or r.get("error_subcode") == 2446079:
            print("  ... limite da Meta, esperando 60s (%s)" % oque)
            time.sleep(60)
            continue
        if r.get("error_subcode") == 2446429 and "targeting" in params:
            t = params["targeting"]
            t["instagram_positions"] = [p for p in t.get("instagram_positions", []) if p != "ig_search"]
            print("  ... sem ig_search (2446429), tentando de novo")
            continue
        print("  ERRO %s: %s | %s | %s" % (oque, r.get("message"), r.get("error_user_title"), r.get("error_user_msg")))
        return False
    return False


def resumo(sid):
    d = b.get(sid, {"fields": "name,effective_status,daily_budget,targeting"})
    t = d.get("targeting", {})
    return {"nome": d["name"][:50], "status": d["effective_status"], "verba": int(d.get("daily_budget") or 0) / 100,
            "relax": t.get("targeting_relaxation_types"), "auto": t.get("targeting_automation"),
            "exclui": [a.get("name") for a in t.get("excluded_custom_audiences", [])],
            "ig_search": "ig_search" in t.get("instagram_positions", [])}


def sem_expansao(t):
    t["targeting_relaxation_types"] = {"lookalike": 0, "custom_audience": 0}
    auto = t.get("targeting_automation") or {}
    auto["advantage_audience"] = 0
    auto.setdefault("individual_setting", {})["geo"] = 0
    t["targeting_automation"] = auto


def main():
    antes = {k: resumo(v) for k, v in (("M15", M15), ("Quente", QUENTE), ("Santoro", SANTORO), ("PINO SP", PINO))}
    print("ANTES:")
    for k, v in antes.items():
        print("  %-8s %s" % (k, json.dumps(v, ensure_ascii=False)))

    print("\nAPLICANDO:")
    t = b.get(M15, {"fields": "targeting"})["targeting"]
    sem_expansao(t)
    tenta(M15, {"targeting": t}, "1. M | 15 sem expansao")

    tenta(SANTORO, {"daily_budget": 13000}, "2. Santoro R$110 -> R$130")
    tenta(PINO, {"daily_budget": 22000}, "2. PINO SP R$240 -> R$220")

    t = b.get(QUENTE, {"fields": "targeting"})["targeting"]
    sem_expansao(t)
    exc = t.setdefault("excluded_custom_audiences", [])
    for aid in (M_FORM, M_VIDEO):
        if aid not in {a["id"] for a in exc}:
            exc.append({"id": aid})
    tenta(QUENTE, {"targeting": t}, "3. Quente sem expansao + exclui os 2 publicos M")

    print("\nDEPOIS:")
    for k, v in (("M15", M15), ("Quente", QUENTE), ("Santoro", SANTORO), ("PINO SP", PINO)):
        print("  %-8s %s" % (k, json.dumps(resumo(v), ensure_ascii=False)))


if __name__ == "__main__":
    main()
