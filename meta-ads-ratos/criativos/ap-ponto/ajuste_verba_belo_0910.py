"""Belo 09/10/2026 - verba de R$1.300/dia pelo CV de 01 a 09/10 (aprovado pela Mileny).

Pausa Interesse (LP), Base Quente e Momento de Vida (Form), sem Simulacao+ no CV.
Verba: RMKT R$250 -> R$340 · Form Leads Qualificados R$200 -> R$260 · Form LAL CAPI R$80 -> R$150.
LAL (R$450) e Servidores (R$100) sem mudanca de verba. UGC do Leo pausados no LAL e em Servidores (0 Simulacao+ no CV).
"""
import json
import os
import sys
import time
from pathlib import Path

import requests

sys.stdout.reconfigure(encoding="utf-8")
env = (Path(os.path.expanduser("~/OneDrive/.claude/skills/meta-ads-ratos")) / ".env").read_text(encoding="utf-8")
TOKEN = [l.split("=", 1)[1].strip().strip('"') for l in env.splitlines() if l.startswith("META_ADS_TOKEN")][0]
G = "https://graph.facebook.com/v23.0/"

PAUSAR_CONJUNTOS = {
    "120245790403680358": "[BELO] Interesse Imóvel 25-45",
    "120245854129560358": "[BELO][FORM] Base Quente AP Ponto",
    "120245855388890358": "[BELO][FORM] Momento de Vida 25-45",
}
VERBA = {  # centavos
    "120245790367990358": ("[BELO] Remarketing 180D", 25000, 34000),
    "120245933397060358": ("[BELO][FORM] LAL Compradores RMBH | Leads Qualificados", 20000, 26000),
    "120245854126000358": ("[BELO][FORM] LAL Qualificados CAPI", 8000, 15000),
}
PAUSAR_ANUNCIOS = {
    "120245790442800358": "LAL · VID UGC Leo v1",
    "120245916003780358": "LAL · VID UGC Leo Chegou v1",
    "120246003835410358": "Servidores · VID UGC Leo v1",
    "120246003892090358": "Servidores · VID UGC Leo Chegou v1",
}


def get(path, **p):
    p["access_token"] = TOKEN
    return requests.get(G + path, params=p, timeout=60).json()


def post(path, data):
    data["access_token"] = TOKEN
    r = requests.post(G + path, data=data, timeout=60).json()
    if "error" in r:
        print("  ERRO", path, json.dumps(r["error"], ensure_ascii=False)[:300])
    return r


# conferir o estado antes (a verba so muda se ainda for a esperada)
for i, (nome, antes, depois) in VERBA.items():
    atual = int(get(i, fields="daily_budget").get("daily_budget", 0))
    if atual != antes:
        sys.exit(f"{nome}: verba atual R${atual/100:.0f}, esperada R${antes/100:.0f}. Nada foi alterado.")

for i, nome in PAUSAR_CONJUNTOS.items():
    post(i, {"status": "PAUSED"})
    print("conjunto pausado:", nome)
    time.sleep(2)
for i, (nome, antes, depois) in VERBA.items():
    post(i, {"daily_budget": depois})
    print(f"verba: {nome} R${antes/100:.0f} -> R${depois/100:.0f}")
    time.sleep(2)
for i, nome in PAUSAR_ANUNCIOS.items():
    post(i, {"status": "PAUSED"})
    print("anuncio pausado:", nome)
    time.sleep(2)

print("\n== conferido na API")
for i in list(PAUSAR_CONJUNTOS) + list(VERBA) + ["120245790363030358", "120246003834740358"]:
    a = get(i, fields="name,status,effective_status,daily_budget")
    print(f"  {a['name'][:55]:55} | {a['status']:7} | {a['effective_status']:15} | R${int(a.get('daily_budget', 0))/100:.0f}")
for i in PAUSAR_ANUNCIOS:
    a = get(i, fields="name,status,adset{name}")
    print(f"  {a['adset']['name'][:30]:30} | {a['name'][:30]:30} | {a['status']}")
total = 0
for a in get("act_1043516946010441/adsets", fields="name,daily_budget,effective_status", limit=100,
             filtering=json.dumps([{"field": "effective_status", "operator": "IN", "value": ["ACTIVE"]}])).get("data", []):
    total += int(a.get("daily_budget", 0))
    print(f"  ATIVO {a['name'][:55]:55} R${int(a.get('daily_budget', 0))/100:.0f}")
print(f"  Verba ativa total: R${total/100:.0f}/dia")
