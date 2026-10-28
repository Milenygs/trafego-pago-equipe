#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cheirin MKT 16/10 - Mileny: "temos que usar o publico do eduardo de engajamento e do wilton tb" / "temos esse publico na
outra conta MT". Compartilha da MT para a MKT e poe no conjunto da campanha THRUPLAY do reel do Eduardo.
  - IG_ENGAJ_EDU_180D 120253568067060212 (dono: MT)
  - PEPA C WILTON - 180DD 120216708550400602 (dono: act_825937812666250, so compartilhado com a MT; pode nao repassar)
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

MKT_NUM = "1398047248415230"
NOVOS = [("pub_edu_engaj_180d", "120253568067060212", "IG_ENGAJ_EDU_180D"),
         ("pub_wilton_engaj_180d", "120216708550400602", "PEPA C WILTON - 180DD")]


def get(path, **params):
    params["access_token"] = b.TOKEN
    try:
        with urllib.request.urlopen(b.API + path + "?" + urllib.parse.urlencode(params), timeout=120) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        return {"ERRO": json.loads(e.read().decode("utf-8")).get("error")}


def main():
    e = json.load(open(b.ESTADO, encoding="utf-8"))
    for chave, aud, nome in NOVOS:
        if e.get(chave):
            continue
        b.post(aud + "/adaccounts", {"adaccounts": [MKT_NUM]}, "compartilha %s com a MKT" % nome)
    time.sleep(5)
    na_mkt = {a["id"] for a in get(b.CONTA + "/customaudiences", fields="id", limit=200).get("data", [])}
    for chave, aud, nome in NOVOS:
        if aud in na_mkt:
            e[chave] = aud
            print("  OK   %s visivel na MKT" % nome)
        else:
            print("  NAO  %s nao aparece na MKT" % nome)
    b.salva(e)

    publicos = [e[k] for k in ("pub_cb", "pub_franquias_compartilhado", "pub_edu_engaj_180d", "pub_wilton_engaj_180d") if e.get(k)]
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
    nome = "Quente (Cheirin oficial 120D + CB Franquias 120D + Edu engaj 180D%s) | BR | 25-55 | IG | R$100" % (
        " + Wilton engaj 180D" if e.get("pub_wilton_engaj_180d") else "")
    b.post(e["conjunto"], {"targeting": targeting, "name": nome}, "conjunto: %d publicos" % len(publicos))
    print(json.dumps(get(e["conjunto"], fields="name,status,daily_budget,targeting{custom_audiences,geo_locations,age_min,age_max,"
                                           "targeting_automation,targeting_relaxation_types}"), ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
