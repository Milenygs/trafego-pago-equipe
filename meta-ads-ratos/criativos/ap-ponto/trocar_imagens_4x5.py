"""Belo 28/09/2026 - troca as imagens 9:16 (cortadas no feed) pelas versoes 4:5 (1080x1350) nos anuncios IMG.

Versoes geradas sem cortar a arte: Azul com laterais na cor do fundo; Fachada com laterais da propria foto desfocada.
Criativo novo identico (textos, titulos, descricoes, CTA, url_tags, opt-outs), so muda o image_hash. Anuncios seguem PAUSED.
"""
import json
import sys
import time
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).parent))
import build_belo_lancamento as lp  # noqa: E402

TOKEN, G, ACT = lp.TOKEN, lp.G, lp.ACT
PASTA = Path(lp.PASTA)
NOVAS = {"c6aaa32c644cfd7966e3222f21f86e4a": PASTA / "Belo - 4x5 feed.png",       # Fachada
         "ee3413bf03630e75650b72f6f90464fc": PASTA / "belo 22 - 4x5 feed.png"}    # Azul
CAMPANHAS = ["120245790359480358", "120245805859660358"]


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


hash_novo = {}
for velho, arq in NOVAS.items():
    with open(arq, "rb") as f:
        r = requests.post(G + ACT + "/adimages", data={"access_token": TOKEN},
                          files={arq.name: (arq.name, f.read(), "image/png")}, timeout=120).json()
    hash_novo[velho] = list(r["images"].values())[0]["hash"]
    print(arq.name, "->", hash_novo[velho])

novo_por_antigo = {}
for camp in CAMPANHAS:
    for a in get(camp + "/ads", fields="id,name,status,adset{name},creative{id}", limit=100)["data"]:
        if not a["name"].startswith("IMG"):
            continue
        old = a["creative"]["id"]
        if old not in novo_por_antigo:
            c = get(old, fields="name,object_story_spec,asset_feed_spec,degrees_of_freedom_spec,url_tags")
            oss = c["object_story_spec"]
            d = oss["link_data"]
            h = d.get("image_hash")
            if h not in hash_novo:
                print("pula (ja trocado ou outra imagem):", a["name"], h)
                novo_por_antigo[old] = old
                continue
            d["image_hash"] = hash_novo[h]
            d.pop("picture", None)
            af = c.get("asset_feed_spec") or {}
            feed = {k: [{"text": x["text"]} for x in af.get(k, [])] for k in ("bodies", "titles", "descriptions") if af.get(k)}
            if feed:
                feed["optimization_type"] = "DEGREES_OF_FREEDOM"
            novo = post(ACT + "/adcreatives", {
                "name": (c.get("name") or a["name"]).split(" 2026-")[0] + " | 4x5",
                "object_story_spec": {"page_id": oss["page_id"], "instagram_user_id": oss.get("instagram_user_id"), "link_data": d},
                **({"asset_feed_spec": feed} if feed else {}),
                **({"degrees_of_freedom_spec": c["degrees_of_freedom_spec"]} if c.get("degrees_of_freedom_spec") else {}),
                **({"url_tags": c["url_tags"]} if c.get("url_tags") else {}),
            })["id"]
            novo_por_antigo[old] = novo
            print("criativo", a["name"], old, "->", novo)
            time.sleep(2)
        if novo_por_antigo[old] != old:
            print("  anuncio", a["adset"]["name"], "|", a["name"], post(a["id"], {"creative": {"creative_id": novo_por_antigo[old]}}, fatal=False))
            time.sleep(2)

print("\n== conferencia")
for camp in CAMPANHAS:
    for a in get(camp + "/ads", fields="name,status,adset{name},creative{object_story_spec{link_data{image_hash,call_to_action}},url_tags}", limit=100)["data"]:
        if a["name"].startswith("IMG"):
            ld = a["creative"]["object_story_spec"]["link_data"]
            print(a["adset"]["name"], "|", a["name"], "|", a["status"], "| img", ld.get("image_hash"),
                  "| cta", ld.get("call_to_action", {}).get("type"), "| utm", bool(a["creative"].get("url_tags")))
