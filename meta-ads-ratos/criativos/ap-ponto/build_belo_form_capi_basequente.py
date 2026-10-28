"""Belo 28/09/2026 - 2 conjuntos novos na campanha de formulario (teste CAPI + base quente). Tudo PAUSED.

A. [BELO][FORM] LAL Qualificados CAPI  -> M_LAL_1_CAPI_Qualificados (semente = eventos do CV via CAPI)
B. [BELO][FORM] Base Quente AP Ponto   -> Blenda_MQL + Luna_MQL + Lis_MQL + LEADS_PERDIDOS_TT
                                         + M_Form_Abriu_Nao_Enviou_30D (novo)
Os dois: geo BH 17 + Contagem 17 + Vespasiano 20, Instagram sem Stories, exclui compradores, complemento,
leads do Belo pela LP (/obrigado) e quem enviou formulario nos ultimos 30 dias. R$150/dia cada.
Anuncios: os 4 videos do Belo (criativos FORM ja existentes, formulario 2287635791803187).
A campanha continua PAUSED: a Mileny integra o formulario no CV antes de ativar.
"""
import json
import os
import sys
import time
from pathlib import Path

import requests

SKILL = Path(os.path.expanduser("~/OneDrive/.claude/skills/meta-ads-ratos"))
env = (SKILL / ".env").read_text(encoding="utf-8")
TOKEN = [l.split("=", 1)[1].strip().strip('"') for l in env.splitlines() if l.startswith("META_ADS_TOKEN")][0]
G = "https://graph.facebook.com/v23.0/"
ACT, PAGE = "act_1043516946010441", "198169833565944"
CAMP_FORM = "120245805859660358"
REGIONAL = {"regional_regulated_categories": ["BRAZIL_REGULATION", "VOLUNTARY_VERIFICATION"],
            "regional_regulation_identities": {"universal_beneficiary": "609854092925940",
                                               "universal_payer": "609854092925940"}}
GEO = {"cities": [{"key": "244661", "radius": 17, "distance_unit": "kilometer"},
                  {"key": "249756", "radius": 17, "distance_unit": "kilometer"},
                  {"key": "273969", "radius": 20, "distance_unit": "kilometer"}]}
CRIATIVOS = {  # criativos FORM ja aprovados/usados, todos no formulario 2287635791803187
    "VID Locucao Lancamento v1": "1574465704360224",
    "VID UGC Leo v1": "1401233955466440",
    "VID Engenheiro Sonho v1": "1662769275469648",
    "VID Engenheiro Familia v1": "28366639636310063",
}
EXCLUIR_FIXOS = ["120245517540390358",  # M_AP_Ponto_Compradores_RMBH
                 "120245517540780358",  # M_AP_Ponto_Exclusao_Complemento
                 "120245802351920358"]  # M_Belo_Leads_Obrigado_180D


def get(p, **k):
    k["access_token"] = TOKEN
    return requests.get(G + p, params=k, timeout=90).json()


def post(path, data, fatal=True):
    data = {k: (json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v) for k, v in data.items()}
    data["access_token"] = TOKEN
    r = requests.post(G + path, data=data, timeout=120).json()
    if "error" in r:
        e = r["error"]
        print(json.dumps({k: e.get(k) for k in ("code", "error_subcode", "error_user_title", "error_user_msg", "message")},
                         ensure_ascii=False, indent=1))
        if fatal:
            sys.exit(1)
    return r


publicos = {a["name"]: a["id"] for a in get(ACT + "/customaudiences", fields="name", limit=500)["data"]}


def publico_form(nome, evento, desc):
    if nome in publicos:
        return publicos[nome]
    rule = {"inclusions": {"operator": "or", "rules": [{
        "event_sources": [{"id": PAGE, "type": "lead"}], "retention_seconds": 30 * 86400,
        "filter": {"operator": "and", "filters": [{"field": "event", "operator": "eq", "value": evento}]}}]}}
    r = post(ACT + "/customaudiences", {"name": nome, "rule": rule, "prefill": True, "description": desc}, fatal=False)
    print(nome, r)
    return r.get("id")


abriu = publico_form("M_Form_Abriu_Nao_Enviou_30D", "lead_generation_dropoff",
                     "Abriu formulario da pagina AP Ponto e nao enviou (30d). Base quente.")
enviou = publico_form("M_Form_Enviou_30D", "lead_generation_submitted",
                      "Enviou formulario da pagina AP Ponto (30d). Excluir de captacao.")

base_quente = [publicos[n] for n in ("Blenda_MQL.csv", "Luna_MQL.csv", "Lis_MQL.csv", "LEADS_PERDIDOS_TT")]
if abriu:
    base_quente.append(abriu)
excluir = EXCLUIR_FIXOS + ([enviou] if enviou else [])


def targeting(incluir, age_min, age_max):
    return {"age_min": age_min, "age_max": age_max, "geo_locations": GEO,
            "custom_audiences": [{"id": i} for i in incluir],
            "excluded_custom_audiences": [{"id": i} for i in excluir],
            "publisher_platforms": ["instagram"], "instagram_positions": ["stream", "explore", "reels", "profile_feed"],
            "device_platforms": ["mobile", "desktop"], "targeting_automation": {"advantage_audience": 0}}


CONJUNTOS = [
    ("[BELO][FORM] LAL Qualificados CAPI", targeting([publicos["M_LAL_1_CAPI_Qualificados"]], 25, 55)),
    ("[BELO][FORM] Base Quente AP Ponto", targeting(base_quente, 21, 65)),
]
existentes = {s["name"]: s["id"] for s in get(CAMP_FORM + "/adsets", fields="name")["data"]}
for nome, t in CONJUNTOS:
    sid = existentes.get(nome)
    if not sid:
        sid = post(ACT + "/adsets", {
            "name": nome, "campaign_id": CAMP_FORM, "status": "PAUSED", "daily_budget": 15000,
            "billing_event": "IMPRESSIONS", "optimization_goal": "LEAD_GENERATION", "destination_type": "ON_AD",
            "bid_strategy": "LOWEST_COST_WITHOUT_CAP", "promoted_object": {"page_id": PAGE},
            "targeting": t, **REGIONAL})["id"]
        print("conjunto", nome, sid)
        time.sleep(2)
    ja = {a["name"] for a in get(sid + "/ads", fields="name")["data"]}
    for ad_name, cr in CRIATIVOS.items():
        if ad_name in ja:
            continue
        ad = post(ACT + "/ads", {"name": ad_name, "adset_id": sid, "creative": {"creative_id": cr}, "status": "PAUSED"},
                  fatal=False)
        print("   anuncio", ad_name, ad.get("id"))
        time.sleep(2)

print("\n== conferencia")
for s in get(CAMP_FORM + "/adsets", fields="name,status,daily_budget,targeting{geo_locations,custom_audiences,excluded_custom_audiences,age_min,age_max}")["data"]:
    t = s["targeting"]
    print(s["name"], "|", s["status"], "| R$", int(s["daily_budget"]) / 100, "| idade", t.get("age_min"), "-", t.get("age_max"),
          "| geo", [(c["name"], c.get("radius")) for c in t.get("geo_locations", {}).get("cities", [])])
    print("    inclui:", [a["name"] for a in t.get("custom_audiences", [])])
    print("    exclui:", [a["name"] for a in t.get("excluded_custom_audiences", [])])
print("campanha:", get(CAMP_FORM, fields="name,status,effective_status"))
for n in ("M_CAPI_Qualificados_180D", "M_LAL_1_CAPI_Qualificados"):
    a = get(publicos[n], fields="approximate_count_lower_bound,approximate_count_upper_bound,operation_status")
    print(n, a.get("approximate_count_lower_bound"), "-", a.get("approximate_count_upper_bound"), "|",
          a.get("operation_status", {}).get("description", "")[:120])
