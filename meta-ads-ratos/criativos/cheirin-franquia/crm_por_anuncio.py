# -*- coding: utf-8 -*-
"""Analise AGREGADA do CRM da Cheirin (pipelines Closer + Franqueados, 30 dias).
Nunca imprime nome, e-mail ou telefone: usa telefone/e-mail so em memoria para juntar duplicados."""
import csv, io, re, json, os
from collections import Counter, defaultdict
from datetime import datetime

import argparse
_ap = argparse.ArgumentParser(description='CRM Cheirin por conjunto/criativo (so contagem, nunca dado pessoal)')
_ap.add_argument('csv', nargs='+', help='exports do CRM (Closer e Franqueados)')
_ap.add_argument('--de', required=True, help='dd/mm/aaaa')
_ap.add_argument('--ate', required=True, help='dd/mm/aaaa')
_a = _ap.parse_args()
ARQ = _a.csv
INI = datetime.strptime(_a.de, '%d/%m/%Y')
FIM = datetime.strptime(_a.ate, '%d/%m/%Y').replace(hour=23, minute=59)

QUALIF = {"Confirmado Capital para Cheirin Bao", "Confirmado Capital", "Falar com o Franqueado",
          "Ficha Cadastral", "1a Reunião", "Ganho"}
RANK = {"Ganho": 9, "1a Reunião": 8, "Ficha Cadastral": 7, "Falar com o Franqueado": 6,
        "Confirmado Capital para Cheirin Bao": 5, "Confirmado Capital": 5, "Em Atendimento": 4,
        "Atendeu": 3, "StandBy": 3, "Capital até 200 mil": 2, "Capital até 100 mil": 2,
        "Sem Capital": 1, "Incoerente": 1, "Perda": 1, "Não Atendeu": 0, "Leads Novos": 0}


def load(f):
    return list(csv.DictReader(io.StringIO(open(f, "rb").read().decode("utf-8-sig"))))


def chave(r):
    tel = re.sub(r"\D", "", r.get("Telefone") or "")
    if len(tel) >= 8:
        return "t" + tel[-9:]
    em = (r.get("Email") or "").strip().lower()
    return "e" + em if em else None


def data(r):
    try:
        return datetime.strptime((r.get("Data Cadastro Lead") or "").strip(), "%d/%m/%Y %H:%M")
    except ValueError:
        return None


def adset_norm(s):
    s = (s or "").replace("✅", "").strip()
    if "QUALI" in s:
        return "PINO SP QUALI"
    if "PINOS SP" in s:
        return "PINO SP"
    if s.startswith("01 - Leads Quente + Geo — 2"):
        return "Quente — 2 (antigo)"
    if s.startswith("01 - Leads Quente"):
        return "01 Quente"
    if s.startswith("04 - LAL"):
        return "04 LAL"
    if s.startswith("03 - LAL"):
        return "03 LAL"
    if s.startswith("VD06"):
        return "Santoro (VD06)"
    if s.startswith("VD02 -Franqueada Raissa") or s.startswith("VD07 -Franqueada Raissa"):
        return "Raissa (VD02/VD07)"
    if s.startswith("Franqueados - Geo"):
        return "Franqueados Geo"
    if s.startswith("07A") or s.startswith("07B"):
        return "07A/07B (teste)"
    if s.startswith("01 - Pinos Lojas"):
        return "14 Pinos Lojas"
    if s.startswith("VD02 -Franqueado Marcelo Santoro"):
        return "Santoro (VD02 antigo)"
    return s or "(sem)"


def ad_norm(s):
    s = (s or "").strip()
    s = re.sub(r"^\[P_quente\]\s*|^\[PINO SP\]\s*|^Quente\s*-\s*|^LAL\s*-\s*|^Lookalike\s*-\s*|^07[AB]\s*\|\s*", "", s)
    s = s.replace("  ", " ").strip()
    low = s.lower()
    if "carrossel" in low:
        return "carrossel como é ter uma"
    if "1 milhão" in low:
        return "1 milhão várias unidades"
    if "santoro" in low and "novo" in low:
        return "depoimento Santoro novo"
    if low.startswith("vd06-franqueado") or low.startswith("vd07-franqueado") or "marcelo santoro" in low:
        return "Santoro (VD06/VD07)"
    if "raissa" in low:
        return "Raissa (VD02/VD08)"
    if "franqueada-clt" in low or "franqueada clt" in low or "depoimento clt" in low:
        return "franqueada CLT / depoimento CLT"
    if "dre 146" in low:
        return "DRE 146k"
    if "experiencia-cliente-produto" in low:
        return "experiência cliente-produto v2"
    if "casal" in low:
        return "casal convenção"
    if "dono-melo" in low:
        return "dono Melo"
    return s or "(sem)"


rows = []
for f in ARQ:
    for r in load(f):
        r["_dt"] = data(r)
        rows.append(r)
rows = [r for r in rows if r["_dt"] and INI <= r["_dt"] <= FIM]

# junta duplicados (mesma pessoa): fica a etapa mais avancada, com a atribuicao do primeiro cadastro
por = {}
sem_chave = []
for r in sorted(rows, key=lambda x: x["_dt"]):
    k = chave(r)
    if not k:
        sem_chave.append(r)
        continue
    if k not in por:
        por[k] = dict(r)
    elif RANK.get(r["Etapa"], 0) > RANK.get(por[k]["Etapa"], 0):
        por[k]["Etapa"] = r["Etapa"]
uni = list(por.values()) + sem_chave


def canal(r):
    camp = (r.get("UTM Campaign") or "") + (r.get("Orig UTM Campaign") or "")
    src = (r.get("Source") or "") + (r.get("Orig Source") or "")
    if "[TM]" in camp or "[TM]" in src or "TM -" in src:
        return "Meta - outro gestor [TM]"
    if any(x in camp for x in ("✅05", "✅09", "✅14", "12-franqueados")) or "[M] FORMS" in src or "FORM Bl 2" in src or "CAMPANHA NOVA" in src or "BL - CAMPANHA" in src:
        return "Meta - Mileny"
    if "google" in (r.get("UTM Source") or "") + (r.get("Orig UTM Source") or ""):
        return "Google (marca)"
    if "WhatsApp" in src or "instagram" in (r.get("UTM Source") or "") + (r.get("Orig UTM Source") or ""):
        return "WhatsApp / Instagram direto"
    return "Site / orgânico / outros"


def linha(nome, grupo, w=40):
    n = len(grupo)
    c = Counter(g["Etapa"] for g in grupo)
    q = sum(v for k, v in c.items() if k in QUALIF)
    at = c["Atendeu"] + c["StandBy"] + c["Em Atendimento"]
    na = c["Não Atendeu"] + c["Leads Novos"]
    pe = c["Perda"] + c["Sem Capital"] + c["Incoerente"] + c["Capital até 100 mil"] + c["Capital até 200 mil"]
    return f"{nome[:w]:{w}} {n:5} | qualif {q:3} ({q/n*100 if n else 0:4.1f}%) | em conversa {at:3} | sem contato {na/n*100 if n else 0:3.0f}% | perdido/sem capital {pe/n*100 if n else 0:3.0f}%"


print(f"Janela {INI:%d/%m}–{FIM:%d/%m} | linhas {len(rows)} | pessoas unicas {len(uni)} | duplicados juntados {len(rows)-len(uni)}")
print("Etapas (pessoas unicas):", dict(Counter(r["Etapa"] for r in uni).most_common()))

print("\n== POR CANAL ==")
g = defaultdict(list)
for r in uni:
    g[canal(r)].append(r)
for k, v in sorted(g.items(), key=lambda x: -len(x[1])):
    print(linha(k, v))

meta = [r for r in uni if canal(r) == "Meta - Mileny"]
print("\n== MILENY: POR CONJUNTO ==")
g = defaultdict(list)
for r in meta:
    g[adset_norm(r.get("UTM Medium") or r.get("Orig UTM Medium"))].append(r)
for k, v in sorted(g.items(), key=lambda x: -len(x[1])):
    print(linha(k, v))

print("\n== MILENY: POR CRIATIVO (todos os conjuntos) ==")
g = defaultdict(list)
for r in meta:
    g[ad_norm(r.get("UTM Content") or r.get("Orig UTM Content"))].append(r)
for k, v in sorted(g.items(), key=lambda x: -len(x[1])):
    print(linha(k, v))

print("\n== MILENY: CONJUNTO x CRIATIVO (>=3 leads) ==")
g = defaultdict(list)
for r in meta:
    g[(adset_norm(r.get("UTM Medium") or r.get("Orig UTM Medium")), ad_norm(r.get("UTM Content") or r.get("Orig UTM Content")))].append(r)
for (a, b), v in sorted(g.items(), key=lambda x: (x[0][0], -len(x[1]))):
    if len(v) >= 3:
        print(linha(f"{a} · {b}", v, 58))

tm = [r for r in uni if canal(r) == "Meta - outro gestor [TM]"]
print("\n== OUTRO GESTOR [TM]: POR CRIATIVO (referencia) ==")
g = defaultdict(list)
for r in tm:
    g[(r.get("UTM Content") or r.get("Orig UTM Content") or "(sem)").strip()].append(r)
for k, v in sorted(g.items(), key=lambda x: -len(x[1])):
    if len(v) >= 3:
        print(linha(k, v, 50))

print("\n== QUALIFICADOS DA MILENY: em que conjunto/criativo e semana ==")
for r in sorted([x for x in meta if x["Etapa"] in QUALIF], key=lambda x: x["_dt"]):
    print(f"  {r['_dt']:%d/%m} | {r['Etapa'][:28]:28} | {adset_norm(r.get('UTM Medium') or r.get('Orig UTM Medium'))[:22]:22} | {ad_norm(r.get('UTM Content') or r.get('Orig UTM Content'))[:34]:34} | capital {(r.get('Capital Disponível') or '').replace(' ', '')}")

print("\n== FAIXA DE CAPITAL x QUALIFICACAO (todas as pessoas unicas) ==")
def faixa(r):
    v = (r.get("Capital Disponível") or r.get("Capital disponível") or "").replace(" ", "").replace("\xa0", "").replace(".", "")
    m = re.search(r"(\d{3})", v)
    return {"100": "R$100 mil", "200": "R$200 mil", "300": "R$300 mil", "400": "R$400 mil"}.get(m.group(1) if m else "", "sem resposta")
g = defaultdict(list)
for r in uni:
    g[faixa(r)].append(r)
for k in ("R$100 mil", "R$200 mil", "R$300 mil", "R$400 mil", "sem resposta"):
    if g[k]:
        print(linha(k, g[k]))

