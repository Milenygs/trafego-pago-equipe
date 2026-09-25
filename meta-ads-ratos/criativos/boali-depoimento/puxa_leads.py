#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Boali — puxa TODOS os leads do formulario nativo com o anuncio de origem.

Serve pra duas coisas:
  1) tabela de juncao com o export do CRM (a chave e o `lead_id`, que o CRM guarda)
  2) leitura imediata do capital DECLARADO por criativo — sinal, nao veredito.
     Capital declarado e o que a pessoa marcou no formulario; quem qualifica de
     verdade e o comercial. Mas ja separa "criativo que atrai quem marca 300+"
     de "criativo que atrai quem marca a faixa mais baixa".

Saida: leads_boali.csv (lead_id, data, campanha, anuncio, capital, cidade, nome,
email, telefone) na mesma pasta.

Uso:
    python puxa_leads.py
    python puxa_leads.py --desde 2026-08-01
"""
import argparse
import csv
import json
import os
import sys
import urllib.parse
import urllib.request

AQUI = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.abspath(os.path.join(AQUI, "..", ".."))
API = "https://graph.facebook.com/v21.0/"

FORM = "913523365113250"
SAIDA = os.path.join(AQUI, "leads_boali.csv")

CAMPOS = ("id,created_time,ad_id,ad_name,adset_name,campaign_name,"
          "is_organic,platform,field_data")


def token():
    with open(os.path.join(SKILL, ".env"), encoding="utf-8") as f:
        for linha in f:
            if linha.strip().startswith("META_ADS_TOKEN"):
                return linha.split("=", 1)[1].strip().strip('"').strip("'")
    sys.exit("META_ADS_TOKEN nao encontrado no .env")


TOKEN = token()


def paginas(url):
    while url:
        with urllib.request.urlopen(url, timeout=90) as r:
            dados = json.load(r)
        for item in dados.get("data", []):
            yield item
        url = dados.get("paging", {}).get("next")


def campo(lead, nome):
    for f in lead.get("field_data", []):
        if f.get("name") == nome:
            vals = f.get("values") or []
            return vals[0] if vals else ""
    return ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--desde", help="AAAA-MM-DD; corta leads anteriores")
    args = ap.parse_args()

    url = (API + FORM + "/leads?" +
           urllib.parse.urlencode({"fields": CAMPOS, "limit": 200,
                                   "access_token": TOKEN}))

    linhas = []
    for lead in paginas(url):
        data = lead.get("created_time", "")[:10]
        if args.desde and data < args.desde:
            continue
        linhas.append({
            "lead_id": lead.get("id", ""),
            "data": data,
            "campanha": lead.get("campaign_name", ""),
            "anuncio": lead.get("ad_name", ""),
            "ad_id": lead.get("ad_id", ""),
            "capital": campo(lead, "capital_disponivel_para_investimento"),
            "cidade": campo(lead, "cidade_onde_quer_sua_boali"),
            "nome": campo(lead, "full_name"),
            "email": campo(lead, "email"),
            "telefone": campo(lead, "phone_number"),
            "organico": lead.get("is_organic", ""),
        })

    if not linhas:
        sys.exit("nenhum lead no periodo")

    with open(SAIDA, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(linhas[0].keys()))
        w.writeheader()
        w.writerows(linhas)

    print("%d leads -> %s" % (len(linhas), SAIDA))
    print("periodo: %s a %s" % (linhas[-1]["data"], linhas[0]["data"]))


if __name__ == "__main__":
    main()
