# -*- coding: utf-8 -*-
"""Cheirin MT: CRM x Meta por publico (conjunto) e por criativo, casando lead a lead pelo "Codigo do lead Meta".

Uso:  python crm_cruza_meta.py <meta.json> <crm.csv> [crm2.csv ...] --de dd/mm/aaaa --ate dd/mm/aaaa
      (meta.json = saida de meta_leads_periodo.py, mesmo periodo)
So contagem: telefone/e-mail ficam em memoria para juntar a mesma pessoa e nunca sao impressos.
"""
import argparse
import csv
import io
import json
import re
from collections import Counter, defaultdict
from datetime import datetime

ap = argparse.ArgumentParser()
ap.add_argument("meta")
ap.add_argument("csv", nargs="+")
ap.add_argument("--de", required=True)
ap.add_argument("--ate", required=True)
ap.add_argument("--json", help="grava o resumo agregado aqui")
ap.add_argument("--alias", action="append", default=[],
                help='anuncio renomeado: "nome antigo na UTM Content=ad_id" (pode repetir)')
ap.add_argument("--conj", action="append", default=[],
                help='conjunto renomeado: "nome antigo na UTM Medium=adset_id" (pode repetir)')
a = ap.parse_args()
ALIAS = {k.strip().lower(): v.strip() for k, v in (s.rsplit("=", 1) for s in a.alias)}
CONJ = {k.strip().lower(): v.strip() for k, v in (s.rsplit("=", 1) for s in a.conj)}
INI = datetime.strptime(a.de, "%d/%m/%Y")
FIM = datetime.strptime(a.ate, "%d/%m/%Y").replace(hour=23, minute=59)

QUALIF = {"Confirmado Capital para Cheirin Bao", "Confirmado Capital", "Falar com o Franqueado", "Ficha Cadastral",
          "1a Reunião", "2a Reunião - COF", "Ganho"}
RANK = {"Ganho": 10, "2a Reunião - COF": 9, "1a Reunião": 8, "Ficha Cadastral": 7, "Falar com o Franqueado": 6,
        "Confirmado Capital para Cheirin Bao": 5, "Confirmado Capital": 5, "Em Atendimento": 4, "Atendeu": 3,
        "StandBy": 3, "Capital até 200 mil": 2, "Capital até 100 mil": 2, "Sem Capital": 1, "Incoerente": 1,
        "Perda": 1, "Não Atendeu": 0, "Leads Novos": 0}
DESCARTE_CAPITAL = {"Sem Capital", "Capital até 100 mil", "Capital até 200 mil", "Incoerente"}
SEM_CONTATO = {"Não Atendeu", "Leads Novos"}

meta = json.load(open(a.meta, encoding="utf-8"))
ADS = {x["ad_id"]: x for x in meta["ads"]}
LEADS = meta["leads"]
POR_NOME = defaultdict(list)
for x in meta["ads"]:
    POR_NOME[(x["ad_name"] or "").strip().lower()].append(x["ad_id"])


def criativo(nome):
    """Junta o mesmo criativo rodando em conjuntos diferentes (tira o prefixo do conjunto)."""
    s = (nome or "").strip()
    s = re.sub(r"^\s*(\[P_quente\]|\[PINO SP\]|\[PINOS SP\]|Quente\s*-|LAL\s*-|LAL-|M15\s*-|07[AB]\s*\|)\s*", "", s, flags=re.I)
    s = re.sub(r"\s+", " ", s).strip()
    low = s.lower()
    m = re.match(r"(ad3\d)\b", low)
    if m:
        return m.group(1).upper() + low[len(m.group(1)):]
    m = re.match(r"(vd\d\d)\s*-\s*franqueada[_ ]raissa", low)
    if m:
        return m.group(1).upper() + " - franqueada_raissa"
    if "carrossel" in low:
        return "carrossel como é ter uma"
    if "1 milhão" in low or "1 milhao" in low:
        return "1 milhão várias unidades"
    if "santoro" in low and "novo" in low:
        return "depoimento Santoro novo"
    if "santoro" in low:
        return "Santoro VD06/VD07"
    if "raissa" in low:
        return "Raissa (anúncios antigos)"
    if "franqueada-clt" in low or "franqueada clt" in low or "depoimento clt" in low:
        return "franqueada CLT"
    if "dre 146" in low:
        return "DRE 146k"
    if "dre 439" in low:
        return "DRE 439k"
    if "dre 4" in low:
        return "DRE 4"
    if "dre 2" in low:
        return "DRE 2"
    if "experiencia" in low or "experiência" in low:
        return "experiência cliente-produto (curtos)"
    return low or "(sem nome)"


def chave(r):
    tel = re.sub(r"\D", "", r.get("Telefone") or "")
    if len(tel) >= 8:
        return "t" + tel[-9:]
    em = (r.get("Email") or "").strip().lower()
    return "e" + em if em else "id" + (r.get("Código do lead Meta") or str(id(r)))


rows = []
for f in a.csv:
    for r in csv.DictReader(io.StringIO(open(f, "rb").read().decode("utf-8-sig"))):
        try:
            r["_dt"] = datetime.strptime((r.get("Data Cadastro Lead") or "").strip(), "%d/%m/%Y %H:%M")
        except ValueError:
            continue
        rows.append(r)

# etapa mais avancada da pessoa em qualquer pipeline (Closer ou Franqueados)
melhor = {}
for r in rows:
    k = chave(r)
    if k not in melhor or RANK.get(r["Etapa"], 0) > RANK.get(melhor[k], 0):
        melhor[k] = r["Etapa"]

# atribuicao: codigo do lead Meta da conta da Mileny; sem codigo, nome exato do anuncio na UTM
pessoas = {}
como = Counter()
for r in sorted(rows, key=lambda x: x["_dt"]):
    if not (INI <= r["_dt"] <= FIM):
        continue
    cod = (r.get("Código do lead Meta") or "").strip()
    ad_id = None
    if cod and cod in LEADS:
        ad_id = LEADS[cod]["ad_id"]
        via = "codigo"
    elif not cod:
        nome = (r.get("UTM Content") or r.get("Orig UTM Content") or "").strip().lower()
        cands = [ALIAS[nome]] if ALIAS.get(nome) in ADS else POR_NOME.get(nome, [])
        if len(cands) == 1:
            ad_id, via = cands[0], "utm"
        elif len(cands) > 1:
            med = (r.get("UTM Medium") or r.get("Orig UTM Medium") or "").strip().lower()
            c2 = [c for c in cands if (ADS[c]["adset_name"] or "").strip().lower() == med
                  or ADS[c]["adset_id"] == CONJ.get(med)]
            if len(c2) == 1:
                ad_id, via = c2[0], "utm"
    if not ad_id:
        continue
    k = chave(r)
    if k in pessoas:  # mesma pessoa de novo: fica a atribuicao do 1o cadastro
        como["recadastro"] += 1
        continue
    como[via] += 1
    pessoas[k] = {"ad_id": ad_id, "etapa": melhor[k], "dt": r["_dt"]}

ids_crm = {(r.get("Código do lead Meta") or "").strip() for r in rows}
leads_janela = {i: l for i, l in LEADS.items()
                if INI <= datetime.strptime(l["created_time"][:16], "%Y-%m-%dT%H:%M") <= FIM}
fora_crm = Counter(l["adset_id"] for i, l in leads_janela.items() if i not in ids_crm)


def resumo(grupo_ids, gasto, leads_meta):
    ps = grupo_ids
    n = len(ps)
    c = Counter(p["etapa"] for p in ps)
    q = sum(v for k, v in c.items() if k in QUALIF)
    return {"gasto": round(gasto, 2), "leads_meta": leads_meta, "pessoas_crm": n, "qualif": q,
            "taxa_qualif": round(q / n * 100, 1) if n else 0.0,
            "perda": c["Perda"], "pct_perda": round(c["Perda"] / n * 100) if n else 0,
            "descarte_capital": sum(c[k] for k in DESCARTE_CAPITAL),
            "sem_contato": sum(c[k] for k in SEM_CONTATO),
            "pct_sem_contato": round(sum(c[k] for k in SEM_CONTATO) / n * 100) if n else 0,
            "custo_qualif": round(gasto / q) if q else None, "etapas": dict(c.most_common())}


def agrega(chave_ad, rotulo_ad):
    gasto, lm, ps, info = defaultdict(float), defaultdict(int), defaultdict(list), {}
    for ad in ADS.values():
        k = chave_ad(ad)
        gasto[k] += ad["spend"]
        lm[k] += ad["leads_meta"]
        info.setdefault(k, rotulo_ad(ad))
    for p in pessoas.values():
        ps[chave_ad(ADS[p["ad_id"]])].append(p)
    out = []
    for k in gasto:
        if gasto[k] < 1 and not ps[k]:
            continue
        out.append(dict(info[k], chave=k, **resumo(ps[k], gasto[k], lm[k])))
    return sorted(out, key=lambda x: -x["gasto"])


por_conjunto = agrega(lambda ad: ad["adset_id"],
                      lambda ad: {"conjunto": ad["adset_name"], "campanha": ad["campaign_name"],
                                  "status": ad["status_conjunto"]})
for c in por_conjunto:
    c["leads_meta_fora_do_crm"] = fora_crm.get(c["chave"], 0)
por_criativo = agrega(lambda ad: criativo(ad["ad_name"]), lambda ad: {"criativo": criativo(ad["ad_name"])})
ativos_por_criativo = defaultdict(list)
for ad in ADS.values():
    if ad["status_anuncio"] == "ACTIVE" and ad["status_conjunto"] == "ACTIVE":
        ativos_por_criativo[criativo(ad["ad_name"])].append(ad["adset_name"])
for c in por_criativo:
    c["no_ar_em"] = sorted(set(ativos_por_criativo.get(c["chave"], [])))
cruz = agrega(lambda ad: ad["adset_id"] + "|" + criativo(ad["ad_name"]),
              lambda ad: {"conjunto": ad["adset_name"], "criativo": criativo(ad["ad_name"]),
                          "no_ar": ad["status_anuncio"] == "ACTIVE" and ad["status_conjunto"] == "ACTIVE"})


def fmt(x):
    return "-" if x is None else ("R$%s" % format(int(round(x)), ",").replace(",", "."))


def tabela(titulo, linhas, rot, w=46, minimo=0):
    print("\n== %s ==" % titulo)
    print("%-*s %9s %5s %5s %4s %6s %6s %6s %7s %10s" % (w, "", "gasto", "leadM", "crm", "qual", "%qual", "%perda",
                                                    "desc.$", "%s/cont", "R$/qualif"))
    for l in linhas:
        if l["pessoas_crm"] < minimo:
            continue
        print("%-*s %9s %5d %5d %4d %5.1f%% %5d%% %6d %6d%% %10s" % (
            w, rot(l)[:w], fmt(l["gasto"]), l["leads_meta"], l["pessoas_crm"], l["qualif"], l["taxa_qualif"],
            l["pct_perda"], l["descarte_capital"], l["pct_sem_contato"], fmt(l["custo_qualif"])))


print("Janela %s–%s | linhas CRM %d | pessoas atribuídas à conta MT %d | via %s" % (
    a.de, a.ate, len(rows), len(pessoas), dict(como)))
print("Leads Meta na janela: %d | não achados no CRM: %d" % (len(leads_janela), sum(fora_crm.values())))
print("Etapas (pessoas da MT):", dict(Counter(p["etapa"] for p in pessoas.values()).most_common()))
tabela("POR CONJUNTO (público)", por_conjunto,
       lambda l: ("%s [%s]" % (l["conjunto"], {"ACTIVE": "no ar", "PAUSED": "pausado",
                                               "CAMPAIGN_PAUSED": "camp. pausada"}.get(l["status"], l["status"]))))
tabela("POR CRIATIVO (todos os conjuntos)", por_criativo,
       lambda l: l["criativo"] + (" [no ar]" if l["no_ar_em"] else ""))
tabela("CONJUNTO x CRIATIVO (>=5 pessoas no CRM)", sorted(cruz, key=lambda x: (x["conjunto"], -x["gasto"])),
       lambda l: "%s · %s%s" % (l["conjunto"][:24], l["criativo"], " *" if l["no_ar"] else ""), w=62, minimo=5)

if a.json:
    json.dump({"janela": [a.de, a.ate], "pessoas": len(pessoas), "por_conjunto": por_conjunto,
               "por_criativo": por_criativo, "cruz": cruz,
               "etapas": dict(Counter(p["etapa"] for p in pessoas.values()).most_common())},
              open(a.json, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
