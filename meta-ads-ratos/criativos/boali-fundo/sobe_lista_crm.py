#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Boali — publico de lista do CRM (fundo de funil), 25/09/2026.

Le o export do pipeline "Boali Ativo", normaliza e criptografa (SHA-256) e-mail,
telefone, nome e sobrenome NA MAQUINA, e sobe para um publico de lista.
Nada em texto aberto sai daqui e nada de dado pessoal e impresso.

Ficam de fora: "Aguardando pagamento" (ja fechando) e quem esta em EXCLUIR_EMAILS.

Uso:
    python sobe_lista_crm.py <caminho do csv> [--dry]
"""
import csv
import hashlib
import json
import os
import re
import sys
import unicodedata
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "boali-depoimento"))
import build_depoimento as b  # noqa: E402

NOME = "CRM_FUNDO_PIPELINE_ATIVO_25-09 (lista, sem aguardando pagamento)"
ETAPAS_FORA = {"Aguardando pagamento"}
EXCLUIR_EMAILS = {"[e-mail removido]"}  # Rodrigo Barros (provavel dono da rede)
SCHEMA = ["EMAIL", "PHONE", "FN", "LN", "COUNTRY"]


def h(v):
    return hashlib.sha256(v.encode("utf-8")).hexdigest() if v else ""


def limpa_nome(s):
    s = unicodedata.normalize("NFKD", s.lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z]", "", s)


def telefone(t):
    d = re.sub(r"\D", "", t)
    if d.startswith("00"):
        return d[2:]
    d = d.lstrip("0")
    if len(d) in (10, 11):
        return "55" + d
    return d if len(d) >= 12 else ""


def email(e):
    e = e.strip().lower()
    return e if re.match(r"^[^@\s]+@[^@\s]+\.[a-z]{2,}$", e) else ""


def linhas(caminho):
    dados, fora = [], 0
    for r in csv.DictReader(open(caminho, encoding="utf-8-sig")):
        em = email(r["Email"])
        if r["Etapa"] in ETAPAS_FORA or em in EXCLUIR_EMAILS:
            fora += 1
            continue
        partes = [p for p in re.split(r"\s+", re.sub(r"[/(|].*$", "", r["Nome"]).strip()) if p]
        fn = limpa_nome(partes[0]) if partes else ""
        ln = limpa_nome(partes[-1]) if len(partes) > 1 else ""
        tel = telefone(r["Telefone"])
        if not (em or tel):
            fora += 1
            continue
        dados.append([h(em), h(tel), h(fn), h(ln), h("br")])
    return dados, fora


def post(path, params):
    params["access_token"] = b.TOKEN
    req = urllib.request.Request(b.API + path, data=urllib.parse.urlencode(params).encode())
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit("erro: %s" % e.read().decode())


def main():
    caminho = sys.argv[1]
    dados, fora = linhas(caminho)
    print("linhas para subir: %d · fora: %d" % (len(dados), fora))
    if "--dry" in sys.argv:
        return
    aud = post("%s/customaudiences" % b.CONTA, {
        "name": NOME,
        "subtype": "CUSTOM",
        "customer_file_source": "USER_PROVIDED_ONLY",
        "description": "Pipeline Boali Ativo (lead qualificado, 1a reuniao, COF/DRE/Minuta, "
                       "ficha cadastral) exportado em 25/09/2026. SHA-256 local.",
    })["id"]
    print("publico criado:", aud)
    r = post("%s/users" % aud, {"payload": json.dumps({"schema": SCHEMA, "data": dados})})
    print("envio: recebidos %s · invalidos %s" % (r.get("num_received"), r.get("num_invalid_entries")))


if __name__ == "__main__":
    main()
