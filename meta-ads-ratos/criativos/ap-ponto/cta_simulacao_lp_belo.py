"""Belo 28/09/2026 - CTA "faca sua simulacao" nos anuncios da LP (pedido da Mileny, depois da leitura do criativo campeao).

- Fim de todo texto: "👇 Faça sua simulação agora mesmo: é rápido e sem cadastro." + "*Consulte condições."
- Titulo "A 2 min do ônibus, a 15 de Confins" -> "Faça sua simulação agora" (fica ao lado do botao).
- Botao continua Saiba mais (o Meta nao tem botao "Simular").
- Troca o criativo dos anuncios Leo, Engenheiro e IMG. A Locucao (campea) NAO e trocada: ganha uma v2 PAUSED
  ao lado em cada conjunto, para comparar sem perder o engajamento/aprendizado da v1.
Uso: python cta_simulacao_lp_belo.py [--dry]
"""
import json
import sys
import time
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).parent))
import build_belo_lancamento as lp  # noqa: E402

TOKEN, G, ACT = lp.TOKEN, lp.G, lp.ACT
CAMP_LP = "120245790359480358"
# 28/09: a Mileny pediu o CTA IGUAL ao do criativo campeao (texto na tela e fala da Locucao)
CTA = "👇 Faça uma simulação agora mesmo."
TITULOS_VELHOS = ("A 2 min do ônibus, a 15 de Confins", "Faça sua simulação agora")
TITULO_NOVO = "Faça uma simulação agora mesmo"
TITULO_VELHO = TITULOS_VELHOS[0]
CAMPEAO = "VID Locucao Lancamento v1"
V2 = "VID Locucao Lancamento v2"


def novo_texto(b):
    linhas = b.rstrip().split("\n")
    if linhas and linhas[-1].startswith("*Consulte"):
        linhas.pop()
    while linhas and ("👇" in linhas[-1] or not linhas[-1].strip()):
        linhas.pop()
    return "\n".join(linhas) + "\n\n" + CTA + "\n*Consulte condições."


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


def criativo_novo(old_id, nome_ad, dry):
    c = get(old_id, fields="name,object_story_spec,asset_feed_spec,degrees_of_freedom_spec,url_tags")
    oss = c["object_story_spec"]
    chave = "video_data" if "video_data" in oss else "link_data"
    d = oss[chave]
    if chave == "video_data" and d.get("image_hash"):
        d.pop("image_url", None)
    af = c.get("asset_feed_spec") or {}
    bodies = [novo_texto(x["text"]) for x in af.get("bodies", [])]
    titles = [TITULO_NOVO if x["text"] in TITULOS_VELHOS else x["text"] for x in af.get("titles", [])]
    if TITULO_NOVO not in titles:
        titles = titles[:4] + [TITULO_NOVO]
    descs = [x["text"] for x in af.get("descriptions", [])]
    if dry:
        print(f"--- {nome_ad} ({old_id})")
        for b in bodies:
            print("   ...", b[-160:].replace("\n", " / "))
        print("   titulos:", titles)
        return None
    feed = {"bodies": [{"text": b} for b in bodies], "titles": [{"text": t} for t in titles],
            "descriptions": [{"text": x} for x in descs], "optimization_type": "DEGREES_OF_FREEDOM"}
    return post(ACT + "/adcreatives", {
        "name": (c.get("name") or nome_ad).split(" 2026-")[0] + " | CTA simulacao",
        "object_story_spec": {"page_id": oss["page_id"], "instagram_user_id": oss.get("instagram_user_id"), chave: d},
        "asset_feed_spec": feed,
        **({"degrees_of_freedom_spec": c["degrees_of_freedom_spec"]} if c.get("degrees_of_freedom_spec") else {}),
        **({"url_tags": c["url_tags"]} if c.get("url_tags") else {}),
    })["id"]


def main():
    dry = "--dry" in sys.argv
    ads = get(CAMP_LP + "/ads", fields="id,name,status,adset{id,name},creative{id}", limit=100)["data"]
    v2_por_conjunto = {a["adset"]["id"]: a["id"] for a in ads if a["name"] == V2}  # de uma rodada anterior
    novos = {}
    for a in ads:
        if a["name"] == V2:
            continue  # tratado junto com o v1 do mesmo conjunto
        old = a["creative"]["id"]
        if old not in novos:
            novos[old] = criativo_novo(old, a["name"], dry)
            time.sleep(2)
        if dry:
            continue
        if a["name"] == CAMPEAO:
            sid = a["adset"]["id"]
            if sid in v2_por_conjunto:
                r = post(v2_por_conjunto[sid], {"creative": {"creative_id": novos[old]}}, fatal=False)
                print(f"v2 ja existia em {a['adset']['name']}: criativo trocado {r}")
            else:
                r = post(ACT + "/ads", {"name": V2, "adset_id": sid,
                                        "creative": {"creative_id": novos[old]}, "status": "PAUSED"}, fatal=False)
                print(f"v2 PAUSED {a['adset']['name']}: {r.get('id')} (v1 {a['id']} mantido)")
        else:
            r = post(a["id"], {"creative": {"creative_id": novos[old]}}, fatal=False)
            print(f"troca {a['adset']['name']} | {a['name']} ({a['status']}): {r}")
        time.sleep(2)


if __name__ == "__main__":
    main()
