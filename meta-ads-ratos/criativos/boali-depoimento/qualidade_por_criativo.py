#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Boali — custo por lead QUALIFICADO por criativo.

Cruza o export do pipeline do CRM com o gasto por anuncio da Meta. O CRM ja
traz o nome do anuncio em `UTM Content` e o `Codigo do lead Meta`, entao nao
precisa casar por telefone.

A regra da casa: CPL nao decide nada num ticket de R$300 mil. Quem decide e o
comercial. Este script troca a regua de "custo por lead" para "custo por lead
que ANDOU no funil".

Etapas que contam como avanco real:
    Lead qualificado · 1a reuniao com o Daniel · COF / DRE / Minuta · Vendido
"Qualificacao com SDR" fica de fora do avanco (ainda esta sendo triado) mas
aparece na tabela.

Uso:
    python qualidade_por_criativo.py <pipeline.csv> <insights.json> [--desde AAAA-MM-DD]
"""
import argparse
import csv
import json
import sys
from collections import defaultdict
from datetime import datetime

AVANCO = {"Lead qualificado", "1ª reunião com o Daniel",
          "COF / DRE / Minuta", "Vendido"}
SDR = "Qualificação com SDR"
PERDA = "Perda"


def le_crm(caminho, desde):
    por_ad = defaultdict(lambda: {"leads": 0, "avancou": 0, "sdr": 0, "perda": 0})
    with open(caminho, encoding="utf-8-sig", newline="") as f:
        for linha in csv.DictReader(f):
            if not linha.get("Código do lead Meta"):
                continue
            ad = (linha.get("UTM Content") or "").strip()
            if not ad:
                continue
            try:
                dt = datetime.strptime(linha["Data Cadastro Lead"], "%d/%m/%Y %H:%M")
            except (KeyError, ValueError):
                continue
            if desde and dt < desde:
                continue
            etapa = (linha.get("Etapa") or "").strip()
            d = por_ad[ad]
            d["leads"] += 1
            if etapa in AVANCO:
                d["avancou"] += 1
            elif etapa == SDR:
                d["sdr"] += 1
            elif etapa == PERDA:
                d["perda"] += 1
    return por_ad


def le_gasto(caminho):
    with open(caminho, encoding="utf-8") as f:
        bruto = json.load(f)
    dados = json.loads(bruto["result"])["data"]
    gasto = defaultdict(float)
    for r in dados:
        gasto[r.get("ad_name", "").strip()] += float(r.get("spend", 0) or 0)
    return gasto


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("crm")
    ap.add_argument("insights")
    ap.add_argument("--desde", default="2026-07-15")
    ap.add_argument("--min-leads", type=int, default=5)
    args = ap.parse_args()

    desde = datetime.strptime(args.desde, "%Y-%m-%d") if args.desde else None
    crm = le_crm(args.crm, desde)
    gasto = le_gasto(args.insights)

    linhas = []
    for ad, d in crm.items():
        if d["leads"] < args.min_leads:
            continue
        g = gasto.get(ad, 0.0)
        linhas.append({
            "ad": ad,
            "gasto": g,
            "leads": d["leads"],
            "cpl": g / d["leads"] if d["leads"] else None,
            "avancou": d["avancou"],
            "sdr": d["sdr"],
            "perda": d["perda"],
            "taxa": d["avancou"] / d["leads"] * 100 if d["leads"] else 0,
            "cpq": g / d["avancou"] if d["avancou"] else None,
        })

    linhas.sort(key=lambda x: (x["cpq"] is None, x["cpq"] if x["cpq"] else 0))

    cab = ("anuncio", "gasto", "leads", "CPL", "and.", "SDR", "perda", "taxa", "custo/qualif")
    print("\n%-44s %9s %6s %8s %5s %4s %6s %7s %13s" % cab)
    print("-" * 112)
    for l in linhas:
        print("%-44s %9s %6d %8s %5d %4d %6d %6.1f%% %13s" % (
            l["ad"][:44],
            "%.0f" % l["gasto"],
            l["leads"],
            "%.0f" % l["cpl"] if l["cpl"] else "-",
            l["avancou"], l["sdr"], l["perda"], l["taxa"],
            "%.0f" % l["cpq"] if l["cpq"] else "nenhum",
        ))

    tot_g = sum(l["gasto"] for l in linhas)
    tot_l = sum(l["leads"] for l in linhas)
    tot_a = sum(l["avancou"] for l in linhas)
    print("-" * 112)
    print("%-44s %9.0f %6d %8.0f %5d %4s %6s %6.1f%% %13s" % (
        "TOTAL", tot_g, tot_l, tot_g / tot_l if tot_l else 0, tot_a, "", "",
        tot_a / tot_l * 100 if tot_l else 0,
        "%.0f" % (tot_g / tot_a) if tot_a else "-"))
    print("\nperiodo: a partir de %s · avanco = qualificado, reuniao, COF ou vendido\n"
          % args.desde)


if __name__ == "__main__":
    main()
