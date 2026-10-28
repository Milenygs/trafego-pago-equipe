"""Belo 15/10/2026 - anuncios do conjunto Noivos Recem-casados Pais Bebe 25-45 (PAUSED).

Pedido da Mileny: o ADS BELO 4 (VID Engenheiro Familia v1, "o lugar da sua familia") e o Leo Aluguel.
Reusa os criativos de LP que ja rodaram na conta, com o mesmo nome (= utm_content no CV).
Confere link, url_tags e OPT_OUT antes de criar.
Uso: python build_belo_casais_ads_1510.py
"""
import json
import os
import sys
from pathlib import Path

import requests

SKILL = Path(os.path.expanduser("~/OneDrive/.claude/skills/meta-ads-ratos"))
env = (SKILL / ".env").read_text(encoding="utf-8")
TOKEN = [l.split("=", 1)[1].strip().strip('"') for l in env.splitlines() if l.startswith("META_ADS_TOKEN")][0]
G = "https://graph.facebook.com/v23.0/"

ACT = "act_1043516946010441"
ADSET = "120246106518310358"  # [BELO] Noivos Recem-casados Pais Bebe 25-45
UTM = "utm_source=meta&utm_medium=paid_social&utm_campaign={{campaign.name}}&utm_term={{adset.name}}&utm_content={{ad.name}}"
CRIATIVOS = {  # nome do anuncio (= utm_content) -> criativo de LP
    "VID Engenheiro Familia v1": "1643017724013945",
    "VID UGC Leo Aluguel v1": "1817675009651382",
}


def post(path, data, fatal=True):
    data = {k: (json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v) for k, v in data.items()}
    data["access_token"] = TOKEN
    r = requests.post(G + path, data=data).json()
    if "error" in r:
        print(json.dumps(r["error"], ensure_ascii=False, indent=1))
        if fatal:
            sys.exit(1)
    return r


def get(path, **params):
    params["access_token"] = TOKEN
    return requests.get(G + path, params=params).json()


def conferir(cr_id):
    cr = get(cr_id, fields="name,url_tags,object_story_spec,asset_feed_spec,degrees_of_freedom_spec")
    if "error" in cr:
        sys.exit(json.dumps(cr["error"], ensure_ascii=False))
    texto = json.dumps(cr, ensure_ascii=False)
    links = sorted({l for l in [cr.get("object_story_spec", {}).get("video_data", {}).get("call_to_action", {})
                                .get("value", {}).get("link")]
                    + [l.get("website_url") for l in cr.get("asset_feed_spec", {}).get("link_urls", [])] if l})
    feats = cr.get("degrees_of_freedom_spec", {}).get("creative_features_spec", {})
    opt_in = [k for k, v in feats.items() if v.get("enroll_status") != "OPT_OUT"]
    corpos = [b.get("text", "") for b in cr.get("asset_feed_spec", {}).get("bodies", [])]
    if not corpos:
        corpos = [cr.get("object_story_spec", {}).get("video_data", {}).get("message", "")]
    print("--", cr_id, cr.get("name"))
    print("   links:", links)
    print("   url_tags ok:", cr.get("url_tags") == UTM)
    print("   recursos fora do OPT_OUT:", opt_in or "nenhum")
    print("   'belo.apponto' no criativo:", "belo.apponto.com.br" in texto)
    for i, c in enumerate(corpos, 1):
        print(f"   corpo {i}:", c.replace("\n", " / ")[:400])
    return cr.get("url_tags") == UTM and "belo.apponto.com.br" in texto and not opt_in


def main():
    if get(ACT, fields="account_status").get("account_status") != 1:
        sys.exit("Conta sem permitir escrita")
    existentes = {a["name"] for a in get(ADSET + "/ads", fields="name").get("data", [])}

    ok = {nome: conferir(cr) for nome, cr in CRIATIVOS.items()}
    if not all(ok.values()):
        sys.exit(f"Criativo fora do padrao, nada criado: {ok}")

    for nome, cr in CRIATIVOS.items():
        if nome in existentes:
            print("ja existe:", nome)
            continue
        ad = post(ACT + "/ads", {"name": nome, "adset_id": ADSET,
                                 "creative": {"creative_id": cr}, "status": "PAUSED"}, fatal=False)
        print("ad", nome, ad.get("id"))

    print(json.dumps(get(ADSET + "/ads", fields="name,status,effective_status,creative{id,url_tags}"),
                     ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
