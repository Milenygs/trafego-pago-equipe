#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cheirin MKT 15/10 - complemento do build_vv_eduardo_1510.py.
O @cheirinbaofranquias (9317933804989351) nao e origem permitida na MKT (#2654 / 1713140), entao o publico de 120D
dele vem da MT por compartilhamento (como o IG_engja_franquiacheirin). Depois o conjunto recebe o targeting inteiro.
"""
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_vv_eduardo_1510 as b  # noqa: E402

FRANQUIAS_MT = "120258417971430212"   # [IG CB FRANQUIAS] Envolvimento todos - 120D (MT, 16-19 mil)
MKT_NUM = "1398047248415230"


def get(path, **params):
    params["access_token"] = b.TOKEN
    try:
        with urllib.request.urlopen(b.API + path + "?" + urllib.parse.urlencode(params), timeout=120) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        return {"ERRO": json.loads(e.read().decode("utf-8")).get("error")}


def main():
    e = json.load(open(b.ESTADO, encoding="utf-8"))
    if not e.get("pub_franquias_compartilhado"):
        r = b.post(FRANQUIAS_MT + "/adaccounts", {"adaccounts": [MKT_NUM]}, "compartilha CB Franquias 120D com a MKT")
        if r is None:
            # o endpoint devolve {"success": true} sem id: conferir pela lista da MKT
            pass
        time.sleep(5)
        lista = get(b.CONTA + "/customaudiences", fields="id,name", limit=200).get("data", [])
        if any(a["id"] == FRANQUIAS_MT for a in lista):
            e["pub_franquias_compartilhado"] = FRANQUIAS_MT
            b.salva(e)
            print("  OK   CB Franquias 120D visivel na MKT")
        else:
            print("  CB Franquias 120D NAO aparece na MKT")
    publicos = [e[k] for k in ("pub_cb", "pub_franquias", "pub_franquias_compartilhado", "pub_wilton") if e.get(k)]
    targeting = {
        "age_min": 25, "age_max": 55,
        "geo_locations": {"countries": ["BR"], "location_types": ["home", "recent"]},
        "custom_audiences": [{"id": i} for i in publicos],
        "publisher_platforms": ["instagram"],
        "instagram_positions": ["stream", "story", "explore", "reels", "explore_home", "profile_feed"],
        "device_platforms": ["mobile", "desktop"],
        "targeting_relaxation_types": {"lookalike": 0, "custom_audience": 0},
        "targeting_automation": {"advantage_audience": 0, "individual_setting": {"age": 0, "gender": 0, "geo": 0}},
    }
    if len(publicos) > 1:
        b.post(e["conjunto"], {"targeting": targeting}, "conjunto: publicos %s" % ",".join(publicos))
    print(json.dumps(get(e["conjunto"], fields="name,status,effective_status,daily_budget,optimization_goal,billing_event,"
                                           "bid_strategy,destination_type,targeting"), ensure_ascii=False, indent=1))
    print(json.dumps(get(e["campanha"], fields="name,status,objective,buying_type"), ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
