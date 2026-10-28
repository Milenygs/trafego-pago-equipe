# -*- coding: utf-8 -*-
"""Cheirin MT: gasto por anuncio + IDs dos leads de formulario num periodo, para cruzar com o CRM.

Uso:  python meta_leads_periodo.py 2026-08-08 2026-10-07 saida.json
LGPD: so o id do lead, data e de onde veio (anuncio/conjunto). Nada de nome, e-mail, telefone ou respostas.
"""
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

BASE = os.path.join(os.path.expanduser("~"), "OneDrive", ".claude", "skills", "meta-ads-ratos")
TOK = [l.split("=", 1)[1].strip().strip('"').strip("'") for l in open(os.path.join(BASE, ".env"), encoding="utf-8")
       if l.strip().startswith("META_ADS_TOKEN")][0]
API = "https://graph.facebook.com/v21.0/"
CONTA = "act_884652616778712"
BRT = timezone(timedelta(hours=-3))
LEAD_TYPES = ("onsite_conversion.lead_grouped", "lead")


def get(path, params):
    params = dict(params, access_token=TOK)
    url = API + path + "?" + urllib.parse.urlencode(params)
    out = []
    while url:
        for espera in (30, 60, 120, None):
            try:
                with urllib.request.urlopen(url, timeout=180) as r:
                    d = json.load(r)
                break
            except urllib.error.HTTPError as e:
                body = e.read().decode("utf-8", "replace")
                if espera and any(c in body for c in ('"code":17,', '"code":613', '"code":4,', '"code":80004', '"code":2,')):
                    time.sleep(espera)
                    continue
                raise RuntimeError("%s -> %s" % (path, body[:300]))
        out += d.get("data", [])
        url = d.get("paging", {}).get("next")
    return out


def leads_de(acoes):
    a = {x["action_type"]: float(x["value"]) for x in (acoes or [])}
    for t in LEAD_TYPES:
        if t in a:
            return int(a[t])
    return 0


def main():
    de, ate, saida = sys.argv[1], sys.argv[2], sys.argv[3]
    ins = get(CONTA + "/insights", {
        "level": "ad", "limit": 500,
        "fields": "campaign_id,campaign_name,adset_id,adset_name,ad_id,ad_name,spend,impressions,actions",
        "time_range": json.dumps({"since": de, "until": ate}),
        "filtering": json.dumps([{"field": "ad.effective_status", "operator": "IN", "value":
                                  ["ACTIVE", "PAUSED", "ADSET_PAUSED", "CAMPAIGN_PAUSED", "ARCHIVED", "WITH_ISSUES",
                                   "IN_PROCESS", "DISAPPROVED", "PENDING_REVIEW", "DELETED"]}]),
    })
    ads = []
    for r in ins:
        ads.append({k: r.get(k) for k in ("campaign_id", "campaign_name", "adset_id", "adset_name", "ad_id", "ad_name")}
                   | {"spend": float(r.get("spend", 0) or 0), "impressions": int(r.get("impressions", 0) or 0),
                      "leads_meta": leads_de(r.get("actions"))})
    print("anuncios com entrega: %d | gasto R$%.2f | leads %d" % (
        len(ads), sum(a["spend"] for a in ads), sum(a["leads_meta"] for a in ads)), flush=True)

    ts0 = int(datetime.strptime(de, "%Y-%m-%d").replace(tzinfo=BRT).timestamp()) - 1
    ts1 = int((datetime.strptime(ate, "%Y-%m-%d").replace(tzinfo=BRT) + timedelta(days=1)).timestamp())
    leads = {}
    com_lead = [a for a in ads if a["leads_meta"] > 0]
    for i, a in enumerate(com_lead, 1):
        try:
            ls = get(a["ad_id"] + "/leads", {"fields": "id,created_time,form_id,is_organic", "limit": 500,
                                              "filtering": json.dumps([
                                                  {"field": "time_created", "operator": "GREATER_THAN", "value": ts0},
                                                  {"field": "time_created", "operator": "LESS_THAN", "value": ts1}])})
        except RuntimeError as e:
            print("  falhou %s: %s" % (a["ad_id"], e), flush=True)
            continue
        for l in ls:
            leads[str(l["id"])] = {"ad_id": a["ad_id"], "adset_id": a["adset_id"], "created_time": l["created_time"],
                                   "form_id": str(l.get("form_id", "")), "organico": bool(l.get("is_organic"))}
        if i % 10 == 0:
            print("  %d/%d anuncios, %d leads" % (i, len(com_lead), len(leads)), flush=True)
        time.sleep(0.3)

    # status atual de conjuntos e anuncios (para dizer o que ainda esta no ar)
    st_set = {s["id"]: s["effective_status"] for s in get(CONTA + "/adsets", {
        "fields": "id,effective_status", "limit": 500,
        "filtering": json.dumps([{"field": "id", "operator": "IN", "value": sorted({a["adset_id"] for a in ads})}])})}
    st_ad = {}
    ids = sorted({a["ad_id"] for a in ads})
    for k in range(0, len(ids), 50):
        for s in get(CONTA + "/ads", {"fields": "id,effective_status", "limit": 500,
                                      "filtering": json.dumps([{"field": "id", "operator": "IN", "value": ids[k:k + 50]}])}):
            st_ad[s["id"]] = s["effective_status"]
    for a in ads:
        a["status_conjunto"] = st_set.get(a["adset_id"], "?")
        a["status_anuncio"] = st_ad.get(a["ad_id"], "?")

    json.dump({"de": de, "ate": ate, "ads": ads, "leads": leads}, open(saida, "w", encoding="utf-8"), ensure_ascii=False)
    print("OK %d anuncios, %d lead IDs -> %s" % (len(ads), len(leads), saida), flush=True)


if __name__ == "__main__":
    main()
