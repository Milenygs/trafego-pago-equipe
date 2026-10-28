# -*- coding: utf-8 -*-
"""Troca o gasto/leads por anuncio do meta_60d.json pelo de uma janela menor (1 chamada de insights).
Reaproveita os IDs de lead e o status ja coletados. Uso: python gasto_janela.py meta_60d.json 2026-09-01 2026-10-07 saida.json
"""
import json
import sys

sys.path.insert(0, r"C:\Users\MilenyGalvão\OneDrive\.claude\skills\meta-ads-ratos\criativos\cheirin-franquia")
from meta_leads_periodo import CONTA, get, leads_de  # noqa: E402

base, de, ate, saida = sys.argv[1:5]
meta = json.load(open(base, encoding="utf-8"))
ins = get(CONTA + "/insights", {
    "level": "ad", "limit": 500, "fields": "ad_id,spend,actions",
    "time_range": json.dumps({"since": de, "until": ate}),
    "filtering": json.dumps([{"field": "ad.effective_status", "operator": "IN", "value":
                              ["ACTIVE", "PAUSED", "ADSET_PAUSED", "CAMPAIGN_PAUSED", "ARCHIVED", "WITH_ISSUES",
                               "IN_PROCESS", "DISAPPROVED", "PENDING_REVIEW", "DELETED"]}]),
})
por_ad = {r["ad_id"]: (float(r.get("spend", 0) or 0), leads_de(r.get("actions"))) for r in ins}
for a in meta["ads"]:
    a["spend"], a["leads_meta"] = por_ad.get(a["ad_id"], (0.0, 0))
faltam = set(por_ad) - {a["ad_id"] for a in meta["ads"]}
meta["de"], meta["ate"] = de, ate
json.dump(meta, open(saida, "w", encoding="utf-8"), ensure_ascii=False)
print("janela %s a %s: %d anuncios com entrega | gasto R$%.2f | leads %d | fora do arquivo base: %d" % (
    de, ate, len(por_ad), sum(s for s, _ in por_ad.values()), sum(l for _, l in por_ad.values()), len(faltam)))
