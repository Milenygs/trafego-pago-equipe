#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cheirin Bao MT — 16/10/2026 (Mileny: "pode sim").
1) AD30 e VD07 Raissa do PINO SP (reativados pela Mileny ~12h com o form antigo) -> form novo 1106977512033195,
   mesmo esquema do troca_form_tel_1610.py (criativo novo, IA OPT_OUT, troca no proprio anuncio).
2) Stories do Instagram fora dos 4 conjuntos de captacao (PINO SP, 16, VD02 Raissa, Santoro): pico de leads incoerentes
   em 16/10 desde as 05h, com 81% do gasto e 100% dos leads nos Stories. Le o targeting inteiro e devolve igual,
   so sem "story" em instagram_positions. Rever em 19/10 com o CRM.
Uso: --dry (so le e mostra) | sem flag: aplica. Estado em estado_sem_stories_1610.json.
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
import build_outubro_depoimentos as b  # noqa: E402
import troca_form_tel_1610 as t  # noqa: E402

AQUI = os.path.dirname(os.path.abspath(__file__))
ESTADO = os.path.join(AQUI, "estado_sem_stories_1610.json")
PINO = "120257337905370212"
CONJUNTOS = {PINO: "PINO SP", "120258418032850212": "✅16 QUENTE + LAL",
             "120257017816020212": "VD02 Raissa", "120256940847150212": "Santoro"}
NOMES_TROCA = ("[PINO SP] AD30", "VD07 - franqueada_raissa")


def salva(e):
    json.dump(e, open(ESTADO, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def plano():
    m = b.modelo()
    e = {"anuncios": {}, "conjuntos": {}}
    ads = t.get(PINO + "/ads", {"fields": "id,name,effective_status,creative{id}", "limit": 50}).get("data", [])
    for a in ads:
        if a["effective_status"] != "ACTIVE" or not a["name"].startswith(NOMES_TROCA):
            continue
        spec, err = t.plano_video(a["id"], a["creative"]["id"], m)
        if err == "criativo sem video_data":
            spec, err = t.plano_afs_painel(a["creative"]["id"], m)
        e["anuncios"][a["id"]] = {"rotulo": a["name"], "nome": a["name"], "conjunto": PINO,
                                  "criativo_antigo": a["creative"]["id"], "spec": spec, "erro": err}
        print("ANUNCIO %-50s | %s | %s" % (a["name"][:50], a["id"], err or "pronto"))
    for cid, rot in CONJUNTOS.items():
        d = t.get(cid, {"fields": "name,effective_status,targeting"})
        tg = d.get("targeting") or {}
        pos = tg.get("instagram_positions")
        novo = [p for p in (pos or []) if p != "story"]
        e["conjuntos"][cid] = {"rotulo": rot, "antes": pos, "depois": novo, "plataformas": tg.get("publisher_platforms"),
                               "targeting": tg, "erro": None if pos and "story" in pos else "sem 'story' explícito: %s" % pos}
        print("CONJUNTO %-18s | %s | plataformas %s | %s -> %s" % (rot, d.get("effective_status"), tg.get("publisher_platforms"), pos, novo))
        time.sleep(0.5)
    salva(e)
    return e


def aplica(e):
    t.aplica(e["anuncios"])  # 35s entre trocas no mesmo conjunto
    time.sleep(35)  # PINO SP acabou de receber escrita
    for cid, r in e["conjuntos"].items():
        if r.get("erro") or r.get("feito"):
            print("PULADO %s: %s" % (r["rotulo"], r.get("erro") or "ja feito"))
            continue
        tg = dict(r["targeting"], instagram_positions=r["depois"])
        ok = t.post(cid, {"targeting": tg}, "%s sem Stories" % r["rotulo"])
        if ok:
            r["feito"] = True
            salva(e)
        time.sleep(5)


def confere(e):
    print("\n--- conferencia")
    for cid, r in e["conjuntos"].items():
        d = t.get(cid, {"fields": "name,effective_status,targeting"})
        tg = d.get("targeting") or {}
        antes = r["targeting"]
        mudou = sorted(k for k in set(antes) | set(tg) if k != "instagram_positions" and antes.get(k) != tg.get(k))
        print("%-18s | %s | posicoes %s | outros campos mudados: %s" % (r["rotulo"], d.get("effective_status"),
                                                                      tg.get("instagram_positions"), mudou or "nenhum"))


if __name__ == "__main__":
    if "--dry" in sys.argv:
        plano()
    else:
        est = json.load(open(ESTADO, encoding="utf-8")) if os.path.exists(ESTADO) else plano()
        aplica(est)
        t.confere(est["anuncios"])
        confere(est)
