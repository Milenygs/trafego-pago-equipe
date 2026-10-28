"""Belo 09/10/2026 (segunda parte) - Mileny: "nao pausa o Interesse de uma vez, diminui bem; conferimos amanha".

Interesse volta ATIVO com R$70 (era R$250), sem os UGC do Leo. LAL CAPI fica em R$80 (o aumento para R$150 fica para
a leitura de 10/10). UGC do Leo pausados no LAL, em Servidores e no Interesse. Total ativo: R$1.300/dia.
"""
import json
import os
import sys
import time
from pathlib import Path

import requests

sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
env = (Path(os.path.expanduser("~/OneDrive/.claude/skills/meta-ads-ratos")) / ".env").read_text(encoding="utf-8")
TOKEN = [l.split("=", 1)[1].strip().strip('"') for l in env.splitlines() if l.startswith("META_ADS_TOKEN")][0]
G = "https://graph.facebook.com/v23.0/"
INTERESSE = "120245790403680358"
PAUSAR_ANUNCIOS = {
    "120245790442800358": "LAL · VID UGC Leo v1",
    "120245916003780358": "LAL · VID UGC Leo Chegou v1",
    "120246003835410358": "Servidores · VID UGC Leo v1",
    "120246003892090358": "Servidores · VID UGC Leo Chegou v1",
    "120245790442160358": "Interesse · VID UGC Leo v1",
    "120245913879990358": "Interesse · VID UGC Leo Chegou v1",
}


def post(path, data):
    data["access_token"] = TOKEN
    r = requests.post(G + path, data=data, timeout=120).json()
    print("  ", path, "->", "ERRO " + json.dumps(r["error"], ensure_ascii=False)[:200] if "error" in r else "ok")
    return r


for i, nome in PAUSAR_ANUNCIOS.items():
    print("pausar", nome)
    post(i, {"status": "PAUSED"})
    time.sleep(1)
print("Interesse: verba R$70 e ativo")
post(INTERESSE, {"daily_budget": 7000})
post(INTERESSE, {"status": "ACTIVE"})

ids = ",".join([INTERESSE, "120245790367990358", "120245790363030358", "120246003834740358", "120245933397060358",
                "120245854126000358", "120245854129560358", "120245855388890358"])
r = requests.get(G, params={"ids": ids, "fields": "name,status,daily_budget", "access_token": TOKEN}, timeout=120).json()
total = 0
print("\n== conferido na API")
for a in r.values():
    if a["status"] == "ACTIVE":
        total += int(a.get("daily_budget", 0))
    print(f"  {a['name'][:55]:55} | {a['status']:7} | R${int(a.get('daily_budget', 0))/100:.0f}")
r = requests.get(G, params={"ids": ",".join(PAUSAR_ANUNCIOS), "fields": "name,status", "access_token": TOKEN},
                 timeout=120).json()
for i, a in r.items():
    print(f"  {PAUSAR_ANUNCIOS[i]:38} | {a['status']}")
print(f"  Verba ativa (conjuntos listados): R${total/100:.0f}/dia")
