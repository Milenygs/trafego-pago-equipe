"""Belo 15/10/2026 (Mileny): teste da imagem "Vantagens 60x" (arte dela) no Remarketing 180D da LP.

Um anuncio so, PAUSED, com a imagem 4:5 nos feeds e a 9:16 em stories/reels (asset_customization_rules).
Textos: os 3 corpos / 5 titulos / 3 descricoes ja aprovados do `IMG Lancamento Fachada v1` (criativo 1762171538400054).
Se a Meta recusar varios textos com regra de posicionamento, cai para 1 corpo / 1 titulo / 1 descricao.
Link da LP com a UTM dinamica do Belo (url_tags), CTA Saiba mais, IA toda em OPT_OUT (copiada do criativo de referencia).
Nome do anuncio = utm_content: `IMG Vantagens 60x v1`.
"""
import base64
import json
import os
import sys
import time
from pathlib import Path

import requests

sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
env = (Path(os.path.expanduser("~/OneDrive/.claude/skills/meta-ads-ratos")) / ".env").read_text(encoding="utf-8")
TOKEN = [l.split("=", 1)[1].strip().strip('"') for l in env.splitlines() if l.startswith("META_ADS_TOKEN")][0]
G = "https://graph.facebook.com/v23.0/"
ACT = "act_1043516946010441"
RMKT = "120245790367990358"
REF = "1762171538400054"  # IMG Lancamento Fachada v1
PAGINA = "198169833565944"
INSTAGRAM = "17841401339383360"
LP = "https://belo.apponto.com.br/"
NOME = "IMG Vantagens 60x v1"
PASTA = Path(os.path.expanduser("~/OneDrive/Carteira/outros/ap-ponto/criativos/2026-10-teste-estatico-carrossel"))
FEED = PASTA / "IMG_Vantagens_60x_v1_feed_1080x1350.png"
STORY = PASTA / "IMG_Vantagens_60x_v1_story_1080x1920.png"


def get(path, **p):
    p["access_token"] = TOKEN
    return requests.get(G + path, params=p, timeout=180).json()


def post(path, data):
    data = {k: (json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v) for k, v in data.items()}
    data["access_token"] = TOKEN
    return requests.post(G + path, data=data, timeout=300).json()


def subir(arq):
    r = post(ACT + "/adimages", {"bytes": base64.b64encode(arq.read_bytes()).decode(), "name": arq.name})
    if "error" in r:
        sys.exit(f"ERRO upload {arq.name}: {json.dumps(r['error'], ensure_ascii=False)[:400]}")
    img = list(r["images"].values())[0]
    print("imagem:", arq.name, "| hash", img["hash"])
    return img["hash"]


existentes = [a["name"] for a in get(RMKT + "/ads", fields="name", limit=100).get("data", [])]
if NOME in existentes:
    sys.exit(f"{NOME} ja existe no Remarketing")

ref = get(REF, fields="asset_feed_spec,degrees_of_freedom_spec,url_tags")
h_feed, h_story = subir(FEED), subir(STORY)

REGRAS = [
    {"customization_spec": {"publisher_platforms": ["facebook", "instagram"],
                            "facebook_positions": ["story", "facebook_reels"],
                            "instagram_positions": ["story", "reels"]},
     "image_label": {"name": "img_story"}, "priority": 1},
    {"customization_spec": {"publisher_platforms": ["facebook", "instagram", "audience_network"],
                            "facebook_positions": ["feed", "right_hand_column"],
                            "instagram_positions": ["stream", "profile_feed"],
                            "audience_network_positions": ["classic"]},
     "image_label": {"name": "img_feed"}, "priority": 2},
]


def afs(bodies, titles, descriptions):
    return {
        "images": [{"hash": h_feed, "adlabels": [{"name": "img_feed"}]},
                   {"hash": h_story, "adlabels": [{"name": "img_story"}]}],
        "bodies": bodies, "titles": titles, "descriptions": descriptions,
        "link_urls": [{"website_url": LP}],
        "call_to_action_types": ["LEARN_MORE"],
        "ad_formats": ["SINGLE_IMAGE"],
        "asset_customization_rules": REGRAS,
    }


base = ref["asset_feed_spec"]
tentativas = [
    ("3 corpos / 5 titulos / 3 descricoes", afs(base["bodies"], base["titles"], base["descriptions"])),
    ("1 corpo / 1 titulo / 1 descricao", afs(base["bodies"][:1], [{"text": "Simule com a renda da sua família"}],
                                            [{"text": "Lançamento em Vespasiano"}])),
]
criativo = None
for rotulo, spec in tentativas:
    r = post(ACT + "/adcreatives", {
        "name": f"{NOME} | BELO OUT26 | facilidades | 4x5 feed + 9x16 stories/reels | CTA simulacao",
        "object_story_spec": {"page_id": PAGINA, "instagram_user_id": INSTAGRAM},
        "asset_feed_spec": spec,
        "degrees_of_freedom_spec": ref["degrees_of_freedom_spec"],
        "url_tags": ref["url_tags"],
    })
    if "error" in r:
        e = r["error"]
        print("criativo recusado (", rotulo, "):", e.get("error_subcode"), e.get("error_user_msg") or e.get("message"))
        time.sleep(2)
        continue
    criativo = r["id"]
    print("criativo:", criativo, "|", rotulo)
    break
if not criativo:
    sys.exit("nenhum criativo aceito, nada criado")

ad = post(ACT + "/ads", {"name": NOME, "adset_id": RMKT, "creative": {"creative_id": criativo}, "status": "PAUSED"})
if "error" in ad:
    e = ad["error"]
    sys.exit(f"ERRO anuncio: {e.get('error_subcode')} {e.get('error_user_msg') or e.get('message')}")
print("anuncio PAUSED:", ad["id"])
time.sleep(3)

# conferir
c = get(criativo, fields="asset_feed_spec,url_tags,degrees_of_freedom_spec")
a = c["asset_feed_spec"]
ia_on = [k for k, v in (c.get("degrees_of_freedom_spec") or {}).get("creative_features_spec", {}).items()
         if v.get("enroll_status") != "OPT_OUT"]
print("imagens:", [(i.get("hash"), [l["name"] for l in i.get("adlabels", [])]) for i in a.get("images", [])])
print("regras:", json.dumps(a.get("asset_customization_rules"), ensure_ascii=False))
print("link:", a.get("link_urls"), "| cta:", a.get("call_to_action_types"))
print("textos:", len(a.get("bodies", [])), "corpos,", len(a.get("titles", [])), "titulos,", len(a.get("descriptions", [])), "descricoes")
print("url_tags ok:", "utm_content={{ad.name}}" in (c.get("url_tags") or ""), "| IA ligada:", ia_on or "nenhuma")
s = get(ad["id"], fields="name,status,effective_status,issues_info")
print("anuncio:", json.dumps(s, ensure_ascii=False))
