#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AP Ponto - resgate dos leads do formulario do aniversario (10/09/2026).

Rede de seguranca enquanto o formulario novo nao esta na integracao que leva
lead para o CV. Le os leads direto na Meta, guarda quais ja foram avisados e
manda os novos no Telegram + acumula num CSV para o time comercial.

NAO substitui a integracao - existe para que nenhum lead da campanha dos 17 anos
fique parado no painel da Meta esperando alguem lembrar de baixar.

Uso:
    python leads_aniv17.py                 le, avisa no Telegram e grava o CSV
    python leads_aniv17.py --sem-telegram  so grava o CSV (util para testar)
    python leads_aniv17.py --todos         reenvia tudo, ignorando o controle
"""
import argparse
import csv
import json
import os
import subprocess
import sys
import urllib.parse
import urllib.request

AQUI = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.abspath(os.path.join(AQUI, "..", ".."))
API = "https://graph.facebook.com/v21.0/"

FORMULARIOS = {
    "2165262060698307": "17 Anos Comprou Ganhou (Lis e Luna)",
}
CONTROLE = os.path.join(AQUI, "leads_avisados.json")
CSV_SAIDA = os.path.join(AQUI, "leads_aniv17.csv")

# ordem em que os campos saem na mensagem e no CSV
CAMPOS = ["full_name", "phone_number", "email", "empreendimento",
          "renda_familiar", "fgts"]
ROTULOS = {"full_name": "nome", "phone_number": "telefone", "email": "e-mail",
           "empreendimento": "quer conhecer", "renda_familiar": "renda", "fgts": "FGTS"}


def token():
    for linha in open(os.path.join(SKILL, ".env"), encoding="utf-8"):
        if linha.strip().startswith("META_ADS_TOKEN"):
            return linha.split("=", 1)[1].strip().strip('"')
    sys.exit("META_ADS_TOKEN nao encontrado")


TOKEN = token()


def get(path, params=None):
    p = dict(params or {})
    p["access_token"] = TOKEN
    with urllib.request.urlopen(API + path + "?" + urllib.parse.urlencode(p)) as r:
        return json.load(r)


def ler_leads(form_id):
    """Pagina todos os leads do formulario."""
    saida = []
    dados = get(form_id + "/leads", {"fields": "id,created_time,ad_id,field_data",
                                     "limit": 100})
    while True:
        saida.extend(dados.get("data", []))
        prox = dados.get("paging", {}).get("next")
        if not prox:
            return saida
        with urllib.request.urlopen(prox) as r:
            dados = json.load(r)


def achatar(lead):
    campos = {c["name"]: (c.get("values") or [""])[0] for c in lead.get("field_data", [])}
    campos["lead_id"] = lead.get("id")
    campos["created_time"] = lead.get("created_time")
    campos["ad_id"] = lead.get("ad_id")
    return campos


def avisados():
    if os.path.exists(CONTROLE):
        return set(json.load(open(CONTROLE, encoding="utf-8")))
    return set()


def gravar_avisados(ids):
    json.dump(sorted(ids), open(CONTROLE, "w", encoding="utf-8"))


def gravar_csv(linhas):
    novo = not os.path.exists(CSV_SAIDA)
    with open(CSV_SAIDA, "a", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        if novo:
            w.writerow(["formulario", "lead_id", "criado_em", "ad_id"] + CAMPOS)
        for form, c in linhas:
            w.writerow([form, c.get("lead_id"), c.get("created_time"), c.get("ad_id")]
                       + [c.get(x, "") for x in CAMPOS])


def telegram(texto):
    subprocess.run([sys.executable, os.path.join(SKILL, "scripts", "notify.py"),
                    "telegram", "--text", texto], check=False)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sem-telegram", action="store_true")
    ap.add_argument("--todos", action="store_true")
    args = ap.parse_args()

    ja = set() if args.todos else avisados()
    novos = []
    for form_id, apelido in FORMULARIOS.items():
        for lead in ler_leads(form_id):
            if lead["id"] not in ja:
                novos.append((apelido, achatar(lead)))

    if not novos:
        print("nenhum lead novo (controle tem %d)" % len(ja))
        return

    novos.sort(key=lambda x: x[1].get("created_time") or "")
    gravar_csv(novos)

    partes = ["🎁 *ANIV17* — %d lead(s) novo(s) no formulario\n" % len(novos)]
    for apelido, c in novos:
        linha = ["• " + (c.get("full_name") or "sem nome")]
        for campo in CAMPOS[1:]:
            if c.get(campo):
                linha.append("  %s: %s" % (ROTULOS[campo], c[campo]))
        linha.append("  entrou: " + (c.get("created_time") or "")[:16].replace("T", " "))
        partes.append("\n".join(linha))
    partes.append("\nCSV: %s" % CSV_SAIDA)
    texto = "\n".join(partes)

    print(texto)
    if not args.sem_telegram:
        telegram(texto)

    gravar_avisados(ja | {c["lead_id"] for _, c in novos})


if __name__ == "__main__":
    main()
